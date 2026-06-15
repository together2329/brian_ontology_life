#!/usr/bin/env python3
"""Small CLI for querying Brian's local life ontology files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = REPO_ROOT / "life/tasks"
CONCEPT_DIR = REPO_ROOT / "life/concepts"

RECORD_INDEXES = [
    ("review", REPO_ROOT / "life/imports/review_archive/entity_linked_records.jsonl"),
    ("gratitude", REPO_ROOT / "life/imports/bke_gratitude_diary_2019/entity_linked_entries.jsonl"),
    ("obsidian_daily", REPO_ROOT / "life/imports/obsidian_daily/entity_linked_records.jsonl"),
    ("happiness_pages", REPO_ROOT / "life/imports/happiness_bundle/page_index.jsonl"),
    ("happiness_images", REPO_ROOT / "life/imports/happiness_bundle/image_index.jsonl"),
]

DAILY_INDEXES = [
    ("review", REPO_ROOT / "life/imports/review_archive/daily_summary.jsonl"),
    ("gratitude", REPO_ROOT / "life/imports/bke_gratitude_diary_2019/daily_summary.jsonl"),
    ("obsidian_daily", REPO_ROOT / "life/imports/obsidian_daily/daily_summary.jsonl"),
]

ACTIVE_STATUSES = {"todo", "planned", "in_progress", "in_review", "waiting_on_synthesis", "blocked"}
STATUS_RANK = {
    "in_progress": 0,
    "in_review": 1,
    "waiting_on_synthesis": 2,
    "todo": 3,
    "planned": 4,
    "blocked": 5,
    "completed": 9,
}
TASK_SEARCH_SECTIONS = [
    "source_records",
    "tasks",
    "planned_time_blocks",
    "work_sessions",
    "task_status_updates",
    "assignments",
    "meetings",
    "recurring_meetings",
    "issues",
    "resolutions",
    "decisions",
    "artifacts",
    "milestones",
]
DIRECT_REF_KEYS = {
    "project_ref",
    "component_ref",
    "task_ref",
    "owner_ref",
    "person_ref",
    "author_ref",
    "recurring_meeting_ref",
    "activity_ref",
    "exercise_ref",
    "training_program_ref",
    "habit_ref",
    "related_workout",
    "related_nutrition_target_ref",
}
DIRECT_REF_LIST_KEYS = {
    "task_refs",
    "participants",
    "known_participant_refs",
    "participant_refs",
    "member_refs",
    "activist_member_refs",
    "people_refs",
    "subjects",
    "linked_entities",
    "related_entities",
}


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def dump_result(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def compact_text(value: Any, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value)


def collect_ref_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        refs: List[str] = []
        for item in value:
            refs.extend(collect_ref_values(item))
        return refs
    if isinstance(value, dict):
        return collect_ref_values(value.get("entity_refs"))
    return []


def iso_date(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def record_date(record: Dict[str, Any]) -> Optional[str]:
    return iso_date(record.get("date") or record.get("original_date"))


def record_title(record: Dict[str, Any]) -> str:
    return (
        record.get("title")
        or record.get("gratitude_text")
        or record.get("text_excerpt")
        or record.get("summary")
        or record.get("raw_text")
        or record.get("notes")
        or record.get("id")
        or ""
    )


def record_excerpt(record: Dict[str, Any]) -> str:
    return compact_text(
        record.get("summary")
        or record.get("raw_text_excerpt")
        or record.get("raw_text")
        or record.get("gratitude_text")
        or record.get("text_excerpt")
        or record.get("notes")
        or record_title(record),
        220,
    )


def entity_refs(record: Dict[str, Any]) -> List[str]:
    refs = []
    for link in record.get("semantic_links") or []:
        refs.append(link.get("entity_ref"))
    linked_entities = record.get("linked_entities") or {}
    refs.extend(collect_ref_values(linked_entities))
    entity_ref_map = record.get("entity_refs") or {}
    if isinstance(entity_ref_map, dict):
        for values in entity_ref_map.values():
            refs.extend(collect_ref_values(values))
    else:
        refs.extend(collect_ref_values(entity_ref_map))
    for key in DIRECT_REF_KEYS:
        if record.get(key):
            refs.append(record.get(key))
    for key in DIRECT_REF_LIST_KEYS:
        refs.extend(collect_ref_values(record.get(key)))
    return sorted(set(ref for ref in refs if ref))


def record_text(record: Dict[str, Any]) -> str:
    parts = [
        record.get("id"),
        record_title(record),
        record.get("summary"),
        record.get("raw_text_excerpt"),
        record.get("gratitude_text"),
        record.get("text_excerpt"),
        record.get("raw_text"),
        record.get("notes"),
        flatten_text(record.get("topics")),
        flatten_text(record.get("findings")),
        flatten_text(record.get("next_steps")),
        " ".join(entity_refs(record)),
    ]
    return "\n".join(str(part) for part in parts if part)


def project_matches(project: Optional[str], task_file: Dict[str, Any], task: Optional[Dict[str, Any]] = None) -> bool:
    if not project:
        return True
    query = project.lower()
    candidates = [
        task_file.get("project_ref"),
        task_file.get("title"),
        task_file.get("current_phase"),
    ]
    if task:
        candidates.extend([task.get("project_ref"), task.get("id"), task.get("title")])
    normalized = [str(candidate or "").lower() for candidate in candidates]
    return any(query in candidate or f"project_{query}" in candidate for candidate in normalized)


def load_task_files() -> List[Dict[str, Any]]:
    task_files = []
    for path in sorted(TASK_DIR.glob("*.yaml")):
        data = load_yaml(path)
        data["_path"] = str(path.relative_to(REPO_ROOT))
        task_files.append(data)
    return task_files


def iter_task_search_records() -> Iterable[Dict[str, Any]]:
    for task_file in load_task_files():
        for section in TASK_SEARCH_SECTIONS:
            for row in task_file.get(section) or []:
                if not isinstance(row, dict):
                    continue
                enriched = dict(row)
                enriched.setdefault("project_ref", task_file.get("project_ref"))
                enriched.setdefault("area", task_file.get("area"))
                enriched["_source"] = f"task:{section}"
                enriched["_source_file"] = task_file["_path"]
                enriched["_record_kind"] = section
                yield enriched


def recent_update_for(task_file: Dict[str, Any], task_id: str) -> Optional[Dict[str, Any]]:
    updates = [u for u in task_file.get("task_status_updates") or [] if u.get("task_ref") == task_id]
    return updates[-1] if updates else None


def cmd_tasks(args: argparse.Namespace) -> None:
    rows = []
    for task_file in load_task_files():
        if not project_matches(args.project, task_file):
            continue
        for task in task_file.get("tasks") or []:
            if not project_matches(args.project, task_file, task):
                continue
            if args.active and task.get("status") not in ACTIVE_STATUSES:
                continue
            if args.status and task.get("status") != args.status:
                continue
            update = recent_update_for(task_file, task.get("id"))
            rows.append(
                {
                    "project_ref": task.get("project_ref") or task_file.get("project_ref"),
                    "task_ref": task.get("id"),
                    "title": task.get("title"),
                    "status": task.get("status"),
                    "priority": task.get("priority"),
                    "progress_percent": task.get("progress_percent"),
                    "due_date": task.get("due_date"),
                    "next_action": (task.get("next_actions") or [None])[0],
                    "recent_update": update,
                    "source_file": task_file["_path"],
                }
            )
    rows.sort(key=lambda row: (STATUS_RANK.get(row["status"], 8), -(row.get("progress_percent") or 0), row["task_ref"]))
    if args.json:
        dump_result(rows, True)
        return
    print(f"tasks={len(rows)}")
    for idx, row in enumerate(rows, 1):
        progress = "n/a" if row["progress_percent"] is None else f"{row['progress_percent']}%"
        print(f"{idx:02d}. [{row['status']}] {progress} {row['task_ref']}")
        print(f"    {row['title']}")
        if row.get("next_action"):
            print(f"    next: {row['next_action']}")
        update = row.get("recent_update") or {}
        if update.get("summary"):
            print(f"    latest: {update.get('date')} - {compact_text(update.get('summary'), 160)}")


def daily_rows(date_value: str) -> List[Dict[str, Any]]:
    rows = []
    for source, path in DAILY_INDEXES:
        for row in iter_jsonl(path):
            if iso_date(row.get("date")) == date_value:
                enriched = dict(row)
                enriched["_source"] = source
                rows.append(enriched)
    return rows


def records_for_date(date_value: str) -> List[Dict[str, Any]]:
    rows = []
    for source, path in RECORD_INDEXES[:3]:
        for row in iter_jsonl(path):
            if record_date(row) == date_value:
                enriched = dict(row)
                enriched["_source"] = source
                rows.append(enriched)
    return rows


def task_time_for_date(date_value: str) -> Dict[str, List[Dict[str, Any]]]:
    result = {"planned_time_blocks": [], "work_sessions": [], "task_status_updates": []}
    for task_file in load_task_files():
        for key in result:
            for row in task_file.get(key) or []:
                row_date = iso_date(row.get("date") or row.get("original_date"))
                if row_date == date_value:
                    enriched = dict(row)
                    enriched["_project_ref"] = task_file.get("project_ref")
                    enriched["_source_file"] = task_file["_path"]
                    result[key].append(enriched)
    return result


def cmd_daily(args: argparse.Namespace) -> None:
    rows = daily_rows(args.date)
    records = records_for_date(args.date)
    task_time = task_time_for_date(args.date)
    result = {"date": args.date, "summaries": rows, "records": records, "task_time": task_time}
    if args.json:
        dump_result(result, True)
        return
    print(f"date={args.date}")
    for row in rows:
        print(f"\n[{row['_source']}]")
        if "total_timeblock_minutes" in row:
            print(f"  time_blocks={row.get('time_block_count')} minutes={row.get('total_timeblock_minutes')}")
            print(f"  area_minutes={row.get('area_minutes')}")
            if row.get("avg_energy_score") is not None:
                print(f"  avg_energy={row.get('avg_energy_score')}")
            if row.get("top_timeblock_titles"):
                print(f"  top={', '.join(row.get('top_timeblock_titles')[:8])}")
        elif "entry_count" in row:
            print(f"  gratitude_entries={row.get('entry_count')} areas={row.get('area_counts')}")
        else:
            print(f"  summary={row}")
    if any(task_time.values()):
        print("\n[task_time]")
        for key, values in task_time.items():
            for row in values:
                label = row.get("task_ref") or row.get("title") or row.get("id")
                time_part = f"{row.get('start', '')}-{row.get('end', '')}".strip("-")
                print(f"  {key}: {time_part} {label}")
                if row.get("summary"):
                    print(f"    {compact_text(row.get('summary'), 180)}")
    if records:
        print(f"\n[records] count={len(records)}")
        for row in records[: args.limit]:
            print(f"  - {row['_source']} {row.get('id')} {row.get('area')} {record_title(row)}")
            print(f"    {record_excerpt(row)}")


def cmd_today(args: argparse.Namespace) -> None:
    args.date = args.date or dt.date.today().isoformat()
    cmd_daily(args)


def cmd_search(args: argparse.Namespace) -> None:
    hits = []
    for source, path in RECORD_INDEXES:
        for row in iter_jsonl(path):
            if args.entity and args.entity not in entity_refs(row):
                continue
            if args.keyword and args.keyword.lower() not in record_text(row).lower():
                continue
            enriched = dict(row)
            enriched["_source"] = source
            hits.append(enriched)
    for row in iter_task_search_records():
        if args.entity and args.entity not in entity_refs(row):
            continue
        if args.keyword and args.keyword.lower() not in record_text(row).lower():
            continue
        hits.append(row)
    hits.sort(key=lambda row: (record_date(row) or "", row.get("id") or ""))
    result = hits[: args.limit]
    if args.json:
        dump_result(result, True)
        return
    print(f"hits={len(hits)} showing={len(result)}")
    for row in result:
        print(f"- {record_date(row)} [{row['_source']}] {row.get('id')} {row.get('area', '')} {record_title(row)}")
        print(f"  entities={', '.join(entity_refs(row)[:10])}")
        print(f"  {record_excerpt(row)}")


def load_concepts() -> List[Dict[str, Any]]:
    concepts = []
    for path in sorted(CONCEPT_DIR.glob("*.yaml")):
        data = load_yaml(path)
        data["_path"] = str(path.relative_to(REPO_ROOT))
        concepts.append(data)
    return concepts


def cmd_concept(args: argparse.Namespace) -> None:
    query = (args.keyword or "").lower()
    concept_hits = []
    for concept in load_concepts():
        if args.entity and concept.get("id") != args.entity:
            continue
        text = "\n".join(
            str(part)
            for part in [
                concept.get("id"),
                concept.get("display_name"),
                concept.get("definition"),
                " ".join(concept.get("aliases") or []),
            ]
            if part
        ).lower()
        if not query or query in text:
            concept_hits.append(concept)

    record_hits = []
    if args.keyword or args.entity:
        for source, path in RECORD_INDEXES:
            for row in iter_jsonl(path):
                if args.keyword and query not in record_text(row).lower():
                    continue
                if args.entity and args.entity not in entity_refs(row):
                    continue
                enriched = dict(row)
                enriched["_source"] = source
                record_hits.append(enriched)

    summary = summarize_records(record_hits)
    result = {"concepts": concept_hits, "record_count": len(record_hits), "summary": summary, "records": record_hits[: args.limit]}
    if args.json:
        dump_result(result, True)
        return
    print(f"concepts={len(concept_hits)}")
    for concept in concept_hits:
        print(f"- {concept.get('id')} ({concept.get('display_name')}) {concept.get('_path')}")
        print(f"  {compact_text(concept.get('definition'), 220)}")
    print(f"\nrecords={len(record_hits)}")
    print(f"areas={summary['areas']}")
    print(f"emotions={summary['emotions']}")
    print(f"top_entities={summary['top_entities'][:10]}")
    for row in record_hits[: args.limit]:
        print(f"- {record_date(row)} [{row['_source']}] {row.get('id')} {row.get('area', '')} {record_title(row)}")
        print(f"  {record_excerpt(row)}")


def summarize_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    areas = Counter(row.get("area") for row in records if row.get("area"))
    emotions = Counter()
    entities = Counter()
    sources = Counter(row.get("_source") for row in records)
    for row in records:
        for emotion in row.get("emotion_tags") or []:
            emotions[emotion] += 1
        for ref in entity_refs(row):
            entities[ref] += 1
    return {
        "sources": dict(sources.most_common()),
        "areas": dict(areas.most_common()),
        "emotions": dict(emotions.most_common()),
        "top_entities": entities.most_common(20),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    tasks = sub.add_parser("tasks", help="List tasks from life/tasks/*.yaml")
    tasks.add_argument("--project", help="Project name or project_ref, e.g. milano")
    tasks.add_argument("--active", action="store_true", help="Exclude completed tasks")
    tasks.add_argument("--status", help="Filter by exact status")
    tasks.add_argument("--json", action="store_true")
    tasks.set_defaults(func=cmd_tasks)

    daily = sub.add_parser("daily", help="Show daily aggregate and records")
    daily.add_argument("--date", required=True, help="YYYY-MM-DD")
    daily.add_argument("--limit", type=int, default=12)
    daily.add_argument("--json", action="store_true")
    daily.set_defaults(func=cmd_daily)

    today = sub.add_parser("today", help="Show today's aggregate and records")
    today.add_argument("--date", help="Override today with YYYY-MM-DD")
    today.add_argument("--limit", type=int, default=12)
    today.add_argument("--json", action="store_true")
    today.set_defaults(func=cmd_today)

    search = sub.add_parser("search", help="Search entity-linked records")
    search.add_argument("--entity", help="Entity ref such as project_milano or concept_fulfilled_mind")
    search.add_argument("--keyword", help="Keyword text search")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    concept = sub.add_parser("concept", help="Search concept files and evidence records")
    concept.add_argument("--keyword", help="Concept keyword, e.g. 충만")
    concept.add_argument("--entity", help="Concept entity ref, e.g. concept_fulfilled_mind")
    concept.add_argument("--limit", type=int, default=20)
    concept.add_argument("--json", action="store_true")
    concept.set_defaults(func=cmd_concept)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
