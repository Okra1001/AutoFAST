#!/usr/bin/env python3
"""Summarize OpenFAST text or binary output by channel name."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path


def parse_text_output(path: Path) -> tuple[list[str], list[str], list[list[float]]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    header = None
    for index, line in enumerate(lines):
        columns = line.split()
        if columns and columns[0].lower() == "time":
            header = index
            break
    if header is None or header + 1 >= len(lines):
        raise ValueError("Could not locate Time channel header")
    names = lines[header].split()
    units = lines[header + 1].split()
    rows = []
    for line in lines[header + 2 :]:
        parts = line.split()
        if len(parts) < len(names):
            continue
        try:
            row = [float(value) for value in parts[: len(names)]]
        except ValueError:
            continue
        rows.append(row)
    if not rows:
        raise ValueError("No numeric output rows found")
    return names, units, rows


def parse_binary_output(path: Path):
    candidates = [
        ("openfast_toolbox.io", "FASTOutputFile"),
        ("pyFAST.input_output", "FASTOutputFile"),
    ]
    for module_name, class_name in candidates:
        try:
            module = __import__(module_name, fromlist=[class_name])
            frame = getattr(module, class_name)(str(path)).toDataFrame()
            names = [str(name) for name in frame.columns]
            units = [name[name.rfind("[") :] if "[" in name else "" for name in names]
            rows = frame.to_numpy(dtype=float).tolist()
            return names, units, rows
        except (ImportError, ModuleNotFoundError):
            continue
    raise RuntimeError(
        "Binary .outb analysis requires openfast_toolbox or pyFAST. "
        "Install one verified reader or request text output."
    )


def summarize(
    names: list[str],
    units: list[str],
    rows: list[list[float]],
    start_time: float | None,
) -> dict:
    time_index = next(
        (i for i, name in enumerate(names) if name.lower().startswith("time")),
        None,
    )
    if time_index is None:
        raise ValueError("Time channel not found")
    selected = [
        row for row in rows if start_time is None or row[time_index] >= start_time
    ]
    if not selected:
        raise ValueError("No rows remain after applying start time")
    channels = {}
    for index, name in enumerate(names):
        values = [row[index] for row in selected]
        finite = all(math.isfinite(value) for value in values)
        channels[name] = {
            "unit": units[index] if index < len(units) else "",
            "count": len(values),
            "finite": finite,
            "mean": statistics.fmean(values) if finite else None,
            "std": statistics.pstdev(values) if finite and len(values) > 1 else 0.0,
            "min": min(values) if finite else None,
            "max": max(values) if finite else None,
        }
    time_values = [row[time_index] for row in selected]
    monotonic = all(b > a for a, b in zip(time_values, time_values[1:]))
    return {
        "schema_version": "1.0",
        "statistics_start_time": start_time,
        "time": {
            "first": time_values[0],
            "last": time_values[-1],
            "monotonic": monotonic,
            "samples": len(time_values),
        },
        "all_channels_finite": all(item["finite"] for item in channels.values()),
        "channels": channels,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--start-time", type=float)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    if args.output.suffix.lower() == ".outb":
        names, units, rows = parse_binary_output(args.output)
    else:
        names, units, rows = parse_text_output(args.output)
    report = summarize(names, units, rows, args.start_time)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        args.json.write_text(payload, encoding="utf-8")
    print(f"Time: {report['time']['first']} -> {report['time']['last']}")
    print(f"Samples: {report['time']['samples']}")
    print(f"Monotonic time: {report['time']['monotonic']}")
    print(f"All channels finite: {report['all_channels_finite']}")
    if args.json:
        print(f"Report: {args.json.resolve()}")
    if not report["time"]["monotonic"] or not report["all_channels_finite"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
