#!/usr/bin/env python3
"""Classify common OpenFAST failures from evidence in a log."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from openfast_common import fatal_messages, read_text, write_json


RULES = [
    {
        "id": "missing-file",
        "pattern": r"(cannot|could not|unable to).*(open|find)|file not found|no such file",
        "cause": "A referenced file cannot be resolved from the run directory.",
        "verify": "Inspect the active dependency graph and resolve the reported path from its parent input file.",
        "repair": "Correct or restore that one reference; keep model physics unchanged.",
    },
    {
        "id": "schema-version",
        "pattern": r"(error|failure).*(reading|parse)|invalid value|unexpected end",
        "cause": "The input layout or value may not match the executable/module version.",
        "verify": "Compare the failing section with a same-release official input and check required placeholder lines.",
        "repair": "Update only the incompatible field or section using the matching version schema.",
    },
    {
        "id": "runtime-library",
        "pattern": r"(dll|shared librar|\.so|\.dylib).*(not found|cannot|failed)|loadlibrary",
        "cause": "A controller or runtime library is missing or architecture-incompatible.",
        "verify": "Check library path, OS, executable architecture, and controller interface version.",
        "repair": "Provide the compatible library or correct its configured path.",
    },
    {
        "id": "numerical",
        "pattern": r"\bnan\b|\binfinity\b|\binf\b|converg|time step|singular|unstable",
        "cause": "A module encountered numerical instability or an inconsistent state.",
        "verify": "Find the earliest affected time/module and compare initial conditions and recent input changes with the baseline.",
        "repair": "Repair the identified inconsistency; treat time-step reduction as a documented diagnostic experiment.",
    },
    {
        "id": "output-channel",
        "pattern": r"(invalid|unrecognized|unknown).*(channel|outlist)|output.*not found",
        "cause": "An output channel is unavailable or misspelled for the active module/version.",
        "verify": "Check the module's same-version output-channel list and units.",
        "repair": "Correct only the invalid OutList entry.",
    },
]


def diagnose(text: str, inspection: dict | None = None) -> dict:
    evidence = fatal_messages(text)
    first_lines = [line.strip() for line in text.splitlines() if line.strip()]
    matches = []
    for rule in RULES:
        hit = next(
            (line for line in first_lines if re.search(rule["pattern"], line, re.I)),
            None,
        )
        if hit:
            matches.append({**rule, "evidence": hit})
    missing = []
    if inspection:
        for graph in inspection.get("graphs", [inspection]):
            missing.extend(graph.get("missing", []))
    if missing and not any(item["id"] == "missing-file" for item in matches):
        matches.insert(
            0,
            {
                **RULES[0],
                "evidence": f"Inspection found {len(missing)} missing references.",
            },
        )
    primary = matches[0] if matches else {
        "id": "unclassified",
        "cause": "The available evidence does not match a known high-confidence class.",
        "verify": "Provide the full log, entry file, inspection report, executable version, and first failing time.",
        "repair": "Do not change physics until the first causal error is identified.",
        "evidence": evidence[0] if evidence else "No explicit fatal line detected.",
    }
    return {
        "schema_version": "1.0",
        "primary": primary,
        "confidence": "high" if primary["id"] != "unclassified" else "low",
        "fatal_messages": evidence,
        "all_matches": matches,
        "principle": "Apply the smallest evidence-backed repair and rerun the baseline.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--inspection", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text, _ = read_text(args.log)
    inspection = (
        json.loads(args.inspection.read_text(encoding="utf-8-sig"))
        if args.inspection
        else None
    )
    report = diagnose(text, inspection)
    if args.output:
        write_json(args.output, report)
    primary = report["primary"]
    print(f"Primary finding: {primary['id']}")
    print(f"Evidence: {primary['evidence']}")
    print(f"Likely cause: {primary['cause']}")
    print(f"Confidence: {report['confidence']}")
    print(f"Verification: {primary['verify']}")
    print(f"Minimal repair: {primary['repair']}")


if __name__ == "__main__":
    main()
