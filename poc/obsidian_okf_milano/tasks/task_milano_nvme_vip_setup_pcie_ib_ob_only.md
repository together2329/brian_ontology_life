---
type: task
id: task_milano_nvme_vip_setup_pcie_ib_ob_only
title: "NVMe VIP setup: PCIe IB/OB만 enable하고 나머지 disable"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: todo
priority: high
progress: 0
tags: [milano, nvme, vip, simulation_setup, pcie, ib, ob, disable_unused, configuration]
related_tasks: ["[[task_milano_gen7_phy_db_synthesis]]", "[[task_milano_disparity_error_injection_debug_followup]]"]
evidence: [source_milano_conversation_20260619_nvme_vip_setup_ib_ob_only]
confidence: high
needs_user_review: false
updated: 2026-06-25
---
# NVMe VIP setup: PCIe IB/OB만 enable하고 나머지 disable

> [!summary] Status
> **todo · high priority · 0%**

## Context
- Milano needs an NVMe VIP setup task.
- The setup should open/enable only PCIe IB and PCIe OB.
- All other paths, features, or ports outside PCIe IB/OB should be disabled for this setup.
- "Milnan" in the source text is interpreted as Milano.
- {'This task is the first Advanced Operational Ontology pilot slice for Milano': 'semantic task/config target, kinetic setup action, dynamic intended state, and feedback loop.'}

## Scope
- Identify the NVMe VIP configuration surface for Milano.
- Enable or open PCIe IB.
- Enable or open PCIe OB.
- Disable every other non-required path, feature, or port for the NVMe VIP setup.
- Check that the final setup does not accidentally expose unrelated PCIe/NVMe paths.

## Expected outputs
- NVMe VIP setup configuration note or patch.
- Explicit enable list containing only PCIe IB and PCIe OB.
- Explicit disable list for all non-IB/OB paths/features/ports.
- Sanity result showing the VIP setup uses only the intended PCIe IB/OB paths.

## Acceptance criteria
- [ ] PCIe IB is enabled/open.
- [ ] PCIe OB is enabled/open.
- [ ] Non-IB/OB paths/features/ports are disabled.
- [ ] Any exception to the "IB/OB only" rule is documented with a reason before the task is considered complete.
- [ ] The setup is linked to later simulation/debug evidence when available.

## Next actions
- [ ] Locate the Milano NVMe VIP setup/config entry point.
- [ ] Build an enable/disable checklist before changing configuration.
- [ ] Apply or review the PCIe IB/OB-only configuration.
- [ ] Run a setup sanity check or compile/elaboration check if available.
- [ ] Record concrete config paths, logs, or issue refs after execution.

## Links
- Component: [[component_milano_pcie]]
- Related: [[task_milano_gen7_phy_db_synthesis]]
- Related: [[task_milano_disparity_error_injection_debug_followup]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

