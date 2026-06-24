---
type: task
id: task_milano_firenze_handler_reflection_check
title: "Firenze에 적용한 handler 변경점이 Milano에 모두 반영되었는지 확인"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: high
progress: 70
tags: [milano, firenze, handler, sfr, rtl_review, cross_project_porting]
related_projects: [project_firenze]
evidence: [source_milano_conversation_20260614_firenze_handler_reflection, source_milano_conversation_20260618_gen7_phy_top_sim_pass_handler_review, source_milano_conversation_20260618_handler_eco_audit, source_milano_conversation_20260619_synth_terminal_restart_handler_sfr_first_pass]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# Firenze에 적용한 handler 변경점이 Milano에 모두 반영되었는지 확인

> [!summary] Status
> **in_progress · high priority · 70%**

## Context
- Firenze has prior handler-related implementation work.
- Milano needs a parity check so relevant Firenze handler changes are not missed before lint and DB synthesis.
- On 2026-06-19, Handler + SFR exhaustive survey reached first-pass completion.

## Scope
- Identify handler changes applied in Firenze.
- Decide which Firenze handler changes are applicable to Milano.
- Check whether each applicable change is already reflected in Milano.
- Classify each item as reflected, missing, or not_applicable.
- Include SFR-related handler/register coverage in the first-pass audit boundary.

## Expected outputs
- Firenze handler change inventory
- Milano reflection checklist
- missing or not_applicable handler change list
- Handler + SFR first-pass audit checklist
- issue list for missing critical changes

## Next actions
- [ ] Collect Firenze handler-related CLs, notes, or source file changes.
- [ ] Compare Firenze handler implementation against Milano RTL/config/register integration.
- [ ] Mark each handler delta as reflected, missing, or not_applicable.
- [ ] ECO11은 반영 완료 상태로 분류하고, ECO18은 parity 정책 미확정으로 미반영 상태를 유지하면서 추적.
- [ ] MF Handler DCG 누락 옵션은 수정 반영 완료로 기록.
- [ ] L0p Handler와 Event Handler 담당 조사자(변승현 TL님, 김성현 TL님) 결과를 기준으로 후속 반영을 정리.
- [ ] Review the first-pass Handler + SFR checklist and split remaining gaps into issues if concrete evidence exists.
- [ ] Capture Confluence/artifact refs for the first-pass audit result.
- [ ] Create Issue objects for missing Milano changes when concrete evidence exists.

## Links
- Component: [[component_milano_pcie]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

