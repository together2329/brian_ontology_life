---
type: task
id: task_milano_gen7_phy_db_synthesis
title: "GEN7 PHY를 함께 DB로 최종 합성"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: in_progress
priority: high
progress: 68
tags: [milano, gen7, phy, db_synthesis, final_integration]
depends_on: ["[[task_milano_sdc_dual_profile_synth_rerun]]", "[[task_milano_arir_precheck]]", "[[task_milano_lint_ip_rev_0_1_rerun]]", "[[task_milano_firenze_handler_reflection_check]]", "[[task_milano_mse_pf_bar0_overlap_guard]]", "[[task_milano_pcie_doe_reg_top_axi_bridge_dcg_power_optimization]]", "[[task_milano_common_module_replacement]]", "[[task_milano_standard_cell_replacement]]", "[[task_milano_cross_domain_signal_naming_cleanup]]"]
evidence: [source_milano_conversation_20260614_current_tasks, source_milano_conversation_20260614_multi_hour_progress_update, source_milano_conversation_20260618_gen7_phy_top_sim_pass_handler_review, source_milano_conversation_20260619_synth_terminal_restart_handler_sfr_first_pass, source_milano_conversation_20260619_next_monday_sdc_phy_link0_filelist_timing_plan, source_milano_conversation_20260623_ide_lint_nearly_fixed_synthesis_rerun_link0_pd_pcie, source_milano_conversation_20260623_bus_downsizing_mps_limit_wait_bus_fix]
confidence: medium
needs_user_review: true
updated: 2026-06-25
---
# GEN7 PHY를 함께 DB로 최종 합성

> [!summary] Status
> **in_progress · high priority · 68%**

## Current state
- Initial DB release was completed on 2026-06-17.
- Exact release artifact path/version and the final relationship to GEN7 PHY DB synthesis are not yet recorded.
- GEN7 PHY top-level simulation has been reported as pass.
- FPGA File List review completed with no issues.
- On 2026-06-19, synthesis was restarted after the synthesis terminal/session ended.
- Brian planned a 2026-06-22 follow-up to re-check PHY GEN7 SDC, link0 wrapper, filelist, and timing-visible issues.
- On 2026-06-23, pd_pcie synthesis was restarted alongside link0 after IDE Lint was almost fixed.
- For the PCIe TLP-to-AXI split caused by suspected bus downsizing, Brian chose temporary MPS limiting while waiting for the bus fix.

## Expected outputs
- final DB synthesis result including GEN7 PHY
- synthesis reports
- blocker list if synthesis fails

## Next actions
- [ ] Confirm whether "제7파이" means GEN7 PHY.
- [ ] Record the initial DB release artifact path/version when available.
- [ ] Confirm whether the initial DB release includes the intended GEN7 PHY scope or whether a later final DB synthesis remains.
- [ ] Review synthesis reports after the run completes.
- [ ] Record failures as Issue objects with logs/artifacts.
- [ ] Keep handler reflection evidence in one checklist before closing synthesis confidence.
- [ ] Confirm the restarted synthesis run is still connected to the intended GEN7 PHY DB synthesis scope.
- [ ] On 2026-06-22, re-check the PHY GEN7 SDC and filelist, then inspect any visible timing-related issue before closure.
- [ ] Capture the latest pd_pcie synthesis rerun report/log path and connect it to final GEN7 PHY DB synthesis confidence.
- [ ] Record the exact MPS value if the workaround is used, and rerun without the workaround after the bus fix.

## Links
- Component: [[component_milano_pcie]]
- Depends on: [[task_milano_sdc_dual_profile_synth_rerun]]
- Depends on: [[task_milano_arir_precheck]]
- Depends on: [[task_milano_lint_ip_rev_0_1_rerun]]
- Depends on: [[task_milano_firenze_handler_reflection_check]]
- Depends on: [[task_milano_mse_pf_bar0_overlap_guard]]
- Depends on: [[task_milano_pcie_doe_reg_top_axi_bridge_dcg_power_optimization]]
- Depends on: [[task_milano_common_module_replacement]]
- Depends on: [[task_milano_standard_cell_replacement]]
- Depends on: [[task_milano_cross_domain_signal_naming_cleanup]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

