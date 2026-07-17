#!/usr/bin/env python3
"""Quantify direction-setting signals in Brian's local conversation ontology."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


FAMILIES = {
    "memory_and_context": ["memory", "기억", "context", "컨텍스트", "compression", "압축", "session", "세션"],
    "evidence_and_closure": ["evidence", "증거", "contract", "obligation", "validator", "validation", "검증", "완료", "closure"],
    "ontology_decision_action": ["ontology", "온톨로지", "decision", "의사결정", "action", "실행", "operational"],
    "real_environment": ["실제 사용", "실제 user", "actual user", "real environment", "runtime", "ui", "user flow"],
    "simplicity_and_pruning": ["복잡", "간단", "단순", "lightweight", "simple", "over-engineer", "overengineer", "제거", "없애"],
    "parallelism_and_boundaries": ["parallel", "병렬", "subagent", "wavefront", "ownership", "dependency", "의존", "orchestrat"],
    "full_power_and_personal_os": ["full power", "personal ontology", "내 온톨로지", "life ontology", "삶", "행복", "자산", "운동", "투자 원칙"],
    "git_checkpoint": ["git commit", "git push", "commit push", "commit and push", "커밋", "체크포인트"],
}

WORK_TOPICS = {
    "agent_architecture", "semiconductor_ip", "verification_evidence",
    "orchestration_parallelism", "career_learning",
}
LIFE_TOPICS = {
    "finance_investing", "body_health", "mind_happiness", "relations_pets",
    "travel_fun", "maintenance_admin",
}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * fraction))
    return ordered[index]


def term_match(text: str, term: str) -> bool:
    if term.isascii() and re.fullmatch(r"[a-z0-9_-]+", term):
        return re.search(rf"(?<![a-z0-9_-]){re.escape(term)}(?![a-z0-9_-])", text) is not None
    return term in text


def representative(rows: list[dict], limit: int = 4) -> list[dict]:
    if len(rows) <= limit:
        selected = rows
    else:
        points = [0, len(rows) // 3, (2 * len(rows)) // 3, len(rows) - 1]
        selected = [rows[index] for index in points]
    return [
        {"source_ref": row["source_ref"], "timestamp": row["timestamp"], "preview": row["preview"]}
        for row in selected
    ]


def follow_rate(rows_by_session: dict[str, list[dict]], source_intent: str, targets: set[str], window: int = 5) -> dict:
    eligible = 0
    followed = 0
    for rows in rows_by_session.values():
        for index, row in enumerate(rows):
            if source_intent not in row["intent_candidates"]:
                continue
            eligible += 1
            later = rows[index + 1:index + 1 + window]
            if any(targets.intersection(candidate["intent_candidates"]) for candidate in later):
                followed += 1
    return {
        "source_turns": eligible,
        "followed_within_five_turns": followed,
        "rate_percent": round(100 * followed / eligible, 1) if eligible else 0.0,
        "interpretation_boundary": "Sequence proximity indicates interaction flow, not causal conversion or successful completion.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--semantic-index", type=Path, required=True)
    parser.add_argument("--session-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = list(read_jsonl(args.semantic_index))
    sessions = list(read_jsonl(args.session_index))
    rows_by_session: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        rows_by_session[row["session_ref"]].append(row)
    for session_rows in rows_by_session.values():
        session_rows.sort(key=lambda row: (row["timestamp"], row.get("raw_source_line") or 0))

    session_lengths = [session["direct_input_count"] for session in sessions]
    long_sessions = [session for session in sessions if session["direct_input_count"] >= 100]
    top_sessions = sorted(sessions, key=lambda row: row["direct_input_count"], reverse=True)[:10]

    topic_inputs = Counter()
    topic_sessions: dict[str, set[str]] = defaultdict(set)
    topic_by_month: dict[str, Counter] = defaultdict(Counter)
    intent_inputs = Counter()
    origin_inputs = Counter()
    for row in rows:
        month = row["timestamp"][:7]
        for topic in row["topic_candidates"]:
            topic_inputs[topic] += 1
            topic_sessions[topic].add(row["session_ref"])
            topic_by_month[month][topic] += 1
        for intent in row["intent_candidates"]:
            intent_inputs[intent] += 1
        origin_inputs[row["input_origin_candidate"]] += 1

    family_analysis = {}
    analyzable_origins = {"direct_user_input", "direct_or_composed_long_input"}
    for family, terms in FAMILIES.items():
        matched = []
        for row in rows:
            if row["input_origin_candidate"] not in analyzable_origins:
                continue
            text = row["preview"].lower()
            if any(term_match(text, term) for term in terms):
                matched.append(row)
        matched.sort(key=lambda row: row["timestamp"])
        family_analysis[family] = {
            "direct_input_mentions": len(matched),
            "unique_sessions": len({row["session_ref"] for row in matched}),
            "first_timestamp": matched[0]["timestamp"] if matched else None,
            "last_timestamp": matched[-1]["timestamp"] if matched else None,
            "representative_evidence": representative(matched),
            "caution": "Keyword-family counts are directional signals and can include context-dependent uses.",
        }

    cross_domain = Counter()
    tension_sessions = {
        "autonomy_and_assurance": [],
        "memory_and_action": [],
        "work_and_life": [],
        "breadth_three_or_more_topics": [],
    }
    for session in sessions:
        topics = set(session["topic_candidates"])
        if topics & WORK_TOPICS:
            cross_domain["work_topic_sessions"] += 1
        if topics & LIFE_TOPICS:
            cross_domain["life_topic_sessions"] += 1
        if topics & WORK_TOPICS and topics & LIFE_TOPICS:
            cross_domain["work_and_life_sessions"] += 1
            tension_sessions["work_and_life"].append(session["id"])
        if "agent_architecture" in topics and "verification_evidence" in topics:
            tension_sessions["autonomy_and_assurance"].append(session["id"])
        if "ontology_memory" in topics and ({"action_request", "decision_or_approval"} & set(session["intent_candidates"])):
            tension_sessions["memory_and_action"].append(session["id"])
        classified_topics = topics - {"unclassified"}
        if len(classified_topics) >= 3:
            tension_sessions["breadth_three_or_more_topics"].append(session["id"])

    monthly = {}
    for month, counts in sorted(topic_by_month.items()):
        classified = sum(value for key, value in counts.items() if key != "unclassified")
        monthly[month] = {
            "classified_topic_mentions": classified,
            "top_topics": [{"topic": topic, "mentions": count} for topic, count in counts.most_common(5)],
        }

    report = {
        "generated_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds"),
        "status": "direction_signals_not_outcome_proof",
        "scope": {
            "direct_input_records": len(rows),
            "sessions": len(sessions),
            "period": f"{rows[0]['timestamp'][:10]}_to_{rows[-1]['timestamp'][:10]}",
            "privacy": "local_only",
        },
        "attention_concentration": {
            "march_through_june_inputs": sum(1 for row in rows if "2026-03" <= row["timestamp"][:7] <= "2026-06"),
            "march_through_june_share_percent": round(100 * sum(1 for row in rows if "2026-03" <= row["timestamp"][:7] <= "2026-06") / len(rows), 1),
            "top_ten_sessions_input_count": sum(session["direct_input_count"] for session in top_sessions),
            "top_ten_sessions_share_percent": round(100 * sum(session["direct_input_count"] for session in top_sessions) / len(rows), 1),
            "top_sessions": [
                {
                    "session_ref": session["id"],
                    "tool": session["tool"],
                    "title_candidate": session["title_candidate"],
                    "direct_input_count": session["direct_input_count"],
                    "topic_candidates": session["topic_candidates"],
                }
                for session in top_sessions
            ],
        },
        "session_depth": {
            "median_inputs": percentile(session_lengths, 0.5),
            "p75_inputs": percentile(session_lengths, 0.75),
            "p90_inputs": percentile(session_lengths, 0.9),
            "maximum_inputs": max(session_lengths),
            "sessions_at_least_100_inputs": len(long_sessions),
            "inputs_in_sessions_at_least_100": sum(session["direct_input_count"] for session in long_sessions),
            "share_of_inputs_in_sessions_at_least_100_percent": round(100 * sum(session["direct_input_count"] for session in long_sessions) / len(rows), 1),
        },
        "interaction_flow": {
            "exploration_to_action_or_decision": follow_rate(rows_by_session, "question_or_exploration", {"action_request", "decision_or_approval"}),
            "action_request_to_feedback_or_status": follow_rate(rows_by_session, "action_request", {"feedback_or_correction", "status_or_result_check"}),
            "decision_to_action_request": follow_rate(rows_by_session, "decision_or_approval", {"action_request"}),
        },
        "topic_reach": {
            topic: {"input_mentions": count, "sessions": len(topic_sessions[topic])}
            for topic, count in topic_inputs.most_common()
        },
        "intent_mentions": dict(intent_inputs.most_common()),
        "origin_counts": dict(origin_inputs.most_common()),
        "cross_domain_session_counts": dict(cross_domain),
        "tension_session_counts": {name: len(values) for name, values in tension_sessions.items()},
        "tension_session_examples": {name: values[:8] for name, values in tension_sessions.items()},
        "keyword_family_signals": family_analysis,
        "monthly_topic_shape": monthly,
        "limitations": [
            "Topic, intent, origin, and keyword-family labels are deterministic candidates.",
            "Input sequences show Brian's requests and corrections, not whether assistant or tool outcomes succeeded.",
            "A high mention count can reflect a persistent problem, a successful focus, or copied context; interpretation requires source review.",
            "Technical-heavy conversation volume must not be interpreted as life-domain importance.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
