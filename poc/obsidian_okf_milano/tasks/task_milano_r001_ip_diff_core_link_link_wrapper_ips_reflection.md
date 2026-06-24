---
type: task
id: task_milano_r001_ip_diff_core_link_link_wrapper_ips_reflection
title: "R001 IP Diff core/link/link wrapper/ips 반영 및 gray 영역 cross-check"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: todo
priority: high
progress: 0
tags: [milano, r001, ip_diff, core, link, link_wrapper, ips, gray_area, rtl_review, cross_check]
evidence: [source_milano_conversation_20260616_r001_ip_diff_gray_cross_check]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# R001 IP Diff core/link/link wrapper/ips 반영 및 gray 영역 cross-check

> [!summary] Status
> **todo · high priority · 0%**

## Context
- R001 IP Diff needs to be reflected in core, link, link wrapper, and ips.
- All gray or ambiguous areas from the diff need cross-check before the task is considered complete.
- This diff reflection should be resolved before relying on later lint, build, synthesis, or final DB confidence.

## Scope
- Collect the R001 IP Diff source or change list.
- Split diff items by core, link, link wrapper, and ips.
- Apply or confirm the required diff items in each affected block.
- Identify every gray area where applicability, ownership, or behavior is unclear.
- Cross-check all gray areas against spec, prior implementation, owner guidance, or test/build evidence.
- Record any unresolved gray area as an Issue object if concrete evidence or ownership exists.

## Expected outputs
- R001 IP Diff source reference or artifact path.
- Per-block reflection checklist for core, link, link wrapper, and ips.
- Applied diff item list.
- Gray-area cross-check checklist.
- Unresolved issue list or explicit all-clear note.
- Follow-up lint/build/synthesis sanity result when available.

## Acceptance criteria
- [ ] All R001 diff items for core, link, link wrapper, and ips are classified as applied, already_reflected, not_applicable, or unresolved.
- [ ] Every gray area is cross-checked and has a recorded decision or follow-up owner.
- [ ] No unresolved gray area is hidden before final lint/build/synthesis confidence is claimed.
- [ ] Later lint/build/synthesis results are reviewed for symptoms caused by the R001 diff reflection.

## Next actions
- [ ] Locate or record the R001 IP Diff source path or CL.
- [ ] Create a per-block checklist for core, link, link wrapper, and ips.
- [ ] Apply or verify the required diff items block by block.
- [ ] List every gray area explicitly instead of keeping it implicit.
- [ ] Cross-check each gray area against available spec, previous project behavior, owner guidance, or validation evidence.
- [ ] After reflection, run or review lint/build/synthesis sanity output and record residual issues.

## Links
- Component: [[component_milano_pcie]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

