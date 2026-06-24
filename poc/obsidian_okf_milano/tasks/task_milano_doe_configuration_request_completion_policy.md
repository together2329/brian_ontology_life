---
type: task
id: task_milano_doe_configuration_request_completion_policy
title: "DOE Configuration Request 완료 정책(SC/UR/RRS) 정의 및 기본값 정리"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: medium
progress: 20
tags: [milano, pcie, doe, configuration_request, completion_policy, spec_review, option]
related_tasks: ["[[task_milano_pcie_doe_reg_top_axi_bridge_dcg_power_optimization]]"]
related_projects: [project_firenze]
evidence: [source_milano_conversation_20260618_doe_completion_policy_sc_ur_rrs]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# DOE Configuration Request 완료 정책(SC/UR/RRS) 정의 및 기본값 정리

> [!summary] Status
> **in_progress · medium priority · 20%**

## Context
- {'user request': 'define DOE Configuration Request completion policy as an option set.'}
- spec re-check requested; policy alias RRS vs CRS must be clarified explicitly in notes.

## Scope
- Review the DOE Configuration Request completion policy section in Milano spec context.
- {'Set policy options explicitly': 'SC, UR, RRS(CRS).'}
- Keep default policy as RRS.
- Keep implementation/spec notes aligned to the selected default behavior.

## Expected outputs
- completion policy option list written as SC, UR, RRS(CRS) in Milano task/spec notes
- default policy fixed to RRS
- spec re-check notes (including naming/alias RRS vs CRS)
- risk/impact note for SC/UR/RRS(CRS) behavior and compatibility

## Acceptance criteria
- [ ] SC, UR, and RRS(CRS) are explicitly represented as selectable options.
- [ ] Default is explicitly defined as RRS and documented in the task context.
- [ ] DOE Configuration Request spec text is reviewed again before closing this task.
- [ ] Any ambiguity between RRS and CRS naming is resolved and recorded.

## Next actions
- [ ] Re-open Milano DOE spec section and re-check completion-policy wording.
- [ ] {'Create/confirm enum definition for request_policy': 'SC, UR, RRS(CRS).'}
- [ ] Apply RRS as the default value in the Milano task record and related notes.
- [ ] Record follow-up risks or cross-check items before handoff to DOE/CLK/DCG work.

## Links
- Component: [[component_milano_pcie]]
- Related: [[task_milano_pcie_doe_reg_top_axi_bridge_dcg_power_optimization]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

