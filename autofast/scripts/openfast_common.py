"""Shared helpers for AutoFAST v1.0.

The parser is deliberately conservative. It recognizes common OpenFAST scalar
records and file references without pretending to implement every module schema.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


INPUT_SUFFIXES = {
    ".fst",
    ".dvr",
    ".drv",
    ".dat",
    ".txt",
    ".inp",
    ".ipt",
    ".yaml",
    ".yml",
    ".json",
}
RESOURCE_SUFFIXES = {
    ".dll",
    ".so",
    ".dylib",
    ".bts",
    ".wnd",
    ".hh",
    ".sum",
    ".gdf",
    ".1",
    ".3",
    ".hst",
    ".ss",
    ".hyd",
}
ENTRY_SUFFIXES = {".fst", ".dvr", ".drv"}
OUTPUT_SUFFIXES = {".out", ".outb", ".ech", ".sum"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}

FIELD_LINE = re.compile(
    r"^(?P<indent>\s*)(?P<value>\"[^\"]*\"|'[^']*'|\S+)"
    r"(?P<spacing>\s+)(?P<field>[A-Za-z][A-Za-z0-9_().-]*)"
    r"(?P<suffix>\s*(?:-|!).*)?$"
)
QUOTED_PATH = re.compile(r"[\"']([^\"']+)[\"']")
UNQUOTED_FILE = re.compile(
    r"(?<![\w./\\-])([A-Za-z0-9_@+().:/\\-]+\.[A-Za-z0-9]{1,8})(?![\w./\\-])"
)


@dataclass
class ScalarRecord:
    line_number: int
    field: str
    value: str
    raw: str


@dataclass
class FileReference:
    source: str
    line_number: int
    field: str | None
    raw_value: str
    resolved: str
    exists: bool
    absolute: bool


def read_text(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1"), "latin-1"


def newline_style(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def parse_scalar_records(path: Path) -> list[ScalarRecord]:
    text, _ = read_text(path)
    records: list[ScalarRecord] = []
    in_outlist = False
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.lower().startswith("outlist"):
            in_outlist = True
            continue
        if in_outlist:
            if stripped.strip("\"'").upper() == "END":
                in_outlist = False
            continue
        if not stripped or stripped.startswith(("!", "#", "---", "===", "-------")):
            continue
        match = FIELD_LINE.match(raw)
        if match:
            records.append(
                ScalarRecord(
                    line_number=number,
                    field=match.group("field"),
                    value=match.group("value"),
                    raw=raw,
                )
            )
    return records


def clean_reference(value: str) -> str:
    cleaned = value.strip()
    if cleaned.startswith("@"):
        cleaned = cleaned[1:].strip()
    cleaned = cleaned.strip("\"'")
    return os.path.expandvars(cleaned.replace("/", os.sep))


def looks_like_reference(value: str) -> bool:
    cleaned = value.strip()
    if cleaned.startswith("@"):
        cleaned = cleaned[1:].strip()
    cleaned = cleaned.strip("\"'")
    if not cleaned or "<" in cleaned or ">" in cleaned:
        return False
    try:
        float(cleaned)
        return False
    except ValueError:
        pass
    suffix = Path(cleaned).suffix.lower()
    return bool(
        suffix in INPUT_SUFFIXES
        or suffix in RESOURCE_SUFFIXES
        or "\\" in cleaned
        or "/" in cleaned
    )


def extract_references(path: Path) -> list[FileReference]:
    text, _ = read_text(path)
    found: list[FileReference] = []
    seen: set[tuple[int, str]] = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith(("!", "#")):
            continue
        data_region = re.split(r"\s+-\s+|\s+!\s*", raw, maxsplit=1)[0]
        candidates: list[tuple[str, str | None]] = [
            (candidate, None) for candidate in QUOTED_PATH.findall(data_region)
        ]
        candidates.extend(
            (candidate, None) for candidate in UNQUOTED_FILE.findall(data_region)
        )
        scalar = FIELD_LINE.match(data_region)
        if scalar:
            candidates.append((scalar.group("value"), scalar.group("field")))
        for candidate, field in candidates:
            if not looks_like_reference(candidate):
                continue
            cleaned = clean_reference(candidate)
            if cleaned.lower() in {"unused", "none", "default", "true", "false"}:
                continue
            key = (number, cleaned.lower())
            if key in seen:
                continue
            seen.add(key)
            raw_path = Path(cleaned)
            resolved = raw_path if raw_path.is_absolute() else path.parent / raw_path
            try:
                normalized = resolved.resolve(strict=False)
            except OSError:
                normalized = resolved.absolute()
            found.append(
                FileReference(
                    source=str(path),
                    line_number=number,
                    field=field,
                    raw_value=candidate,
                    resolved=str(normalized),
                    exists=normalized.exists(),
                    absolute=raw_path.is_absolute(),
                )
            )
    return found


def walk_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def dependency_graph(entry: Path, max_files: int = 2000) -> dict:
    entry = entry.resolve()
    queue = [entry]
    visited: set[Path] = set()
    references: list[FileReference] = []
    while queue and len(visited) < max_files:
        current = queue.pop(0)
        if current in visited or not current.exists() or not current.is_file():
            continue
        visited.add(current)
        if current.suffix.lower() not in INPUT_SUFFIXES:
            continue
        for reference in extract_references(current):
            references.append(reference)
            target = Path(reference.resolved)
            if (
                reference.exists
                and target.is_file()
                and target.suffix.lower() in INPUT_SUFFIXES
                and target not in visited
            ):
                queue.append(target)
    return {
        "entry": str(entry),
        "files": sorted(str(path) for path in visited),
        "references": [asdict(item) for item in references],
        "missing": [asdict(item) for item in references if not item.exists],
        "absolute_references": [
            asdict(item) for item in references if item.absolute
        ],
        "truncated": bool(queue),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write(path: Path, text: str, encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding=encoding,
        newline="",
        dir=path.parent,
        delete=False,
    ) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def find_executables(root: Path) -> list[Path]:
    names = re.compile(
        r"(openfast|aerodyn.*driver|beamdyn.*driver|hydrodyn.*driver|fast\.farm)",
        re.IGNORECASE,
    )
    return sorted(
        path
        for path in walk_files(root)
        if path.suffix.lower() in {".exe", ""}
        and names.search(path.name)
    )


def normal_termination(text: str) -> bool:
    return bool(
        re.search(
            r"(openfast\s+terminated\s+normally|terminated\s+normally)",
            text,
            re.IGNORECASE,
        )
    )


def fatal_messages(text: str) -> list[str]:
    patterns = (
        r"fatal\s+error.*",
        r"severe\s+error.*",
        r"forrtl:\s*severe.*",
        r"segmentation\s+fault.*",
        r"traceback.*",
    )
    lines = text.splitlines()
    return [
        line.strip()
        for line in lines
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns)
    ]
