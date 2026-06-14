#!/usr/bin/env python3
"""Import Obsidian Daily notes into ontology-friendly indexes."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml


SOURCE_ROOT = Path("raw_data/obsidian/01_Daily")
CATALOG_PATH = Path("life/entities/semantic_entity_catalog.yaml")
IMPORT_DIR = Path("life/imports/obsidian_daily")
MANIFEST_PATH = IMPORT_DIR / "manifest.yaml"
NORMALIZED_PATH = IMPORT_DIR / "normalized_records.jsonl"
LINKED_PATH = IMPORT_DIR / "entity_linked_records.jsonl"
DAILY_SUMMARY_PATH = IMPORT_DIR / "daily_summary.jsonl"
SUMMARY_PATH = IMPORT_DIR / "summary.yaml"
README_PATH = IMPORT_DIR / "README.md"

DATE_FILE_RE = re.compile(r"^(20\d{2}-\d{2}-\d{2})(?:\s.*)?\.md$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TIMEBLOCK_RE = re.compile(r"^\s*[-*]\s+(\d{1,2}:\d{2})\s*[-–~]\s*(\d{1,2}:\d{2})\s*(.*)$")
TAG_RE = re.compile(r"#[A-Za-z0-9_가-힣]+")
ENERGY_RE = re.compile(r"#에너지(\d{1,3})")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

PLURAL_KEYS = {
    "Person": "people",
    "CompanionAnimal": "companion_animals",
    "Project": "projects",
    "Component": "components",
    "Activity": "activities",
}

AREA_KEYWORDS = {
    "CAREER": [
        "업무",
        "회사",
        "미팅",
        "세미나",
        "발표",
        "설계",
        "검증",
        "디버깅",
        "debug",
        "debugging",
        "lint",
        "timing",
        "sdc",
        "rtl",
        "tc",
        "fail",
        "sim",
        "synthesis",
        "firenze",
        "milano",
        "grizzly",
        "pcie",
        "gen7",
        "ide",
        "tdisp",
        "rid",
        "flit",
        "atlas",
        "codex",
        "cursor",
        "agent",
        "claude",
        "llm",
    ],
    "BODY": [
        "운동",
        "헬스",
        "스쿼트",
        "푸쉬업",
        "걷기",
        "산책",
        "수면",
        "잠",
        "식사",
        "아침",
        "점심",
        "저녁",
        "음식",
        "밥",
        "샐러드",
        "단백질",
        "치료",
        "피부",
        "건강",
        "두유",
        "닭가슴살",
        "약",
    ],
    "FINANCE": [
        "경제",
        "주식",
        "투자",
        "etf",
        "매수",
        "매도",
        "자산",
        "포트폴리오",
        "대장주",
        "월텍남",
        "finance",
    ],
    "RELATION": [
        "미야",
        "아름",
        "와이프",
        "엄마",
        "아빠",
        "어머님",
        "아버님",
        "가족",
        "대화",
        "통화",
        "사랑",
        "감사",
        "함께",
        "저녁",
        "팀장님",
        "tl님",
        "수석님",
        "책임님",
    ],
    "MAINTENANCE": [
        "집안일",
        "청소",
        "정리",
        "차량",
        "정비",
        "니로",
        "수리",
        "문서 정리",
        "옵시디언 정리",
        "분리수거",
        "설거지",
    ],
    "FUN": [
        "휴식",
        "행복꾸러미",
        "즐거",
        "재밌",
        "게임",
        "영화",
        "카페",
        "커피",
        "여행",
        "산책",
        "놀",
    ],
    "MIND": [
        "공부",
        "학습",
        "독서",
        "목표",
        "계획",
        "생각",
        "마인드맵",
        "뇌과학",
        "일기",
        "회고",
        "감정",
        "명상",
        "정리하고 방향성",
        "영어",
    ],
}

AREA_PRIORITY = ["CAREER", "BODY", "FINANCE", "RELATION", "MAINTENANCE", "FUN", "MIND"]

OBSERVATION_RULES = [
    ("goal_review", ["목표", "계획", "방향성"]),
    ("meal", ["식사", "아침", "점심", "저녁", "밥", "샐러드", "닭가슴살", "두유", "리조또", "커피"]),
    ("workout", ["운동", "헬스", "스쿼트", "푸쉬업", "웨이트", "맨몸"]),
    ("sleep", ["수면", "잠", "낮잠"]),
    ("work_session", ["업무", "디버깅", "debug", "lint", "timing", "sdc", "rtl", "tc", "sim", "설계", "검증"]),
    ("learning", ["공부", "학습", "독서", "경제뉴스", "마인드맵", "뇌과학", "영어"]),
    ("meeting", ["미팅", "세미나", "회의 참석", "회의 참가", "회의록", "발표"]),
    ("finance_decision", ["주식", "투자", "etf", "매수", "매도", "포트폴리오"]),
    ("maintenance", ["정비", "청소", "집안일", "정리", "수리", "분리수거", "설거지"]),
    ("social_interaction", ["미야", "아름", "가족", "대화", "통화", "함께", "감사", "사랑"]),
    ("rest", ["휴식", "쉬", "카페", "커피"]),
    ("happiness_trigger", ["행복꾸러미", "행복 포인트", "happiness point"]),
]

EMOTION_KEYWORDS = {
    "happy": ["행복", "즐겁", "재밌", "좋", "기분 업", "웃", "만족"],
    "grateful": ["감사", "고맙"],
    "proud": ["뿌듯", "잘함", "고생했다", "성공", "완료", "해결"],
    "tired": ["피곤", "지침", "졸림", "힘듦", "힘들"],
    "stressed": ["스트레스", "압박", "부담", "찝찝"],
    "anxious": ["불안", "걱정", "두려"],
    "calm": ["차분", "평온", "안정", "맑아지고"],
    "regretful": ["반성", "아쉽", "후회"],
}

SECTION_TYPES = {
    "three important goal": "goal_review",
    "review": "daily_review",
    "thank you": "gratitude",
    "happiness point": "happiness_point",
}


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.as_posix())


def is_daily_note(path: Path) -> bool:
    return path.parent.name in {"Daily", "Daily_2025"} and bool(DATE_FILE_RE.match(path.name))


def date_from_daily_note(path: Path) -> str:
    match = DATE_FILE_RE.match(path.name)
    if not match:
        raise ValueError(f"not a dated daily note: {path}")
    return match.group(1)


def daily_note_id(path: Path) -> str:
    date = date_from_daily_note(path)
    suffix = path.stem[10:].strip()
    note_id = f"obsidian_daily_{date.replace('-', '')}"
    if not suffix:
        return note_id
    slug = re.sub(r"[^A-Za-z0-9]+", "_", suffix).strip("_").lower()
    if not slug:
        slug = sha256_text(path.name)[:8]
    return f"{note_id}_{slug}"


def strip_code_fences(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def clean_inline(text: str) -> str:
    text = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), text)
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", lambda m: m.group(0).split("](")[0][1:], text)
    text = TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -\t")


def wiki_links(text: str) -> List[str]:
    links = []
    for match in WIKILINK_RE.finditer(text):
        links.append(match.group(2) or match.group(1))
    return sorted(set(link.strip() for link in links if link.strip()))


def tags(text: str) -> List[str]:
    return sorted(set(TAG_RE.findall(text)))


def parse_time(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def duration_minutes(start: str, end: str) -> int:
    start_minutes = parse_time(start)
    end_minutes = parse_time(end)
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    return max(0, end_minutes - start_minutes)


def normalize_time(value: str) -> str:
    hour, minute = value.split(":")
    return f"{int(hour):02d}:{int(minute):02d}"


def section_key(title: str) -> str:
    normalized = clean_inline(title).lower()
    return re.sub(r"\s+", " ", normalized).strip()


def extract_sections(text: str) -> Dict[str, Dict[str, Any]]:
    stripped = strip_code_fences(text)
    sections: Dict[str, Dict[str, Any]] = {}
    current_title = "Preamble"
    current_key = "preamble"
    current_level = 0
    current_lines: List[str] = []

    def flush() -> None:
        body = "\n".join(current_lines).strip()
        if body:
            sections[current_key] = {
                "title": current_title,
                "level": current_level,
                "body": body,
            }

    for line in stripped.splitlines():
        match = HEADING_RE.match(line)
        if match:
            flush()
            current_title = clean_inline(match.group(2))
            current_key = section_key(current_title)
            current_level = len(match.group(1))
            current_lines = []
            continue
        current_lines.append(line)
    flush()
    return sections


def extract_day_planner_blocks(section_body: str) -> List[Dict[str, Any]]:
    blocks = []
    current: Optional[Dict[str, Any]] = None

    for line in section_body.splitlines():
        match = TIMEBLOCK_RE.match(line)
        if match:
            if current:
                blocks.append(current)
            start = normalize_time(match.group(1))
            end = normalize_time(match.group(2))
            raw_title = match.group(3).strip()
            energy_match = ENERGY_RE.search(raw_title)
            current = {
                "start": start,
                "end": end,
                "raw_title": raw_title,
                "title": clean_inline(raw_title),
                "duration_minutes": duration_minutes(start, end),
                "energy_score": int(energy_match.group(1)) if energy_match else None,
                "tags": tags(raw_title),
                "obsidian_links": wiki_links(raw_title),
                "note_lines": [],
            }
            continue

        if current and line.strip():
            current["note_lines"].append(line.rstrip())

    if current:
        blocks.append(current)
    return blocks


def score_area(text: str) -> Tuple[str, Dict[str, int]]:
    lowered = text.lower()
    scores: Dict[str, int] = {}
    for area, keywords in AREA_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in lowered:
                score += 1
        if score:
            scores[area] = score
    if not scores:
        return "MIND", {}
    best = max(AREA_PRIORITY, key=lambda area: (scores.get(area, 0), -AREA_PRIORITY.index(area)))
    return best, scores


def observation_type(text: str, section_type: Optional[str] = None) -> str:
    if section_type == "gratitude":
        return "gratitude_entry"
    if section_type == "happiness_point":
        return "happiness_trigger"
    if section_type == "goal_review":
        return "goal_review"
    lowered = text.lower()
    for candidate, keywords in OBSERVATION_RULES:
        if any(keyword.lower() in lowered for keyword in keywords):
            return candidate
    return "note"


def emotion_tags(text: str) -> List[str]:
    lowered = text.lower()
    found = []
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            found.append(emotion)
    return found


def text_excerpt(text: str, limit: int = 1200) -> str:
    cleaned = re.sub(r"\s+", " ", clean_inline(text)).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def build_entities(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    entities = []
    for group_name, group_entities in catalog.get("entities", {}).items():
        for entity in group_entities:
            aliases = list(entity.get("aliases") or [])
            display_name = entity.get("display_name")
            if display_name:
                aliases.append(display_name)
            aliases = sorted(set(alias for alias in aliases if alias), key=len, reverse=True)
            enriched = dict(entity)
            enriched["group"] = group_name
            enriched["_aliases"] = aliases
            entities.append(enriched)
    return entities


def contains_alias(text: str, alias: str) -> bool:
    if not alias:
        return False
    if alias.isascii():
        return alias.lower() in text.lower()
    return alias in text


def entity_matches(entity: Dict[str, Any], text: str) -> Tuple[bool, str]:
    for negative in entity.get("negative_aliases", []) or []:
        if contains_alias(text, negative):
            return False, ""
    required_context = entity.get("requires_any_context", []) or []
    if required_context and not any(contains_alias(text, context) for context in required_context):
        return False, ""
    for alias in entity["_aliases"]:
        if contains_alias(text, alias):
            return True, alias
    return False, ""


def confidence_rank(confidence: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(confidence, 0)


def merge_confidence(a: str, b: str) -> str:
    return a if confidence_rank(a) <= confidence_rank(b) else b


def record_link_text(record: Dict[str, Any]) -> str:
    parts = [
        record.get("title"),
        record.get("summary"),
        record.get("raw_text_excerpt"),
        " ".join(record.get("obsidian_links") or []),
        " ".join(record.get("notes") or []),
    ]
    return "\n".join(str(part) for part in parts if part)


def link_record(record: Dict[str, Any], entities: List[Dict[str, Any]], relations: Dict[str, str]) -> Dict[str, Any]:
    text = record_link_text(record)
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
                "display_name": entity.get("display_name"),
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


def build_time_block_record(note_id: str, date: str, source_path: Path, index: int, block: Dict[str, Any]) -> Dict[str, Any]:
    notes = [clean_inline(line) for line in block["note_lines"] if clean_inline(line)]
    note_text = "\n".join(notes)
    combined = "\n".join([block["title"], note_text])
    area, area_scores = score_area(combined)
    obs_type = observation_type(combined)
    return {
        "id": f"{note_id}_timeblock_{index:03d}",
        "object_type": "TimeBlock",
        "observation_type": obs_type,
        "source_ref": note_id,
        "source_path": rel(source_path),
        "original_date": date,
        "date": date,
        "start": block["start"],
        "end": block["end"],
        "duration_minutes": block["duration_minutes"],
        "area": area,
        "area_scores": area_scores,
        "mode": "actual_or_planned_from_daily_note",
        "title": block["title"] or "Untitled",
        "summary": text_excerpt(note_text, limit=800),
        "notes": notes,
        "energy_score": block["energy_score"],
        "emotion_tags": emotion_tags(combined),
        "tags": block["tags"],
        "obsidian_links": sorted(set(block["obsidian_links"] + wiki_links(note_text))),
        "confidence": "medium",
        "needs_user_review": False,
        "raw_text_excerpt": text_excerpt("\n".join([block["raw_title"]] + block["note_lines"])),
        "raw_text_sha256": sha256_text("\n".join([block["raw_title"]] + block["note_lines"])),
    }


def build_section_record(note_id: str, date: str, source_path: Path, section_name: str, section: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    section_type = SECTION_TYPES.get(section_name)
    if not section_type:
        return None
    body = section["body"].strip()
    if not clean_inline(body):
        return None
    area, area_scores = score_area(body)
    obs_type = observation_type(body, section_type)
    slug = re.sub(r"[^a-z0-9]+", "_", section_name).strip("_")
    return {
        "id": f"{note_id}_section_{slug}",
        "object_type": "DailySection",
        "observation_type": obs_type,
        "section_type": section_type,
        "source_ref": note_id,
        "source_path": rel(source_path),
        "original_date": date,
        "date": date,
        "area": area,
        "area_scores": area_scores,
        "title": section["title"],
        "summary": text_excerpt(body),
        "emotion_tags": emotion_tags(body),
        "tags": tags(body),
        "obsidian_links": wiki_links(body),
        "confidence": "medium",
        "needs_user_review": False,
        "raw_text_excerpt": text_excerpt(body),
        "raw_text_sha256": sha256_text(body),
    }


def normalize_daily_note(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    date = date_from_daily_note(path)
    note_id = daily_note_id(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    sections = extract_sections(text)
    records = []

    day_planner = sections.get("day planner")
    if day_planner:
        for index, block in enumerate(extract_day_planner_blocks(day_planner["body"]), start=1):
            records.append(build_time_block_record(note_id, date, path, index, block))

    for section_name, section in sections.items():
        record = build_section_record(note_id, date, path, section_name, section)
        if record:
            records.append(record)

    note = {
        "id": note_id,
        "object_type": "DailyNote",
        "source_path": rel(path),
        "original_date": date,
        "date": date,
        "sha256": sha256_file(path),
        "section_names": [section["title"] for section in sections.values()],
        "has_day_planner": bool(day_planner),
        "time_block_count": sum(1 for record in records if record["object_type"] == "TimeBlock"),
        "section_record_count": sum(1 for record in records if record["object_type"] == "DailySection"),
        "line_count": len(text.splitlines()),
    }
    return note, records


def summarize_daily(notes: List[Dict[str, Any]], linked_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    notes_by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for note in notes:
        notes_by_date[note["date"]].append(note)
    records_by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in linked_records:
        records_by_date[record["date"]].append(record)

    rows = []
    for date in sorted(notes_by_date):
        date_notes = sorted(notes_by_date[date], key=lambda item: item["source_path"])
        records = records_by_date.get(date, [])
        time_blocks = [record for record in records if record["object_type"] == "TimeBlock"]
        area_minutes = defaultdict(int)
        area_records = Counter()
        observation_counts = Counter()
        emotion_counts = Counter()
        entity_counts = Counter()
        energy_values = []

        for record in records:
            area_records[record["area"]] += 1
            observation_counts[record["observation_type"]] += 1
            for emotion in record.get("emotion_tags") or []:
                emotion_counts[emotion] += 1
            for link in record.get("semantic_links") or []:
                entity_counts[link["entity_ref"]] += 1
            if record["object_type"] == "TimeBlock":
                area_minutes[record["area"]] += int(record.get("duration_minutes") or 0)
                if record.get("energy_score") is not None:
                    energy_values.append(int(record["energy_score"]))

        rows.append(
            {
                "id": f"obsidian_daily_summary_{date.replace('-', '')}",
                "date": date,
                "source_refs": [note["id"] for note in date_notes],
                "source_paths": [note["source_path"] for note in date_notes],
                "has_day_planner": any(note["has_day_planner"] for note in date_notes),
                "time_block_count": len(time_blocks),
                "section_record_count": sum(note["section_record_count"] for note in date_notes),
                "total_timeblock_minutes": sum(int(record.get("duration_minutes") or 0) for record in time_blocks),
                "area_minutes": dict(sorted(area_minutes.items())),
                "area_records": dict(sorted(area_records.items())),
                "observation_counts": dict(sorted(observation_counts.items())),
                "emotion_counts": dict(sorted(emotion_counts.items())),
                "avg_energy_score": round(sum(energy_values) / len(energy_values), 2) if energy_values else None,
                "semantic_entity_refs": [entity for entity, _ in entity_counts.most_common()],
                "record_refs": [record["id"] for record in records],
                "top_timeblock_titles": [record["title"] for record in time_blocks[:8]],
            }
        )
    return rows


def summarize_import(
    raw_files: List[Path],
    notes: List[Dict[str, Any]],
    linked_records: List[Dict[str, Any]],
    daily_rows: List[Dict[str, Any]],
    catalog: Dict[str, Any],
) -> Dict[str, Any]:
    time_blocks = [record for record in linked_records if record["object_type"] == "TimeBlock"]
    section_records = [record for record in linked_records if record["object_type"] == "DailySection"]
    linked = [record for record in linked_records if record["semantic_links"]]

    by_year = Counter(record["date"][:4] for record in linked_records)
    by_area_records = Counter(record["area"] for record in linked_records)
    by_area_minutes = defaultdict(int)
    observation_counts = Counter(record["observation_type"] for record in linked_records)
    emotion_counts = Counter()
    entity_counts = Counter()
    entity_minutes = defaultdict(int)
    object_type_counts = Counter()
    relation_counts = Counter()
    review_counts = Counter()
    examples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    energy_values = []

    for record in linked_records:
        if record["object_type"] == "TimeBlock":
            by_area_minutes[record["area"]] += int(record.get("duration_minutes") or 0)
            if record.get("energy_score") is not None:
                energy_values.append(int(record["energy_score"]))
        for emotion in record.get("emotion_tags") or []:
            emotion_counts[emotion] += 1
        for link in record.get("semantic_links") or []:
            entity_ref = link["entity_ref"]
            entity_counts[entity_ref] += 1
            entity_minutes[entity_ref] += int(record.get("duration_minutes") or 0)
            object_type_counts[link["object_type"]] += 1
            relation_counts[link["relation"]] += 1
            if link["needs_user_review"]:
                review_counts[entity_ref] += 1
            if len(examples[entity_ref]) < 4:
                examples[entity_ref].append(
                    {
                        "record_ref": record["id"],
                        "date": record["date"],
                        "area": record["area"],
                        "title": record["title"],
                        "matched_alias": link["matched_alias"],
                    }
                )

    catalog_entities = {}
    for group, values in catalog.get("entities", {}).items():
        for entity in values:
            catalog_entities[entity["id"]] = {
                "object_type": entity["object_type"],
                "display_name": entity.get("display_name"),
                "group": group,
                "needs_user_review": entity.get("needs_user_review", False),
            }

    top_entities = []
    for entity_ref, count in entity_counts.most_common(30):
        info = catalog_entities.get(entity_ref, {})
        top_entities.append(
            {
                "entity_ref": entity_ref,
                "display_name": info.get("display_name"),
                "object_type": info.get("object_type"),
                "records": count,
                "hours": round(entity_minutes[entity_ref] / 60, 2),
                "needs_user_review_records": review_counts[entity_ref],
                "examples": examples[entity_ref],
            }
        )

    dates = sorted(note["date"] for note in notes)
    duplicate_dates = {
        date: [note["source_path"] for note in date_notes]
        for date, date_notes in sorted(
            {
                date: [note for note in notes if note["date"] == date]
                for date in sorted(set(note["date"] for note in notes))
            }.items()
        )
        if len(date_notes) > 1
    }
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "import_scope": {
            "source_root": rel(SOURCE_ROOT),
            "raw_file_count": len(raw_files),
            "markdown_file_count": sum(1 for path in raw_files if path.suffix.lower() == ".md"),
            "daily_note_count": len(notes),
            "daily_note_folders": dict(Counter(path.parent.name for path in sorted(SOURCE_ROOT.rglob("*.md")) if is_daily_note(path))),
            "date_range": {"start": dates[0] if dates else None, "end": dates[-1] if dates else None},
            "unique_day_count": len(set(dates)),
            "duplicate_dates": duplicate_dates,
            "raw_policy": "Raw Obsidian files are preserved under raw_data/obsidian/01_Daily; derived indexes keep source paths, hashes, and excerpts.",
        },
        "records": {
            "total": len(linked_records),
            "time_blocks": len(time_blocks),
            "section_records": len(section_records),
            "with_semantic_links": len(linked),
            "without_semantic_links": len(linked_records) - len(linked),
            "with_review_needed": sum(1 for record in linked if record["semantic_needs_user_review"]),
            "by_year": dict(sorted(by_year.items())),
            "by_area_records": dict(sorted(by_area_records.items())),
            "by_area_hours_from_time_blocks": {
                area: round(minutes / 60, 2) for area, minutes in sorted(by_area_minutes.items())
            },
            "by_observation_type": dict(observation_counts.most_common()),
            "emotion_tag_counts": dict(emotion_counts.most_common()),
            "energy": {
                "record_count": len(energy_values),
                "avg": round(sum(energy_values) / len(energy_values), 2) if energy_values else None,
                "min": min(energy_values) if energy_values else None,
                "max": max(energy_values) if energy_values else None,
            },
        },
        "daily_summary": {
            "daily_summary_ref": rel(DAILY_SUMMARY_PATH),
            "day_count": len(daily_rows),
            "days_with_time_blocks": sum(1 for row in daily_rows if row["time_block_count"]),
            "days_with_semantic_links": sum(1 for row in daily_rows if row["semantic_entity_refs"]),
        },
        "link_counts": {
            "by_object_type": dict(object_type_counts),
            "by_relation": dict(relation_counts),
        },
        "top_entities": top_entities,
        "outputs": {
            "manifest_ref": rel(MANIFEST_PATH),
            "normalized_records_ref": rel(NORMALIZED_PATH),
            "entity_linked_records_ref": rel(LINKED_PATH),
            "daily_summary_ref": rel(DAILY_SUMMARY_PATH),
            "summary_ref": rel(SUMMARY_PATH),
        },
    }


def build_manifest(raw_files: List[Path], notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    inventory = []
    daily_paths = {note["source_path"] for note in notes}
    for path in sorted(raw_files):
        path_text = rel(path)
        inventory.append(
            {
                "path": path_text,
                "role": "daily_note" if path_text in daily_paths else "supporting_raw_file",
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "source_root": rel(SOURCE_ROOT),
        "raw_file_count": len(raw_files),
        "daily_note_count": len(notes),
        "outputs": {
            "normalized_records_ref": rel(NORMALIZED_PATH),
            "entity_linked_records_ref": rel(LINKED_PATH),
            "daily_summary_ref": rel(DAILY_SUMMARY_PATH),
            "summary_ref": rel(SUMMARY_PATH),
        },
        "inventory": inventory,
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# Obsidian Daily Import

This folder contains ontology-friendly indexes generated from Brian's Obsidian `01_Daily` raw snapshot.

Raw source files are preserved in the repository under:

- `raw_data/obsidian/01_Daily/`

Generated files:

- `manifest.yaml`: source file inventory with path, role, size, and sha256.
- `summary.yaml`: aggregate import summary, area totals, energy stats, emotion tags, and semantic link counts.
- `normalized_records.jsonl`: parsed `TimeBlock` and `DailySection` records from dated Daily notes.
- `entity_linked_records.jsonl`: normalized records with semantic links to ontology objects.
- `daily_summary.jsonl`: day-level aggregates for time blocks, sections, areas, emotions, and entity refs.

Regenerate with:

```bash
python3 tools/import_obsidian_daily.py
```

Semantic links are candidates when their source entity is marked `needs_user_review` in `life/entities/semantic_entity_catalog.yaml`.
Daily note time blocks come from the `### Day planner` section and should be treated as mixed planned/actual unless Brian confirms otherwise.
""",
        encoding="utf-8",
    )


def main() -> None:
    catalog = load_yaml(CATALOG_PATH)
    entities = build_entities(catalog)
    relations = catalog.get("link_relations", {})
    raw_files = [path for path in SOURCE_ROOT.rglob("*") if path.is_file()]
    daily_files = sorted(path for path in SOURCE_ROOT.rglob("*.md") if is_daily_note(path))

    notes = []
    records = []
    for path in daily_files:
        note, note_records = normalize_daily_note(path)
        notes.append(note)
        records.extend(note_records)

    linked_records = [link_record(record, entities, relations) for record in records]
    daily_rows = summarize_daily(notes, linked_records)

    dump_jsonl(NORMALIZED_PATH, records)
    dump_jsonl(LINKED_PATH, linked_records)
    dump_jsonl(DAILY_SUMMARY_PATH, daily_rows)
    dump_yaml(MANIFEST_PATH, build_manifest(raw_files, notes))
    dump_yaml(SUMMARY_PATH, summarize_import(raw_files, notes, linked_records, daily_rows, catalog))
    write_readme()

    print(f"raw_files={len(raw_files)}")
    print(f"daily_notes={len(notes)}")
    print(f"records={len(records)}")
    print(f"time_blocks={sum(1 for record in records if record['object_type'] == 'TimeBlock')}")
    print(f"linked_records={sum(1 for record in linked_records if record['semantic_links'])}")


if __name__ == "__main__":
    main()
