#!/usr/bin/env python3
"""Compare common channels in two controlled OpenFAST outputs."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from analyze_output import parse_binary_output, parse_text_output


def load(path: Path):
    return (
        parse_binary_output(path)
        if path.suffix.lower() == ".outb"
        else parse_text_output(path)
    )


def canonical(name: str) -> str:
    return name.split("[", 1)[0].strip()


def linear_interpolate(x, y, targets):
    result = []
    index = 0
    for target in targets:
        while index + 1 < len(x) and x[index + 1] < target:
            index += 1
        if target <= x[0]:
            result.append(y[0])
        elif target >= x[-1]:
            result.append(y[-1])
        else:
            left, right = index, index + 1
            weight = (target - x[left]) / (x[right] - x[left])
            result.append(y[left] + weight * (y[right] - y[left]))
    return result


def compare(base, candidate, start_time):
    base_names, _, base_rows = base
    cand_names, _, cand_rows = candidate
    base_map = {canonical(name): i for i, name in enumerate(base_names)}
    cand_map = {canonical(name): i for i, name in enumerate(cand_names)}
    common = sorted(set(base_map) & set(cand_map))
    time_name = next((name for name in common if name.lower() == "time"), None)
    if time_name is None:
        raise ValueError("Both outputs require a Time channel")
    bi, ci = base_map[time_name], cand_map[time_name]
    base_rows = [
        row for row in base_rows if start_time is None or row[bi] >= start_time
    ]
    cand_rows = [
        row for row in cand_rows if start_time is None or row[ci] >= start_time
    ]
    if not base_rows or not cand_rows:
        raise ValueError("No overlapping data after start-time filtering")
    candidate_time = [row[ci] for row in cand_rows]
    overlap = [
        time for time in candidate_time
        if base_rows[0][bi] <= time <= base_rows[-1][bi]
    ]
    rows = []
    for name in common:
        if name == time_name:
            continue
        base_values = [row[base_map[name]] for row in base_rows]
        cand_values_all = [row[cand_map[name]] for row in cand_rows]
        cand_values = [
            value
            for time, value in zip(candidate_time, cand_values_all)
            if base_rows[0][bi] <= time <= base_rows[-1][bi]
        ]
        reference = linear_interpolate(
            [row[bi] for row in base_rows], base_values, overlap
        )
        if not reference or not all(
            math.isfinite(value) for value in reference + cand_values
        ):
            continue
        errors = [value - ref for ref, value in zip(reference, cand_values)]
        rmse = math.sqrt(statistics.fmean(error * error for error in errors))
        denominator = statistics.fmean(abs(value) for value in reference)
        rows.append(
            {
                "channel": name,
                "baseline_mean": statistics.fmean(reference),
                "candidate_mean": statistics.fmean(cand_values),
                "mean_bias_candidate_minus_baseline": statistics.fmean(errors),
                "rmse": rmse,
                "rrmse_percent_mean_abs_denominator": (
                    100.0 * rmse / denominator if denominator else None
                ),
            }
        )
    return {
        "schema_version": "1.0",
        "statistics_start_time": start_time,
        "overlap_samples": len(overlap),
        "channels": rows,
        "rrmse_denominator": "mean absolute baseline value",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--start-time", type=float)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = compare(load(args.baseline), load(args.candidate), args.start_time)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        args.json.write_text(payload, encoding="utf-8")
    print(f"Overlap samples: {report['overlap_samples']}")
    print(f"Common numeric channels compared: {len(report['channels'])}")
    if args.json:
        print(f"Report: {args.json.resolve()}")


if __name__ == "__main__":
    main()
