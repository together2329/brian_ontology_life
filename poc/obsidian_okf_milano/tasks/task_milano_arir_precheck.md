---
type: task
id: task_milano_arir_precheck
title: "합성 재시도 결과로 ARIR area/instance count 사전 확인"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: high
progress: 20
tags: [milano, synthesis, arir, area, instance_count, precheck]
depends_on: ["[[task_milano_sdc_dual_profile_synth_rerun]]", "[[task_milano_link0_wrapper_etc_area_analysis]]"]
evidence: [source_milano_conversation_20260614_current_tasks, source_milano_conversation_20260614_arir_definition, source_milano_conversation_20260614_multi_hour_progress_update, source_milano_conversation_20260619_synth_terminal_restart_handler_sfr_first_pass, source_milano_conversation_20260622_link0_wrapper_ide_resynth_etc_area]
confidence: medium
needs_user_review: false
updated: 2026-06-25
---
# 합성 재시도 결과로 ARIR area/instance count 사전 확인

> [!summary] Status
> **in_progress · high priority · 20%**

## Expected outputs
- area report or area summary from synthesis rerun
- instance count report or instance summary from synthesis rerun
- ETC area bucket breakdown for link0 wrapper synthesis
- IDE-missing versus IDE-inclusive area/timing delta summary
- risk list before final DB synthesis

## Next actions
- [ ] Wait for the IDE-inclusive link0 wrapper synthesis rerun to complete.
- [ ] Collect area results from the synthesis rerun.
- [ ] Collect instance count results from the synthesis rerun.
- [ ] Break down the ETC area bucket and identify whether it is real IDE logic, wrapper miscellaneous logic, unmapped hierarchy, library/cell grouping, or report categorization noise.
- [ ] Compare the completed IDE-missing run against the IDE-inclusive rerun so the expected IDE area delta is not mistaken for an unexplained ETC increase.
- [ ] Compare area and instance count against expected baseline or prior run if available.
- [ ] Identify early blockers before final DB synthesis.
- [ ] Convert any blocker into Issue objects when concrete failure evidence exists.

## Links
- Component: [[component_milano_pcie]]
- Depends on: [[task_milano_sdc_dual_profile_synth_rerun]]
- Depends on: [[task_milano_link0_wrapper_etc_area_analysis]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

