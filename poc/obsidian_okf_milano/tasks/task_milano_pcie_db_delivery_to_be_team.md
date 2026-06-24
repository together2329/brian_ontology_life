---
type: task
id: task_milano_pcie_db_delivery_to_be_team
title: "Milano PCIe .db 전체 생성 후 BE 팀 전달"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: todo
priority: high
progress: 0
tags: [milano, pcie, db, backend_handoff, be_team, deliverable]
evidence: [source_milano_conversation_20260624_pcie_db_delivery_to_be_team]
confidence: high
needs_user_review: true
updated: 2026-06-25
---

# Milano PCIe `.db` 전체 생성 후 BE 팀 전달

> [!summary] One-liner
> Milano PCIe `.db` 파일을 **전부 생성**해서 **BE(back-end) 팀에 전달**하는 cross-team handoff.

## Context
- Generate all Milano PCIe `.db` files and deliver them to the BE (back-end / physical design) team.
- Cross-team handoff deliverable.
- ⚠️ Exact `.db` type (Synopsys Liberty `.db`, synthesized design DB, or other) not yet confirmed.

## Acceptance criteria
- [ ] All required Milano PCIe `.db` files generated — no missing blocks or corners.
- [ ] `.db` set delivered to the BE team; handoff/receipt confirmed.
- [ ] `.db` version/scope matches the intended synthesis baseline.

## Next actions
- [ ] Confirm exactly which `.db` type, corners, and blocks the BE team needs.
- [ ] Generate the full `.db` set.
- [ ] Verify completeness (all blocks and corners present, none broken/missing).
- [ ] Deliver to the BE team and record the handoff (date, version, recipient).

## Links
- Component: [[component_milano_pcie]]
- Related synthesis work: [[task_milano_sdc_dual_profile_synth_rerun]]
- Index: [[index]]

## History
- **2026-06-24** — Recorded as a `todo` handoff task.
- **2026-06-25** — Converted to OKF/Obsidian POC note.
