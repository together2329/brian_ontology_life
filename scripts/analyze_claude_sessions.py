#!/usr/bin/env python3
"""Index and classify Brian's local Claude history without external services."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from analyze_codex_inputs import (
    INTENT_RULES,
    TOPIC_RULES,
    classify_origin,
    matched_labels,
    percentile,
    preview,
)


CONTROL_WORDS = {
    "quit", "exit", "clear", "compact", "login", "logout", "usage", "model",
    "help", "context", "effort", "fast", "rate-limit-options",
}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if line.strip():
                yield line_no, json.loads(line)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify_claude_origin(text: str, pasted_contents) -> tuple[str, str]:
    stripped = text.strip()
    command = stripped.removeprefix("/").lower()
    if command in CONTROL_WORDS or stripped.startswith("/"):
        return "ui_command_or_control", "high"
    if pasted_contents:
        return "direct_input_with_pasted_context", "high"
    if re.search(r"\[(?:Pasted text|Image) #[0-9]+", text):
        return "direct_input_with_attachment_reference", "high"
    return classify_origin(text)


def extract_message_text(row: dict) -> str:
    message = row.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude-home", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tz = ZoneInfo("Asia/Seoul")

    history_path = args.claude_home / "history.jsonl"
    history = [(line_no, row) for line_no, row in read_jsonl(history_path)]
    session_history = defaultdict(list)
    project_counts = Counter()
    monthly_counts = Counter()
    origin_counts = Counter()
    topic_counts = Counter()
    intent_counts = Counter()
    text_lengths = []
    repeated_inputs = Counter()
    topic_by_month = defaultdict(Counter)
    intent_by_month = defaultdict(Counter)
    analyzed = []
    message_index = []

    for line_no, row in history:
        session_id = row.get("sessionId")
        text = row.get("display", "")
        pasted_contents = row.get("pastedContents") or {}
        timestamp = datetime.fromtimestamp(row["timestamp"] / 1000, tz).isoformat(timespec="seconds")
        month = timestamp[:7]
        project = row.get("project")
        origin, origin_confidence = classify_claude_origin(text, pasted_contents)
        topics = matched_labels(text, TOPIC_RULES) or ["unclassified"]
        intents = matched_labels(text, INTENT_RULES) or ["unclassified"]
        source_ref = f"claude_user_message_{session_id}_{line_no:06d}"

        message_index.append({
            "id": source_ref,
            "source_type": "chat",
            "source_name": "claude_history_jsonl",
            "source_path": str(history_path),
            "source_line": line_no,
            "session_id": session_id,
            "timestamp": timestamp,
            "project": project,
            "raw_text": text,
            "raw_pasted_contents": pasted_contents,
            "preview": preview(text),
            "authorship_note": "raw_text is Brian's direct history entry; pasted contents are attached context and not automatically Brian-authored beliefs.",
        })
        analyzed.append({
            "id": f"claude_input_analysis_{session_id}_{line_no:06d}",
            "source_ref": source_ref,
            "session_id": session_id,
            "timestamp": timestamp,
            "project": project,
            "text_length": len(text),
            "pasted_content_item_count": len(pasted_contents) if isinstance(pasted_contents, dict) else 0,
            "input_origin_candidate": origin,
            "origin_confidence": origin_confidence,
            "topic_candidates": topics,
            "intent_candidates": intents,
            "preview": preview(text),
            "needs_user_review": origin not in {"direct_user_input", "ui_command_or_control"},
        })
        session_history[session_id].append((line_no, row, timestamp))
        project_counts[project or "unknown"] += 1
        monthly_counts[month] += 1
        origin_counts[origin] += 1
        text_lengths.append(len(text))
        repeated_inputs[normalize(text)] += 1
        for topic in topics:
            topic_counts[topic] += 1
            topic_by_month[month][topic] += 1
        for intent in intents:
            intent_counts[intent] += 1
            intent_by_month[month][intent] += 1

    projects_root = args.claude_home / "projects"
    top_session_files = {path.stem: path for path in projects_root.glob("*/*.jsonl")}
    project_record_types = Counter()
    root_session_stats = defaultdict(Counter)
    root_session_meta = defaultdict(dict)
    total_project_rows = 0
    project_files = list(projects_root.rglob("*.jsonl"))
    for path in project_files:
        is_subagent = "subagents" in path.parts
        root_session_id = path.parent.parent.name if is_subagent else path.stem
        if is_subagent:
            root_session_stats[root_session_id]["subagent_file_count"] += 1
        for _, row in read_jsonl(path):
            total_project_rows += 1
            row_type = row.get("type", "unknown")
            project_record_types[row_type] += 1
            prefix = "subagent" if is_subagent else "main"
            root_session_stats[root_session_id][f"{prefix}_{row_type}_rows"] += 1
            meta = root_session_meta[root_session_id]
            for key in ("cwd", "version", "gitBranch", "entrypoint"):
                if row.get(key) is not None and key not in meta:
                    meta[key] = row.get(key)
            if row_type == "ai-title" and row.get("aiTitle") and "ai_title" not in meta:
                meta["ai_title"] = row.get("aiTitle")

    session_index = []
    for session_id, rows in sorted(session_history.items(), key=lambda item: item[1][0][2]):
        first_line, first_row, first_timestamp = rows[0]
        last_line, _, last_timestamp = rows[-1]
        session_index.append({
            "id": f"claude_session_{session_id}",
            "session_id": session_id,
            "project": first_row.get("project"),
            "first_timestamp": first_timestamp,
            "last_timestamp": last_timestamp,
            "user_input_count": len(rows),
            "first_source_ref": f"claude_user_message_{session_id}_{first_line:06d}",
            "last_source_ref": f"claude_user_message_{session_id}_{last_line:06d}",
            "project_transcript_path": str(top_session_files[session_id]) if session_id in top_session_files else None,
            "project_transcript_available": session_id in top_session_files,
            "project_transcript_stats": dict(root_session_stats.get(session_id, {})),
            "project_transcript_meta": root_session_meta.get(session_id, {}),
        })

    auxiliary_index = []
    auxiliary_type_counts = Counter()
    auxiliary_user_origin_counts = Counter()
    transcripts_root = args.claude_home / "transcripts"
    for path in sorted(transcripts_root.glob("*.jsonl")):
        type_counts = Counter()
        first_timestamp = None
        last_timestamp = None
        for _, row in read_jsonl(path):
            row_type = row.get("type", "unknown")
            type_counts[row_type] += 1
            auxiliary_type_counts[row_type] += 1
            timestamp = row.get("timestamp")
            first_timestamp = first_timestamp or timestamp
            last_timestamp = timestamp or last_timestamp
            if row_type == "user":
                text = row.get("content", "")
                normalized = normalize(text if isinstance(text, str) else str(text))
                if normalized.startswith(("<system-reminder>", "[SYSTEM REMINDER", "[analyze-mode]", "[search-mode]", "TASK:")):
                    auxiliary_user_origin_counts["delegated_or_automated_prompt"] += 1
                else:
                    auxiliary_user_origin_counts["direct_like_but_not_canonical"] += 1
        auxiliary_index.append({
            "session_id": path.stem,
            "source_path": str(path),
            "first_timestamp": first_timestamp,
            "last_timestamp": last_timestamp,
            "row_type_counts": dict(type_counts),
            "interpretation": "Auxiliary execution transcript; user-typed rows may contain system reminders or delegated prompts and are not merged into Brian's canonical direct-input history.",
        })

    for name, rows in (
        ("claude_user_message_index.jsonl", message_index),
        ("claude_input_analysis.jsonl", analyzed),
        ("claude_session_index.jsonl", session_index),
        ("claude_auxiliary_transcript_index.jsonl", auxiliary_index),
    ):
        with (args.output_dir / name).open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "generated_at": datetime.now(tz).isoformat(timespec="seconds"),
        "canonical_direct_input_source": str(history_path),
        "message_count": len(history),
        "session_count": len(session_history),
        "project_count": len(project_counts),
        "period": {
            "first": message_index[0]["timestamp"] if message_index else None,
            "last": message_index[-1]["timestamp"] if message_index else None,
        },
        "monthly_counts": dict(sorted(monthly_counts.items())),
        "project_counts": dict(project_counts.most_common()),
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
        "pasted_context_message_count": sum(bool(row.get("pastedContents")) for _, row in history),
        "topic_counts_by_month": {
            month: dict(counts.most_common()) for month, counts in sorted(topic_by_month.items())
        },
        "intent_counts_by_month": {
            month: dict(counts.most_common()) for month, counts in sorted(intent_by_month.items())
        },
        "repeated_direct_inputs": [
            {"text": text, "count": count}
            for text, count in repeated_inputs.most_common(40)
            if text and count >= 2
        ],
        "largest_sessions": [
            {
                "session_id": session_id,
                "message_count": len(rows),
                "project": rows[0][1].get("project"),
                "first_timestamp": rows[0][2],
            }
            for session_id, rows in sorted(session_history.items(), key=lambda item: -len(item[1]))[:30]
        ],
        "project_transcript_storage": {
            "jsonl_file_count": len(project_files),
            "top_level_session_file_count": len(top_session_files),
            "subagent_file_count": sum("subagents" in path.parts for path in project_files),
            "row_count": total_project_rows,
            "row_type_counts": dict(project_record_types.most_common()),
            "history_sessions_with_top_level_transcript": sum(session_id in top_session_files for session_id in session_history),
            "history_sessions_without_top_level_transcript": sum(session_id not in top_session_files for session_id in session_history),
        },
        "auxiliary_transcript_storage": {
            "file_count": len(auxiliary_index),
            "row_type_counts": dict(auxiliary_type_counts.most_common()),
            "user_origin_candidates": dict(auxiliary_user_origin_counts.most_common()),
        },
        "method": "Local deterministic indexing and candidate classification; no external model or service used.",
    }
    with (args.output_dir / "claude_analysis_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
