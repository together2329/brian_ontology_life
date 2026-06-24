---
type: task
id: task_milano_standard_cell_replacement
title: "latch 등 standard cell로 교체할 부분 교체"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: completed
priority: high
progress: 100
tags: [milano, rtl_cleanup, standard_cell, latch, std_icg_cell, synthesis]
evidence: [source_milano_conversation_20260614_standard_cell_replacement, source_milano_conversation_20260616_latch_std_icg_cell_clear]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# latch 등 standard cell로 교체할 부분 교체

> [!summary] Status
> **completed · high priority · 100%**

## Scope
- Identify latch and other cell-like RTL/common instances that should use approved standard cells.
- Replace eligible instances with standard cell implementations.
- Leave explicit review notes for any instance that cannot be safely replaced.

## Expected outputs
- standard cell replacement candidate inventory
- replaced latch/standard-cell instance list
- exceptions or not_applicable list
- build/lint/synthesis sanity result after replacement

## Next actions
- [ ] Use later lint/build/synthesis runs to catch any residual integration issue if it appears.

## Links
- Component: [[component_milano_pcie]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

