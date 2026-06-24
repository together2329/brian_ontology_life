---
type: task
id: task_milano_lint_ip_rev_0_1_rerun
title: "신규 IP revision 0.1 반영 후 lint 재확인"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: high
progress: 95
tags: [milano, lint, ip_revision, rev_0_1]
evidence: [source_milano_conversation_20260614_current_tasks, source_milano_conversation_20260616_today_focus_sdc_interrupt_handler_lint, source_milano_conversation_20260616_gen7_merge_lint_complete_disparity_jira, source_milano_conversation_20260616_r001_ip_diff_gray_cross_check, source_milano_conversation_20260616_late_night_tired_missed_brian_owned_followups, source_milano_conversation_20260616_2238_compile_pass_lint_sim_running_release_tomorrow, source_milano_conversation_20260623_synthesis_ok_ide_lint_critical, source_milano_conversation_20260623_ide_lint_fix_lint_tool_running, source_milano_conversation_20260623_ide_lint_nearly_fixed_synthesis_rerun_link0_pd_pcie, source_milano_conversation_20260623_ide_lint_critical_all_fixed]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# 신규 IP revision 0.1 반영 후 lint 재확인

> [!summary] Status
> **in_progress · high priority · 95%**

## Context
- Previous lint cleanup was already performed.
- New IP revision 0.1 must be reflected before trusting lint status.
- After GEN7 merge, 박길봉 TL님 reported that the lint work was completed.
- Brian is doing final confirmation before the lint task is marked complete.
- R001 IP Diff reflection for core, link, link wrapper, and ips may need to be included before final lint confidence is claimed.
- Brian later noticed possible missed Brian-owned follow-ups around common module and related work; this audit should be considered before closing lint confidence.
- At 22:38 on 2026-06-16, compile passed and lint was running; Brian plans to review lint on 2026-06-17 before release.
- On 2026-06-23, an IDE Lint Critical issue was found while synthesis itself appeared to be progressing well.
- The lint task is reopened as a blocker for the current synthesis closure path until the Critical issue is fixed and rerun.
- Brian applied a fix for the IDE Lint issue and is running the lint tool again; result is pending.
- IDE Lint is now almost fixed; link0 and pd_pcie synthesis reruns have started before final lint closure is recorded, so lint closure remains near-fixed but pending confirmation.
- IDE Lint Critical violations are now fixed; report/result path and any residual non-critical items are not yet recorded.

## Expected outputs
- lint rerun report after IP rev 0.1
- new violations list
- waived or fixed issue list

## Next actions
- [ ] Let the current lint run finish.
- [ ] Review lint result on 2026-06-17 before release.
- [ ] Complete Brian's final lint confirmation after 박길봉 TL님의 completion report.
- [ ] Check whether R001 IP Diff reflection and gray-area cross-check affect the final lint confirmation.
- [ ] Check whether the Brian-owned missed-followup audit exposes any common module or integration item that affects lint closure.
- [ ] Capture lint report path, result summary, and remaining violation or waiver status.
- [ ] If clean, mark the lint task completed.
- [ ] If residual issues remain, classify them into fix, waive, or owner handoff.
- [ ] Fix the IDE Lint Critical issue.
- [ ] Rerun IDE Lint after the fix and capture the result summary.
- [ ] Rerun the affected synthesis path if the fix changes RTL, filelist, constraints, or IDE integration scope.
- [ ] Wait for the current lint tool rerun result.
- [ ] If clean, record the lint result and move to affected synthesis rerun.
- [ ] If residual lint issues remain, classify and fix before synthesis rerun.
- [ ] Capture the IDE Lint report/result path showing Critical closure.
- [ ] Classify any remaining non-critical lint items as fix, waive, defer, or owner handoff.

## Links
- Component: [[component_milano_pcie]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

