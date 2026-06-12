#!/usr/bin/env python3
"""Run a CSV-defined sweep with incremental, resumable status."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from run_case import run_case


FIELDS = [
    "case_id",
    "entry",
    "executable",
    "passed",
    "return_code",
    "elapsed_s",
    "status_file",
    "notes",
]


def load_previous(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return {row["case_id"]: row for row in csv.DictReader(stream)}


def write_status(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--default-executable", type=Path)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()
    args.result_dir.mkdir(parents=True, exist_ok=True)
    status_path = args.result_dir / "sweep_status.csv"
    previous = load_previous(status_path)
    with args.manifest.open(newline="", encoding="utf-8-sig") as stream:
        cases = list(csv.DictReader(stream))
    required = {"case_id", "entry"}
    if not cases or not required.issubset(cases[0]):
        raise ValueError("Manifest requires case_id and entry columns")
    rows: list[dict] = []
    for case in cases:
        case_id = case["case_id"].strip()
        prior = previous.get(case_id)
        if prior and prior.get("passed", "").lower() == "true":
            rows.append(prior)
            print(f"{case_id}: skipped (previously passed)")
            continue
        executable_text = case.get("executable", "").strip()
        executable = Path(executable_text) if executable_text else args.default_executable
        if executable is None:
            raise ValueError(f"{case_id}: no executable specified")
        case_result = args.result_dir / case_id
        status = run_case(
            executable,
            Path(case["entry"]),
            case_result,
            args.timeout,
        )
        row = {
            "case_id": case_id,
            "entry": case["entry"],
            "executable": str(executable),
            "passed": status["passed"],
            "return_code": status["return_code"],
            "elapsed_s": status["elapsed_s"],
            "status_file": str(case_result / "status.json"),
            "notes": case.get("notes", ""),
        }
        rows.append(row)
        write_status(status_path, rows)
        print(f"{case_id}: {'passed' if status['passed'] else 'FAILED'}")
        if not status["passed"] and not args.continue_on_error:
            raise SystemExit(1)
    write_status(status_path, rows)
    summary = {
        "total": len(rows),
        "passed": sum(str(row["passed"]).lower() == "true" for row in rows),
        "failed": sum(str(row["passed"]).lower() != "true" for row in rows),
    }
    (args.result_dir / "sweep_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Status: {status_path.resolve()}")
    raise SystemExit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
