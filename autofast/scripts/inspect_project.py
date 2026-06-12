#!/usr/bin/env python3
"""Inspect an OpenFAST directory and build conservative dependency graphs."""

from __future__ import annotations

import argparse
from pathlib import Path

from openfast_common import (
    ENTRY_SUFFIXES,
    dependency_graph,
    find_executables,
    walk_files,
    write_json,
)


MODULE_HINTS = {
    "aerodyn": "AeroDyn",
    "beamdyn": "BeamDyn",
    "elastodyn": "ElastoDyn",
    "servodyn": "ServoDyn",
    "inflowwind": "InflowWind",
    "hydrodyn": "HydroDyn",
    "seastate": "SeaState",
    "subdyn": "SubDyn",
    "moordyn": "MoorDyn",
    "icedyn": "IceDyn",
    "fast.farm": "FAST.Farm",
}


def inspect(root: Path) -> dict:
    root = root.resolve()
    files = list(walk_files(root))
    entries = sorted(path for path in files if path.suffix.lower() in ENTRY_SUFFIXES)
    executables = find_executables(root)
    graphs = [dependency_graph(entry) for entry in entries]
    module_names: set[str] = set()
    for graph in graphs:
        for filename in graph["files"]:
            lower = Path(filename).name.lower()
            for hint, module in MODULE_HINTS.items():
                if hint in lower:
                    module_names.add(module)
    missing_all = [
        item for graph in graphs for item in graph["missing"]
    ]
    absolute_all = [
        item for graph in graphs for item in graph["absolute_references"]
    ]
    missing = len({item["resolved"] for item in missing_all})
    absolute = len({item["resolved"] for item in absolute_all})
    if not entries:
        readiness = "NO_RUNNABLE_MODEL"
    elif missing:
        readiness = "REVIEW_UNRESOLVED_REFERENCES"
    elif absolute:
        readiness = "PASS_WITH_PORTABILITY_WARNINGS"
    else:
        readiness = "PASS_STATIC_INSPECTION"
    return {
        "schema_version": "1.0",
        "root": str(root),
        "readiness": readiness,
        "entry_files": [str(path) for path in entries],
        "executables": [str(path) for path in executables],
        "module_hints": sorted(module_names),
        "summary": {
            "entry_count": len(entries),
            "executable_count": len(executables),
            "missing_reference_count": missing,
            "missing_reference_occurrences": len(missing_all),
            "absolute_reference_count": absolute,
            "absolute_reference_occurrences": len(absolute_all),
        },
        "graphs": graphs,
        "limitations": [
            "Reference discovery is conservative and not a complete schema parser.",
            "Unresolved references may belong to disabled modules; review them against active switches.",
            "Review version-specific, generated, or extensionless resources manually.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(args.path)
    if args.output:
        write_json(args.output, report)
    print(f"Readiness: {report['readiness']}")
    print(f"Entries: {report['summary']['entry_count']}")
    print(f"Executables: {report['summary']['executable_count']}")
    print(f"Missing references: {report['summary']['missing_reference_count']}")
    print(f"Absolute references: {report['summary']['absolute_reference_count']}")
    if args.output:
        print(f"Report: {args.output.resolve()}")


if __name__ == "__main__":
    main()
