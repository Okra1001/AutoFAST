#!/usr/bin/env python3
"""Run one OpenFAST or driver case and record evidence."""

from __future__ import annotations

import argparse
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from create_provenance import create
from openfast_common import (
    OUTPUT_SUFFIXES,
    fatal_messages,
    normal_termination,
    write_json,
)


def snapshot_outputs(directory: Path, stem: str) -> dict[str, tuple[int, int]]:
    result = {}
    for path in directory.glob(stem + ".*"):
        if path.is_file() and path.suffix.lower() in OUTPUT_SUFFIXES:
            stat = path.stat()
            result[str(path.resolve())] = (stat.st_size, stat.st_mtime_ns)
    return result


def run_case(
    executable: Path,
    entry: Path,
    result_dir: Path,
    timeout: float | None = None,
) -> dict:
    executable = executable.resolve()
    entry = entry.resolve()
    result_dir = result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    log = result_dir / "run.log"
    provenance = result_dir / "provenance"
    create(entry, executable, provenance)
    command = [str(executable), entry.name]
    (result_dir / "command.txt").write_text(
        subprocess.list2cmdline(command) + "\n", encoding="utf-8"
    )
    before = snapshot_outputs(entry.parent, entry.stem)
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    timed_out = False
    return_code: int | None
    with log.open("w", encoding="utf-8", errors="replace") as stream:
        try:
            completed = subprocess.run(
                command,
                cwd=entry.parent,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
            return_code = completed.returncode
        except subprocess.TimeoutExpired:
            return_code = None
            timed_out = True
    elapsed = time.perf_counter() - start
    log_text = log.read_text(encoding="utf-8", errors="replace")
    after = snapshot_outputs(entry.parent, entry.stem)
    changed_outputs = [
        path
        for path, state in after.items()
        if path not in before or before[path] != state
    ]
    nonempty_outputs = [
        path for path in changed_outputs if Path(path).stat().st_size > 0
    ]
    fatal = fatal_messages(log_text)
    normal = normal_termination(log_text)
    passed = (
        return_code == 0
        and normal
        and not fatal
        and bool(nonempty_outputs)
        and not timed_out
    )
    status = {
        "schema_version": "1.0",
        "started_at_utc": started_at,
        "elapsed_s": round(elapsed, 3),
        "command": command,
        "working_directory": str(entry.parent),
        "return_code": return_code,
        "timed_out": timed_out,
        "normal_termination": normal,
        "fatal_messages": fatal,
        "changed_outputs": changed_outputs,
        "nonempty_outputs": nonempty_outputs,
        "passed": passed,
        "log": str(log),
        "note": "Final output time and physical validity require output analysis.",
    }
    write_json(result_dir / "status.json", status)
    return status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--entry", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float)
    args = parser.parse_args()
    status = run_case(
        args.executable, args.entry, args.result_dir, args.timeout
    )
    print(f"Passed: {status['passed']}")
    print(f"Return code: {status['return_code']}")
    print(f"Normal termination: {status['normal_termination']}")
    print(f"Status: {(args.result_dir / 'status.json').resolve()}")
    raise SystemExit(0 if status["passed"] else 1)


if __name__ == "__main__":
    main()
