#!/usr/bin/env python3
"""Load the seed and demo data from ../seed into Dataverse.

Rows are upserted through the alternate keys defined in the schema, so the script can be re-run:
existing rows are updated, missing rows are created. Tables without an alternate key (Idea) are
matched by their primary name.

    python load_seed_data.py --url https://<org>.crm4.dynamics.com --use-az
    python load_seed_data.py --dry-run          list the operations without connecting

Run provision_dataverse.py first and wait until the alternate keys are active (a few minutes).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.parse
from pathlib import Path

from provision_dataverse import DEFAULT_SCHEMA, Dataverse, az_token, error_text

HERE = Path(__file__).resolve().parent
SEED = HERE.parent / "seed"


def build_operations(schema: dict, seed_dir: Path = SEED) -> list[dict]:
    """Translate the seed CSV files into typed upsert operations."""
    tables = {t["schema"].lower(): t for t in schema["tables"]}
    choices = {name: {o["label"]: o["value"] for o in ch["options"]} for name, ch in schema["choices"].items()}
    ops: list[dict] = []
    for path in sorted(seed_dir.glob("*.csv")):
        logical = path.stem.split("_", 1)[1]
        table = tables[logical]
        cols = {c["schema"].lower(): c for c in table["columns"]}
        lookups = {l["schema"]: l for l in table["lookups"]}
        primary = table["primary"]["schema"].lower()
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        header = list(rows[0].keys()) if rows else []
        key_col = next((k["columns"][0] for k in table["keys"] if len(k["columns"]) == 1 and k["columns"][0] in header), None)
        for n, row in enumerate(rows, start=2):
            body, binds = {}, []
            for head, raw in row.items():
                raw = (raw or "").strip()
                if raw == "":
                    continue
                if "@" in head:
                    nav, target_key = head.split("@", 1)
                    if nav not in lookups:
                        raise ValueError(f"{path.name}: unknown lookup {nav}")
                    binds.append({"nav": nav, "target": lookups[nav]["target"], "key_col": target_key, "value": raw})
                    continue
                if head == primary:
                    body[head] = raw
                    continue
                col = cols.get(head)
                if col is None:
                    raise ValueError(f"{path.name}: unknown column {head}")
                kind = col["type"]
                if kind == "decimal":
                    body[head] = float(raw)
                elif kind == "int":
                    body[head] = int(raw)
                elif kind == "bool":
                    body[head] = raw.lower() in ("yes", "true", "1")
                elif kind == "choice":
                    try:
                        body[head] = choices[col["choice"]][raw]
                    except KeyError:
                        raise ValueError(f"{path.name} line {n}: '{raw}' is not an option of {col['choice']}") from None
                else:
                    body[head] = raw
            op = {"table": logical, "file": path.name, "line": n, "body": body, "binds": binds}
            if key_col:
                op["key"] = {"col": key_col, "value": body.pop(key_col) if key_col != primary else body[primary]}
                if key_col == primary:
                    body.pop(primary)
            else:
                op["match_name"] = {"col": primary, "value": body[primary], "id_col": logical + "id"}
            ops.append(op)
    return ops


def quote(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def entity_sets(dv: Dataverse, logical_names: set[str]) -> dict[str, str]:
    out = {}
    for name in sorted(logical_names):
        status, body, _ = dv.get(f"EntityDefinitions(LogicalName='{name}')?$select=EntitySetName")
        if status != 200:
            sys.exit(f"Table {name} not found (HTTP {status}). Run provision_dataverse.py first.")
        out[name] = body["EntitySetName"]
    return out


def run(dv: Dataverse, ops: list[dict]) -> int:
    sets = entity_sets(dv, {o["table"] for o in ops} | {b["target"] for o in ops for b in o["binds"]})
    done = failed = 0
    for op in ops:
        body = dict(op["body"])
        for b in op["binds"]:
            body[f"{b['nav']}@odata.bind"] = f"/{sets[b['target']]}({b['key_col']}={quote(b['value'])})"
        target = sets[op["table"]]
        if "key" in op:
            status, answer, _ = dv._request("PATCH", f"{target}({op['key']['col']}={quote(op['key']['value'])})", body)
        else:
            m = op["match_name"]
            status, answer, _ = dv.get(f"{target}?$select={m['id_col']}&$filter={m['col']} eq {quote(m['value'])}&$top=1")
            if status == 200 and answer.get("value"):
                status, answer, _ = dv._request("PATCH", f"{target}({answer['value'][0][m['id_col']]})", body)
            elif status == 200:
                status, answer, _ = dv.post(target, body)
        if status in (200, 201, 204):
            done += 1
        else:
            failed += 1
            print(f"  ERROR {op['file']} line {op['line']}: HTTP {status} {error_text(answer)}")
    print(f"Seed data: {done} rows written, {failed} failed")
    return 1 if failed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Load seed and demo data into Dataverse.")
    ap.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    ap.add_argument("--seed", default=str(SEED))
    ap.add_argument("--url")
    ap.add_argument("--token")
    ap.add_argument("--use-az", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    ops = build_operations(schema, Path(args.seed))
    if args.dry_run:
        per_table: dict[str, int] = {}
        for o in ops:
            per_table[o["table"]] = per_table.get(o["table"], 0) + 1
        for t, n in per_table.items():
            print(f"  {t:22s} {n} rows")
        print(f"{len(ops)} operations")
        return 0
    if not args.url:
        ap.error("--url is required unless --dry-run is used")
    token = args.token or os.environ.get("DATAVERSE_TOKEN") or (az_token(args.url) if args.use_az else None)
    if not token:
        ap.error("No token: pass --token, set DATAVERSE_TOKEN or use --use-az")
    return run(Dataverse(args.url, token, schema["solution"]["uniquename"]), ops)


if __name__ == "__main__":
    sys.exit(main())
