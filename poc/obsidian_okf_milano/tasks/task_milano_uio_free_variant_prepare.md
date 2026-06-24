---
type: task
id: task_milano_uio_free_variant_prepare
title: "UIO 없는 Milano variant 준비"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: medium
progress: 15
tags: [milano, uio, feature_pruning, no_uio, variant, rtl_cleanup, synthesis, area]
related_tasks: ["[[task_milano_sdc_dual_profile_synth_rerun]]", "[[task_milano_arir_precheck]]", "[[task_milano_lint_ip_rev_0_1_rerun]]", "[[task_milano_link0_wrapper_etc_area_analysis]]", "[[task_milano_gen7_phy_db_synthesis]]"]
evidence: [source_milano_conversation_20260623_uio_free_variant_prepare]
confidence: medium
needs_user_review: false
updated: 2026-06-25
---
# UIO 없는 Milano variant 준비

> [!summary] Status
> **in_progress · medium priority · 15%**

## Context
- Brian is preparing a version without UIO.
- The intent is to remove a feature that may not be used before it adds unnecessary integration, lint, synthesis, or area burden.
- The exact UIO feature scope and final requirement status are not yet recorded.

## Scope
- Identify the UIO-related feature/interface/hierarchy/configuration surface.
- Prepare or track a no-UIO variant separately from the current synthesis baseline.
- Keep the removal reversible or clearly reviewable until UIO is confirmed unused.
- Compare lint, synthesis, timing, and area impact if the variant reaches a runnable state.

## Expected outputs
- UIO dependency or hierarchy checklist.
- no-UIO patch/branch/config note or equivalent artifact path.
- Lint/build/synthesis comparison against the baseline when available.
- Decision note if UIO is finally removed from the active Milano path.

## Acceptance criteria
- [ ] UIO scope is clear enough that unrelated logic is not removed accidentally.
- [ ] Any compile/lint fallout from removing UIO is classified as expected cleanup, real dependency, or blocker.
- [ ] Area/timing impact is compared before using the no-UIO version as the trusted synthesis baseline.
- [ ] The no-UIO variant is not treated as final product behavior until the requirement/owner confirms UIO is unused or optional.

## Next actions
- [ ] {'List UIO touch points': 'files, modules, configs, ports, constraints, and testbench assumptions.'}
- [ ] Keep a baseline versus no-UIO comparison path so area/timing/lint deltas are explainable.
- [ ] Capture the no-UIO artifact path and any compile/lint/synthesis report path once available.
- [ ] Confirm whether UIO is truly unused before finalizing feature removal.

## Links
- Component: [[component_milano_pcie]]
- Related: [[task_milano_sdc_dual_profile_synth_rerun]]
- Related: [[task_milano_arir_precheck]]
- Related: [[task_milano_lint_ip_rev_0_1_rerun]]
- Related: [[task_milano_link0_wrapper_etc_area_analysis]]
- Related: [[task_milano_gen7_phy_db_synthesis]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

