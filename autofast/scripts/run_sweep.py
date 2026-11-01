#!/usr/bin/env python3
"""Run a CSV-defined sweep with incremental, resumable status."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from run_case import run_case
from openfast_common import dependency_graph, sha256, atomic_write


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
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    atomic_write(path, stream.getvalue(), "utf-8-sig")


def prior_matches(prior: dict, entry: Path, executable: Path) -> bool:
    """Only reuse records when the discovered input graph and hashes match."""
    try:
        provenance = Path(prior["status_file"]).parent / "provenance"
        old_graph = json.loads((provenance / "inspection.json").read_text(encoding="utf-8"))
        graph = dependency_graph(entry)
        if graph["truncated"] or old_graph["truncated"] or graph != old_graph:
            return False
        with (provenance / "file_hashes.csv").open(encoding="utf-8-sig", newline="") as f:
            old = {row["path"]: row["sha256"] for row in csv.DictReader(f)}
        paths = set(graph["files"]) | {str(executable.resolve())}
        return set(old) == paths and all(Path(p).is_file() and sha256(Path(p)) == old[p] for p in paths)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


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
    ids = [case["case_id"].strip() for case in cases]
    if any(not x or x in {".", ".."} or Path(x).name != x or "/" in x or "\\" in x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("case_id values must be unique, nonempty directory names")
    rows: list[dict] = []
    for case in cases:
        case_id = case["case_id"].strip()
        executable_text = case.get("executable", "").strip()
        executable = Path(executable_text) if executable_text else args.default_executable
        if executable is None:
            raise ValueError(f"{case_id}: no executable specified")
        prior = previous.get(case_id)
        if prior and prior.get("passed", "").lower() == "true" and prior_matches(prior, Path(case["entry"]), executable):
            rows.append(prior)
            print(f"{case_id}: skipped (matching previously passed run)")
            continue
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
        retained = rows + [previous[x] for x in ids[len(rows):] if x in previous]
        write_status(status_path, retained)
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
