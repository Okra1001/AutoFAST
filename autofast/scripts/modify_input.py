#!/usr/bin/env python3
"""Safely modify one exact scalar field in an OpenFAST-style input file."""

from __future__ import annotations

import argparse
import difflib
import shutil
from pathlib import Path

from openfast_common import FIELD_LINE, atomic_write, newline_style, read_text


def replace_exact_field(text: str, field: str, value: str) -> tuple[str, int, str]:
    newline = newline_style(text)
    lines = text.splitlines()
    matches: list[tuple[int, object]] = []
    in_outlist = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("outlist"):
            in_outlist = True
            continue
        if in_outlist:
            if stripped.strip("\"'").upper() == "END":
                in_outlist = False
            continue
        match = FIELD_LINE.match(line)
        if match and match.group("field").lower() == field.lower():
            matches.append((index, match))
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one exact field match for {field!r}; found {len(matches)}"
        )
    index, match = matches[0]
    old_value = match.group("value")
    lines[index] = (
        f"{match.group('indent')}{value}{match.group('spacing')}"
        f"{match.group('field')}{match.group('suffix') or ''}"
    )
    trailing = newline if text.endswith(("\n", "\r")) else ""
    return newline.join(lines) + trailing, index + 1, old_value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("field")
    parser.add_argument("value")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    args = parser.parse_args()

    original, encoding = read_text(args.file)
    updated, line_number, old_value = replace_exact_field(
        original, args.field, args.value
    )
    diff = difflib.unified_diff(
        original.splitlines(),
        updated.splitlines(),
        fromfile=str(args.file),
        tofile=str(args.file),
        lineterm="",
    )
    print("\n".join(diff))
    print(
        f"Field {args.field} line {line_number}: {old_value} -> {args.value}"
    )
    if args.dry_run:
        print("Dry run: no file written.")
        return
    if args.backup:
        backup = args.file.with_suffix(args.file.suffix + ".bak")
        shutil.copy2(args.file, backup)
        print(f"Backup: {backup}")
    atomic_write(args.file, updated, encoding)
    reparsed, _ = read_text(args.file)
    _, _, written_value = replace_exact_field(reparsed, args.field, old_value)
    if written_value != args.value:
        raise RuntimeError("Post-write verification failed")
    print(f"Updated: {args.file.resolve()}")


if __name__ == "__main__":
    main()
