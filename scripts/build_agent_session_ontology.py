#!/usr/bin/env python3
"""Build local ontology indexes from imported Codex and Claude inputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


TOPIC_TO_AREAS = {
    "agent_architecture": ["CAREER", "MIND"],
    "ontology_memory": ["MIND", "CAREER"],
    "semiconductor_ip": ["CAREER"],
    "verification_evidence": ["CAREER"],
    "orchestration_parallelism": ["CAREER"],
    "career_learning": ["CAREER", "MIND"],
    "finance_investing": ["FINANCE"],
    "body_health": ["BODY"],
    "mind_happiness": ["MIND"],
    "relations_pets": ["RELATION"],
    "travel_fun": ["FUN"],
    "maintenance_admin": ["MAINTENANCE"],
}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def write_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def unique(values):
    return list(dict.fromkeys(value for value in values if value))


def project_candidate(path: str | None) -> tuple[str | None, str | None, str]:
    if not path:
        return None, None, "low"
    lower = path.lower()
    if "finance" in lower or "포트 폴리오" in lower:
        return None, "finance_research", "high"
    if "brian_ontology_agent" in lower or "codex_ontology_test" in lower:
        return "project_ai_agent", "personal_ontology", "high"
    ai_tokens = (
        "common_ai_agent", "atlas", "ontology_ip_agent", "ip_dev", "oag_",
        "oh-my-openagent", "codex", "gajae-code", "open_code", "brian_coder",
    )
    if any(token in lower for token in ai_tokens):
        return "project_ai_agent", "ai_agent_development", "high"
    hardware_tokens = ("iverilog", "hw_ip", "root_ip", "new_bus", "mctp", "brian_hw")
    if any(token in lower for token in hardware_tokens):
        return "project_ai_agent", "semiconductor_ip_experiment", "medium"
    return None, "other_local_workspace", "low"


def areas_for(raw: dict, analysis: dict) -> list[str]:
    areas = [area for area in raw.get("area_candidates", []) if area != "UNCLASSIFIED"]
    for topic in analysis.get("topic_candidates", []):
        areas.extend(TOPIC_TO_AREAS.get(topic, []))
    return unique(areas) or ["UNCLASSIFIED"]


def load_promotions(path: Path) -> tuple[list[dict], dict[str, list[str]]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    promotions = data.get("promotions", [])
    by_source: dict[str, list[str]] = defaultdict(list)
    for promotion in promotions:
        for source_ref in promotion.get("source_refs", []):
            by_source[source_ref].append(promotion["target_ref"])
    return promotions, by_source


def semantic_rows(tool: str, raw_path: Path, analysis_path: Path, promotion_by_source: dict[str, list[str]]):
    analyses = {row["source_ref"]: row for row in read_jsonl(analysis_path)}
    for raw in read_jsonl(raw_path):
        source_ref = raw["id"]
        analysis = analyses[source_ref]
        project_path = raw.get("project")
        if tool == "codex":
            project_path = None
        project_ref, workspace_group, project_confidence = project_candidate(project_path)
        promotions = promotion_by_source.get(source_ref, [])
        yield {
            "id": source_ref,
            "object_type": "UserInputRecord",
            "source_ref": source_ref,
            "tool": tool,
            "session_ref": f"conversation_session_{tool}_{raw['session_id']}",
            "timestamp": raw["timestamp"],
            "raw_index_ref": str(raw_path),
            "raw_source_line": raw.get("source_line"),
            "project_path": project_path,
            "project_ref_candidate": project_ref,
            "project_ref_confidence": project_confidence,
            "workspace_group_candidate": workspace_group,
            "area_candidates": areas_for(raw, analysis),
            "topic_candidates": analysis.get("topic_candidates", ["unclassified"]),
            "intent_candidates": analysis.get("intent_candidates", ["unclassified"]),
            "input_origin_candidate": analysis.get("input_origin_candidate"),
            "preview": analysis.get("preview") or raw.get("preview"),
            "promotion_refs": promotions,
            "promotion_status": "promoted_evidence" if promotions else "indexed_not_promoted",
            "confidence": analysis.get("origin_confidence", raw.get("confidence", "medium")),
            "needs_user_review": analysis.get("needs_user_review", False),
        }


def build_sessions(rows: list[dict], codex_meta_path: Path, claude_sessions_path: Path) -> list[dict]:
    codex_meta = {row["session_id"]: row for row in read_jsonl(codex_meta_path)}
    claude_meta = {row["session_id"]: row for row in read_jsonl(claude_sessions_path)}
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        source_session_id = row["session_ref"].split("_", 3)[-1]
        grouped[(row["tool"], source_session_id)].append(row)

    sessions = []
    for (tool, session_id), inputs in sorted(grouped.items(), key=lambda item: min(row["timestamp"] for row in item[1])):
        inputs.sort(key=lambda row: (row["timestamp"], row["raw_source_line"] or 0))
        topic_counts = Counter(topic for row in inputs for topic in row["topic_candidates"])
        intent_counts = Counter(intent for row in inputs for intent in row["intent_candidates"])
        area_counts = Counter(area for row in inputs for area in row["area_candidates"])
        topic_candidates = [item for item, _ in topic_counts.most_common() if item != "unclassified"] or ["unclassified"]
        intent_candidates = [item for item, _ in intent_counts.most_common() if item != "unclassified"] or ["unclassified"]
        area_candidates = [item for item, _ in area_counts.most_common() if item != "UNCLASSIFIED"] or ["UNCLASSIFIED"]
        promotion_refs = unique(target for row in inputs for target in row["promotion_refs"])
        classified_count = sum(1 for row in inputs if row["topic_candidates"] != ["unclassified"])
        reasons = []
        if promotion_refs:
            reasons.append("contains_promoted_evidence")
        if len(inputs) >= 10:
            reasons.append("ten_or_more_direct_inputs")
        if classified_count >= 3:
            reasons.append("three_or_more_topic_classified_inputs")
        significance = "meaningful" if reasons else "contextual"

        if tool == "codex":
            meta = codex_meta.get(session_id, {})
            project_path = meta.get("cwd")
            raw_available = bool(meta.get("rollout_path"))
        else:
            meta = claude_meta.get(session_id, {})
            project_path = meta.get("project")
            raw_available = bool(meta.get("project_transcript_available"))
        project_ref, workspace_group, project_confidence = project_candidate(project_path)
        sessions.append({
            "id": f"conversation_session_{tool}_{session_id}",
            "object_type": "ConversationSession",
            "tool": tool,
            "source_session_id": session_id,
            "title_candidate": inputs[0]["preview"],
            "first_timestamp": inputs[0]["timestamp"],
            "last_timestamp": inputs[-1]["timestamp"],
            "direct_input_count": len(inputs),
            "first_source_ref": inputs[0]["source_ref"],
            "last_source_ref": inputs[-1]["source_ref"],
            "source_input_index_ref": inputs[0]["raw_index_ref"],
            "project_path": project_path,
            "project_ref_candidate": project_ref,
            "project_ref_confidence": project_confidence,
            "workspace_group_candidate": workspace_group,
            "area_candidates": area_candidates[:8],
            "topic_candidates": topic_candidates[:8],
            "topic_counts": dict(topic_counts.most_common()),
            "intent_candidates": intent_candidates[:6],
            "intent_counts": dict(intent_counts.most_common()),
            "significance": significance,
            "significance_reasons": reasons or ["retained_for_context_and_chronology"],
            "promoted_object_refs": promotion_refs,
            "raw_session_available": raw_available,
            "outcome_audit_status": "not_audited",
            "confidence": "high" if project_path else "medium",
            "needs_user_review": False,
        })
    return sessions


def evidence_rows(promotions: list[dict], input_lookup: dict[str, dict]) -> list[dict]:
    rows = []
    for promotion in promotions:
        for index, source_ref in enumerate(promotion.get("source_refs", []), 1):
            source = input_lookup.get(source_ref)
            if source is None:
                raise ValueError(f"Promotion source does not exist: {source_ref}")
            rows.append({
                "id": f"evidence_link_{promotion['id']}_{index:02d}",
                "object_type": "EvidenceLink",
                "source_ref": source_ref,
                "source_session_ref": source["session_ref"],
                "target_ref": promotion["target_ref"],
                "target_type": promotion["target_type"],
                "evidence_type": promotion.get("relation", "supports"),
                "summary": promotion["rationale"],
                "confidence": promotion.get("confidence", "medium"),
                "needs_user_review": promotion.get("needs_user_review", False),
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-dir", type=Path, required=True)
    parser.add_argument("--claude-dir", type=Path, required=True)
    parser.add_argument("--promotion-map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    promotions, promotion_by_source = load_promotions(args.promotion_map)
    codex_rows = list(semantic_rows(
        "codex",
        args.codex_dir / "user_message_index.jsonl",
        args.codex_dir / "input_analysis.jsonl",
        promotion_by_source,
    ))
    codex_session_meta = {
        row["session_id"]: row for row in read_jsonl(args.codex_dir / "session_metadata.jsonl")
    }
    for row in codex_rows:
        session_id = row["session_ref"].split("_", 3)[-1]
        project_path = codex_session_meta.get(session_id, {}).get("cwd")
        project_ref, workspace_group, project_confidence = project_candidate(project_path)
        row["project_path"] = project_path
        row["project_ref_candidate"] = project_ref
        row["project_ref_confidence"] = project_confidence
        row["workspace_group_candidate"] = workspace_group
    claude_rows = list(semantic_rows(
        "claude",
        args.claude_dir / "claude_user_message_index.jsonl",
        args.claude_dir / "claude_input_analysis.jsonl",
        promotion_by_source,
    ))
    rows = sorted(codex_rows + claude_rows, key=lambda row: (row["timestamp"], row["tool"], row["raw_source_line"] or 0))
    sessions = build_sessions(
        rows,
        args.codex_dir / "session_metadata.jsonl",
        args.claude_dir / "claude_session_index.jsonl",
    )
    input_lookup = {row["id"]: row for row in rows}
    links = evidence_rows(promotions, input_lookup)

    write_jsonl(args.output_dir / "user_input_semantic_index.jsonl", rows)
    write_jsonl(args.output_dir / "conversation_session_index.jsonl", sessions)
    write_jsonl(args.output_dir / "promotion_evidence_links.jsonl", links)

    by_tool_inputs = Counter(row["tool"] for row in rows)
    by_tool_sessions = Counter(row["tool"] for row in sessions)
    meaningful = Counter(row["significance"] for row in sessions)
    timestamps = [row["timestamp"] for row in rows]
    report = {
        "generated_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds"),
        "object_type": "ConversationCorpus",
        "corpus_id": "conversation_corpus_codex_claude_20250731_20260717",
        "period": f"{min(timestamps)[:10]}_to_{max(timestamps)[:10]}",
        "direct_input_count": len(rows),
        "session_count": len(sessions),
        "meaningful_session_count": meaningful["meaningful"],
        "contextual_session_count": meaningful["contextual"],
        "promotion_count": len(promotions),
        "evidence_link_count": len(links),
        "by_tool": {
            tool: {"direct_inputs": by_tool_inputs[tool], "sessions": by_tool_sessions[tool]}
            for tool in sorted(by_tool_inputs)
        },
        "outcome_audit_status": "not_audited",
        "privacy": {"processing": "local_only", "external_services_used": False},
    }
    (args.output_dir / "ontology_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
