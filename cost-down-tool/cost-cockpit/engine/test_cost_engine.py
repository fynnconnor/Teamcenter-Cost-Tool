"""Tests for the reference engine. Run:  python -m unittest test_cost_engine  (from the engine folder).

Expected values are calculated by hand from the seed data, so a failing test means either the
engine or the seed data changed.
"""
import csv
import unittest

import cost_engine as ce

M = ce.Model()


class Transparency(unittest.TestCase):
    def test_item_amount_with_fx(self):
        item = next(i for i in ce.version_items(M, "DEMO-V001") if i["name"] == "Transformer-rectifier set")
        self.assertAlmostEqual(ce.amount_eur(item), 13_200_000 * 0.9)

    def test_blank_fx_is_one(self):
        self.assertEqual(ce.amount_eur({"quantity": 2, "unit_price": 10, "fx": None}), 20)

    def test_version_totals(self):
        self.assertAlmostEqual(ce.version_total(M, "DEMO-V001"), 91_380_000)
        self.assertAlmostEqual(ce.version_total(M, "DEMO-V002"), 90_380_000)

    def test_rollup_parents_equal_children(self):
        roll = ce.rollup(M, "DEMO-V001")
        self.assertAlmostEqual(roll["DEMO-1"], 27_000_000)      # 20.0 + 5.0 + 2.0 million
        self.assertAlmostEqual(roll["DEMO-1.2"], 7_000_000)
        self.assertAlmostEqual(roll["DEMO-7"], 7_500_000)       # 2.0 + 5.5 million
        top = sum(v for c, v in roll.items() if M.cbs[c]["level"] == 1)
        self.assertAlmostEqual(top, 91_380_000)

    def test_breakdowns_sum_to_total(self):
        for by in ("scope", "cost_type", "tic"):
            self.assertAlmostEqual(sum(ce.breakdown(M, "DEMO-V001", by).values()), 91_380_000)
        scope = ce.breakdown(M, "DEMO-V001", "scope")
        self.assertAlmostEqual(scope["NCA scope"], 20e6 + 7e6 + 6e6 + 11.88e6 + 2e6)   # 46.88 million
        self.assertAlmostEqual(scope["EPC scope"], 91.38e6 - 46.88e6)
        self.assertAlmostEqual(ce.breakdown(M, "DEMO-V001", "cost_type")["Engineering hours"], 7_500_000)

    def test_pareto(self):
        rows = ce.pareto(M, "DEMO-V001")
        self.assertEqual(rows[0]["item"], "Cell stack")
        self.assertAlmostEqual(rows[0]["share"], 20 / 91.38)
        self.assertAlmostEqual(rows[-1]["cumulative_share"], 1.0)


class Versions(unittest.TestCase):
    def test_bridge(self):
        delta = {r["cbs"]: r["delta"] for r in ce.version_bridge(M, "DEMO-V001", "DEMO-V002")}
        self.assertAlmostEqual(delta["DEMO-1.1"], -1_000_000)
        self.assertAlmostEqual(delta["DEMO-2.2"], 200_000)
        self.assertAlmostEqual(delta["DEMO-7.1"], -200_000)
        self.assertAlmostEqual(sum(delta.values()), -1_000_000)


class Scenarios(unittest.TestCase):
    def test_ratios(self):
        self.assertEqual(ce.module_ratio(100, 100, 20), 1.0)
        self.assertEqual(ce.module_ratio(200, 100, 20), 2.0)
        self.assertEqual(ce.module_ratio(30, 100, 20), 2 / 5)      # 30 MW needs 2 modules
        self.assertEqual(ce.module_ratio(20, 100, 20), 1 / 5)
        self.assertEqual(ce.scale_factor(3, None, 5, 5), 1.0)
        self.assertAlmostEqual(ce.scale_factor(2, 0.6, 2, 2), 2 ** 0.6)

    def test_reference_scenario_equals_baseline(self):
        lines = ce.scenario_lines(M, "SCN-100-DE")
        self.assertAlmostEqual(ce.scenario_total(lines), 91_380_000)
        self.assertTrue(all(l["scale_factor"] == 1.0 and l["regional_factor"] == 1.0 for l in lines))

    def test_200mw_spain_lines(self):
        lines = ce.scenario_lines(M, "SCN-200-ES")
        get = lambda cbs, ct, typ="Base cost": next(l for l in lines if (l["cbs"], l["cost_type"], l["line_type"]) == (cbs, ct, typ))
        self.assertAlmostEqual(get("DEMO-1.1", "Material")["final_cost"], 40_000_000)                      # per module, x2
        self.assertAlmostEqual(get("DEMO-2.1", "Material")["final_cost"], 6e6 * 2 ** 0.7)                  # power law
        self.assertAlmostEqual(get("DEMO-5.1", "Construction & installation")["final_cost"], 5e6 * 2 ** 0.7 * 0.85)
        self.assertAlmostEqual(get("DEMO-7.1", "Engineering hours")["final_cost"], 2e6 * 0.9)              # fixed, regional factor only
        self.assertAlmostEqual(get("DEMO-7.2", "Engineering hours")["final_cost"], 5.5e6 * 2 ** 0.4 * 0.9)
        outdoor = get("DEMO-5.1", "Construction & installation", "Feature effect")
        self.assertAlmostEqual(outdoor["base_amount"], -0.4 * 8e6)                                          # -40 % of the element
        self.assertAlmostEqual(outdoor["final_cost"], -3.2e6 * 2 ** 0.7 * 0.85)
        redundant = get("DEMO-3.1", "Material", "Feature effect")
        self.assertAlmostEqual(redundant["final_cost"], 15_000 * 200)                                       # EUR/MW x project size
        expected = (40e6 + 10e6 + 4e6 + 6e6 * 2 ** 0.7 + 4e6 * 2 ** 0.65 + 11.88e6 * 2 ** 0.85 + 5e6 * 2 ** 0.6
                    + 3e6 * 2 ** 0.7 + 5e6 * 2 ** 0.7 * 0.85 + 12e6 * 2 ** 0.8 * 0.85 + 2e6 * 0.9 + 5.5e6 * 2 ** 0.4 * 0.9
                    + 4e6 * 2 ** 0.8 * 0.9 + 6e6 * 2 ** 0.8 - 3.2e6 * 2 ** 0.7 * 0.85 + 3e6)
        self.assertAlmostEqual(ce.scenario_total(lines), expected, places=3)

    def test_20mw_india(self):
        lines = ce.scenario_lines(M, "SCN-20-IN")
        get = lambda cbs, ct: next(l for l in lines if (l["cbs"], l["cost_type"]) == (cbs, ct))
        self.assertAlmostEqual(get("DEMO-1.1", "Material")["final_cost"], 20e6 / 5 * 0.9)                  # one module
        self.assertAlmostEqual(get("DEMO-6.1", "Construction & installation")["final_cost"], 12e6 * 0.2 ** 0.8 * 0.55)
        self.assertAlmostEqual(get("DEMO-7.1", "Engineering hours")["cost_per_kw"], 2e6 * 0.5 / 20_000)    # fixed cost on a small plant

    def test_capex_dataset_sums_to_total(self):
        for code in M.scenarios:
            lines = ce.scenario_lines(M, code)
            self.assertAlmostEqual(sum(r["cost_eur"] for r in ce.capex_dataset(lines)), ce.scenario_total(lines), places=3)

    def test_fixed_feature(self):
        M.scenario_features["SCN-100-DE"].append("F-COMPRESSION")
        try:
            self.assertAlmostEqual(ce.scenario_total(ce.scenario_lines(M, "SCN-100-DE")), 91_380_000 + 1_500_000)
        finally:
            M.scenario_features["SCN-100-DE"].remove("F-COMPRESSION")


class TargetsAndMeasures(unittest.TestCase):
    def test_scores(self):
        s = {m["code"]: m for m in ce.measure_scores(M)}
        self.assertAlmostEqual(s["M-001"]["weighted_saving"], 840_000)
        self.assertAlmostEqual(s["M-001"]["priority_score"], 840_000 / (150_000 + 60 * 800))
        self.assertAlmostEqual(s["M-002"]["priority_score"], 250_000 / (50_000 + 40 * 800))
        self.assertAlmostEqual(s["M-003"]["priority_score"], 1_280_000 / (300_000 + 150 * 800))
        self.assertEqual([m["code"] for m in ce.measure_scores(M)][0], "M-001")

    def test_gaps(self):
        g = {r["cbs"]: r for r in ce.target_gaps(M, "DEMO-V001")}
        self.assertAlmostEqual(g["DEMO-1"]["current_per_kw"], 270.0)
        self.assertAlmostEqual(g["DEMO-1"]["gap_per_kw"], 40.0)
        self.assertAlmostEqual(g["DEMO-1"]["weighted_measures_per_kw"], 8.4)      # M-001: 840,000 EUR / 100,000 kW
        self.assertAlmostEqual(g["DEMO-3"]["gap_per_kw"], 18.8)
        self.assertAlmostEqual(sum(r["current_per_kw"] for r in g.values()), 913.8)
        self.assertAlmostEqual(sum(r["target_per_kw"] for r in g.values()), 790.0)


class GoldenFiles(unittest.TestCase):
    def test_golden_files_are_current(self):
        for name, rows in ce.golden_tables(M).items():
            with (ce.GOLDEN / name).open(newline="", encoding="utf-8") as fh:
                stored = list(csv.DictReader(fh))
            self.assertEqual(len(stored), len(rows), name)
            for got, want in zip(stored, rows):
                for key, value in want.items():
                    if isinstance(value, float):
                        self.assertAlmostEqual(float(got[key]), value, places=3, msg=f"{name} {key}")
                    else:
                        self.assertEqual(got[key], str(value), f"{name} {key}")


if __name__ == "__main__":
    unittest.main()
