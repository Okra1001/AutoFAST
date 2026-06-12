#!/usr/bin/env python3
"""Assess an executable-only or newly downloaded OpenFAST directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from create_provenance import executable_version
from inspect_project import inspect
from openfast_common import sha256, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(args.path)
    candidates = [Path(item) for item in report["executables"]]
    executable = args.executable or (candidates[0] if len(candidates) == 1 else None)
    if executable:
        executable = executable.resolve()
        solver = {
            "path": str(executable),
            "exists": executable.exists(),
            "sha256": sha256(executable) if executable.exists() else None,
            "version_output": executable_version(executable)
            if executable.exists()
            else None,
        }
    else:
        solver = {
            "path": None,
            "exists": False,
            "sha256": None,
            "version_output": None,
        }
    entry_count = report["summary"]["entry_count"]
    if not solver["exists"]:
        state = "NO_SOLVER_SELECTED"
        next_action = "Provide --executable or place one recognizable OpenFAST executable in the directory."
    elif entry_count == 0:
        state = "SOLVER_ONLY"
        next_action = "Obtain a version-compatible, source-pinned complete model and run it unchanged."
    else:
        state = "MODEL_PRESENT"
        next_action = "Inspect dependencies and establish an unchanged baseline run."
    payload = {
        "schema_version": "1.0",
        "state": state,
        "solver": solver,
        "inspection": report,
        "next_action": next_action,
        "warning": "Solver health is not a physical simulation result.",
    }
    if args.output:
        write_json(args.output, payload)
    print(f"State: {state}")
    print(f"Solver: {solver['path'] or 'not selected'}")
    print(f"Entry files: {entry_count}")
    print(f"Next action: {next_action}")


if __name__ == "__main__":
    main()
