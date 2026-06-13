#!/usr/bin/env python3
"""Import the 2019 BKE gratitude diary into ontology-friendly indexes."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from xml.etree import ElementTree as ET

import yaml


RAW_DIR = Path("raw_data/documents/bke_gratitude_campaign_2019")
SOURCE_PATH = next(RAW_DIR.glob("BKE Group*.docx"))
ORIGINAL_SOURCE_PATH = (
    "/Users/brian/Downloads/BKE Group 감사일기 캠페인 2019년 최정윤.docx"
)
CATALOG_PATH = Path("life/entities/semantic_entity_catalog.yaml")
IMPORT_DIR = Path("life/imports/bke_gratitude_diary_2019")
MANIFEST_PATH = IMPORT_DIR / "manifest.yaml"
NORMALIZED_PATH = IMPORT_DIR / "normalized_entries.jsonl"
LINKED_PATH = IMPORT_DIR / "entity_linked_entries.jsonl"
DAILY_SUMMARY_PATH = IMPORT_DIR / "daily_summary.jsonl"
SUMMARY_PATH = IMPORT_DIR / "summary.yaml"
README_PATH = IMPORT_DIR / "README.md"
PATTERN_PATH = Path("life/patterns/bke_gratitude_diary_pattern_candidates.yaml")

DATE_RE = re.compile(r"^(20\d{2})년\s+(\d{1,2})월\s+(\d{1,2})일\s+([월화수목금토일])요일$")

AREA_KEYWORDS = {
    "RELATION": [
        "아름",
        "미야",
        "사랑",
        "함께",
        "대화",
        "통화",
        "이야기",
        "가족",
        "엄마",
        "아빠",
        "할머니",
        "어머님",
        "아버님",
        "친구",
        "형",
        "누나",
        "동료",
        "팀원",
        "분들과",
    ],
    "CAREER": [
        "회사",
        "출근",
        "퇴근",
        "업무",
        "일을",
        "문서",
        "프로젝트",
        "미팅",
        "회의",
        "팀장",
        "수석",
        "이사님",
        "책임님",
        "연구",
        "발표",
        "Jira",
        "Confluence",
        "Synopsys",
        "시놉시스",
        "DDR",
        "Controller",
        "라닉스",
        "디퍼아이",
        "Deeper",
        "FPU",
    ],
    "BODY": [
        "먹",
        "식사",
        "아침을",
        "아침 식사",
        "아침밥",
        "점심",
        "저녁을",
        "저녁 식사",
        "저녁밥",
        "요리",
        "반찬",
        "잠",
        "숙면",
        "낮잠",
        "운동",
        "산책",
        "감기",
        "건강",
        "몸",
        "따뜻한 물",
    ],
    "MIND": [
        "감사일기",
        "책을 읽",
        "책 읽",
        "독서",
        "강의를",
        "강의도",
        "강의 들",
        "강의할",
        "강의 할",
        "유튜브",
        "롤 모델",
        "생각",
        "목표",
        "계획",
        "공부",
        "배움",
        "마음",
        "평온",
        "몰입",
        "행복꾸러미",
        "시각화",
        "깨달음",
    ],
    "FUN": [
        "여행",
        "유럽",
        "로마",
        "나폴리",
        "피렌체",
        "베네치아",
        "카페",
        "커피",
        "맥주",
        "와인",
        "풍경",
        "노을",
        "자연",
        "휴식",
        "게임",
        "젠가",
        "크리스마스",
        "주말",
    ],
    "FINANCE": [
        "금융",
        "돈",
        "1억",
        "대출",
        "집을 보러",
        "살 집",
        "자산",
        "재무",
        "스마트 스토어",
        "스마트스토어",
    ],
    "MAINTENANCE": [
        "청소",
        "정리",
        "식물",
        "집이 잘",
        "깨끗",
        "보온통",
        "준비",
    ],
}

AREA_PRIORITY = ["RELATION", "CAREER", "BODY", "MIND", "FUN", "FINANCE", "MAINTENANCE"]

THEME_KEYWORDS = {
    "relationship_spouse": ["아름", "미야", "사랑하는", "사랑을", "온전히 사랑"],
    "relationship_family": ["엄마", "아빠", "할머니", "어머님", "아버님", "가족"],
    "relationship_friend_colleague": ["친구", "형", "누나", "동료", "팀원", "책임님", "팀장님", "이사님", "수석님"],
    "conversation_connection": ["대화", "이야기", "통화", "연락", "속마음"],
    "food_home_cooking": [
        "아침을",
        "아침 식사",
        "아침밥",
        "점심",
        "저녁을",
        "저녁 식사",
        "저녁밥",
        "식사",
        "먹",
        "요리",
        "반찬",
        "찌개",
        "밥",
    ],
    "health_recovery": ["감기", "건강", "몸이 좋아", "회복", "따뜻한 물", "보온통"],
    "sleep_rest": ["잠", "숙면", "낮잠", "푹 쉬", "휴식", "편안하게"],
    "exercise_movement": ["운동", "산책", "걷"],
    "learning_growth": [
        "책을 읽",
        "책 읽",
        "독서",
        "강의를",
        "강의도",
        "강의 들",
        "강의할",
        "강의 할",
        "유튜브",
        "공부",
        "배움",
        "실력이 증가",
        "익힐",
    ],
    "work_progress": ["회사", "업무", "일을", "문서", "프로젝트", "Jira", "Confluence", "미팅"],
    "problem_solving": ["해결", "방법을 찾", "성공", "이슈", "파악", "문제"],
    "goal_planning": ["목표", "계획", "방향", "미래", "시각화", "2020년"],
    "finance_home": ["금융", "돈", "1억", "대출", "집을 보러", "살 집", "스마트 스토어"],
    "travel_memory": ["여행", "유럽", "로마", "나폴리", "피렌체", "베네치아", "공항", "비행"],
    "nature_scene": ["하늘", "햇빛", "풍경", "노을", "자연", "바다"],
    "gratitude_practice": ["감사일기", "감사가 마음", "감사하며"],
    "happiness_presence": ["행복", "기쁨", "충만", "평온", "좋았습니다", "기분이 좋"],
}

EMOTION_KEYWORDS = {
    "happy": ["행복", "기쁨", "즐겁", "좋았습니다", "기분이 좋", "신나"],
    "calm": ["평온", "편안", "평안", "마음이 좋"],
    "moved": ["감동", "벅차", "따뜻함"],
    "relieved": ["후련", "다행", "무사히", "나아지고"],
    "proud": ["성공", "실력이 증가", "해결", "완료"],
    "anxious": ["걱정", "불안"],
    "angry": ["화가"],
}

RELATED_OBSERVATION_BY_THEME = {
    "relationship_spouse": "social_interaction",
    "relationship_family": "social_interaction",
    "relationship_friend_colleague": "social_interaction",
    "conversation_connection": "social_interaction",
    "food_home_cooking": "meal",
    "health_recovery": "mood",
    "sleep_rest": "sleep",
    "exercise_movement": "workout",
    "learning_growth": "learning",
    "work_progress": "work_session",
    "problem_solving": "resolution",
    "goal_planning": "goal_review",
    "finance_home": "finance_decision",
    "travel_memory": "fun",
    "nature_scene": "fun",
    "gratitude_practice": "gratitude_entry",
    "happiness_presence": "mood",
}

PLURAL_KEYS = {
    "Person": "people",
    "CompanionAnimal": "companion_animals",
    "Project": "projects",
    "Component": "components",
    "Activity": "activities",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def dump_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def text_excerpt(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def extract_docx_paragraphs(path: Path) -> List[Dict[str, Any]]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as docx:
        root = ET.fromstring(docx.read("word/document.xml"))

    paragraphs = []
    for paragraph_index, para in enumerate(root.findall(".//w:p", ns), start=1):
        text = "".join((node.text or "") for node in para.findall(".//w:t", ns)).strip()
        if text:
            paragraphs.append({"paragraph_index": paragraph_index, "text": " ".join(text.split())})
    return paragraphs


def parse_date(text: str) -> Tuple[str, str] | None:
    match = DATE_RE.match(text)
    if not match:
        return None
    year, month, day, weekday = match.groups()
    date_value = dt.date(int(year), int(month), int(day)).isoformat()
    return date_value, f"{weekday}요일"


def classify_area(text: str) -> Tuple[str, str, List[Dict[str, Any]]]:
    scores = Counter()
    matches = defaultdict(list)
    for area, keywords in AREA_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[area] += 1
                matches[area].append(keyword)

    if not scores:
        return "MIND", "low", []

    def sort_key(area: str) -> Tuple[int, int]:
        return scores[area], -AREA_PRIORITY.index(area)

    primary = max(scores, key=sort_key)
    top_score = scores[primary]
    confidence = "high" if top_score >= 3 else "medium"
    candidates = [
        {"area": area, "score": scores[area], "matched_keywords": sorted(set(matches[area]))[:8]}
        for area in sorted(scores, key=lambda item: (-scores[item], AREA_PRIORITY.index(item)))
    ]
    if len(candidates) > 1 and candidates[0]["score"] == candidates[1]["score"]:
        confidence = "medium"
    return primary, confidence, candidates


def detect_theme_tags(text: str) -> List[str]:
    return sorted(
        theme
        for theme, keywords in THEME_KEYWORDS.items()
        if any(keyword in text for keyword in keywords)
    )


def detect_emotion_tags(text: str) -> List[str]:
    tags = {"grateful"}
    for tag, keywords in EMOTION_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            tags.add(tag)
    return sorted(tags)


def related_observation_types(theme_tags: List[str]) -> List[str]:
    return sorted({RELATED_OBSERVATION_BY_THEME[tag] for tag in theme_tags if tag in RELATED_OBSERVATION_BY_THEME})


def parse_entries(paragraphs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    current_date = None
    current_weekday = None
    day_index = Counter()
    entries = []
    header_lines = []
    date_order = []

    for paragraph in paragraphs:
        text = paragraph["text"]
        parsed_date = parse_date(text)
        if parsed_date:
            current_date, current_weekday = parsed_date
            date_order.append(current_date)
            continue
        if current_date is None:
            header_lines.append(text)
            continue

        day_index[current_date] += 1
        entry_no = day_index[current_date]
        area, area_confidence, area_candidates = classify_area(text)
        theme_tags = detect_theme_tags(text)
        entry = {
            "id": f"bke_gratitude_{current_date.replace('-', '')}_{entry_no:03d}",
            "source_ref": "bke_gratitude_diary_2019",
            "source_type": "gratitude_diary_docx",
            "source_path": str(SOURCE_PATH),
            "source_paragraph_index": paragraph["paragraph_index"],
            "original_date": current_date,
            "weekday": current_weekday,
            "entry_index_for_day": entry_no,
            "observation_type": "gratitude_entry",
            "area": area,
            "area_confidence": area_confidence,
            "area_candidates": area_candidates,
            "gratitude_text": text,
            "raw_text_sha256": sha256_text(text),
            "raw_text_excerpt": text_excerpt(text),
            "emotion_tags": detect_emotion_tags(text),
            "theme_tags": theme_tags,
            "related_observation_types": related_observation_types(theme_tags),
            "confidence": "high",
            "needs_user_review": False,
        }
        entries.append(entry)

    metadata = {
        "header_line_count": len(header_lines),
        "title": header_lines[0] if header_lines else None,
        "personal_contact_fields_present": any("전화번호" in line or "이메일" in line for line in header_lines),
        "birth_date_field_present": any("생년월일" in line for line in header_lines),
        "name_field_present": any(line.startswith("이름") for line in header_lines),
        "date_order": date_order,
    }
    return sorted(entries, key=lambda item: (item["original_date"], item["entry_index_for_day"])), metadata


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_entities(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    entities = []
    for group_name, group_entities in catalog["entities"].items():
        for entity in group_entities:
            enriched = dict(entity)
            enriched["group"] = group_name
            entities.append(enriched)
    return entities


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
    return {"none": 0, "low": 1, "medium": 2, "high": 3}.get(confidence, 0)


def merge_confidence(a: str, b: str) -> str:
    return a if confidence_rank(a) <= confidence_rank(b) else b


def link_entry(entry: Dict[str, Any], entities: List[Dict[str, Any]], relations: Dict[str, str]) -> Dict[str, Any]:
    linked = dict(entry)
    entity_refs: Dict[str, List[str]] = defaultdict(list)
    semantic_links = []
    seen = set()

    default_key = ("activities", "activity_gratitude")
    seen.add(default_key)
    entity_refs["activities"].append("activity_gratitude")
    semantic_links.append(
        {
            "entity_ref": "activity_gratitude",
            "object_type": "Activity",
            "relation": "involves_activity",
            "matched_alias": "gratitude_diary_source",
            "confidence": "high",
            "needs_user_review": False,
        }
    )

    text = entry["gratitude_text"]
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

    linked["entity_refs"] = {key: sorted(values) for key, values in sorted(entity_refs.items())}
    linked["semantic_links"] = sorted(
        semantic_links,
        key=lambda item: (item["object_type"], item["entity_ref"], item["matched_alias"]),
    )
    confidence = "high"
    needs_review = False
    for link in semantic_links:
        confidence = merge_confidence(confidence, link["confidence"])
        needs_review = needs_review or link["needs_user_review"]
    linked["semantic_link_confidence"] = confidence
    linked["semantic_needs_user_review"] = needs_review
    return linked


def summarize_daily(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry["original_date"]].append(entry)

    rows = []
    for date_value in sorted(grouped):
        day_entries = grouped[date_value]
        entity_refs = defaultdict(set)
        for entry in day_entries:
            for group, refs in entry.get("entity_refs", {}).items():
                entity_refs[group].update(refs)
        rows.append(
            {
                "date": date_value,
                "weekday": day_entries[0]["weekday"],
                "entry_count": len(day_entries),
                "area_counts": dict(Counter(entry["area"] for entry in day_entries)),
                "theme_tag_counts": dict(Counter(tag for entry in day_entries for tag in entry["theme_tags"])),
                "emotion_tag_counts": dict(Counter(tag for entry in day_entries for tag in entry["emotion_tags"])),
                "entity_refs": {group: sorted(refs) for group, refs in sorted(entity_refs.items())},
                "entry_refs": [entry["id"] for entry in day_entries],
            }
        )
    return rows


def summarize(entries: List[Dict[str, Any]], daily_rows: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
    entity_counts = Counter()
    object_type_counts = Counter()
    review_needed = Counter()
    entity_examples = defaultdict(list)
    for entry in entries:
        for link in entry["semantic_links"]:
            entity_ref = link["entity_ref"]
            entity_counts[entity_ref] += 1
            object_type_counts[link["object_type"]] += 1
            if link["needs_user_review"]:
                review_needed[entity_ref] += 1
            if len(entity_examples[entity_ref]) < 5:
                entity_examples[entity_ref].append(
                    {
                        "entry_ref": entry["id"],
                        "date": entry["original_date"],
                        "matched_alias": link["matched_alias"],
                        "text_excerpt": entry["raw_text_excerpt"],
                    }
                )

    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        "source": {
            "id": "bke_gratitude_diary_2019",
            "raw_ref": str(SOURCE_PATH),
            "original_source_path": ORIGINAL_SOURCE_PATH,
            "sha256": sha256_file(SOURCE_PATH),
            "source_type": "gratitude_diary_docx",
            "title": metadata["title"],
            "personal_contact_fields_present": metadata["personal_contact_fields_present"],
            "birth_date_field_present": metadata["birth_date_field_present"],
            "name_field_present": metadata["name_field_present"],
        },
        "outputs": {
            "manifest_ref": str(MANIFEST_PATH),
            "normalized_entries_ref": str(NORMALIZED_PATH),
            "entity_linked_entries_ref": str(LINKED_PATH),
            "daily_summary_ref": str(DAILY_SUMMARY_PATH),
            "summary_ref": str(SUMMARY_PATH),
            "pattern_candidates_ref": str(PATTERN_PATH),
        },
        "records": {
            "entry_count": len(entries),
            "daily_count": len(daily_rows),
            "date_range": {
                "start": min(entry["original_date"] for entry in entries),
                "end": max(entry["original_date"] for entry in entries),
            },
            "by_month": dict(Counter(entry["original_date"][:7] for entry in entries)),
            "by_area": dict(Counter(entry["area"] for entry in entries)),
            "by_emotion_tag": dict(Counter(tag for entry in entries for tag in entry["emotion_tags"])),
            "by_theme_tag": dict(Counter(tag for entry in entries for tag in entry["theme_tags"])),
            "with_semantic_links": sum(1 for entry in entries if entry["semantic_links"]),
            "with_review_needed": sum(1 for entry in entries if entry["semantic_needs_user_review"]),
        },
        "link_counts": {
            "by_object_type": dict(object_type_counts),
            "top_entities": [
                {
                    "entity_ref": entity_ref,
                    "records": count,
                    "needs_user_review_records": review_needed[entity_ref],
                    "examples": entity_examples[entity_ref],
                }
                for entity_ref, count in entity_counts.most_common(40)
            ],
        },
    }


def evidence_for(entries: List[Dict[str, Any]], predicate, limit: int = 8) -> List[Dict[str, Any]]:
    evidence = []
    for entry in entries:
        if predicate(entry):
            evidence.append(
                {
                    "entry_ref": entry["id"],
                    "date": entry["original_date"],
                    "area": entry["area"],
                    "text_excerpt": entry["raw_text_excerpt"],
                }
            )
        if len(evidence) >= limit:
            break
    return evidence


def has_entity(entry: Dict[str, Any], entity_ref: str) -> bool:
    return any(entity_ref in refs for refs in entry.get("entity_refs", {}).values())


def build_pattern_candidates(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = []
    specs = [
        (
            "bke_gratitude_2019_spouse_support",
            "2019 감사일기에서 spouse support, shared meals, conversation, future planning이 반복적인 감사 근거로 등장한다.",
            lambda entry: has_entity(entry, "person_wife"),
        ),
        (
            "bke_gratitude_2019_learning_growth",
            "Books, lectures, study, role models, and new technical understanding repeatedly appear as gratitude and growth evidence.",
            lambda entry: "learning_growth" in entry["theme_tags"],
        ),
        (
            "bke_gratitude_2019_work_progress",
            "Work focus, technical problem solving, helpful leaders, and project progress repeatedly appear as gratitude evidence.",
            lambda entry: "work_progress" in entry["theme_tags"] or "problem_solving" in entry["theme_tags"],
        ),
        (
            "bke_gratitude_2019_shared_travel",
            "Shared travel and vivid place memories repeatedly appear as happiness and gratitude anchors.",
            lambda entry: "travel_memory" in entry["theme_tags"],
        ),
        (
            "bke_gratitude_2019_food_care",
            "Home-cooked meals, shared meals, and being cared for through food repeatedly appear as gratitude evidence.",
            lambda entry: "food_home_cooking" in entry["theme_tags"],
        ),
        (
            "bke_gratitude_2019_gratitude_practice",
            "The gratitude-writing practice itself appears as an evidence-backed calming and focusing ritual candidate.",
            lambda entry: "gratitude_practice" in entry["theme_tags"] or "감사일기" in entry["gratitude_text"],
        ),
    ]
    for candidate_id, statement, predicate in specs:
        evidence = evidence_for(entries, predicate)
        total = sum(1 for entry in entries if predicate(entry))
        if not evidence:
            continue
        candidates.append(
            {
                "id": candidate_id,
                "source_import_ref": "bke_gratitude_diary_2019",
                "statement": statement,
                "evidence_count": total,
                "evidence": evidence,
                "confidence": "high" if total >= 100 else "medium",
                "needs_user_review": True,
                "causality_policy": "association_only_do_not_overclaim",
            }
        )
    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        "source_import_ref": "life/imports/bke_gratitude_diary_2019/summary.yaml",
        "pattern_candidates": candidates,
    }


def build_manifest(metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        "import_id": "bke_gratitude_diary_2019",
        "source": {
            "raw_ref": str(SOURCE_PATH),
            "original_source_path": ORIGINAL_SOURCE_PATH,
            "sha256": sha256_file(SOURCE_PATH),
            "source_type": "docx",
            "title": metadata["title"],
            "header_line_count": metadata["header_line_count"],
            "personal_contact_fields_present": metadata["personal_contact_fields_present"],
            "birth_date_field_present": metadata["birth_date_field_present"],
            "name_field_present": metadata["name_field_present"],
        },
        "parse": {
            "parser": "tools/import_bke_gratitude_diary.py",
            "method": "docx_word_document_xml_paragraph_extraction",
            "date_pattern": "YYYY년 M월 D일 weekday",
            "record_model": "one GratitudeEntry per dated bullet/paragraph",
        },
        "outputs": {
            "normalized_entries": str(NORMALIZED_PATH),
            "entity_linked_entries": str(LINKED_PATH),
            "daily_summary": str(DAILY_SUMMARY_PATH),
            "summary": str(SUMMARY_PATH),
            "pattern_candidates": str(PATTERN_PATH),
        },
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# BKE Gratitude Diary 2019

Ontology import for Brian's 2019 BKE Group gratitude diary campaign document.

Raw source stays under `raw_data/documents/bke_gratitude_campaign_2019/`.

Generated files:

- `manifest.yaml`: source and parser metadata.
- `normalized_entries.jsonl`: one `GratitudeEntry` per dated gratitude paragraph.
- `entity_linked_entries.jsonl`: gratitude entries with semantic object links.
- `daily_summary.jsonl`: one row per diary date.
- `summary.yaml`: aggregate counts for querying.

Pattern candidates are written to `life/patterns/bke_gratitude_diary_pattern_candidates.yaml`.
""",
        encoding="utf-8",
    )


def main() -> None:
    paragraphs = extract_docx_paragraphs(SOURCE_PATH)
    entries, metadata = parse_entries(paragraphs)
    catalog = load_yaml(CATALOG_PATH)
    entities = build_entities(catalog)
    relations = catalog.get("link_relations", {})
    linked_entries = [link_entry(entry, entities, relations) for entry in entries]
    daily_rows = summarize_daily(linked_entries)

    dump_yaml(MANIFEST_PATH, build_manifest(metadata))
    dump_jsonl(NORMALIZED_PATH, entries)
    dump_jsonl(LINKED_PATH, linked_entries)
    dump_jsonl(DAILY_SUMMARY_PATH, daily_rows)
    dump_yaml(SUMMARY_PATH, summarize(linked_entries, daily_rows, metadata))
    dump_yaml(PATTERN_PATH, build_pattern_candidates(linked_entries))
    write_readme()

    print(f"entries={len(entries)}")
    print(f"days={len(daily_rows)}")
    print(f"linked_entries={sum(1 for entry in linked_entries if entry['semantic_links'])}")
    print(f"review_needed={sum(1 for entry in linked_entries if entry['semantic_needs_user_review'])}")


if __name__ == "__main__":
    main()
