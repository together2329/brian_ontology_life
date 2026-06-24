---
type: task
id: task_milano_mse_pf_bar0_overlap_guard
title: "MSE 연동 PF BAR0 address overlap 방지 기능 추가"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: todo
priority: high
progress: 0
tags: [milano, pcie, pf, bar0, mse, address_overlap, rtl, regression]
related_projects: [project_firenze]
evidence: [source_milano_conversation_20260615_mse_pf_bar0_overlap_guard]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# MSE 연동 PF BAR0 address overlap 방지 기능 추가

> [!summary] Status
> **todo · high priority · 0%**

## Context
- Milano needs an MSE-linked guard to prevent PF BAR0 address overlap.
- A prior Firenze attempt failed because BAR0 became unusable when MSE was 0.
- Milano implementation must avoid repeating the Firenze failure while still preventing real overlap.

## Expected outputs
- MSE/PF BAR0 behavior table for MSE=0 and MSE=1 cases
- RTL or spec patch implementing PF BAR0 overlap prevention
- Review note explaining how the Firenze MSE=0 failure mode is avoided
- Targeted regression or checklist result for MSE=0 and MSE=1 behavior

## Failure modes to avoid
- BAR0 becomes unusable solely because MSE is 0.
- Disabled or inactive BAR state is incorrectly treated as an address overlap.
- Overlap prevention changes BAR0 enable/reset semantics without an explicit requirement.

## Acceptance criteria
- [ ] PF BAR0 address overlap is prevented in the enabled/active scenarios defined by the requirement.
- [ ] MSE=0 case does not reproduce the Firenze failure where BAR0 cannot be used.
- [ ] MSE=0 and MSE=1 behavior are explicitly documented and reviewed before implementation is considered done.
- [ ] Build, lint, regression, or targeted test evidence is captured before marking the task complete.

## Next actions
- [ ] Identify Milano PF BAR0 decode/config path and the exact MSE source signal.
- [ ] Find the Firenze implementation attempt or notes that caused the MSE=0 BAR0 issue.
- [ ] Define the behavior table for MSE=0/1 and overlap/non-overlap cases before coding.
- [ ] Implement the overlap guard with narrow conditions so MSE=0 does not globally break BAR0 behavior.
- [ ] Add targeted checks for the prior Firenze failure mode.
- [ ] Record Issue/Resolution evidence after implementation and validation artifacts exist.

## Links
- Component: [[component_milano_pcie]]
- Issue: [[issue_firenze_mse0_pf_bar0_disabled]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

