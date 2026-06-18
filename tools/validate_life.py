#!/usr/bin/env python3
"""Validate referential integrity of the life ontology (read-only).

This is the "guardrail" the hand-edit workflow (Mode A) otherwise lacks: it
checks that every reference in the ontology actually resolves to something real.

What it checks:
  1. Every YAML file parses.
  2. Every object-id reference (*_ref / *_refs / related_workout / related_meal /
     companions) points to an `id:` defined somewhere in life/ or .codex/,
     including ids harvested from imported .jsonl indexes.
  3. Every local file-path reference (value that looks like a path) points to a
     file that exists on disk.
  External http(s) URLs are listed but not fetched.

Usage:
    python3 tools/validate_life.py            # summary + any problems
    python3 tools/validate_life.py --verbose  # also list every reference
Exit code: 0 if clean, 1 if any broken id or missing file is found.
"""
import os, sys, glob, json, yaml
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBOSE = "--verbose" in sys.argv

AREA_IDS = {"MIND", "BODY", "CAREER", "FINANCE", "RELATION", "MAINTENANCE", "FUN"}
# id-valued keys that don't end in _ref/_refs
EXTRA_REF_KEYS = {"related_workout", "related_meal", "companions"}
# pseudo-ids used as references without a backing object
ALLOWED_PSEUDO_IDS = {"walking"}
FILE_EXT = (".yaml", ".yml", ".jsonl", ".json", ".md", ".pdf",
            ".png", ".jpg", ".jpeg", ".html", ".txt", ".docx")


def is_ref_key(k):
    return k.endswith("_ref") or k.endswith("_refs") or k in EXTRA_REF_KEYS


def is_url(v):
    return v.startswith("http://") or v.startswith("https://")


def looks_like_path(v):
    return "/" in v or v.lower().endswith(FILE_EXT)


def collect_ids(node, into):
    if isinstance(node, dict):
        if isinstance(node.get("id"), str):
            into.setdefault(node["id"], True)
        for v in node.values():
            collect_ids(v, into)
    elif isinstance(node, list):
        for v in node:
            collect_ids(v, into)


def collect_refs(node, f, out, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}" if path else k
            if is_ref_key(k):
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, str) and x:
                        out.append((f, here, k, x))
            collect_refs(v, f, out, here)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            collect_refs(v, f, out, f"{path}[{i}]")


def main():
    yaml_files = sorted(glob.glob(os.path.join(ROOT, "life", "**", "*.yaml"), recursive=True)) + \
                 sorted(glob.glob(os.path.join(ROOT, ".codex", "*.yaml")))
    jsonl_files = sorted(glob.glob(os.path.join(ROOT, "life", "**", "*.jsonl"), recursive=True))

    defined = {}
    refs = []
    parse_fail = []

    for f in yaml_files:
        rel = os.path.relpath(f, ROOT)
        try:
            with open(f) as fh:
                doc = yaml.safe_load(fh)
        except Exception as e:
            parse_fail.append((rel, str(e)))
            continue
        collect_ids(doc, defined)
        collect_refs(doc, rel, refs)

    for f in jsonl_files:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    collect_ids(json.loads(line), defined)
                except Exception:
                    pass

    known = set(defined) | AREA_IDS | ALLOWED_PSEUDO_IDS

    url_refs = [r for r in refs if is_url(r[3])]
    id_refs = [r for r in refs if not is_url(r[3]) and not looks_like_path(r[3])]
    file_refs = [r for r in refs if not is_url(r[3]) and looks_like_path(r[3])]

    broken_ids = [r for r in id_refs if r[3] not in known]
    missing_files = [r for r in file_refs
                     if not os.path.exists(os.path.join(ROOT, r[3]))]

    print(f"yaml files       : {len(yaml_files)}  (parse failures: {len(parse_fail)})")
    print(f"jsonl files      : {len(jsonl_files)}")
    print(f"defined ids      : {len(defined)}")
    print(f"id references    : {len(id_refs)}  (broken: {len(broken_ids)})")
    print(f"file references  : {len(file_refs)}  (missing: {len(missing_files)})")
    print(f"external urls    : {len(url_refs)}  (not checked)")
    print("=" * 60)

    def report(title, items, render):
        print(f"\n### {title}: {len(items)}")
        if not items:
            print("  OK")
            return
        by_file = defaultdict(list)
        for r in items:
            by_file[r[0]].append(r)
        for f in sorted(by_file):
            print(f"\n{f}:")
            for r in by_file[f]:
                print("  " + render(r))

    if parse_fail:
        report("YAML PARSE FAILURES", parse_fail, lambda r: f"- {r[0]}: {r[1]}")
    report("BROKEN object-id references", broken_ids,
           lambda r: f"- {r[2]} = '{r[3]}'   (at {r[1]})")
    report("MISSING file references", missing_files,
           lambda r: f"- {r[2]} = '{r[3]}'   (at {r[1]})")
    if VERBOSE:
        report("ALL id references (resolved)",
               [r for r in id_refs if r[3] in known],
               lambda r: f"- {r[2]} = '{r[3]}'")

    bad = len(broken_ids) + len(missing_files) + len(parse_fail)
    print("\n" + ("FAIL: %d problem(s)." % bad if bad else "PASS: all references resolve."))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
