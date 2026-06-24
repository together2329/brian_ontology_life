---
type: task
id: task_milano_pcie_doe_reg_top_axi_bridge_dcg_power_optimization
title: "PCIe DOE DCG 및 REG TOP AXI Bridge DCG 담당/Power Optimization"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: planned
priority: medium
progress: 0
tags: [milano, firenze, pcie, doe, dcg, reg_top_axi_bridge, power_optimization, synthesis, rtl]
related_projects: [project_firenze]
depends_on: ["[[task_milano_doe_configuration_request_completion_policy]]"]
confidence: high
needs_user_review: false
updated: 2026-06-25
---

# PCIe DOE / REG TOP AXI Bridge DCG — Power Optimization

> [!summary] One-liner
> PCIe **DOE DCG** 와 **REG TOP AXI Bridge DCG** 담당 + Power Optimization.
> Firenze power가 예상보다 높게 나와서 Milano에서 적극적 최적화 필요. (지금은 later task)

## Context
- Brian agreed (2026-06-15) to own PCIe DOE DCG and REG TOP AXI Bridge DCG for Milano.
- Firenze power came out higher than expected → Milano needs aggressive power optimization before signoff.
- **06-16:** this is a *later* task; near-term focus stays on SDC clean-up, lint, Disparity tracking, Firenze handler reflection.

## Scope
- PCIe DOE DCG; REG TOP AXI Bridge DCG.
- Power-optimization opportunities in clock/data gating of those blocks.
- Comparison against Firenze power findings where applicable.

## Acceptance criteria
- [ ] DCG target scope explicitly listed for PCIe DOE and REG TOP AXI Bridge.
- [ ] Power changes don't break register/AXI access, reset, timing, or lint/CDC expectations.
- [ ] Power report or review evidence captured before complete.
- [ ] Firenze high-power learnings reflected where they apply to Milano.

## Next actions
- [ ] Defer until SDC clean-up, lint, Disparity tracking, Firenze handler reflection are under control.
- [ ] Confirm exact DOE / REG TOP AXI Bridge DCG scope.
- [ ] Inspect Firenze power report to identify high-power drivers.
- [ ] Identify Milano gating candidates; classify by power impact + functional risk.
- [ ] Implement/review safest high-impact DCG changes first; collect power report deltas.

## Links
- Component: [[component_milano_pcie]]
- Presentation: [[task_milano_pcie_doe_reg_top_axi_bridge_pptx]]
- Depends on: [[task_milano_doe_configuration_request_completion_policy]]
- Index: [[index]]

## History
- **2026-06-15** — Ownership agreed.
- **2026-06-16** — Marked as a later task behind SDC/lint/Disparity/handler work.
- **2026-06-25** — Converted to OKF/Obsidian POC note.
