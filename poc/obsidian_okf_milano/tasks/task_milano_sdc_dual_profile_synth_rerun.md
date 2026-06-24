---
type: task
id: task_milano_sdc_dual_profile_synth_rerun
title: "링크형 레퍼용/PDBCI용 SDC clean-up 및 3nm 합성 재시도"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: high
progress: 86
tags: [milano, synthesis, sdc, sdc_cleanup, 3nm, timing_constraint]
depends_on: ["[[task_milano_3nm_synth_env_setup]]"]
evidence: [source_milano_conversation_20260614_current_tasks, source_milano_conversation_20260614_multi_hour_progress_update, source_milano_conversation_20260614_sdc_firenze_gen7_phy_porting, source_milano_conversation_20260616_today_focus_sdc_interrupt_handler_lint, source_milano_conversation_20260616_morning_pd_pcie_sdc_error_cleanup, source_milano_conversation_20260616_link0_wrapper_synthesis_meaningful_wns, source_milano_conversation_20260617_initial_db_release_completed_rest, source_milano_conversation_20260617_focus_sdc_cleanup, source_milano_conversation_20260619_synth_terminal_restart_handler_sfr_first_pass, source_milano_conversation_20260619_next_monday_sdc_phy_link0_filelist_timing_plan, source_milano_conversation_20260622_link0_wrapper_ide_resynth_etc_area, source_milano_conversation_20260622_june_focus_area_sdc_link0_pd_pcie_synth, source_milano_conversation_20260623_synthesis_ok_ide_lint_critical, source_milano_conversation_20260623_ide_lint_fix_lint_tool_running, source_milano_conversation_20260623_ide_lint_nearly_fixed_synthesis_rerun_link0_pd_pcie, source_milano_conversation_20260623_ide_lint_critical_all_fixed]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# 링크형 레퍼용/PDBCI용 SDC clean-up 및 3nm 합성 재시도

> [!summary] Status
> **in_progress · high priority · 86%**

## Inputs
- link-type reference SDC
- PDBCI SDC
- 3nm synthesis environment

## Current state
- PDCI/PDBCI SDC and link wrapper SDC first drafts are written.
- First-pass review is done.
- Synthesis run has been launched and is expected to take time.
- New GEN7 PHY SDC was ported from the existing Firenze project pd_pcie SDC.
- Cursor was used as the main porting assistant.
- A Python script was added to support the flow after initial attempts did not work well.
- Result quality is still unknown until synthesis reports are reviewed.
- As of 2026-06-16, SDC clean-up is one of today's primary Milano focus items.
- On the morning of 2026-06-16, Brian cleaned up PD PCIe SDC errors by reading an unmapped file in farm DC.
- Link0 wrapper synthesis is now running and producing meaningful results, with Brian reporting WNS around 1.
- After completing the initial DB release on 2026-06-17, Brian reset the Milano focus back to SDC clean-up.
- On 2026-06-19, the synthesis terminal/session ended and Brian restarted synthesis.
- Brian planned a 2026-06-22 arrival pass for SDC cleanup, PHY GEN7 SDC, link0 wrapper, filelist, and visible timing issue checks.
- On 2026-06-22, link0 wrapper synthesis completed once, but Brian found that IDE was missing from that completed run.
- Brian added IDE back and started an urgent IDE-inclusive synthesis rerun.
- The IDE-missing completed result should be treated as incomplete evidence for final area/timing confidence.
- Through the end of June 2026, Brian narrowed Milano execution focus to Area/ARIR, SDC, link0 wrapper, and pd_pcie synthesis.
- On 2026-06-23, Brian checked after arriving at the company and confirmed synthesis appears to be progressing well.
- However, IDE Lint Critical is present, so the current path needs a fix and rerun before final synthesis/area confidence.
- Brian applied an IDE Lint fix and started running the lint tool; synthesis should be rerun after lint confirms the fix or remaining blockers are resolved.
- Later on 2026-06-23, IDE Lint was almost fixed and synthesis was restarted for link0 and pd_pcie.
- IDE Lint Critical violations are now fixed; link0/pd_pcie synthesis rerun report paths and area/timing results remain pending.

## Tooling notes
- Cursor was useful for SDC porting, but needed examples and iteration.
- Python scripting helped stabilize or automate parts of the SDC porting flow.
- The workflow appears to need few-shot examples for better reliability.

## Expected outputs
- SDC profile comparison result
- synthesis rerun result
- synthesis log/report artifacts

## Next actions
- [ ] Validate whether the PD PCIe SDC error cleanup is reflected in the next synthesis or lint output.
- [ ] Track link0 wrapper synthesis to completion and capture the actual WNS/TNS/report path when available.
- [ ] Wait for synthesis run completion.
- [ ] Collect synthesis logs and reports.
- [ ] Compare failures, warnings, and timing/synthesis report deltas.
- [ ] Review whether the ported GEN7 PHY SDC works after synthesis completes.
- [ ] Clean up SDC warnings, mismatches, portability issues, and profile differences before trusting final synthesis.
- [ ] Continue checking whether the PD PCIe SDC cleanup fully resolves downstream synthesis or lint symptoms.
- [ ] Capture effective few-shot examples and Python script usage as repeatable porting guidance if results are good.
- [ ] Decide which SDC profile should be the working baseline or whether both must remain.
- [ ] Use SDC clean-up as the next primary Milano workstream after the initial DB release and rest.
- [ ] Capture the restarted synthesis log/report path and restart time if the run becomes important evidence.
- [ ] If the synthesis terminal/session ends again, record it as a repeatability or environment issue.
- [ ] On 2026-06-22, run one more SDC clean-up pass and inspect PHY GEN7 SDC and link0 wrapper before trusting the synthesis/timing path.
- [ ] Let the IDE-inclusive link0 wrapper rerun finish before closing the link0 wrapper synthesis path.
- [ ] Fix the IDE Lint Critical issue before treating the IDE-inclusive synthesis path as closure evidence.
- [ ] Rerun the affected lint/synthesis flow after the IDE Lint Critical fix.
- [ ] Wait for the current lint tool rerun result.
- [ ] If lint is clean or the Critical is fixed, rerun the affected synthesis flow before area/timing closure.
- [ ] Monitor the restarted link0 and pd_pcie synthesis runs.
- [ ] Capture link0/pd_pcie synthesis report and log paths once the reruns finish.
- [ ] Capture the IDE Lint report/result path showing Critical closure.
- [ ] Compare IDE-missing versus IDE-inclusive area/timing deltas, especially the ETC area bucket.
- [ ] Use the IDE-inclusive result as the baseline for ARIR and downstream GEN7 PHY DB synthesis confidence.
- [ ] Keep adjacent tasks such as NVMe VIP setup, MSE/PF BAR0, DCG power optimization, and Port 1 requirement out of the main June path unless they directly block area/SDC/link0/pd_pcie synthesis.

## Links
- Component: [[component_milano_pcie]]
- Depends on: [[task_milano_3nm_synth_env_setup]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

