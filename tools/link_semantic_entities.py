#!/usr/bin/env python3
"""Attach semantic ontology object links to normalized historical records."""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml


CATALOG_PATH = Path("life/entities/semantic_entity_catalog.yaml")
INPUT_PATH = Path("life/imports/review_archive/normalized_records.jsonl")
OUTPUT_PATH = Path("life/imports/review_archive/entity_linked_records.jsonl")
SUMMARY_PATH = Path("life/imports/review_archive/entity_link_summary.yaml")

PLURAL_KEYS = {
    "Person": "people",
    "CompanionAnimal": "companion_animals",
    "Project": "projects",
    "Component": "components",
    "Activity": "activities",
}


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_records(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def dump_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def record_text(record: Dict[str, Any]) -> str:
    parts = [
        record.get("title"),
        record.get("raw_text_excerpt"),
        record.get("legacy_activity"),
        record.get("legacy_component"),
        record.get("source_key"),
    ]
    return "\n".join(str(part) for part in parts if part)


def entity_matches(entity: Dict[str, Any], text: str) -> Tuple[bool, str]:
    for negative in entity.get("negative_aliases", []) or []:
        if negative and negative in text:
            return False, ""
    required_context = entity.get("requires_any_context", []) or []
    if required_context and not any(context and context in text for context in required_context):
        return False, ""
    for alias in entity.get("aliases", []) or []:
        if alias and alias in text:
            return True, alias
    return False, ""


def confidence_rank(confidence: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(confidence, 0)


def merge_confidence(a: str, b: str) -> str:
    return a if confidence_rank(a) <= confidence_rank(b) else b


def build_entities(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    entities = []
    for group_name, group_entities in catalog["entities"].items():
        for entity in group_entities:
            enriched = dict(entity)
            enriched["group"] = group_name
            entities.append(enriched)
    return entities


def link_record(record: Dict[str, Any], entities: List[Dict[str, Any]], relations: Dict[str, str]) -> Dict[str, Any]:
    text = record_text(record)
    linked = dict(record)
    entity_refs: Dict[str, List[str]] = defaultdict(list)
    semantic_links = []
    seen = set()

    for entity in entities:
        matched, alias = entity_matches(entity, text)
        if not matched:
            continue
        object_type = entity["object_type"]
        group = PLURAL_KEYS.get(object_type, entity["group"])
        key = (group, entity["id"])
        if key in seen:
            continue
        seen.add(key)
        entity_refs[group].append(entity["id"])
        semantic_links.append(
            {
                "entity_ref": entity["id"],
                "object_type": object_type,
                "relation": relations.get(object_type, "associated_with"),
                "matched_alias": alias,
                "confidence": entity.get("confidence", "medium"),
                "needs_user_review": bool(entity.get("needs_user_review", False)),
            }
        )

    if semantic_links:
        linked["entity_refs"] = {key: sorted(values) for key, values in sorted(entity_refs.items())}
        linked["semantic_links"] = sorted(
            semantic_links,
            key=lambda item: (item["object_type"], item["entity_ref"], item["matched_alias"]),
        )
        confidence = "high"
        needs_user_review = False
        for link in semantic_links:
            confidence = merge_confidence(confidence, link["confidence"])
            needs_user_review = needs_user_review or link["needs_user_review"]
        linked["semantic_link_confidence"] = confidence
        linked["semantic_needs_user_review"] = needs_user_review
    else:
        linked["entity_refs"] = {}
        linked["semantic_links"] = []
        linked["semantic_link_confidence"] = "none"
        linked["semantic_needs_user_review"] = False
    return linked


def summarize(records: List[Dict[str, Any]], catalog: Dict[str, Any]) -> Dict[str, Any]:
    linked_records = [record for record in records if record["semantic_links"]]
    entity_counts = Counter()
    entity_minutes = defaultdict(float)
    object_type_counts = Counter()
    relation_counts = Counter()
    review_counts = Counter()
    entity_examples = defaultdict(list)

    for record in linked_records:
        minutes = record.get("duration_minutes") or 0
        for link in record["semantic_links"]:
            entity = link["entity_ref"]
            entity_counts[entity] += 1
            entity_minutes[entity] += minutes
            object_type_counts[link["object_type"]] += 1
            relation_counts[link["relation"]] += 1
            if link["needs_user_review"]:
                review_counts[entity] += 1
            if len(entity_examples[entity]) < 5:
                entity_examples[entity].append(
                    {
                        "record_ref": record["id"],
                        "date": record["original_date"],
                        "area": record["area"],
                        "title": record["title"],
                        "matched_alias": link["matched_alias"],
                    }
                )

    catalog_entities = {}
    for group, values in catalog["entities"].items():
        for entity in values:
            catalog_entities[entity["id"]] = {
                "object_type": entity["object_type"],
                "display_name": entity.get("display_name"),
                "group": group,
                "needs_user_review": entity.get("needs_user_review", False),
            }

    top_entities = []
    for entity_ref, count in entity_counts.most_common():
        info = catalog_entities.get(entity_ref, {})
        top_entities.append(
            {
                "entity_ref": entity_ref,
                "display_name": info.get("display_name"),
                "object_type": info.get("object_type"),
                "records": count,
                "hours": round(entity_minutes[entity_ref] / 60, 2),
                "needs_user_review_records": review_counts[entity_ref],
                "examples": entity_examples[entity_ref],
            }
        )

    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        "input_ref": str(INPUT_PATH),
        "catalog_ref": str(CATALOG_PATH),
        "output_ref": str(OUTPUT_PATH),
        "records": {
            "total": len(records),
            "with_semantic_links": len(linked_records),
            "without_semantic_links": len(records) - len(linked_records),
            "with_review_needed": sum(1 for record in linked_records if record["semantic_needs_user_review"]),
        },
        "link_counts": {
            "by_object_type": dict(object_type_counts),
            "by_relation": dict(relation_counts),
        },
        "top_entities": top_entities,
    }


def main() -> None:
    catalog = load_yaml(CATALOG_PATH)
    entities = build_entities(catalog)
    relations = catalog.get("link_relations", {})
    linked_records = [link_record(record, entities, relations) for record in load_records(INPUT_PATH)]
    dump_jsonl(OUTPUT_PATH, linked_records)
    dump_yaml(SUMMARY_PATH, summarize(linked_records, catalog))
    print(f"records={len(linked_records)}")
    print(f"linked_records={sum(1 for record in linked_records if record['semantic_links'])}")


if __name__ == "__main__":
    main()
