#!/usr/bin/env python3
"""Validate local life ontology YAML/JSONL files.

Checks:
  1. YAML files parse.
  2. JSONL files parse line by line.
  3. *_ref and *_refs values point to known IDs when they look like object IDs.
  4. Local path-like references exist.

This script is read-only.
"""

from __future__ import annotations

import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
VERBOSE = "--verbose" in sys.argv
AREA_IDS = {"MIND", "BODY", "CAREER", "FINANCE", "RELATION", "MAINTENANCE", "FUN"}
FILE_EXTENSIONS = (
    ".yaml",
    ".yml",
    ".jsonl",
    ".json",
    ".md",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".html",
    ".txt",
    ".docx",
)


def is_ref_key(key: str) -> bool:
    return key.endswith("_ref") or key.endswith("_refs")


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def looks_like_path(value: str) -> bool:
    return "/" in value or value.lower().endswith(FILE_EXTENSIONS)


def collect_ids(node: Any, into: dict[str, bool]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("id"), str):
            into[node["id"]] = True
        for value in node.values():
            collect_ids(value, into)
    elif isinstance(node, list):
        for value in node:
            collect_ids(value, into)


def collect_refs(node: Any, file_name: str, out: list[tuple[str, str, str, str]], path: str = "") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else key
            if is_ref_key(key):
                values = value if isinstance(value, list) else [value]
                for item in values:
                    if isinstance(item, str) and item:
                        out.append((file_name, here, key, item))
            collect_refs(value, file_name, out, here)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            collect_refs(value, file_name, out, f"{path}[{index}]")


def iter_yaml_files() -> list[Path]:
    paths = []
    for pattern in [".codex/*.yaml", "life/**/*.yaml", "templates/*.yaml"]:
        paths.extend(ROOT.glob(pattern))
    return sorted(paths)


def iter_jsonl_files() -> list[Path]:
    return sorted(ROOT.glob("life/**/*.jsonl"))


def report(title: str, items: list[Any], render) -> None:
    print(f"\n### {title}: {len(items)}")
    if not items:
        print("  OK")
        return
    by_file: dict[str, list[Any]] = defaultdict(list)
    for item in items:
        by_file[item[0]].append(item)
    for file_name in sorted(by_file):
        print(f"\n{file_name}:")
        for item in by_file[file_name]:
            print("  " + render(item))


def main() -> int:
    defined: dict[str, bool] = {}
    refs: list[tuple[str, str, str, str]] = []
    parse_failures: list[tuple[str, str]] = []

    yaml_files = iter_yaml_files()
    jsonl_files = iter_jsonl_files()

    for path in yaml_files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_failures.append((rel, str(exc)))
            continue
        collect_ids(doc, defined)
        collect_refs(doc, rel, refs)

    for path in jsonl_files:
        rel = path.relative_to(ROOT).as_posix()
        with path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except Exception as exc:
                    parse_failures.append((rel, f"line {line_no}: {exc}"))
                    continue
                collect_ids(record, defined)
                collect_refs(record, rel, refs)

    known_ids = set(defined) | AREA_IDS
    url_refs = [ref for ref in refs if is_url(ref[3])]
    id_refs = [ref for ref in refs if not is_url(ref[3]) and not looks_like_path(ref[3])]
    file_refs = [ref for ref in refs if not is_url(ref[3]) and looks_like_path(ref[3])]
    broken_ids = [ref for ref in id_refs if ref[3] not in known_ids]
    missing_files = [
        ref for ref in file_refs
        if not (ROOT / ref[3]).exists()
    ]

    print(f"yaml files       : {len(yaml_files)}  (parse failures: {len(parse_failures)})")
    print(f"jsonl files      : {len(jsonl_files)}")
    print(f"defined ids      : {len(defined)}")
    print(f"id references    : {len(id_refs)}  (broken: {len(broken_ids)})")
    print(f"file references  : {len(file_refs)}  (missing: {len(missing_files)})")
    print(f"external urls    : {len(url_refs)}  (not checked)")
    print("=" * 60)

    report("PARSE FAILURES", parse_failures, lambda item: f"- {item[1]}")
    report("BROKEN object-id references", broken_ids, lambda item: f"- {item[2]} = {item[3]!r} at {item[1]}")
    report("MISSING file references", missing_files, lambda item: f"- {item[2]} = {item[3]!r} at {item[1]}")

    if VERBOSE:
        resolved = [ref for ref in id_refs if ref[3] in known_ids]
        report("RESOLVED id references", resolved, lambda item: f"- {item[2]} = {item[3]!r}")

    problem_count = len(parse_failures) + len(broken_ids) + len(missing_files)
    print("\n" + (f"FAIL: {problem_count} problem(s)." if problem_count else "PASS: all references resolve."))
    return 1 if problem_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

