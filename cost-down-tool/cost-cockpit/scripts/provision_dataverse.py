#!/usr/bin/env python3
"""Create the Cost Cockpit data model in a Dataverse environment.

Reads schema/cost_cockpit.schema.json and creates, through the Dataverse Web API:
publisher, solution, global choices, tables, columns, lookups and alternate keys.
The script is idempotent: whatever already exists is skipped, so it can be re-run.

It uses only the Python standard library.

Typical use
-----------
1. Dry run (no connection, writes every request to out/payloads for review):

       python provision_dataverse.py --dry-run

2. Real run with an access token for the environment:

       az login
       python provision_dataverse.py --url https://<org>.crm4.dynamics.com --use-az

   or, with a token you obtained yourself (PowerShell: Get-AzAccessToken -ResourceUrl <url>):

       set DATAVERSE_TOKEN=<token>
       python provision_dataverse.py --url https://<org>.crm4.dynamics.com

3. Check what exists without changing anything:

       python provision_dataverse.py --url https://<org>.crm4.dynamics.com --use-az --check

Formula columns are not created by this script. They are listed at the end of the run
and described in docs/03-data-dictionary.md; create them in the maker portal.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMA = HERE.parent / "schema" / "cost_cockpit.schema.json"
API = "/api/data/v9.2/"


# --------------------------------------------------------------------------- payload builders
def label(text: str, lcid: int) -> dict:
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [
            {"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": text, "LanguageCode": lcid}
        ],
    }


def required_level(required: bool) -> dict:
    return {
        "Value": "ApplicationRequired" if required else "None",
        "CanBeChanged": True,
        "ManagedPropertyLogicalName": "canmodifyrequirementlevelsettings",
    }


def primary_attribute(table: dict, lcid: int) -> dict:
    prim = table["primary"]
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "AttributeType": "String",
        "AttributeTypeName": {"Value": "StringType"},
        "SchemaName": prim["schema"],
        "IsPrimaryName": True,
        "MaxLength": prim["maxlen"],
        "FormatName": {"Value": "Text"},
        "RequiredLevel": required_level(True),
        "DisplayName": label(prim["display"], lcid),
        "Description": label(f"Primary name of {table['display']}", lcid),
    }


def table_payload(table: dict, lcid: int) -> dict:
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
        "SchemaName": table["schema"],
        "DisplayName": label(table["display"], lcid),
        "DisplayCollectionName": label(table["plural"], lcid),
        "Description": label(table["description"], lcid),
        "OwnershipType": table.get("ownership", "UserOwned"),
        "IsActivity": False,
        "HasActivities": False,
        "HasNotes": False,
        "Attributes": [primary_attribute(table, lcid)],
    }


def column_payload(col: dict, lcid: int) -> dict:
    base = {
        "SchemaName": col["schema"],
        "DisplayName": label(col["display"], lcid),
        "Description": label(col.get("description") or col["display"], lcid),
        "RequiredLevel": required_level(bool(col.get("required"))),
    }
    kind = col["type"]
    if kind == "text":
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
            "AttributeType": "String",
            "AttributeTypeName": {"Value": "StringType"},
            "FormatName": {"Value": "Text"},
            "MaxLength": col["maxlen"],
        })
    elif kind == "memo":
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
            "AttributeType": "Memo",
            "AttributeTypeName": {"Value": "MemoType"},
            "Format": "TextArea",
            "ImeMode": "Disabled",
            "MaxLength": col["maxlen"],
        })
    elif kind == "decimal":
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
            "AttributeType": "Decimal",
            "AttributeTypeName": {"Value": "DecimalType"},
            "MinValue": col["min"],
            "MaxValue": col["max"],
            "Precision": col["precision"],
        })
    elif kind == "int":
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
            "AttributeType": "Integer",
            "AttributeTypeName": {"Value": "IntegerType"},
            "MinValue": col["min"],
            "MaxValue": col["max"],
            "Format": "None",
            "SourceTypeMask": 0,
        })
    elif kind == "bool":
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
            "AttributeType": "Boolean",
            "AttributeTypeName": {"Value": "BooleanType"},
            "DefaultValue": bool(col.get("default")),
            "OptionSet": {
                "TrueOption": {"Value": 1, "Label": label("Yes", lcid)},
                "FalseOption": {"Value": 0, "Label": label("No", lcid)},
                "OptionSetType": "Boolean",
            },
        })
    elif kind in ("date", "datetime"):
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
            "AttributeType": "DateTime",
            "AttributeTypeName": {"Value": "DateTimeType"},
            "Format": "DateOnly" if kind == "date" else "DateAndTime",
        })
    elif kind == "choice":
        base.update({
            "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
            "AttributeType": "Picklist",
            "AttributeTypeName": {"Value": "PicklistType"},
            "SourceTypeMask": 0,
            "GlobalOptionSet@odata.bind": f"/GlobalOptionSetDefinitions(Name='{col['choice']}')",
        })
    else:
        raise ValueError(f"Unknown column type {kind!r} for {col['schema']}")
    return base


def choice_payload(name: str, choice: dict, lcid: int) -> dict:
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
        "Name": name,
        "DisplayName": label(choice["label"], lcid),
        "Description": label(choice["label"], lcid),
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [{"Value": o["value"], "Label": label(o["label"], lcid)} for o in choice["options"]],
    }


def relationship_name(table: dict, lk: dict) -> str:
    return f"{lk['target']}_{table['schema']}_{lk['schema'].split('_', 1)[1]}".replace("__", "_")


def relationship_payload(table: dict, lk: dict, tables_by_logical: dict, lcid: int) -> dict:
    target = tables_by_logical[lk["target"]]
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
        "SchemaName": relationship_name(table, lk),
        "ReferencedEntity": lk["target"],
        "ReferencedAttribute": lk["target"] + "id",
        "ReferencingEntity": table["schema"].lower(),
        "ReferencingEntityNavigationPropertyName": lk["schema"],
        "AssociatedMenuConfiguration": {
            "Behavior": "UseCollectionName",
            "Group": "Details",
            "Label": label(table["plural"], lcid),
            "Order": 10000,
        },
        "CascadeConfiguration": {
            "Assign": "NoCascade",
            "Delete": lk.get("delete", "RemoveLink"),
            "Merge": "NoCascade",
            "Reparent": "NoCascade",
            "Share": "NoCascade",
            "Unshare": "NoCascade",
        },
        "Lookup": {
            "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
            "AttributeType": "Lookup",
            "AttributeTypeName": {"Value": "LookupType"},
            "SchemaName": lk["schema"],
            "DisplayName": label(lk["display"], lcid),
            "Description": label(lk.get("description") or f"{lk['display']} ({target['display']})", lcid),
            "RequiredLevel": required_level(bool(lk.get("required"))),
        },
    }


def key_payload(k: dict, lcid: int) -> dict:
    return {"SchemaName": k["schema"], "DisplayName": label(k["display"], lcid), "KeyAttributes": k["columns"]}


# --------------------------------------------------------------------------- plan
def build_plan(schema: dict) -> list[dict]:
    """Return the ordered list of steps. Each step knows how to check for existence and how to create."""
    lcid = schema.get("language_code", 1033)
    pub, sol = schema["publisher"], schema["solution"]
    tables_by_logical = {t["schema"].lower(): t for t in schema["tables"]}
    steps: list[dict] = []

    steps.append({
        "kind": "publisher", "name": pub["uniquename"],
        "exists": f"publishers?$select=publisherid&$filter=uniquename eq '{pub['uniquename']}'",
        "exists_mode": "collection",
        "post": "publishers",
        "body": {
            "uniquename": pub["uniquename"], "friendlyname": pub["friendlyname"],
            "customizationprefix": pub["prefix"], "customizationoptionvalueprefix": pub["optionvalueprefix"],
        },
        "in_solution": False,
    })
    steps.append({
        "kind": "solution", "name": sol["uniquename"],
        "exists": f"solutions?$select=solutionid&$filter=uniquename eq '{sol['uniquename']}'",
        "exists_mode": "collection",
        "post": "solutions",
        "body": {
            "uniquename": sol["uniquename"], "friendlyname": sol["friendlyname"], "version": sol["version"],
            "publisherid@odata.bind": "/publishers(<publisherid>)",
        },
        "in_solution": False,
    })
    for name, choice in schema["choices"].items():
        steps.append({
            "kind": "choice", "name": name,
            "exists": f"GlobalOptionSetDefinitions(Name='{name}')",
            "exists_mode": "single",
            "post": "GlobalOptionSetDefinitions",
            "body": choice_payload(name, choice, lcid),
            "in_solution": True,
        })
    for t in schema["tables"]:
        logical = t["schema"].lower()
        steps.append({
            "kind": "table", "name": logical,
            "exists": f"EntityDefinitions(LogicalName='{logical}')?$select=LogicalName",
            "exists_mode": "single",
            "post": "EntityDefinitions",
            "body": table_payload(t, lcid),
            "in_solution": True,
        })
    for t in schema["tables"]:
        logical = t["schema"].lower()
        for col in t["columns"]:
            steps.append({
                "kind": "column", "name": f"{logical}.{col['schema'].lower()}",
                "exists": f"EntityDefinitions(LogicalName='{logical}')/Attributes(LogicalName='{col['schema'].lower()}')?$select=LogicalName",
                "exists_mode": "single",
                "post": f"EntityDefinitions(LogicalName='{logical}')/Attributes",
                "body": column_payload(col, lcid),
                "in_solution": True,
            })
    for t in schema["tables"]:
        logical = t["schema"].lower()
        for lk in t["lookups"]:
            rel = relationship_name(t, lk)
            steps.append({
                "kind": "lookup", "name": f"{logical}.{lk['schema'].lower()}",
                "exists": f"RelationshipDefinitions(SchemaName='{rel}')?$select=SchemaName",
                "exists_mode": "single",
                "post": "RelationshipDefinitions",
                "body": relationship_payload(t, lk, tables_by_logical, lcid),
                "in_solution": True,
            })
    for t in schema["tables"]:
        logical = t["schema"].lower()
        for k in t["keys"]:
            steps.append({
                "kind": "key", "name": f"{logical}.{k['schema'].lower()}",
                "exists": f"EntityDefinitions(LogicalName='{logical}')/Keys?$select=SchemaName",
                "exists_mode": "key-list",
                "key_schema": k["schema"],
                "post": f"EntityDefinitions(LogicalName='{logical}')/Keys",
                "body": key_payload(k, lcid),
                "in_solution": True,
                "optional": True,
            })
    return steps


# --------------------------------------------------------------------------- HTTP client
class Dataverse:
    def __init__(self, url: str, token: str, solution: str, timeout: int = 120):
        self.base = url.rstrip("/") + API
        self.token = token
        self.solution = solution
        self.timeout = timeout

    def _request(self, method: str, path: str, body: dict | None = None, in_solution: bool = False):
        url = self.base + urllib.parse.quote(path, safe="/()'=?&$,@:._-")
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        if in_solution:
            headers["MSCRM.SolutionUniqueName"] = self.solution
        for attempt in range(6):
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read()
                    return resp.status, (json.loads(raw) if raw else None), dict(resp.headers)
            except urllib.error.HTTPError as err:
                raw = err.read()
                if err.code in (429, 503) and attempt < 5:
                    wait = int(err.headers.get("Retry-After", "5"))
                    print(f"    service protection limit, waiting {wait}s")
                    time.sleep(wait)
                    continue
                try:
                    detail = json.loads(raw)
                except Exception:
                    detail = raw.decode("utf-8", "replace")
                return err.code, detail, dict(err.headers)
        raise RuntimeError("retries exhausted")

    def get(self, path):
        return self._request("GET", path)

    def post(self, path, body, in_solution=False):
        return self._request("POST", path, body, in_solution)


def exists(dv: Dataverse, step: dict) -> tuple[bool, dict | None]:
    status, body, _ = dv.get(step["exists"])
    mode = step["exists_mode"]
    if mode == "single":
        if status == 200:
            return True, body
        if status == 404:
            return False, None
        # Dataverse answers 400 for an unknown metadata name on some endpoints
        if status == 400 and "does not exist" in json.dumps(body).lower():
            return False, None
        if status == 400 and "could not find" in json.dumps(body).lower():
            return False, None
        raise RuntimeError(f"Unexpected answer {status} while checking {step['name']}: {body}")
    if status != 200:
        if mode == "key-list" and status == 404:
            return False, None
        raise RuntimeError(f"Unexpected answer {status} while checking {step['name']}: {body}")
    values = (body or {}).get("value", [])
    if mode == "collection":
        return (len(values) > 0), (values[0] if values else None)
    if mode == "key-list":
        wanted = step["key_schema"].lower()
        return any(v.get("SchemaName", "").lower() == wanted for v in values), None
    raise ValueError(mode)


def error_text(body) -> str:
    if isinstance(body, dict):
        return body.get("error", {}).get("message", json.dumps(body))[:500]
    return str(body)[:500]


# --------------------------------------------------------------------------- run modes
def dry_run(steps: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, st in enumerate(steps, start=1):
        safe = st["name"].replace(".", "__")
        (out_dir / f"{i:03d}_{st['kind']}_{safe}.json").write_text(
            json.dumps({"method": "POST", "path": API + st["post"], "solution_header": st["in_solution"], "body": st["body"]},
                       indent=1, ensure_ascii=False), encoding="utf-8")
    counts: dict[str, int] = {}
    for st in steps:
        counts[st["kind"]] = counts.get(st["kind"], 0) + 1
    print(f"Dry run: {len(steps)} requests written to {out_dir}")
    for kind, n in counts.items():
        print(f"  {kind:10s} {n}")


def run(dv: Dataverse, steps: list[dict], check_only: bool) -> int:
    created = skipped = failed = missing = 0
    publisher_id = None
    for st in steps:
        try:
            found, existing = exists(dv, st)
        except RuntimeError as err:
            print(f"  ERROR   {st['kind']:9s} {st['name']}: {err}")
            failed += 1
            continue
        if st["kind"] == "publisher" and found:
            publisher_id = existing["publisherid"]
        if found:
            skipped += 1
            print(f"  exists  {st['kind']:9s} {st['name']}")
            continue
        if check_only:
            missing += 1
            print(f"  MISSING {st['kind']:9s} {st['name']}")
            continue
        body = st["body"]
        if st["kind"] == "solution":
            if not publisher_id:
                print("  ERROR   solution: publisher id unknown")
                failed += 1
                continue
            body = dict(body, **{"publisherid@odata.bind": f"/publishers({publisher_id})"})
        status, answer, headers = dv.post(st["post"], body, in_solution=st["in_solution"])
        if status in (200, 201, 204):
            created += 1
            print(f"  created {st['kind']:9s} {st['name']}")
            if st["kind"] == "publisher":
                entity_id = headers.get("OData-EntityId") or headers.get("odata-entityid") or ""
                publisher_id = entity_id[entity_id.rfind("(") + 1: entity_id.rfind(")")] or None
                if not publisher_id:
                    _, existing = exists(dv, st)
                    publisher_id = existing["publisherid"] if existing else None
        else:
            tag = "WARN   " if st.get("optional") else "ERROR  "
            print(f"  {tag} {st['kind']:9s} {st['name']}: HTTP {status} {error_text(answer)}")
            failed += 1
    if not check_only and created:
        status, answer, _ = dv.post("PublishAllXml", {})
        print("  published all customizations" if status in (200, 204) else f"  WARN publish failed: HTTP {status} {error_text(answer)}")
    print(f"\nSummary: {created} created, {skipped} already existed, {missing} missing, {failed} failed")
    return 1 if failed else 0


def list_formulas(schema: dict) -> None:
    rows = [(t["display"], f) for t in schema["tables"] for f in t.get("formulas", [])]
    if not rows:
        return
    print("\nFormula columns to create by hand in the maker portal (Tables > table > New column > Data type: fx Formula):")
    for table, f in rows:
        print(f"  {table}: '{f['display']}' (schema name {f['schema']}, {f['datatype']}, {f['decimals']} decimals)\n      {f['formula']}")


def az_token(url: str) -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource", url.rstrip("/"), "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, shell=(os.name == "nt"))
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("Could not get a token from the Azure CLI. Run 'az login' first.\n" + out.stderr)
    return out.stdout.strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Create the Cost Cockpit data model in Dataverse.")
    ap.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    ap.add_argument("--url", help="Environment URL, e.g. https://org.crm4.dynamics.com")
    ap.add_argument("--token", help="Access token; default: environment variable DATAVERSE_TOKEN")
    ap.add_argument("--use-az", action="store_true", help="Get the token from the Azure CLI (az login)")
    ap.add_argument("--dry-run", action="store_true", help="Write all requests to --out and do not connect")
    ap.add_argument("--check", action="store_true", help="Only report what exists and what is missing")
    ap.add_argument("--only", help="Comma-separated kinds to process: publisher,solution,choice,table,column,lookup,key")
    ap.add_argument("--out", default=str(HERE.parent / "out" / "payloads"))
    args = ap.parse_args(argv)

    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    steps = build_plan(schema)
    if args.only:
        kinds = {k.strip() for k in args.only.split(",")}
        steps = [s for s in steps if s["kind"] in kinds or s["kind"] == "publisher"]

    if args.dry_run:
        dry_run(steps, Path(args.out))
        list_formulas(schema)
        return 0
    if not args.url:
        ap.error("--url is required unless --dry-run is used")
    token = args.token or os.environ.get("DATAVERSE_TOKEN") or (az_token(args.url) if args.use_az else None)
    if not token:
        ap.error("No token: pass --token, set DATAVERSE_TOKEN or use --use-az")
    dv = Dataverse(args.url, token, schema["solution"]["uniquename"])
    status, who, _ = dv.get("WhoAmI")
    if status != 200:
        sys.exit(f"Connection failed: HTTP {status} {error_text(who)}")
    print(f"Connected to {args.url} as user {who.get('UserId')}")
    code = run(dv, steps, args.check)
    list_formulas(schema)
    return code


if __name__ == "__main__":
    sys.exit(main())
