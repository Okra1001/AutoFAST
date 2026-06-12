#!/usr/bin/env python3
"""Create a portable provenance manifest for an OpenFAST case."""

from __future__ import annotations

import argparse
import csv
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from openfast_common import dependency_graph, sha256, write_json


def executable_version(executable: Path) -> str:
    attempts = ([str(executable), "-version"], [str(executable), "-help"])
    for command in attempts:
        try:
            result = subprocess.run(
                command,
                cwd=executable.parent,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=15,
                check=False,
            )
            output = (result.stdout + "\n" + result.stderr).strip()
            if output:
                return output[:4000]
        except (OSError, subprocess.TimeoutExpired):
            continue
    return "Version output unavailable"


def create(entry: Path, executable: Path | None, output: Path) -> dict:
    entry = entry.resolve()
    output.mkdir(parents=True, exist_ok=True)
    graph = dependency_graph(entry)
    hashes: list[dict[str, str | int]] = []
    for filename in graph["files"]:
        path = Path(filename)
        if path.exists() and path.is_file():
            hashes.append(
                {
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    if executable and executable.exists():
        hashes.append(
            {
                "path": str(executable.resolve()),
                "bytes": executable.stat().st_size,
                "sha256": sha256(executable),
            }
        )
    with (output / "file_hashes.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(hashes)
    write_json(output / "inspection.json", graph)
    environment = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "hostname": platform.node(),
    }
    write_json(output / "environment.json", environment)
    manifest = {
        "schema_version": "1.0",
        "entry": str(entry),
        "executable": str(executable.resolve()) if executable else None,
        "executable_version": executable_version(executable)
        if executable
        else None,
        "dependency_count": len(graph["files"]),
        "missing_reference_count": len(graph["missing"]),
        "hash_count": len(hashes),
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("entry", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = create(args.entry, args.executable, args.output)
    print(f"Provenance: {args.output.resolve()}")
    print(f"Dependencies hashed: {manifest['dependency_count']}")
    print(f"Missing references: {manifest['missing_reference_count']}")


if __name__ == "__main__":
    main()
