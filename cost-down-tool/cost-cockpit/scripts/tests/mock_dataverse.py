"""Minimal in-memory stand-in for the Dataverse Web API metadata endpoints.

It enforces the ordering rules that matter for provisioning (a column needs its table, a choice column
needs its global choice, a lookup needs both tables, a key needs its columns), so the provisioning
plan can be tested without an environment.
"""
from __future__ import annotations

import json
import re
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class State:
    def __init__(self):
        self.publishers, self.solutions = {}, {}
        self.choices, self.tables, self.relationships = {}, {}, {}
        self.requests, self.published = [], 0
        self.rows = {}          # entity set -> list of row dicts
        self.solution_header_missing = []


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, code, body=None, headers=None):
            raw = json.dumps(body).encode() if body is not None else b""
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(raw)

        def _err(self, code, msg):
            self._send(code, {"error": {"code": "0x0", "message": msg}})

        def _path(self):
            p = urllib.parse.unquote(self.path)
            assert p.startswith("/api/data/v9.2/"), p
            return p[len("/api/data/v9.2/"):]

        def do_GET(self):
            p = self._path()
            state.requests.append(("GET", p))
            if not self.headers.get("Authorization", "").startswith("Bearer ") and not self.headers.get("X-Test-Cookie"):
                return self._err(401, "no auth")
            if p == "WhoAmI":
                return self._send(200, {"UserId": "00000000-0000-0000-0000-000000000001"})
            m = re.fullmatch(r"(publishers|solutions)\?\$select=\w+&\$filter=uniquename eq '([^']+)'", p)
            if m:
                store = state.publishers if m.group(1) == "publishers" else state.solutions
                row = store.get(m.group(2))
                return self._send(200, {"value": [row] if row else []})
            m = re.fullmatch(r"GlobalOptionSetDefinitions\(Name='([^']+)'\)", p)
            if m:
                return self._send(200, state.choices[m.group(1)]) if m.group(1) in state.choices else self._err(404, "Could not find optionset")
            m = re.fullmatch(r"EntityDefinitions\(LogicalName='([^']+)'\)\?\$select=EntitySetName", p)
            if m:
                if m.group(1) not in state.tables:
                    return self._err(404, "does not exist")
                return self._send(200, {"EntitySetName": m.group(1) + "s"})
            m = re.fullmatch(r"(cdt_\w+)\?\$select=(\w+)&\$filter=(\w+) eq '((?:[^']|'')*)'&\$top=1", p)
            if m:
                rows = [r for r in state.rows.get(m.group(1), []) if r.get(m.group(3)) == m.group(4).replace("''", "'")]
                return self._send(200, {"value": [{m.group(2): r["_id"]} for r in rows[:1]]})
            m = re.fullmatch(r"EntityDefinitions\(LogicalName='([^']+)'\)\?\$select=LogicalName", p)
            if m:
                return self._send(200, {"LogicalName": m.group(1)}) if m.group(1) in state.tables else self._err(404, "does not exist")
            m = re.fullmatch(r"EntityDefinitions\(LogicalName='([^']+)'\)/Attributes\(LogicalName='([^']+)'\)\?\$select=LogicalName", p)
            if m:
                t = state.tables.get(m.group(1))
                if t is None:
                    return self._err(404, "table does not exist")
                return self._send(200, {"LogicalName": m.group(2)}) if m.group(2) in t["attributes"] else self._err(404, "Could not find attribute")
            m = re.fullmatch(r"RelationshipDefinitions\(SchemaName='([^']+)'\)\?\$select=SchemaName", p)
            if m:
                return self._send(200, {"SchemaName": m.group(1)}) if m.group(1) in state.relationships else self._err(404, "Could not find relationship")
            m = re.fullmatch(r"EntityDefinitions\(LogicalName='([^']+)'\)/Keys\?\$select=SchemaName", p)
            if m:
                t = state.tables.get(m.group(1))
                if t is None:
                    return self._err(404, "table does not exist")
                return self._send(200, {"value": [{"SchemaName": k} for k in t["keys"]]})
            return self._err(400, "mock: unknown GET " + p)

        def _check_row(self, entity_set, body):
            table = state.tables.get(entity_set[:-1])
            if table is None:
                return "unknown entity set " + entity_set
            for key, value in body.items():
                if key.endswith("@odata.bind"):
                    mm = re.fullmatch(r"/(cdt_\w+)\((\w+)='((?:[^']|'')*)'\)", value)
                    if not mm:
                        return "bad bind " + value
                    if key[:-len("@odata.bind")].lower() not in table["attributes"]:
                        return "unknown navigation property " + key
                    if not any(r.get(mm.group(2)) == mm.group(3) for r in state.rows.get(mm.group(1), [])):
                        return "bind target not found: " + value
                elif key not in table["attributes"]:
                    return "unknown column " + key
            return None

        def do_PATCH(self):
            p = self._path()
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0")) or 0) or b"{}")
            state.requests.append(("PATCH", p))
            m = re.fullmatch(r"(cdt_\w+)\((\w+)='((?:[^']|'')*)'\)", p) or re.fullmatch(r"(cdt_\w+)\(()([0-9a-f-]{36})\)", p)
            if not m:
                return self._err(400, "mock: unknown PATCH " + p)
            entity_set, col, value = m.group(1), m.group(2), m.group(3).replace("''", "'")
            problem = self._check_row(entity_set, body)
            if problem:
                return self._err(400, problem)
            rows = state.rows.setdefault(entity_set, [])
            if col:
                table = state.tables[entity_set[:-1]]
                if not any(col in k for k in table["key_columns"]):
                    return self._err(400, f"{col} is not an alternate key of {entity_set}")
                row = next((r for r in rows if r.get(col) == value), None)
            else:
                row = next((r for r in rows if r["_id"] == value), None)
            if row is None:
                row = {"_id": f"{len(rows) + 1:08d}-0000-0000-0000-000000000000"}
                rows.append(row)
            row.update(body)
            if col:
                row[col] = value
            return self._send(204)

        def do_POST(self):
            p = self._path()
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0")) or 0) or b"{}")
            state.requests.append(("POST", p))
            sol = self.headers.get("MSCRM.SolutionUniqueName")
            ok = lambda eid="": self._send(204, None, {"OData-EntityId": f"http://mock/api/data/v9.2/x({eid or '11111111-1111-1111-1111-111111111111'})"})
            if p == "publishers":
                state.publishers[body["uniquename"]] = dict(body, publisherid="22222222-2222-2222-2222-222222222222")
                return ok("22222222-2222-2222-2222-222222222222")
            if p == "solutions":
                if body.get("publisherid@odata.bind") != "/publishers(22222222-2222-2222-2222-222222222222)":
                    return self._err(400, "bad publisher bind " + str(body.get("publisherid@odata.bind")))
                state.solutions[body["uniquename"]] = dict(body, solutionid="33333333-3333-3333-3333-333333333333")
                return ok()
            if p == "PublishAllXml":
                state.published += 1
                return ok()
            if re.fullmatch(r"cdt_\w+", p):
                problem = self._check_row(p, body)
                if problem:
                    return self._err(400, problem)
                rows = state.rows.setdefault(p, [])
                rows.append(dict(body, _id=f"{len(rows) + 1:08d}-0000-0000-0000-000000000000"))
                return ok()
            if sol not in state.solutions:
                state.solution_header_missing.append(p)
                return self._err(400, "solution header missing or unknown")
            if p == "GlobalOptionSetDefinitions":
                if not body.get("Options") or body.get("OptionSetType") != "Picklist":
                    return self._err(400, "bad option set")
                state.choices[body["Name"]] = body
                return ok()
            if p == "EntityDefinitions":
                attrs = body.get("Attributes", [])
                if len(attrs) != 1 or not attrs[0].get("IsPrimaryName"):
                    return self._err(400, "primary name attribute missing")
                logical = body["SchemaName"].lower()
                state.tables[logical] = {"attributes": {attrs[0]["SchemaName"].lower(), logical + "id"}, "keys": set(), "key_columns": []}
                return ok()
            m = re.fullmatch(r"EntityDefinitions\(LogicalName='([^']+)'\)/Attributes", p)
            if m:
                t = state.tables.get(m.group(1))
                if t is None:
                    return self._err(404, "table does not exist")
                if "@odata.type" not in body or "SchemaName" not in body:
                    return self._err(400, "bad attribute")
                bind = body.get("GlobalOptionSet@odata.bind")
                if body["AttributeType"] == "Picklist":
                    mm = re.fullmatch(r"/GlobalOptionSetDefinitions\(Name='([^']+)'\)", bind or "")
                    if not mm or mm.group(1) not in state.choices:
                        return self._err(400, "global option set not found: " + str(bind))
                t["attributes"].add(body["SchemaName"].lower())
                return ok()
            if p == "RelationshipDefinitions":
                ref, refing = body["ReferencedEntity"], body["ReferencingEntity"]
                if ref not in state.tables or refing not in state.tables:
                    return self._err(400, f"entity missing for relationship {ref} -> {refing}")
                if body["ReferencedAttribute"] not in state.tables[ref]["attributes"]:
                    return self._err(400, "referenced attribute missing")
                if len(body["SchemaName"]) > 100:
                    return self._err(400, "relationship name too long")
                state.relationships[body["SchemaName"]] = body
                state.tables[refing]["attributes"].add(body["Lookup"]["SchemaName"].lower())
                return ok()
            m = re.fullmatch(r"EntityDefinitions\(LogicalName='([^']+)'\)/Keys", p)
            if m:
                t = state.tables.get(m.group(1))
                if t is None:
                    return self._err(404, "table does not exist")
                for col in body["KeyAttributes"]:
                    if col not in t["attributes"]:
                        return self._err(400, "key column missing: " + col)
                t["keys"].add(body["SchemaName"])
                t["key_columns"].append(body["KeyAttributes"])
                return ok()
            return self._err(400, "mock: unknown POST " + p)

    return Handler


def start():
    state = State()
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, state
