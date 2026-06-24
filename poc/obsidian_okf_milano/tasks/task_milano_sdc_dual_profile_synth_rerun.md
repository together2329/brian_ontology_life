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
confidence: high
needs_user_review: false
updated: 2026-06-25
---

# SDC clean-up + 3nm 합성 재시도 (link-ref / PDBCI)

> [!summary] One-liner
> link형 reference / PDBCI SDC를 정리하고 3nm 합성을 재시도. **86%** — IDE Lint Critical은
> 다 잡았고 link0/pd_pcie synthesis rerun report·area/timing 결과 대기 중.

## Inputs
- link-type reference SDC, PDBCI SDC, 3nm synthesis environment.
- Depends on [[task_milano_3nm_synth_env_setup]].

## Current state (latest first)
- **IDE Lint Critical violations are now fixed**; link0/pd_pcie synthesis rerun report paths and area/timing results remain pending.
- GEN7 PHY SDC was ported from the Firenze pd_pcie SDC (Cursor-assisted + a Python helper script).
- IDE-missing completed run on 06-22 is **incomplete evidence**; IDE-inclusive rerun is the trusted baseline.
- June focus narrowed to **Area/ARIR, SDC, link0 wrapper, pd_pcie synthesis**.

## History (timeline)
- **06-14** — SDC clean-up identified as a current task; GEN7 PHY SDC ported from Firenze.
- **06-16** — Cleaned PD PCIe SDC errors (unmapped file in farm DC); link0 wrapper synth meaningful, WNS ~1.
- **06-17** — Initial DB release done → reset focus back to SDC cleanup.
- **06-19** — Synth session ended; restarted synthesis.
- **06-22** — link0 wrapper synth completed once but **IDE was missing**; added IDE, started urgent rerun.
- **06-23** — IDE Lint Critical found → fixed → restarted link0/pd_pcie synth; **all Critical fixed**, reports pending.

## Next actions (condensed)
- [ ] Let the IDE-inclusive link0/pd_pcie reruns finish; capture report + log paths.
- [ ] Capture the IDE Lint report path showing Critical closure.
- [ ] Compare IDE-missing vs IDE-inclusive area/timing deltas (esp. ETC area bucket).
- [ ] Use the IDE-inclusive result as baseline for [[task_milano_pcie_db_delivery_to_be_team|GEN7 PHY DB]] and ARIR confidence.
- [ ] Decide which SDC profile is the working baseline (or keep both).
- [ ] Capture few-shot examples + Python script usage as repeatable SDC-porting guidance if results are good.

## Tooling notes
- Cursor useful for SDC porting but needed examples + iteration; Python scripting stabilized the flow; workflow benefits from few-shot examples.

## Links
- Component: [[component_milano_pcie]]
- Depends on: [[task_milano_3nm_synth_env_setup]]
- Feeds: [[task_milano_pcie_db_delivery_to_be_team]]
- Index: [[index]]

## History (record)
- **2026-06-25** — Converted to OKF/Obsidian POC note; the long YAML `current_state`/`next_actions`
  arrays were folded into a readable timeline (this is the readability win the POC targets).
