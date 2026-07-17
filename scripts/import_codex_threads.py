#!/usr/bin/env python3
"""Build a local, reviewable index of Brian's Codex threads and prompts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


AREA_RULES = {
    "CAREER": [
        "codex", "claude", "agent", "mcp", "llm", "prompt", "skill", "plugin",
        "rtl", "verilog", "soc", "milano", "firenze", "uvm", "axi", "mctp",
        "simulation", "timing", "ip", "코덱스", "클로드", "에이전트", "반도체",
    ],
    "FINANCE": [
        "주식", "투자", "자산", "성과급", "하이닉스", "삼성전자", "포트폴리오",
        "예금", "연금", "퇴직금", "대출", "아파트", "부동산", "경제", "금리",
    ],
    "BODY": [
        "운동", "헬스", "pt", "스쿼트", "가슴", "어깨", "등운동", "하체",
        "칼로리", "단백질", "인바디", "몸무게", "건강", "병원",
    ],
    "MIND": [
        "기분", "감정", "마음", "행복", "스트레스", "생각", "철학", "원칙",
        "배우", "공부", "이해", "기억", "온톨로지",
    ],
    "RELATION": ["와이프", "아내", "가족", "명재", "지구", "해이", "반려견", "부모"],
    "FUN": ["여행", "방콕", "태국", "호텔", "맛집", "놀", "재미"],
    "MAINTENANCE": ["보험", "영수증", "서류", "정리", "청소", "수리", "예약", "구매"],
}

THOUGHT_TERMS = [
    "생각", "느낌", "궁금", "왜", "어떻게", "같아", "낙관", "원칙", "철학",
    "중요", "이해", "의견", "피드백", "what", "why", "how", "think",
]
ACTIVITY_TERMS = [
    "해줘", "만들", "수정", "테스트", "실행", "기록", "운동", "다녀", "완료",
    "설치", "조사", "분석", "리뷰", "commit", "run ", "fix ", "create ", "update ",
]
DECISION_TERMS = ["하자", "해야", "할게", "정했", "기준", "보수적으로", "로 하", "결정"]


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_no, json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSONL: {path}:{line_no}: {exc}") from exc


def clean_preview(text: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def term_matches(text: str, term: str) -> bool:
    if term.isascii() and re.fullmatch(r"[a-z0-9_]+", term):
        return re.search(rf"(?<![a-z0-9_]){re.escape(term)}(?![a-z0-9_])", text) is not None
    return term in text


def classify_areas(text: str) -> list[str]:
    lower = f" {text.lower()} "
    scores = {
        area: sum(1 for term in terms if term_matches(lower, term))
        for area, terms in AREA_RULES.items()
    }
    matched = [area for area, score in sorted(scores.items(), key=lambda item: (-item[1], item[0])) if score]
    return matched[:3] or ["UNCLASSIFIED"]


def classify_record_types(text: str) -> list[str]:
    lower = text.lower()
    result = []
    if any(term in lower for term in THOUGHT_TERMS):
        result.append("thought")
    if any(term in lower for term in ACTIVITY_TERMS):
        result.append("activity_or_request")
    if any(term in lower for term in DECISION_TERMS):
        result.append("decision_candidate")
    return result or ["uncategorized_user_input"]


def iso_from_epoch(value: int | float, timezone: ZoneInfo) -> str:
    return datetime.fromtimestamp(value, timezone).isoformat(timespec="seconds")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    index_path = args.codex_home / "session_index.jsonl"
    history_path = args.codex_home / "history.jsonl"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    timezone = ZoneInfo("Asia/Seoul")

    ui_threads = {}
    duplicate_ui_rows = 0
    for line_no, row in read_jsonl(index_path):
        thread_id = row.get("id")
        if not thread_id:
            continue
        if thread_id in ui_threads:
            duplicate_ui_rows += 1
        ui_threads[thread_id] = {
            "thread_id": thread_id,
            "thread_name": row.get("thread_name") or "untitled",
            "updated_at": row.get("updated_at"),
            "source": "session_index",
            "source_line": line_no,
        }

    messages_by_session = defaultdict(list)
    all_messages = []
    area_counts = Counter()
    type_counts = Counter()
    for line_no, row in read_jsonl(history_path):
        session_id = row.get("session_id")
        text = row.get("text")
        timestamp = row.get("ts")
        if not session_id or text is None or timestamp is None:
            continue
        areas = classify_areas(text)
        record_types = classify_record_types(text)
        for area in areas:
            area_counts[area] += 1
        for record_type in record_types:
            type_counts[record_type] += 1
        message = {
            "id": f"codex_user_message_{session_id}_{line_no:06d}",
            "source_type": "chat",
            "source_name": "codex_history_jsonl",
            "source_path": str(history_path),
            "source_line": line_no,
            "session_id": session_id,
            "timestamp": iso_from_epoch(timestamp, timezone),
            "raw_text": text,
            "preview": clean_preview(text),
            "area_candidates": areas,
            "record_type_candidates": record_types,
            "parse_status": "partially_parsed",
            "confidence": "medium" if areas != ["UNCLASSIFIED"] else "low",
            "needs_user_review": "decision_candidate" in record_types,
        }
        messages_by_session[session_id].append(message)
        all_messages.append(message)

    union_ids = sorted(set(ui_threads) | set(messages_by_session))
    thread_rows = []
    for thread_id in union_ids:
        meta = ui_threads.get(thread_id)
        messages = messages_by_session.get(thread_id, [])
        if meta:
            name = meta["thread_name"]
            updated_at = meta["updated_at"]
        elif messages:
            name = clean_preview(messages[0]["raw_text"], 100)
            updated_at = messages[-1]["timestamp"]
        else:
            name = "untitled"
            updated_at = None
        area_summary = Counter(area for message in messages for area in message["area_candidates"])
        type_summary = Counter(kind for message in messages for kind in message["record_type_candidates"])
        thread_rows.append({
            "thread_id": thread_id,
            "thread_name": name,
            "updated_at": updated_at,
            "index_membership": {
                "session_index": thread_id in ui_threads,
                "history": thread_id in messages_by_session,
            },
            "user_message_count": len(messages),
            "first_user_message_at": messages[0]["timestamp"] if messages else None,
            "last_user_message_at": messages[-1]["timestamp"] if messages else None,
            "area_counts": dict(area_summary.most_common()),
            "record_type_counts": dict(type_summary.most_common()),
            "first_user_message_preview": messages[0]["preview"] if messages else None,
            "source_refs": [
                ref for ref, present in (
                    ("codex_session_index", thread_id in ui_threads),
                    ("codex_history", thread_id in messages_by_session),
                ) if present
            ],
        })

    with (output_dir / "thread_index.jsonl").open("w", encoding="utf-8") as handle:
        for row in thread_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (output_dir / "user_message_index.jsonl").open("w", encoding="utf-8") as handle:
        for row in all_messages:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "generated_at": datetime.now(timezone).isoformat(timespec="seconds"),
        "source_counts": {
            "session_index_rows": sum(1 for _ in read_jsonl(index_path)),
            "session_index_unique_threads": len(ui_threads),
            "session_index_duplicate_rows": duplicate_ui_rows,
            "history_user_messages": len(all_messages),
            "history_unique_sessions": len(messages_by_session),
            "union_thread_count": len(union_ids),
            "threads_in_both_sources": len(set(ui_threads) & set(messages_by_session)),
        },
        "classification_counts": {
            "areas": dict(area_counts.most_common()),
            "record_types": dict(type_counts.most_common()),
        },
        "limitations": [
            "Area and record-type classifications are keyword-based candidates, not confirmed interpretation.",
            "Session index and history IDs are only partially overlapping because Codex stores imported, legacy, UI, and execution sessions differently.",
            "Assistant responses and tool transcripts are not copied into the user-message index.",
        ],
    }
    with (output_dir / "import_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
