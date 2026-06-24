---
type: task
id: task_milano_link0_wrapper_etc_area_analysis
title: "link0 wrapper 합성 리포트 ETC Area breakdown 분석"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: high
progress: 20
tags: [milano, link0_wrapper, synthesis, area, arir, etc_bucket, ide, report_analysis]
related_tasks: ["[[task_milano_sdc_dual_profile_synth_rerun]]", "[[task_milano_arir_precheck]]", "[[task_milano_gen7_phy_db_synthesis]]"]
evidence: [source_milano_conversation_20260622_link0_wrapper_ide_resynth_etc_area, source_milano_conversation_20260623_ide_lint_nearly_fixed_synthesis_rerun_link0_pd_pcie, source_milano_conversation_20260623_ide_lint_critical_all_fixed]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# link0 wrapper 합성 리포트 ETC Area breakdown 분석

> [!summary] Status
> **in_progress · high priority · 20%**

## Context
- Link0 wrapper synthesis completed once on 2026-06-22.
- Brian found that IDE was missing from the completed synthesis scope.
- IDE was added back and urgent resynthesis is running.
- On 2026-06-23, IDE Lint was almost fixed and link0 synthesis was restarted alongside pd_pcie.
- IDE Lint Critical violations are now fixed, so the remaining link0 blocker is report availability and ETC/area analysis.
- ETC area must be analyzed before the area result is trusted for ARIR or final synthesis judgment.

## Scope
- Use the IDE-inclusive rerun as the trusted baseline once it finishes.
- Keep the IDE-missing completed run only as a comparison point, not as final closure evidence.
- Break down the ETC area bucket into concrete contributors wherever the synthesis report allows.
- Classify ETC contributors as expected IDE area, wrapper miscellaneous logic, ungrouped or unmapped hierarchy, library/report categorization, constraint/setup artifact, or unresolved.
- Check whether any large ETC contributor indicates filelist/hierarchy/ungrouping/setup mistakes rather than real logic.

## Expected outputs
- ETC area contributor list with top instances or categories.
- IDE-missing versus IDE-inclusive area delta.
- Classification of expected versus suspicious ETC area.
- Follow-up issue list if ETC contains abnormal or unexplained growth.

## Acceptance criteria
- [ ] IDE-inclusive synthesis report is reviewed before final area confidence is claimed.
- [ ] ETC area is not left as a single opaque bucket if the report can expose lower-level contributors.
- [ ] Expected IDE area growth is separated from unexplained ETC growth.
- [ ] Any suspicious ETC contributor has an owner, next action, or issue record.

## Next actions
- [ ] Let the IDE-inclusive rerun finish.
- [ ] Capture the latest link0 synthesis rerun report/log path separately from the older IDE-missing and IDE-inclusive attempts.
- [ ] Capture report paths for both the completed IDE-missing run and the IDE-inclusive rerun.
- [ ] Extract top-level area and instance count first, then drill down into the ETC bucket.
- [ ] Compare IDE-missing and IDE-inclusive reports to isolate expected IDE area delta.
- [ ] If ETC remains too large or opaque, inspect hierarchy/ungrouping/report grouping and filelist inclusion before assuming it is real logic area.

## Links
- Component: [[component_milano_pcie]]
- Related: [[task_milano_sdc_dual_profile_synth_rerun]]
- Related: [[task_milano_arir_precheck]]
- Related: [[task_milano_gen7_phy_db_synthesis]]
- Issue: [[issue_milano_link0_wrapper_ide_missing_from_synthesis_20260622]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

