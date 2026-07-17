#!/usr/bin/env python3
"""Classify local Codex user inputs without sending private records externally."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TOPIC_RULES = {
    "agent_architecture": ["agent", "에이전트", "codex", "claude", "llm", "prompt", "subagent", "mcp", "skill", "plugin"],
    "ontology_memory": ["ontology", "온톨로지", "memory", "기억", "compression", "ssot", "context", "컨텍스트"],
    "semiconductor_ip": ["rtl", "verilog", "systemverilog", "soc", "ip", "mctp", "pl330", "apb", "axi", "uvm", "cocotb"],
    "verification_evidence": ["verification", "검증", "test", "테스트", "coverage", "커버리지", "evidence", "contract", "obligation", "requirement"],
    "orchestration_parallelism": ["parallel", "병렬", "wavefront", "dispatch", "ownership", "dependency", "orchestration", "orchestrator"],
    "career_learning": ["공부", "배우", "세미나", "발표", "자료", "research", "조사", "설명", "철학"],
    "finance_investing": ["주식", "투자", "포트폴리오", "하이닉스", "삼성전자", "성과급", "자산", "경제", "금리", "아파트", "대출"],
    "body_health": ["운동", "헬스", "인바디", "칼로리", "단백질", "스쿼트", "가슴 운동", "등운동", "하체 운동", "pt"],
    "mind_happiness": ["기분", "행복", "마음", "스트레스", "에너지", "통제되는 느낌", "충만"],
    "relations_pets": ["와이프", "가족", "반려견", "지구", "해이", "명재"],
    "travel_fun": ["여행", "태국", "방콕", "호텔", "재미"],
    "maintenance_admin": ["보험", "요금제", "영수증", "예약", "서류", "정리", "설치"],
}

INTENT_RULES = {
    "question_or_exploration": ["?", "왜", "어떻게", "뭐", "무엇", "궁금", "어때", "알려", "설명"],
    "action_request": ["해줘", "해 줘", "만들어", "수정", "고쳐", "실행", "테스트", "조사", "분석", "검토", "기록", "정리"],
    "decision_or_approval": ["하자", "로 하", "결정", "승인", "그래 ", "좋아 ", "일단 ", "기준으로", "할게"],
    "feedback_or_correction": ["아니", "맞아", "근데", "그런데", "다시", "왜 안", "이상", "문제", "틀"],
    "status_or_result_check": ["상황", "현황", "어디까지", "끝났", "완료", "결과", "통과", "되었", "됐"],
    "personal_fact_or_experience": ["다녀옴", "받음", "보유", "다니는 중", "키우고", "먹", "운동했", "기분이", "느낌", "예정이야"],
}

PASTE_MARKERS = [
    "• Ran ", "• Explored", "⏺", "────────────────", "ctrl + t to view transcript",
    "Token usage:", "You are the OAG", "OAG DISPATCH", "Service tier set to",
    "Added ", "Edited ", "Spawned ", "tool call", "call_id",
]


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if line.strip():
                yield line_no, json.loads(line)


def term_matches(text: str, term: str) -> bool:
    if term == "?":
        return "?" in text
    if term.isascii() and re.fullmatch(r"[a-z0-9_]+", term):
        return re.search(rf"(?<![a-z0-9_]){re.escape(term)}(?![a-z0-9_])", text) is not None
    return term in text


def matched_labels(text: str, rules: dict[str, list[str]], limit: int | None = None) -> list[str]:
    lower = text.lower()
    scored = []
    for label, terms in rules.items():
        score = sum(1 for term in terms if term_matches(lower, term))
        if score:
            scored.append((label, score))
    labels = [label for label, _ in sorted(scored, key=lambda item: (-item[1], item[0]))]
    return labels[:limit] if limit else labels


def classify_origin(text: str) -> tuple[str, str]:
    stripped = text.strip()
    line_count = stripped.count("\n") + 1
    marker_count = sum(marker in text for marker in PASTE_MARKERS)
    if re.fullmatch(r"/?(?:exit|quit|qquit|clear|model|login|logout|status|help)", stripped, re.I):
        return "ui_command_or_control", "high"
    if stripped.startswith(("<command-name>", "/model", "/goal", "$")) and len(stripped) < 300:
        return "ui_command_or_control", "medium"
    if stripped.startswith(("You are ", "TASK:", "Subagent availability probe", "OAG DISPATCH")):
        return "delegated_or_automated_task_prompt", "high"
    if marker_count >= 2 or (len(text) >= 1200 and marker_count >= 1):
        return "pasted_transcript_or_tool_log", "high"
    if len(text) >= 5000 or line_count >= 80:
        return "pasted_document_or_long_context", "medium"
    if re.search(r"/Users/brian/[^\s]+\.(?:png|jpe?g|pdf|docx|pptx)(?:\s|$)", text, re.I):
        return "attachment_or_file_reference", "high"
    if len(text) <= 600 and line_count <= 8:
        return "direct_user_input", "high"
    return "direct_or_composed_long_input", "medium"


def preview(text: str, limit: int = 220) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean if len(clean) <= limit else clean[: limit - 1] + "…"


def percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * fraction))
    return ordered[index]


def session_file_map(codex_home: Path, wanted_ids: set[str]) -> dict[str, Path]:
    result = {}
    roots = [codex_home / "sessions", codex_home / "archived_sessions"]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("rollout-*"):
            name = path.name
            for session_id in wanted_ids:
                if session_id in name:
                    result.setdefault(session_id, path)
    return result


def read_session_meta(path: Path) -> dict:
    try:
        if path.suffix == ".jsonl":
            with path.open(encoding="utf-8") as handle:
                for _ in range(8):
                    line = handle.readline()
                    if not line:
                        break
                    row = json.loads(line)
                    if row.get("type") == "session_meta":
                        return row.get("payload", {})
        else:
            row = json.loads(path.read_text(encoding="utf-8"))
            return row.get("session_meta", row.get("meta", {})) if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}
    return {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tz = ZoneInfo("Asia/Seoul")

    history_path = args.codex_home / "history.jsonl"
    history = [(line_no, row) for line_no, row in read_jsonl(history_path)]
    session_ids = {row.get("session_id") for _, row in history if row.get("session_id")}
    file_map = session_file_map(args.codex_home, session_ids)
    session_meta = {}
    for session_id in sorted(session_ids):
        path = file_map.get(session_id)
        meta = read_session_meta(path) if path else {}
        session_meta[session_id] = {
            "session_id": session_id,
            "rollout_path": str(path) if path else None,
            "cwd": meta.get("cwd"),
            "originator": meta.get("originator"),
            "source": meta.get("source"),
            "thread_source": meta.get("thread_source"),
            "model_provider": meta.get("model_provider"),
            "cli_version": meta.get("cli_version"),
        }

    origin_counts = Counter()
    topic_counts = Counter()
    intent_counts = Counter()
    monthly_counts = Counter()
    session_counts = Counter()
    cwd_counts = Counter()
    originator_counts = Counter()
    execution_context_counts = Counter()
    direct_topic_by_month = defaultdict(Counter)
    repeated_direct_inputs = Counter()
    text_lengths = []
    analyzed = []
    for line_no, row in history:
        text = row.get("text", "")
        session_id = row.get("session_id")
        timestamp = datetime.fromtimestamp(row.get("ts"), tz).isoformat(timespec="seconds")
        origin, origin_confidence = classify_origin(text)
        topics = matched_labels(text, TOPIC_RULES)
        intents = matched_labels(text, INTENT_RULES)
        meta = session_meta.get(session_id, {})
        cwd = meta.get("cwd")
        execution_context = "interactive_or_unknown"
        if meta.get("originator") == "codex_exec" or meta.get("source") == "exec":
            execution_context = "codex_exec"
        elif cwd and cwd.startswith("/tmp/"):
            execution_context = "temporary_experiment_workspace"

        origin_counts[origin] += 1
        for topic in topics or ["unclassified"]:
            topic_counts[topic] += 1
        for intent in intents or ["unclassified"]:
            intent_counts[intent] += 1
        monthly_counts[timestamp[:7]] += 1
        session_counts[session_id] += 1
        cwd_counts[cwd or "unknown"] += 1
        originator_counts[meta.get("originator") or "unknown"] += 1
        execution_context_counts[execution_context] += 1
        text_lengths.append(len(text))
        if origin == "direct_user_input":
            for topic in topics or ["unclassified"]:
                direct_topic_by_month[timestamp[:7]][topic] += 1
            normalized = re.sub(r"\s+", " ", text).strip()
            if normalized:
                repeated_direct_inputs[normalized] += 1
        analyzed.append({
            "id": f"codex_input_analysis_{session_id}_{line_no:06d}",
            "source_ref": f"codex_user_message_{session_id}_{line_no:06d}",
            "session_id": session_id,
            "timestamp": timestamp,
            "text_length": len(text),
            "line_count": text.count("\n") + 1,
            "input_origin_candidate": origin,
            "origin_confidence": origin_confidence,
            "execution_context": execution_context,
            "topic_candidates": topics or ["unclassified"],
            "intent_candidates": intents or ["unclassified"],
            "preview": preview(text),
            "needs_user_review": origin not in {"direct_user_input", "ui_command_or_control"},
        })

    with (args.output_dir / "session_metadata.jsonl").open("w", encoding="utf-8") as handle:
        for row in session_meta.values():
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (args.output_dir / "input_analysis.jsonl").open("w", encoding="utf-8") as handle:
        for row in analyzed:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "generated_at": datetime.now(tz).isoformat(timespec="seconds"),
        "message_count": len(analyzed),
        "session_count": len(session_ids),
        "sessions_with_rollout_metadata": len(file_map),
        "monthly_counts": dict(sorted(monthly_counts.items())),
        "origin_counts": dict(origin_counts.most_common()),
        "topic_counts": dict(topic_counts.most_common()),
        "intent_counts": dict(intent_counts.most_common()),
        "text_length": {
            "total_characters": sum(text_lengths),
            "median": percentile(text_lengths, 0.5),
            "p90": percentile(text_lengths, 0.9),
            "p99": percentile(text_lengths, 0.99),
            "maximum": max(text_lengths, default=0),
            "at_least_1000_characters": sum(value >= 1000 for value in text_lengths),
            "at_least_5000_characters": sum(value >= 5000 for value in text_lengths),
        },
        "cwd_counts": dict(cwd_counts.most_common()),
        "originator_counts": dict(originator_counts.most_common()),
        "execution_context_counts": dict(execution_context_counts.most_common()),
        "direct_topic_counts_by_month": {
            month: dict(counts.most_common())
            for month, counts in sorted(direct_topic_by_month.items())
        },
        "repeated_direct_inputs": [
            {"text": text, "count": count}
            for text, count in repeated_direct_inputs.most_common(30)
            if count >= 2
        ],
        "largest_sessions": [
            {"session_id": session_id, "message_count": count}
            for session_id, count in session_counts.most_common(20)
        ],
        "method": "Local deterministic classification with explicit candidate and confidence labels; no external model or service used.",
    }
    with (args.output_dir / "deep_analysis_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
