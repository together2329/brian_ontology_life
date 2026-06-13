#!/usr/bin/env python3
"""Import Brian's happiness bundle PDF as ontology-ready local indexes."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

import fitz
import yaml


SOURCE_PATH = Path(
    os.environ.get(
        "HAPPINESS_BUNDLE_PDF",
        "/Users/brian/Library/CloudStorage/GoogleDrive-together2329@gmail.com/내 드라이브/"
        "Brian's Life/행복꾸러미.doc.pdf",
    )
)
IMPORT_DIR = Path("life/imports/happiness_bundle")
MANIFEST_PATH = IMPORT_DIR / "manifest.yaml"
PAGE_INDEX_PATH = IMPORT_DIR / "page_index.jsonl"
IMAGE_INDEX_PATH = IMPORT_DIR / "image_index.jsonl"
PARSED_ITEMS_PATH = IMPORT_DIR / "parsed_items.yaml"
CONCEPT_PATH = Path("life/concepts/happiness_bundle.yaml")

AREA_MAP = {
    "MIND": "MIND",
    "BODY": "BODY",
    "RELATION": "RELATION",
    "FINANCIAL": "FINANCE",
    "FINANCE": "FINANCE",
    "CAREER": "CAREER",
    "FUN": "FUN",
    "Multiple": "MULTIPLE",
}

KEYWORD_TAGS = {
    "immediate_action": ["바로 실행", "바로 행동", "행동", "실천"],
    "planning": ["계획", "목표", "시뮬레이션", "스토리", "데드라인"],
    "gratitude": ["감사"],
    "memory_visualization": ["기억", "사진", "영상", "시각화", "상상"],
    "presence": ["순간", "온전히", "천천히", "호흡", "충만"],
    "learning_growth": ["책", "강의", "배우", "성장", "개선", "공부"],
    "flow_mastery": ["몰입", "탁월", "최고", "원리", "전문가"],
    "writing_reflection": ["글", "데일리리포트", "메타인지", "기록", "반성"],
    "body_movement": ["걷", "달리", "운동", "근력", "탁구", "등산", "산책"],
    "body_recovery": ["목욕", "족욕", "반신욕", "여유"],
    "relationship": ["아름", "사람", "전화", "사랑", "고마움", "여행", "대화"],
    "companion_animal": ["지구", "강아지", "반려견", "해이"],
    "finance_progress": ["돈", "저축", "300 만원", "소득", "재산"],
    "career_creation": ["SoC", "PCIe", "발표", "가치", "상품", "Youtube", "영어"],
    "nature_music": ["자연", "음악", "바다", "햇살"],
    "food_scene": ["식사", "요리", "샌드위치", "카페모카", "와인", "음식"],
}

ENTITY_KEYWORDS = {
    "person_wife": ["아름"],
    "person_mother": ["엄마"],
    "person_father": ["아빠"],
    "person_mother_in_law": ["어머님", "장모"],
    "person_father_in_law": ["아버님", "장인"],
    "pet_dog_1": ["지구"],
    "pet_dog_2": ["해이"],
    "component_pcie": ["PCIe", "PCIE"],
    "activity_happiness_bundle": ["행복꾸러미", "행복 꾸러미", "행복꾸러기"],
    "activity_gratitude": ["감사"],
    "activity_goal_review": ["데일리리포트", "목표", "계획", "Hot Spots"],
    "activity_memo": ["글", "기록", "메모", "생각 정리"],
    "activity_workout": ["걷", "달리", "운동", "근력", "탁구", "등산", "산책"],
    "activity_meal": ["식사", "요리", "샌드위치", "카페모카", "와인"],
    "activity_rest": ["휴식", "여유", "목욕", "족욕", "반신욕"],
}

VISUAL_CATEGORY_PAGE_GROUPS = {
    "nature_sky_sea_travel": [12, 13, 67, 68, 111, 112, 113, 114, 115, 121],
    "exercise_movement": [61, 67, 68],
    "body_recovery_bath": [71],
    "workspace_cafe_focus": [54, 56, 57, 63, 75, 123, 126, 130, 132, 133],
    "relationship_family_friends": [30, 31, 32, 35, 72, 74, 81, 83, 90, 91, 95, 125, 127, 129, 130],
    "companion_animal_jigu": [90, 91, 92, 93, 94],
    "food_home_cooking": [74, 75, 125, 127, 129, 130, 132, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 148, 149, 150, 151],
    "music_media_inspiration": [20, 44, 116, 117, 128],
    "planning_record_screenshot": [10, 21, 22, 58, 65, 72, 82, 128],
    "gratitude_message": [58, 65, 81],
    "learning_creation": [6, 7, 8, 11, 20, 44],
    "memory_photo_archive": [30, 31, 32, 35, 90, 91, 92, 94, 95, 111, 112, 113, 114, 115],
}

VISUAL_CATEGORY_DESCRIPTIONS = {
    "nature_sky_sea_travel": "Natural scenes such as sky, sea, forest, garden, track, and travel views.",
    "exercise_movement": "Movement scenes such as running track, walking, or outdoor exercise context.",
    "body_recovery_bath": "Bathing or hot-water recovery scenes.",
    "workspace_cafe_focus": "Laptop, desk, cafe, monitor, or focused personal workspace scenes.",
    "relationship_family_friends": "People-centered memories with spouse, family, friends, or shared meals.",
    "companion_animal_jigu": "Photos of 지구, Brian's first dog.",
    "food_home_cooking": "Home cooking, meals, ingredients, drinks, and shared food scenes.",
    "music_media_inspiration": "Music, video, movie, lecture, or media that evokes inspiration.",
    "planning_record_screenshot": "Screenshots or photos of notes, plans, chats, diagrams, or records.",
    "gratitude_message": "Message or record screenshots connected to gratitude and appreciation.",
    "learning_creation": "Learning, content creation, YouTube, tools, or skill-building visuals.",
    "memory_photo_archive": "Photos used as memory anchors for recollection and emotional recall.",
}

VISUAL_KIND_BY_PAGE = {
    "screenshot_or_note": [10, 20, 21, 22, 44, 58, 65, 72, 82, 128],
    "photo": [
        12,
        13,
        30,
        31,
        32,
        35,
        54,
        56,
        57,
        61,
        63,
        67,
        68,
        71,
        74,
        75,
        90,
        91,
        92,
        94,
        95,
        111,
        112,
        113,
        114,
        115,
        121,
        123,
        125,
        126,
        127,
        129,
        130,
        132,
        133,
        135,
        136,
        137,
        138,
        139,
        140,
        141,
        142,
        143,
        144,
        145,
        146,
        148,
        149,
        150,
        151,
    ],
    "mixed_document_photo": [6, 7, 8, 11, 81, 83, 116, 117],
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


def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())


def text_excerpt(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def extract_pages(path: Path) -> List[Dict[str, Any]]:
    doc = fitz.open(path)
    pages = []
    for index, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        normalized = "\n".join(normalize_line(line) for line in text.splitlines())
        pages.append(
            {
                "page": index,
                "text": normalized.strip(),
                "char_count": len(normalized.strip()),
                "has_extractable_text": bool(normalized.strip()),
            }
        )
    return pages


def detect_tags(text: str) -> List[str]:
    tags = []
    for tag, keywords in KEYWORD_TAGS.items():
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    return sorted(tags)


def detect_entities(text: str) -> Dict[str, List[str]]:
    refs = []
    for entity_ref, keywords in ENTITY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            refs.append(entity_ref)
    return {"entity_refs": sorted(refs)}


def visual_categories_for_page(page_no: int) -> List[str]:
    categories = set()
    for category, pages in VISUAL_CATEGORY_PAGE_GROUPS.items():
        if page_no in pages:
            categories.add(category)
    return sorted(categories)


def visual_kind_for_page(page_no: int, image_count: int, text: str) -> str:
    for kind, pages in VISUAL_KIND_BY_PAGE.items():
        if page_no in pages:
            return kind
    if image_count == 0:
        return "text_only_or_blank"
    if text and len(text) > 120:
        return "mixed_document_visual"
    return "visual_page"


def image_entity_refs(page_no: int, text: str) -> Dict[str, List[str]]:
    refs = set(detect_entities(text)["entity_refs"])
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["companion_animal_jigu"]:
        refs.add("pet_dog_1")
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["food_home_cooking"]:
        refs.add("activity_meal")
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["exercise_movement"]:
        refs.add("activity_workout")
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["body_recovery_bath"]:
        refs.add("activity_rest")
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["workspace_cafe_focus"]:
        refs.add("activity_memo")
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["planning_record_screenshot"]:
        refs.add("activity_goal_review")
    if page_no in VISUAL_CATEGORY_PAGE_GROUPS["gratitude_message"]:
        refs.add("activity_gratitude")
    return {"entity_refs": sorted(refs)}


def image_rows(path: Path, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    doc = fitz.open(path)
    rows = []
    for index, page in enumerate(doc, start=1):
        images = []
        for image_no, image in enumerate(page.get_images(full=True), start=1):
            xref = image[0]
            info = doc.extract_image(xref)
            image_bytes = info.get("image", b"")
            images.append(
                {
                    "image_no": image_no,
                    "xref": xref,
                    "ext": info.get("ext"),
                    "width": info.get("width"),
                    "height": info.get("height"),
                    "colorspace": info.get("colorspace"),
                    "bpc": info.get("bpc"),
                    "sha256": hashlib.sha256(image_bytes).hexdigest() if image_bytes else None,
                }
            )

        page_text = pages[index - 1]["text"]
        categories = visual_categories_for_page(index)
        text_tags = detect_tags(page_text)
        row = {
            "id": f"happiness_bundle_visual_page_{index:03d}",
            "source_ref": "source_happiness_bundle_pdf",
            "page": index,
            "image_count": len(images),
            "visual_kind": visual_kind_for_page(index, len(images), page_text),
            "visual_categories": categories,
            "text_tags": text_tags,
            "category_descriptions": [VISUAL_CATEGORY_DESCRIPTIONS[category] for category in categories if category in VISUAL_CATEGORY_DESCRIPTIONS],
            "linked_entities": image_entity_refs(index, page_text),
            "has_extractable_text": pages[index - 1]["has_extractable_text"],
            "text_excerpt": text_excerpt(page_text),
            "images": images,
            "confidence": "high" if index in {page for pages_ in VISUAL_CATEGORY_PAGE_GROUPS.values() for page in pages_} else "medium",
            "review_method": "page_render_contact_sheet" if images else "text_index_only",
            "stores_image_bytes": False,
        }
        if images or categories or not pages[index - 1]["has_extractable_text"]:
            rows.append(row)
    return rows


def extract_items(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    current_area = "UNKNOWN"
    current: Dict[str, Any] | None = None

    def flush() -> None:
        nonlocal current
        if not current:
            return
        text = re.sub(r"\s+", " ", current["text"]).strip()
        if text and text not in {"•", "o"}:
            item_no = len(items) + 1
            current["id"] = f"happiness_trigger_{item_no:03d}"
            current["text"] = text
            current["tags"] = detect_tags(text)
            current["linked_entities"] = detect_entities(text)
            current["confidence"] = "high" if current["area"] in AREA_MAP.values() else "medium"
            current["needs_user_review"] = False
            current["source_ref"] = "source_happiness_bundle_pdf"
            current["source_pages"] = sorted(current["source_pages"])
            items.append(current)
        current = None

    for page in pages:
        blank_seen = False
        for raw_line in page["text"].splitlines():
            line = normalize_line(raw_line)
            if not line:
                if blank_seen:
                    flush()
                blank_seen = True
                continue
            blank_seen = False
            if line in AREA_MAP:
                flush()
                current_area = AREA_MAP[line]
                continue
            if line == "•":
                flush()
                continue

            bullet_match = re.match(r"^(?:o|§|\*)\s+(.+)$", line)
            if bullet_match:
                flush()
                current = {
                    "area": current_area,
                    "text": bullet_match.group(1).strip(),
                    "source_pages": {page["page"]},
                }
                continue

            if current and should_append_continuation(current["text"], line):
                current["text"] += " " + line
                current["source_pages"].add(page["page"])
            else:
                flush()
    flush()
    return items


def should_append_continuation(current_text: str, line: str) -> bool:
    if line.startswith("#"):
        return False
    if line in AREA_MAP:
        return False
    if re.match(r"^\d{4}[.]\d{1,2}[.]\d{1,2}", line):
        return False
    if re.match(r"^\[Brian", line):
        return False
    if len(line) > 140:
        return False
    if current_text.endswith((".", "!", "?", "다.", "요.", "함", ")")):
        return line.startswith(("→", "-", ":", "(", "좋아", "느낀다", "받아", "정리", "늘려", "존재"))
    return True


def page_index_rows(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for page in pages:
        text = page["text"]
        rows.append(
            {
                "id": f"happiness_bundle_page_{page['page']:03d}",
                "source_ref": "source_happiness_bundle_pdf",
                "page": page["page"],
                "char_count": page["char_count"],
                "has_extractable_text": page["has_extractable_text"],
                "text_sha256": sha256_text(text),
                "text_excerpt": text_excerpt(text),
                "tags": detect_tags(text),
                "linked_entities": detect_entities(text),
                "parse_status": "parsed" if page["has_extractable_text"] else "visual_page_pending_ocr",
            }
        )
    return rows


def build_manifest(path: Path, pages: List[Dict[str, Any]], items: List[Dict[str, Any]], images: List[Dict[str, Any]]) -> Dict[str, Any]:
    stat = path.stat()
    empty_pages = [page["page"] for page in pages if not page["has_extractable_text"]]
    image_pages = [row["page"] for row in images if row["image_count"]]
    return {
        "schema_version": 1,
        "source": {
            "id": "source_happiness_bundle_pdf",
            "title": "행복꾸러미",
            "source_type": "pdf",
            "path": str(path),
            "sha256": sha256_file(path),
            "size_bytes": stat.st_size,
            "mtime": dt.datetime.fromtimestamp(stat.st_mtime).replace(microsecond=0).isoformat(),
        },
        "imported_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        "page_count": len(pages),
        "total_text_chars": sum(page["char_count"] for page in pages),
        "empty_or_visual_pages": empty_pages,
        "pages_with_images": image_pages,
        "embedded_image_ref_count": sum(row["image_count"] for row in images),
        "parsed_item_count": len(items),
        "generated_files": {
            "page_index": str(PAGE_INDEX_PATH),
            "image_index": str(IMAGE_INDEX_PATH),
            "parsed_items": str(PARSED_ITEMS_PATH),
            "concept": str(CONCEPT_PATH),
        },
        "raw_policy": "Raw PDF remains at source path; derived ontology stores source path, sha256, page refs, short excerpts, and structured triggers.",
    }


def build_parsed_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    area_counts = Counter(item["area"] for item in items)
    tag_counts = Counter(tag for item in items for tag in item["tags"])
    return {
        "schema_version": 1,
        "source_ref": "source_happiness_bundle_pdf",
        "status": "parsed_from_pdf_text",
        "purpose": "Structured happiness trigger candidates extracted from Brian's 행복꾸러미 PDF.",
        "counts": {
            "total_items": len(items),
            "by_area": dict(sorted(area_counts.items())),
            "by_tag": dict(tag_counts.most_common()),
        },
        "items": items,
    }


def build_concept(items: List[Dict[str, Any]], images: List[Dict[str, Any]]) -> Dict[str, Any]:
    area_to_items: Dict[str, List[str]] = defaultdict(list)
    for item in items:
        area_to_items[item["area"]].append(item["id"])

    visual_summary: Dict[str, Dict[str, Any]] = {}
    for row in images:
        for category in row["visual_categories"]:
            visual_summary.setdefault(
                category,
                {
                    "description": VISUAL_CATEGORY_DESCRIPTIONS.get(category, category),
                    "pages": [],
                },
            )
            visual_summary[category]["pages"].append(row["page"])

    return {
        "schema_version": 1,
        "id": "happiness_bundle",
        "object_type": "HappinessBundle",
        "activity_ref": "activity_happiness_bundle",
        "status": "confirmed_by_brian",
        "updated_at": dt.date.today().isoformat(),
        "definition": "Brian-defined bundle of scenes, actions, values, memories, and sensory anchors that reliably make life feel happy or meaningful.",
        "source_refs": ["source_happiness_bundle_pdf"],
        "source_files": {
            "manifest_ref": str(MANIFEST_PATH),
            "page_index_ref": str(PAGE_INDEX_PATH),
            "image_index_ref": str(IMAGE_INDEX_PATH),
            "parsed_items_ref": str(PARSED_ITEMS_PATH),
        },
        "core_principles": [
            {
                "id": "happiness_principle_concrete_values",
                "statement": "Brian lives more densely when his values are concrete, visual, and connected to why they matter.",
                "source_pages": [1],
                "confidence": "high",
            },
            {
                "id": "happiness_principle_process_over_goal",
                "statement": "A goal does not automatically create happiness; goals should be designed so the process itself can be felt and enjoyed.",
                "source_pages": [5],
                "confidence": "high",
            },
            {
                "id": "happiness_principle_present_window",
                "statement": "Happiness can be embedded into the current 30-60 minute window by attending to the moment with care and gratitude.",
                "source_pages": [6],
                "confidence": "high",
            },
            {
                "id": "happiness_principle_memory_media",
                "statement": "Positive memories become stronger happiness anchors when preserved with writing, photos, videos, music, lighting, and sensory detail.",
                "source_pages": [3, 4, 16, 57],
                "confidence": "high",
            },
            {
                "id": "happiness_principle_action_precedes_feeling",
                "statement": "Intentional action can precede and generate the feeling of happiness.",
                "source_pages": [3, 153],
                "confidence": "high",
            },
            {
                "id": "happiness_principle_observe_and_adjust",
                "statement": "Daily reflection should identify which activities, places, times, and people raise or lower Brian's emotional quality of life.",
                "source_pages": [47, 153],
                "confidence": "high",
            },
        ],
        "area_model": {
            area: {
                "trigger_count": len(refs),
                "trigger_refs": refs,
            }
            for area, refs in sorted(area_to_items.items())
        },
        "visual_evidence_model": {
            category: {
                "description": info["description"],
                "page_count": len(sorted(set(info["pages"]))),
                "pages": sorted(set(info["pages"])),
            }
            for category, info in sorted(visual_summary.items())
        },
        "assistant_usage": [
            "When Brian is low-energy or unhappy, recommend one small happiness trigger from the least-covered life area.",
            "When planning a day, reserve at least one concrete happiness trigger, not only productive work.",
            "When CAREER load is high, check BODY, RELATION, MIND, and FUN triggers before adding more work.",
            "When Brian records happiness, link the record to the matching happiness trigger and update evidence.",
            "When a trigger has not appeared recently, surface it as a gentle candidate rather than a command.",
        ],
        "query_examples": [
            "최근 내가 놓치고 있는 행복꾸러미는 뭐야?",
            "CAREER 압박이 큰 날에 쓸 수 있는 20분짜리 행복꾸러미 추천해줘.",
            "아름이/지구/해이와 연결된 행복꾸러미를 보여줘.",
            "운동, 식사, 수면과 행복꾸러미가 같이 나온 날을 찾아줘.",
        ],
    }


def main() -> None:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(SOURCE_PATH)

    pages = extract_pages(SOURCE_PATH)
    items = extract_items(pages)
    images = image_rows(SOURCE_PATH, pages)
    dump_jsonl(PAGE_INDEX_PATH, page_index_rows(pages))
    dump_jsonl(IMAGE_INDEX_PATH, images)
    dump_yaml(PARSED_ITEMS_PATH, build_parsed_items(items))
    dump_yaml(CONCEPT_PATH, build_concept(items, images))
    dump_yaml(MANIFEST_PATH, build_manifest(SOURCE_PATH, pages, items, images))

    print(f"pages={len(pages)}")
    print(f"text_chars={sum(page['char_count'] for page in pages)}")
    print(f"parsed_items={len(items)}")
    print(f"image_pages={sum(1 for row in images if row['image_count'])}")
    print(f"embedded_image_refs={sum(row['image_count'] for row in images)}")
    print(f"visual_pages={sum(1 for page in pages if not page['has_extractable_text'])}")


if __name__ == "__main__":
    main()
