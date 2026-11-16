"""Tests for the provisioning plan. Run:  python -m unittest discover -s tests  (from the scripts folder)."""
import io
import json
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import mock_dataverse  # noqa: E402
import load_seed_data as seed  # noqa: E402
import provision_dataverse as prov  # noqa: E402

SCHEMA = json.loads(Path(prov.DEFAULT_SCHEMA).read_text(encoding="utf-8"))


class SchemaRules(unittest.TestCase):
    def test_names_and_references(self):
        prefix = SCHEMA["publisher"]["prefix"] + "_"
        logical = {t["schema"].lower() for t in SCHEMA["tables"]}
        self.assertEqual(len(logical), len(SCHEMA["tables"]))
        for t in SCHEMA["tables"]:
            self.assertTrue(t["schema"].startswith(prefix))
            names = [t["primary"]["schema"].lower()] + [c["schema"].lower() for c in t["columns"]] + [l["schema"].lower() for l in t["lookups"]]
            self.assertEqual(len(names), len(set(names)), f"duplicate column in {t['schema']}")
            for c in t["columns"]:
                self.assertTrue(c["schema"].startswith(prefix))
                if c["type"] == "choice":
                    self.assertIn(c["choice"], SCHEMA["choices"])
            for l in t["lookups"]:
                self.assertIn(l["target"], logical)
                self.assertIn(l["delete"], ("Cascade", "Restrict", "RemoveLink"))
            self.assertLessEqual(sum(1 for l in t["lookups"] if l["delete"] == "Cascade"), 1, f"more than one cascade-delete parent in {t['schema']}")
            for k in t["keys"]:
                for col in k["columns"]:
                    self.assertIn(col, names)
            for f in t.get("formulas", []):
                self.assertLessEqual(len(f["formula"]), 1000, "Dataverse formula columns allow at most 1,000 characters")
        for name, ch in SCHEMA["choices"].items():
            values = [o["value"] for o in ch["options"]]
            self.assertEqual(len(values), len(set(values)))
            self.assertTrue(all(str(v).startswith(str(SCHEMA["publisher"]["optionvalueprefix"])) for v in values))

    def test_plan_order(self):
        kinds = [s["kind"] for s in prov.build_plan(SCHEMA)]
        order = ["publisher", "solution", "choice", "table", "column", "lookup", "key"]
        self.assertEqual(kinds, sorted(kinds, key=order.index))


class ProvisionAgainstMock(unittest.TestCase):
    def setUp(self):
        self.server, self.state = mock_dataverse.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def run_script(self, *extra):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = prov.main(["--url", self.url, "--token", "test", *extra])
        return code, buf.getvalue()

    def test_full_run_is_complete_and_idempotent(self):
        code, out = self.run_script()
        self.assertEqual(code, 0, out)
        self.assertNotIn("ERROR", out)
        self.assertNotIn("WARN", out)
        self.assertEqual(len(self.state.tables), len(SCHEMA["tables"]))
        self.assertEqual(len(self.state.choices), len(SCHEMA["choices"]))
        self.assertEqual(len(self.state.relationships), sum(len(t["lookups"]) for t in SCHEMA["tables"]))
        for t in SCHEMA["tables"]:
            got = self.state.tables[t["schema"].lower()]
            for c in t["columns"] + t["lookups"]:
                self.assertIn(c["schema"].lower(), got["attributes"])
            self.assertEqual(len(got["keys"]), len(t["keys"]))
        self.assertEqual(self.state.published, 1)
        self.assertEqual(self.state.solution_header_missing, [])
        posts_before = sum(1 for m, _ in self.state.requests if m == "POST")
        code, out = self.run_script()
        self.assertEqual(code, 0, out)
        self.assertIn("0 created", out)
        self.assertEqual(sum(1 for m, _ in self.state.requests if m == "POST"), posts_before, "second run must not create anything")

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_browser_console_script(self):
        script = Path(prov.HERE) / "provision_browser_console.js"
        runner = (
            "const fs=require('fs'),vm=require('vm');const base=process.argv[1];const real=globalThis.fetch;"
            "globalThis.fetch=(p,o={})=>real(base+p,{...o,headers:{...(o.headers||{}),'X-Test-Cookie':'1'}});"
            "(async()=>{await vm.runInThisContext(fs.readFileSync(process.argv[2],'utf8'));})()"
            ".catch(e=>{console.error(e);process.exit(1)});"
        )
        for expected in ("0 failed", "0 created"):
            res = subprocess.run(["node", "-e", runner, self.url, str(script)], capture_output=True, text=True, timeout=120)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn(expected, res.stdout + res.stderr)
            self.assertNotIn("ERROR", res.stdout + res.stderr)
        self.assertEqual(len(self.state.tables), len(SCHEMA["tables"]))
        self.assertEqual(len(self.state.relationships), sum(len(t["lookups"]) for t in SCHEMA["tables"]))
        self.assertEqual(sum(len(t["keys"]) for t in self.state.tables.values()), sum(len(t["keys"]) for t in SCHEMA["tables"]))

    def test_seed_loader_python_and_console(self):
        self.assertEqual(self.run_script()[0], 0)
        ops = seed.build_operations(SCHEMA)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = seed.main(["--url", self.url, "--token", "test"])
        self.assertEqual(code, 0, buf.getvalue())
        self.assertIn(f"{len(ops)} rows written, 0 failed", buf.getvalue())
        count = lambda: {k: len(v) for k, v in self.state.rows.items()}
        first = count()
        self.assertEqual(sum(first.values()), len(ops))
        self.assertEqual(first["cdt_costitems"], 28)
        item = next(r for r in self.state.rows["cdt_costitems"] if r["cdt_importkey"] == "DEMO-V001~DEMO-3.1~100030")
        self.assertEqual(item["cdt_costtype"], 710000001)
        self.assertEqual(item["cdt_CBSElement@odata.bind"], "/cdt_cbselements(cdt_code='DEMO-3.1')")
        self.assertAlmostEqual(item["cdt_amounteur"], 11_880_000)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(seed.main(["--url", self.url, "--token", "test"]), 0)
        self.assertEqual(count(), first, "re-running the loader must not create duplicates")
        if shutil.which("node"):
            runner = (
                "const fs=require('fs'),vm=require('vm');const base=process.argv[1];const real=globalThis.fetch;"
                "globalThis.fetch=(p,o={})=>real(base+p,{...o,headers:{...(o.headers||{}),'X-Test-Cookie':'1'}});"
                "(async()=>{await vm.runInThisContext(fs.readFileSync(process.argv[2],'utf8'));})()"
                ".catch(e=>{console.error(e);process.exit(1)});"
            )
            res = subprocess.run(["node", "-e", runner, self.url, str(Path(prov.HERE) / "load_seed_browser_console.js")],
                                 capture_output=True, text=True, timeout=120)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn(f"{len(ops)} rows written, 0 failed", res.stdout + res.stderr)
            self.assertEqual(count(), first)

    def test_check_mode_changes_nothing(self):
        code, out = self.run_script("--check")
        self.assertEqual(code, 0)
        self.assertIn("MISSING", out)
        self.assertEqual(sum(1 for m, _ in self.state.requests if m == "POST"), 0)


if __name__ == "__main__":
    unittest.main()
