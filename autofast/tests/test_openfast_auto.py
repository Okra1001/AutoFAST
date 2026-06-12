from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from analyze_output import parse_text_output, summarize
from compare_outputs import compare
from diagnose_failure import diagnose
from inspect_project import inspect
from modify_input import replace_exact_field
from openfast_common import dependency_graph
from run_case import run_case


class OpenFASTAutoTests(unittest.TestCase):
    def test_dependency_graph_and_missing_reference(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fst = root / "model.fst"
            aero = root / "AeroDyn.dat"
            fst.write_text(
                '"AeroDyn.dat"   AeroFile   - active aerodynamic file\n'
                '"missing.dat"   ServoFile  - missing dependency\n',
                encoding="utf-8",
            )
            aero.write_text("1   Wake_Mod   - wake model\n", encoding="utf-8")
            graph = dependency_graph(fst)
            self.assertIn(str(fst.resolve()), graph["files"])
            self.assertIn(str(aero.resolve()), graph["files"])
            self.assertEqual(len(graph["missing"]), 1)
            self.assertTrue(graph["missing"][0]["resolved"].endswith("missing.dat"))

    def test_comments_numbers_and_placeholders_are_not_references(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.fst"
            path.write_text(
                "0.1   DT   - time step; example output <RootName>.sum\n"
                "False Echo - write .ech file\n",
                encoding="utf-8",
            )
            graph = dependency_graph(path)
            self.assertEqual(graph["missing"], [])

    def test_at_prefixed_reference_is_cleaned(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            coords = root / "coords.txt"
            coords.write_text("0 0\n", encoding="utf-8")
            polar = root / "polar.dat"
            polar.write_text(
                '@"coords.txt"   NumCoords   ! external coordinate file\n',
                encoding="utf-8",
            )
            graph = dependency_graph(polar)
            self.assertIn(str(coords.resolve()), graph["files"])
            self.assertEqual(graph["missing"], [])

    def test_inspection_without_model(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "openfast.exe").write_bytes(b"placeholder")
            report = inspect(root)
            self.assertEqual(report["readiness"], "NO_RUNNABLE_MODEL")
            self.assertEqual(report["summary"]["entry_count"], 0)

    def test_exact_scalar_replacement(self):
        original = (
            "800.0      TMax       - total time\n"
            "0.0125     DT         - time step\n"
        )
        updated, line, old = replace_exact_field(original, "DT", "0.01")
        self.assertEqual(line, 2)
        self.assertEqual(old, "0.0125")
        self.assertIn("0.01     DT", updated)
        with self.assertRaises(ValueError):
            replace_exact_field(original, "MissingField", "1")

    def test_error_diagnosis(self):
        report = diagnose(
            "FAST encountered a FATAL ERROR\n"
            "Could not open file Airfoils/test.dat\n"
        )
        self.assertEqual(report["primary"]["id"], "missing-file")
        self.assertEqual(report["confidence"], "high")

    def test_text_output_analysis(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "case.out"
            output.write_text(
                "header\n"
                "Time RotSpeed GenPwr\n"
                "(s) (rpm) (W)\n"
                "0.0 5.0 10.0\n"
                "1.0 6.0 20.0\n"
                "2.0 7.0 30.0\n",
                encoding="utf-8",
            )
            names, units, rows = parse_text_output(output)
            report = summarize(names, units, rows, 1.0)
            self.assertEqual(report["time"]["first"], 1.0)
            self.assertEqual(report["channels"]["GenPwr"]["mean"], 25.0)
            self.assertTrue(report["all_channels_finite"])

    def test_controlled_output_comparison(self):
        names = ["Time", "Load"]
        units = ["(s)", "(N)"]
        baseline = (names, units, [[0.0, 1.0], [1.0, 2.0], [2.0, 3.0]])
        candidate = (names, units, [[0.0, 2.0], [1.0, 3.0], [2.0, 4.0]])
        report = compare(baseline, candidate, 0.0)
        load = report["channels"][0]
        self.assertEqual(load["channel"], "Load")
        self.assertAlmostEqual(load["mean_bias_candidate_minus_baseline"], 1.0)

    def test_run_case_end_to_end(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            entry = root / "case.py"
            result = root / "record"
            entry.write_text(
                "from pathlib import Path\n"
                "Path('case.out').write_text("
                "'header\\nTime Value\\n(s) (-)\\n0.0 1.0\\n1.0 2.0\\n',"
                " encoding='utf-8')\n"
                "print('OpenFAST terminated normally')\n",
                encoding="utf-8",
            )
            status = run_case(Path(sys.executable), entry, result)
            self.assertTrue(status["passed"])
            self.assertTrue((result / "status.json").exists())
            self.assertTrue((result / "provenance" / "manifest.json").exists())
            saved = json.loads(
                (result / "status.json").read_text(encoding="utf-8")
            )
            self.assertEqual(saved["return_code"], 0)

    def test_cli_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.fst"
            original = "100.0    TMax    - duration\n"
            path.write_text(original, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "modify_input.py"),
                    str(path),
                    "TMax",
                    "200.0",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertIn("Dry run", result.stdout)

    def test_case_manifest_template(self):
        path = SKILL / "assets" / "case-manifest.csv"
        with path.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["case_id"], "baseline")
        self.assertIn("entry", rows[0])


if __name__ == "__main__":
    unittest.main()
