#!/usr/bin/env python3
"""Small read-only helper for local life ontology files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]


def yaml_files() -> list[Path]:
    paths = []
    for pattern in [".codex/*.yaml", "life/**/*.yaml", "templates/*.yaml"]:
        paths.extend(ROOT.glob(pattern))
    return sorted(paths)


def jsonl_files() -> list[Path]:
    return sorted(ROOT.glob("life/**/*.jsonl"))


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)


def iter_records() -> Iterable[tuple[Path, Any]]:
    for path in yaml_files():
        try:
            yield path, yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    for path in jsonl_files():
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    try:
                        yield path, json.loads(line)
                    except Exception:
                        continue


def collect_ids(value: Any, out: list[str]) -> None:
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            out.append(value["id"])
        for item in value.values():
            collect_ids(item, out)
    elif isinstance(value, list):
        for item in value:
            collect_ids(item, out)


def cmd_ids(_: argparse.Namespace) -> None:
    ids: list[str] = []
    for _, record in iter_records():
        collect_ids(record, ids)
    for item in sorted(set(ids)):
        print(item)


def cmd_search(args: argparse.Namespace) -> None:
    pattern = re.compile(re.escape(args.query), re.IGNORECASE)
    count = 0
    for path, record in iter_records():
        text = flatten(record)
        if pattern.search(text):
            count += 1
            rel = path.relative_to(ROOT).as_posix()
            snippet = re.sub(r"\s+", " ", text).strip()[:240]
            print(f"{rel}: {snippet}")
            if count >= args.limit:
                break
    if count == 0:
        print("No matches.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ids = sub.add_parser("ids", help="List known object IDs")
    ids.set_defaults(func=cmd_ids)

    search = sub.add_parser("search", help="Search YAML/JSONL records")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

