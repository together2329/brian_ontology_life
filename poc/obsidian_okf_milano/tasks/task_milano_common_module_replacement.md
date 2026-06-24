---
type: task
id: task_milano_common_module_replacement
title: "PCI 내부용 common module을 ASIC common module로 교체"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: completed
priority: high
progress: 100
tags: [milano, rtl_cleanup, common_module, reset, sync_flop]
evidence: [source_milano_conversation_20260614_current_tasks, source_milano_conversation_20260614_multi_hour_progress_update, source_milano_conversation_20260615_common_module_replacement_completed]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# PCI 내부용 common module을 ASIC common module로 교체

> [!summary] Status
> **completed · high priority · 100%**

## Scope
- sync flip-flop common module
- reset common module
- sync 5V or similarly named synchronizer module
- other PCI-internal common module instances that should use ASIC-common implementation

## Expected outputs
- replaced common module instance list
- build/lint result after replacement
- review notes for any module that cannot be safely swapped

## Next actions
- [ ] Use later lint/build/synthesis runs to catch any integration issue if it appears.

## Links
- Component: [[component_milano_pcie]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

