#!/usr/bin/env python3
"""Reference implementation of the Cost Cockpit calculation logic.

This module is the test oracle for the app: the flows, the Dataverse formula columns and the
Power BI measures must reproduce the numbers it produces on the demo data (see golden/).
It reads the seed CSV files, so it needs no Dataverse environment.

    python cost_engine.py                 print a summary for the demo data
    python cost_engine.py --write-golden  rewrite the files in golden/

Logic (identical in every implementation)
-----------------------------------------
amount            = quantity x unit price x FX rate (blank FX rate = 1)
roll-up           = an element is the sum of its children; a leaf is the sum of its cost items
size ratio        = project size / reference size
module ratio      = roundup(project size / module size) / roundup(reference size / module size)
scale factor      = module ratio            (scaling code 1, per module)
                  = size ratio ^ exponent   (scaling code 2, power law)
                  = 1                       (scaling code 3, fixed)
final cost        = base amount x scale factor x regional factor x escalation factor
regional factor   = factor of (region, cost type); 1 if none is maintained
feature lines     = fixed amount:      base = value,                          fixed
                    amount per MW:     base = value x reference size,         power law with exponent 1
                    percent of element: base = value % x element base amount,  scaled like the element
priority score    = saving x probability / (one-off cost + effort x day rate)
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE.parent / "seed"
GOLDEN = HERE / "golden"

SCALING_CODE = {"Per module": 1, "Power law": 2, "Fixed": 3}
DEFAULT_DAY_RATE = 800.0


# --------------------------------------------------------------------------- loading
def _num(text: str, default: float | None = None) -> float | None:
    text = (text or "").strip()
    return float(text) if text else default


def _rows(seed: Path, pattern: str) -> list[dict]:
    files = sorted(seed.glob(pattern))
    if not files:
        raise FileNotFoundError(f"no seed file matches {pattern} in {seed}")
    with files[0].open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class Model:
    """All input data, keyed by the alternate-key codes used in the seed files."""

    def __init__(self, seed: Path = SEED):
        self.products = {r["cdt_code"]: {
            "code": r["cdt_code"], "name": r["cdt_name"],
            "reference_size": _num(r["cdt_referencesizemw"]), "module_size": _num(r["cdt_modulesizemw"])}
            for r in _rows(seed, "*cdt_product.csv")}
        self.cbs = {r["cdt_code"]: {
            "code": r["cdt_code"], "name": r["cdt_name"], "product": r["cdt_Product@cdt_code"],
            "parent": r["cdt_Parent@cdt_code"] or None, "level": int(r["cdt_level"]),
            "scope": r["cdt_scope"] or None, "tic": r["cdt_ticcategory"] or None,
            "scaling": r["cdt_scalingmethod"] or None, "exponent": _num(r["cdt_scalingexponent"]),
            "leaf": r["cdt_isleaf"] == "Yes", "sort": int(r["cdt_sortorder"] or 0)}
            for r in _rows(seed, "*cdt_cbselement.csv")}
        self.versions = {r["cdt_code"]: {
            "code": r["cdt_code"], "name": r["cdt_name"], "product": r["cdt_Product@cdt_code"],
            "status": r["cdt_status"], "number": int(r["cdt_versionnumber"])}
            for r in _rows(seed, "*cdt_costversion.csv")}
        self.items = [{
            "key": r["cdt_importkey"], "name": r["cdt_name"], "version": r["cdt_CostVersion@cdt_code"],
            "cbs": r["cdt_CBSElement@cdt_code"], "cost_type": r["cdt_costtype"],
            "tc_item": r["cdt_teamcenteritemid"], "supplier": r["cdt_Supplier@cdt_teamcenterid"],
            "quantity": _num(r["cdt_quantity"], 0.0), "unit_price": _num(r["cdt_unitprice"], 0.0),
            "fx": _num(r["cdt_fxrate"])} for r in _rows(seed, "*cdt_costitem.csv")]
        self.factors = {(r["cdt_Region@cdt_code"], r["cdt_costtype"]): _num(r["cdt_factor"])
                        for r in _rows(seed, "*cdt_regionalfactor.csv")}
        self.features = {r["cdt_code"]: r["cdt_name"] for r in _rows(seed, "*cdt_feature.csv")}
        self.impacts = [{
            "feature": r["cdt_Feature@cdt_code"], "cbs": r["cdt_CBSElement@cdt_code"], "type": r["cdt_impacttype"],
            "value": _num(r["cdt_value"]), "cost_type": r["cdt_costtype"]} for r in _rows(seed, "*cdt_featureimpact.csv")]
        self.scenarios = {r["cdt_code"]: {
            "code": r["cdt_code"], "name": r["cdt_name"], "product": r["cdt_Product@cdt_code"],
            "version": r["cdt_CostVersion@cdt_code"], "region": r["cdt_Region@cdt_code"],
            "size": _num(r["cdt_sizemw"]), "escalation": _num(r["cdt_escalationfactor"])}
            for r in _rows(seed, "*cdt_scenario.csv")}
        self.scenario_features = defaultdict(list)
        for r in _rows(seed, "*cdt_scenariofeature.csv"):
            self.scenario_features[r["cdt_Scenario@cdt_code"]].append(r["cdt_Feature@cdt_code"])
        self.targets = {r["cdt_CBSElement@cdt_code"]: _num(r["cdt_targeteurperkw"]) for r in _rows(seed, "*cdt_target.csv")}
        self.measures = [{
            "code": r["cdt_code"], "name": r["cdt_name"], "cbs": r["cdt_CBSElement@cdt_code"],
            "saving": _num(r["cdt_savingeur"], 0.0), "one_off": _num(r["cdt_oneoffcosteur"], 0.0),
            "effort": _num(r["cdt_effortpd"], 0.0), "day_rate": _num(r["cdt_dayrateeur"]),
            "probability": _num(r["cdt_probability"], 0.0), "di": r["cdt_dilevel"], "status": r["cdt_status"]}
            for r in _rows(seed, "*cdt_measure.csv")]


# --------------------------------------------------------------------------- R1, R2, R4: transparency
def amount_eur(item: dict) -> float:
    fx = 1.0 if item["fx"] is None else item["fx"]
    return item["quantity"] * item["unit_price"] * fx


def version_items(model: Model, version: str) -> list[dict]:
    return [i for i in model.items if i["version"] == version]


def version_total(model: Model, version: str) -> float:
    return sum(amount_eur(i) for i in version_items(model, version))


def rollup(model: Model, version: str) -> dict[str, float]:
    """Cost per CBS element including all descendants."""
    totals = defaultdict(float)
    for item in version_items(model, version):
        code = item["cbs"]
        while code:
            totals[code] += amount_eur(item)
            code = model.cbs[code]["parent"]
    return {code: totals.get(code, 0.0) for code in model.cbs}


def breakdown(model: Model, version: str, by: str) -> dict[str, float]:
    """Split a version by 'scope', 'tic' (taken from the CBS element) or 'cost_type' (taken from the item)."""
    out = defaultdict(float)
    for item in version_items(model, version):
        label = item["cost_type"] if by == "cost_type" else model.cbs[item["cbs"]][by]
        out[label or "(blank)"] += amount_eur(item)
    return dict(out)


def pareto(model: Model, version: str) -> list[dict]:
    """Cost items sorted by amount with share and cumulative share: the cost-driver list."""
    total = version_total(model, version)
    rows, cumulative = [], 0.0
    for item in sorted(version_items(model, version), key=lambda i: -amount_eur(i)):
        cumulative += amount_eur(item)
        rows.append({"item": item["name"], "cbs": item["cbs"], "cost_type": item["cost_type"], "amount": amount_eur(item),
                     "share": amount_eur(item) / total, "cumulative_share": cumulative / total})
    return rows


# --------------------------------------------------------------------------- R6: versions
def version_bridge(model: Model, old: str, new: str) -> list[dict]:
    """Change per CBS leaf between two versions."""
    a, b = rollup(model, old), rollup(model, new)
    rows = []
    for code, el in sorted(model.cbs.items(), key=lambda kv: kv[1]["sort"]):
        if el["leaf"]:
            rows.append({"cbs": code, "name": el["name"], "old": a[code], "new": b[code], "delta": b[code] - a[code]})
    return rows


# --------------------------------------------------------------------------- R7, R8, R3: scenarios
def round_up(value: float) -> int:
    return math.ceil(round(value, 9))


def module_ratio(size: float, reference: float, module: float) -> float:
    if not module or not reference:
        return 0.0
    return round_up(size / module) / round_up(reference / module)


def scale_factor(code: int, exponent: float | None, size_ratio: float, mod_ratio: float) -> float:
    if code == 1:
        return mod_ratio
    if code == 2:
        return size_ratio ** (exponent or 0.0)
    return 1.0


def scenario_lines(model: Model, scenario_code: str) -> list[dict]:
    scn = model.scenarios[scenario_code]
    product = model.products[scn["product"]]
    size, ref = scn["size"], product["reference_size"]
    size_ratio = size / ref
    mod_ratio = module_ratio(size, ref, product["module_size"])
    escalation = 1.0 if scn["escalation"] is None else scn["escalation"]

    base = defaultdict(float)  # (cbs, cost type) -> amount at reference size
    for item in version_items(model, scn["version"]):
        base[(item["cbs"], item["cost_type"])] += amount_eur(item)
    element_base = defaultdict(float)
    for (cbs, _ct), value in base.items():
        element_base[cbs] += value

    def line(cbs, cost_type, line_type, feature, base_amount, code, exponent):
        el = model.cbs[cbs]
        regional = model.factors.get((scn["region"], cost_type), 1.0)
        factor = scale_factor(code, exponent, size_ratio, mod_ratio)
        final = base_amount * factor * regional * escalation
        return {"scenario": scenario_code, "cbs": cbs, "cost_type": cost_type, "line_type": line_type, "feature": feature or "",
                "scope": el["scope"], "tic": el["tic"], "base_amount": base_amount, "scaling_code": code,
                "exponent": exponent if exponent is not None else "", "size_ratio": size_ratio, "module_ratio": mod_ratio,
                "regional_factor": regional, "escalation_factor": escalation, "size_mw": size,
                "scale_factor": factor, "final_cost": final, "cost_per_kw": final / (size * 1000)}

    lines = []
    for (cbs, cost_type), value in sorted(base.items(), key=lambda kv: (model.cbs[kv[0][0]]["sort"], kv[0][1])):
        el = model.cbs[cbs]
        lines.append(line(cbs, cost_type, "Base cost", None, value, SCALING_CODE[el["scaling"]], el["exponent"]))
    for feature in model.scenario_features.get(scenario_code, []):
        for imp in (i for i in model.impacts if i["feature"] == feature):
            el = model.cbs[imp["cbs"]]
            if imp["type"].startswith("Fixed"):
                args = (imp["value"], 3, None)
            elif imp["type"].startswith("Amount per MW"):
                args = (imp["value"] * ref, 2, 1.0)
            else:  # percent of element
                args = (imp["value"] / 100.0 * element_base[imp["cbs"]], SCALING_CODE[el["scaling"]], el["exponent"])
            lines.append(line(imp["cbs"], imp["cost_type"], "Feature effect", feature, *args))
    return lines


def scenario_total(lines: list[dict]) -> float:
    return sum(l["final_cost"] for l in lines)


def capex_dataset(lines: list[dict]) -> list[dict]:
    """Aggregation per scope and TIC category: the content of the CAPEX dataset table for the LCOH Suite."""
    agg = defaultdict(float)
    for l in lines:
        agg[(l["scope"], l["tic"])] += l["final_cost"]
    size = lines[0]["size_mw"]
    return [{"scenario": lines[0]["scenario"], "scope": scope, "tic": tic, "cost_eur": value, "cost_per_kw": value / (size * 1000)}
            for (scope, tic), value in sorted(agg.items())]


# --------------------------------------------------------------------------- R10, R12: targets and measures
def measure_scores(model: Model) -> list[dict]:
    rows = []
    for m in model.measures:
        day_rate = DEFAULT_DAY_RATE if m["day_rate"] is None else m["day_rate"]
        weighted = m["saving"] * m["probability"] / 100.0
        cost = m["one_off"] + m["effort"] * day_rate
        rows.append({"code": m["code"], "name": m["name"], "cbs": m["cbs"], "di": m["di"], "weighted_saving": weighted,
                     "implementation_cost": cost, "priority_score": weighted / cost if cost > 0 else 0.0})
    return sorted(rows, key=lambda r: -r["priority_score"])


def _top_level(model: Model, code: str) -> str:
    while model.cbs[code]["parent"]:
        code = model.cbs[code]["parent"]
    return code


def target_gaps(model: Model, version: str) -> list[dict]:
    """Current cost, target and gap in EUR/kW per element that has a target, with measure coverage."""
    product = model.products[model.versions[version]["product"]]
    kw = product["reference_size"] * 1000
    totals = rollup(model, version)
    coverage = defaultdict(float)
    for m in measure_scores(model):
        if next(x for x in model.measures if x["code"] == m["code"])["status"] != "Cancelled":
            coverage[_top_level(model, m["cbs"])] += m["weighted_saving"]
    rows = []
    for code, target in sorted(model.targets.items(), key=lambda kv: model.cbs[kv[0]]["sort"]):
        current = totals[code] / kw
        gap = current - target
        covered = coverage.get(code, 0.0) / kw
        rows.append({"cbs": code, "name": model.cbs[code]["name"], "current_per_kw": current, "target_per_kw": target,
                     "gap_per_kw": gap, "weighted_measures_per_kw": covered, "open_gap_per_kw": gap - covered})
    return rows


# --------------------------------------------------------------------------- golden files
def _write(name: str, rows: list[dict], digits: int = 4) -> None:
    GOLDEN.mkdir(exist_ok=True)
    with (GOLDEN / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, digits) if isinstance(v, float) else v) for k, v in r.items()})


def golden_tables(model: Model) -> dict[str, list[dict]]:
    baseline = "DEMO-V001"
    lines = [l for code in model.scenarios for l in scenario_lines(model, code)]
    roll = rollup(model, baseline)
    return {
        "rollup_DEMO-V001.csv": [{"cbs": c, "name": e["name"], "level": e["level"], "amount_eur": roll[c],
                                  "eur_per_kw": roll[c] / (model.products[e["product"]]["reference_size"] * 1000)}
                                 for c, e in sorted(model.cbs.items(), key=lambda kv: kv[1]["sort"])],
        "breakdown_DEMO-V001.csv": [{"dimension": by, "label": k, "amount_eur": v}
                                    for by in ("scope", "cost_type", "tic") for k, v in sorted(breakdown(model, baseline, by).items())],
        "pareto_DEMO-V001.csv": pareto(model, baseline),
        "version_bridge_V001_V002.csv": version_bridge(model, "DEMO-V001", "DEMO-V002"),
        "scenario_lines.csv": lines,
        "scenario_totals.csv": [{"scenario": code, "size_mw": s["size"], "region": s["region"],
                                 "total_eur": scenario_total(scenario_lines(model, code)),
                                 "eur_per_kw": scenario_total(scenario_lines(model, code)) / (s["size"] * 1000)}
                                for code, s in model.scenarios.items()],
        "capex_dataset.csv": [r for code in model.scenarios for r in capex_dataset(scenario_lines(model, code))],
        "target_gaps_DEMO-V001.csv": target_gaps(model, baseline),
        "measure_scores.csv": measure_scores(model),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write-golden", action="store_true")
    args = ap.parse_args()
    model = Model()
    if args.write_golden:
        for name, rows in golden_tables(model).items():
            _write(name, rows)
        print(f"golden files written to {GOLDEN}")
        return
    for version in model.versions:
        print(f"{version}: total {version_total(model, version):,.0f} EUR")
    for code, s in model.scenarios.items():
        total = scenario_total(scenario_lines(model, code))
        print(f"{code}: {s['size']:.0f} MW in {s['region']}: {total:,.0f} EUR = {total / (s['size'] * 1000):,.2f} EUR/kW")
    for g in target_gaps(model, "DEMO-V001"):
        print(f"{g['cbs']}: current {g['current_per_kw']:.1f}, target {g['target_per_kw']:.1f}, gap {g['gap_per_kw']:.1f}, "
              f"measures {g['weighted_measures_per_kw']:.1f} EUR/kW")
    for m in measure_scores(model):
        print(f"{m['code']}: weighted saving {m['weighted_saving']:,.0f} EUR, score {m['priority_score']:.2f}")


if __name__ == "__main__":
    main()
