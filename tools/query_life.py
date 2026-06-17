#!/usr/bin/env python3
"""Small CLI for querying Brian's local life ontology files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = REPO_ROOT / "life/tasks"
BODY_DIR = REPO_ROOT / "life/body"
CONCEPT_DIR = REPO_ROOT / "life/concepts"
KNOWLEDGE_DIR = REPO_ROOT / "life/knowledge"
MIND_DIR = REPO_ROOT / "life/mind"
FINANCE_DIR = REPO_ROOT / "life/finance"
ENTITY_CATALOG_PATH = REPO_ROOT / "life/entities/semantic_entity_catalog.yaml"

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
    "event_records",
    "experience_records",
    "repositories",
    "tasks",
    "planned_time_blocks",
    "work_sessions",
    "task_status_updates",
    "project_status_updates",
    "assignments",
    "meetings",
    "recurring_meetings",
    "issues",
    "resolutions",
    "decisions",
    "artifacts",
    "artifact_candidates",
    "milestones",
]
BODY_SEARCH_SECTIONS = [
    "body_profile",
    "training_programs",
    "body_composition_records",
    "nutrition_targets",
    "exercise_catalog",
    "workout_records",
    "meal_records",
    "sleep_records",
    "trend_observations",
    "raw_records",
]
KNOWLEDGE_SEARCH_SECTIONS = [
    "source_records",
    "thought_threads",
    "understandings",
    "architecture_directions",
    "knowledge_interests",
    "follow_up_tasks",
]
MIND_SEARCH_SECTIONS = [
    "source_records",
    "mood_entries",
    "observations",
    "patterns",
    "identity_statements",
    "operating_rules",
    "interventions",
    "mind_status_updates",
]
FINANCE_SEARCH_SECTIONS = [
    "source_records",
    "finance_goals",
    "accounts",
    "assets",
    "holdings",
    "transactions",
    "spending_records",
    "tool_trials",
    "investment_decisions",
    "investment_theses",
    "investment_reviews",
    "market_trends",
    "finance_status_updates",
]
DIRECT_REF_KEYS = {
    "project_ref",
    "component_ref",
    "task_ref",
    "owner_ref",
    "person_ref",
    "author_ref",
    "profile_ref",
    "recurring_meeting_ref",
    "activity_ref",
    "exercise_ref",
    "training_program_ref",
    "habit_ref",
    "related_workout",
    "related_nutrition_target_ref",
    "source_ref",
    "clarification_source_ref",
    "participant_source_ref",
    "related_thread_ref",
    "knowledge_thread_ref",
    "related_knowledge_thread_ref",
    "latest_weight_record_ref",
    "protein_target_ref",
    "current_training_program_ref",
    "knowledge_file_ref",
    "discovered_in_session",
}
DIRECT_REF_LIST_KEYS = {
    "task_refs",
    "participants",
    "known_participant_refs",
    "participant_refs",
    "member_refs",
    "activist_member_refs",
    "related_project_refs",
    "related_issue_refs",
    "evidence_refs",
    "source_refs",
    "blocker_for",
    "related_concept_refs",
    "related_task_refs",
    "follow_up_task_refs",
    "people_refs",
    "subjects",
    "linked_entities",
    "related_entities",
}
DATE_KEYS = ("date", "original_date", "recorded_on", "created_on", "imported_at")


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
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, default=str))


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


def collect_string_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        refs: List[str] = []
        for item in value:
            refs.extend(collect_string_values(item))
        return refs
    if isinstance(value, dict):
        refs = []
        for item in value.values():
            refs.extend(collect_string_values(item))
        return refs
    return []


def is_ref_key(key: str) -> bool:
    return key.endswith("_ref") or key.endswith("_refs") or key in DIRECT_REF_KEYS or key in DIRECT_REF_LIST_KEYS


def record_ref_edges(record: Dict[str, Any]) -> List[Dict[str, str]]:
    edges: List[Dict[str, str]] = []

    def add_edge(relation: str, target_ref: Any) -> None:
        if isinstance(target_ref, str) and target_ref:
            edges.append({"relation": relation, "target_ref": target_ref})

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "semantic_links" and isinstance(item, list):
                    for link in item:
                        if isinstance(link, dict):
                            add_edge(link.get("relation") or "semantic_link", link.get("entity_ref"))
                    continue
                if key in {"entity_refs", "linked_entities"}:
                    if isinstance(item, dict):
                        for group, refs in item.items():
                            for ref in collect_string_values(refs):
                                add_edge(f"{key}.{group}", ref)
                    else:
                        for ref in collect_string_values(item):
                            add_edge(key, ref)
                    continue
                if is_ref_key(key):
                    for ref in collect_string_values(item):
                        add_edge(key, ref)
                    continue
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(record)
    unique_edges = []
    seen = set()
    for edge in edges:
        key = (edge["relation"], edge["target_ref"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)
    return unique_edges


def iso_date(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def record_date(record: Dict[str, Any]) -> Optional[str]:
    for key in DATE_KEYS:
        if record.get(key):
            return iso_date(record.get(key))
    return None


def record_title(record: Dict[str, Any]) -> str:
    return (
        record.get("title")
        or record.get("topic")
        or record.get("statement")
        or record.get("display_name")
        or record.get("name")
        or record.get("gratitude_text")
        or record.get("text_excerpt")
        or record.get("text")
        or record.get("summary")
        or record.get("performance_note")
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
        or record.get("text")
        or record.get("gratitude_text")
        or record.get("text_excerpt")
        or record.get("performance_note")
        or record.get("statement")
        or record.get("definition")
        or record.get("notes")
        or record_title(record),
        220,
    )


def entity_refs(record: Dict[str, Any]) -> List[str]:
    refs = [edge["target_ref"] for edge in record_ref_edges(record)]
    return sorted(set(ref for ref in refs if ref))


def record_text(record: Dict[str, Any]) -> str:
    parts = [
        record.get("id"),
        record_title(record),
        record.get("summary"),
        record.get("raw_text_excerpt"),
        record.get("gratitude_text"),
        record.get("text_excerpt"),
        record.get("text"),
        record.get("raw_text"),
        record.get("notes"),
        record.get("topic"),
        record.get("statement"),
        record.get("brian_wording_ko"),
        flatten_text(record.get("items")),
        flatten_text(record.get("exercises")),
        flatten_text(record.get("topics")),
        flatten_text(record.get("findings")),
        flatten_text(record.get("next_steps")),
        flatten_text(record.get("summary")),
        flatten_text(record.get("conversation_flow")),
        flatten_text(record.get("current_interest")),
        flatten_text(record.get("development_direction")),
        flatten_text(record.get("rationale")),
        flatten_text(record.get("implementation_direction")),
        flatten_text(record.get("tradeoffs")),
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


def iter_section_records(
    data: Dict[str, Any],
    path: Path,
    source_prefix: str,
    sections: List[str],
    defaults: Optional[Dict[str, Any]] = None,
) -> Iterable[Dict[str, Any]]:
    defaults = defaults or {}
    source_file = str(path.relative_to(REPO_ROOT))
    for section in sections:
        value = data.get(section)
        if isinstance(value, dict):
            rows = [value]
        elif isinstance(value, list):
            rows = value
        else:
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            enriched = dict(row)
            for key, default_value in defaults.items():
                enriched.setdefault(key, default_value)
            enriched["_source"] = f"{source_prefix}:{section}"
            enriched["_source_file"] = source_file
            enriched["_record_kind"] = section
            yield enriched


def iter_task_search_records() -> Iterable[Dict[str, Any]]:
    for task_file in load_task_files():
        path = REPO_ROOT / task_file["_path"]
        defaults = {
            "project_ref": task_file.get("project_ref"),
            "component_ref": task_file.get("component_ref"),
            "area": task_file.get("area"),
        }
        yield from iter_section_records(task_file, path, "task", TASK_SEARCH_SECTIONS, defaults)


def iter_knowledge_search_records() -> Iterable[Dict[str, Any]]:
    for path in sorted(KNOWLEDGE_DIR.glob("*.yaml")):
        data = load_yaml(path)
        defaults = {
            "project_ref": data.get("project_ref"),
            "area": data.get("area"),
            "secondary_areas": data.get("secondary_areas"),
        }
        yield from iter_section_records(data, path, "knowledge", KNOWLEDGE_SEARCH_SECTIONS, defaults)


def iter_mind_search_records() -> Iterable[Dict[str, Any]]:
    for path in sorted(MIND_DIR.glob("*.yaml")):
        data = load_yaml(path)
        defaults = {
            "area": data.get("area"),
            "profile_ref": data.get("profile_ref"),
            "secondary_areas": data.get("secondary_areas"),
        }
        yield from iter_section_records(data, path, "mind", MIND_SEARCH_SECTIONS, defaults)


def iter_finance_search_records() -> Iterable[Dict[str, Any]]:
    for path in sorted(FINANCE_DIR.glob("*.yaml")):
        data = load_yaml(path)
        defaults = {
            "area": data.get("area"),
            "profile_ref": data.get("profile_ref"),
            "secondary_areas": data.get("secondary_areas"),
        }
        yield from iter_section_records(data, path, "finance", FINANCE_SEARCH_SECTIONS, defaults)


def iter_body_search_records() -> Iterable[Dict[str, Any]]:
    for path in sorted(BODY_DIR.glob("*.yaml")):
        data = load_yaml(path)
        defaults = {
            "area": data.get("area"),
            "profile_ref": data.get("profile_ref"),
        }
        yield from iter_section_records(data, path, "body", BODY_SEARCH_SECTIONS, defaults)


def iter_concept_search_records() -> Iterable[Dict[str, Any]]:
    for path in sorted(CONCEPT_DIR.glob("*.yaml")):
        data = load_yaml(path)
        if not isinstance(data, dict) or not data.get("id"):
            continue
        enriched = dict(data)
        enriched["_source"] = "concept:file"
        enriched["_source_file"] = str(path.relative_to(REPO_ROOT))
        enriched["_record_kind"] = "concept"
        yield enriched


def iter_entity_catalog_records() -> Iterable[Dict[str, Any]]:
    if not ENTITY_CATALOG_PATH.exists():
        return
    data = load_yaml(ENTITY_CATALOG_PATH)
    entities = data.get("entities") or {}
    if not isinstance(entities, dict):
        return
    for section, rows in entities.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            enriched = dict(row)
            enriched["_source"] = f"entity:{section}"
            enriched["_source_file"] = str(ENTITY_CATALOG_PATH.relative_to(REPO_ROOT))
            enriched["_record_kind"] = section
            yield enriched


def iter_current_search_records(include_catalog: bool = True) -> Iterable[Dict[str, Any]]:
    yield from iter_task_search_records()
    yield from iter_body_search_records()
    yield from iter_mind_search_records()
    yield from iter_finance_search_records()
    yield from iter_knowledge_search_records()
    yield from iter_concept_search_records()
    if include_catalog:
        yield from iter_entity_catalog_records()


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


def node_key(record: Dict[str, Any]) -> str:
    record_id = record.get("id")
    source = record.get("_source") or "record"
    source_file = record.get("_source_file") or ""
    if record_id:
        return f"{record_id}|{source}|{source_file}"
    return f"{source}|{source_file}|{record.get('_record_kind') or ''}|{record_title(record)}"


def node_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "key": node_key(record),
        "id": record.get("id"),
        "date": record_date(record),
        "time": record.get("time") or record.get("start") or record.get("planned_start"),
        "end": record.get("end"),
        "area": record.get("area"),
        "secondary_areas": record.get("secondary_areas"),
        "object_type": record.get("object_type"),
        "source": record.get("_source"),
        "source_file": record.get("_source_file"),
        "record_kind": record.get("_record_kind"),
        "title": record_title(record),
        "excerpt": record_excerpt(record),
        "refs": entity_refs(record),
    }


def build_current_object_index() -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]], Dict[str, List[Tuple[Dict[str, Any], str]]]]:
    records = list(iter_current_search_records())
    by_id: Dict[str, List[Dict[str, Any]]] = {}
    referrers: Dict[str, List[Tuple[Dict[str, Any], str]]] = {}
    for record in records:
        record_id = record.get("id")
        if record_id:
            by_id.setdefault(record_id, []).append(record)
        for edge in record_ref_edges(record):
            referrers.setdefault(edge["target_ref"], []).append((record, edge["relation"]))
    return records, by_id, referrers


def should_expand_graph_node(record: Dict[str, Any]) -> bool:
    source = record.get("_source") or ""
    return not (source.startswith("entity:") or source.startswith("concept:"))


def build_day_graph(date_value: str, depth: int = 1) -> Dict[str, Any]:
    current_records, by_id, referrers = build_current_object_index()
    roots = [record for record in current_records if record_date(record) == date_value]
    roots.extend(records_for_date(date_value))

    nodes: Dict[str, Dict[str, Any]] = {}
    root_keys: List[str] = []
    linked_keys: List[str] = []
    links: List[Dict[str, Any]] = []
    seen_links = set()

    def add_node(record: Dict[str, Any], role: str) -> Tuple[str, bool]:
        key = node_key(record)
        is_new = key not in nodes
        if is_new:
            nodes[key] = node_summary(record)
        if role == "root" and key not in root_keys:
            root_keys.append(key)
        elif role == "linked" and key not in root_keys and key not in linked_keys:
            linked_keys.append(key)
        return key, is_new

    def add_link(source_key: str, relation: str, target_ref: str, target_key: Optional[str], direction: str) -> None:
        link_key = (source_key, relation, target_ref, target_key, direction)
        if link_key in seen_links:
            return
        seen_links.add(link_key)
        links.append(
            {
                "source_key": source_key,
                "relation": relation,
                "target_ref": target_ref,
                "target_key": target_key,
                "direction": direction,
                "resolved": target_key is not None,
            }
        )

    frontier = []
    for root in roots:
        _, is_new = add_node(root, "root")
        if is_new:
            frontier.append(root)

    for level in range(max(depth, 0)):
        next_frontier: List[Dict[str, Any]] = []
        for record in frontier:
            source_key, _ = add_node(record, "root" if node_key(record) in root_keys else "linked")

            for edge in record_ref_edges(record):
                target_ref = edge["target_ref"]
                targets = by_id.get(target_ref) or []
                if not targets:
                    add_link(source_key, edge["relation"], target_ref, None, "forward")
                    continue
                for target in targets:
                    target_key, is_new = add_node(target, "linked")
                    add_link(source_key, edge["relation"], target_ref, target_key, "forward")
                    if is_new and level + 1 < depth and should_expand_graph_node(target):
                        next_frontier.append(target)

            record_id = record.get("id")
            if record_id:
                for referrer, relation in referrers.get(record_id) or []:
                    referrer_key, is_new = add_node(referrer, "linked")
                    add_link(referrer_key, relation, record_id, source_key, "backlink")
                    if is_new and level + 1 < depth and should_expand_graph_node(referrer):
                        next_frontier.append(referrer)
        frontier = next_frontier

    root_nodes = [nodes[key] for key in root_keys]
    linked_nodes = [nodes[key] for key in linked_keys]
    return {
        "date": date_value,
        "depth": depth,
        "summary": summarize_day_graph(root_nodes, linked_nodes, links),
        "roots": root_nodes,
        "linked": linked_nodes,
        "links": links,
    }


def summarize_day_graph(root_nodes: List[Dict[str, Any]], linked_nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> Dict[str, Any]:
    root_areas = Counter(node.get("area") for node in root_nodes if node.get("area"))
    root_sources = Counter(node.get("source") for node in root_nodes if node.get("source"))
    root_types = Counter(node.get("object_type") or node.get("record_kind") for node in root_nodes if node.get("object_type") or node.get("record_kind"))
    linked_sources = Counter(node.get("source") for node in linked_nodes if node.get("source"))
    unresolved = [link for link in links if not link.get("resolved")]
    return {
        "root_count": len(root_nodes),
        "linked_count": len(linked_nodes),
        "link_count": len(links),
        "unresolved_link_count": len(unresolved),
        "root_areas": dict(root_areas.most_common()),
        "root_sources": dict(root_sources.most_common()),
        "root_types": dict(root_types.most_common()),
        "linked_sources": dict(linked_sources.most_common()),
    }


def format_time_part(node: Dict[str, Any]) -> str:
    start = node.get("time")
    end = node.get("end")
    if start and end:
        return f"{start}-{end} "
    if start:
        return f"{start} "
    return ""


def print_day_graph(graph: Dict[str, Any], limit: int) -> None:
    summary = graph["summary"]
    print("\n[day_graph]")
    print(
        "  "
        f"roots={summary['root_count']} linked={summary['linked_count']} "
        f"links={summary['link_count']} unresolved={summary['unresolved_link_count']}"
    )
    print(f"  root_areas={summary['root_areas']}")
    print(f"  root_sources={summary['root_sources']}")

    roots_by_area: Dict[str, List[Dict[str, Any]]] = {}
    for node in graph["roots"]:
        roots_by_area.setdefault(node.get("area") or "UNSET", []).append(node)

    area_count = max(len(roots_by_area), 1)
    per_area_limit = max(1, limit // area_count)
    print(f"  showing_up_to={per_area_limit}_roots_per_area")
    for area in sorted(roots_by_area):
        print(f"  {area}:")
        for node in roots_by_area[area][:per_area_limit]:
            label = node.get("id") or node.get("title")
            kind = node.get("object_type") or node.get("record_kind") or node.get("source")
            print(f"    - {format_time_part(node)}{kind} {label}")
            excerpt = node.get("excerpt")
            if excerpt and excerpt != label:
                print(f"      {compact_text(excerpt, 140)}")
            refs = node.get("refs") or []
            if refs:
                print(f"      refs={', '.join(refs[:8])}")
        remaining = len(roots_by_area[area]) - per_area_limit
        if remaining > 0:
            print(f"    ... {remaining} more")


def cmd_daily(args: argparse.Namespace) -> None:
    rows = daily_rows(args.date)
    records = records_for_date(args.date)
    task_time = task_time_for_date(args.date)
    day_graph = build_day_graph(args.date, args.graph_depth)
    result = {"date": args.date, "summaries": rows, "records": records, "task_time": task_time, "day_graph": day_graph}
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
    print_day_graph(day_graph, args.limit)


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
    for row in iter_current_search_records():
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
    daily.add_argument("--graph-depth", type=int, default=1, help="How many direct ref hops to include in the day graph")
    daily.add_argument("--json", action="store_true")
    daily.set_defaults(func=cmd_daily)

    today = sub.add_parser("today", help="Show today's aggregate and records")
    today.add_argument("--date", help="Override today with YYYY-MM-DD")
    today.add_argument("--limit", type=int, default=12)
    today.add_argument("--graph-depth", type=int, default=1, help="How many direct ref hops to include in the day graph")
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
