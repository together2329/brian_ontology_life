---
type: task
id: task_milano_pcie_multi_pf_separated_bar0_size_mux
title: "Milano multi-PF BAR0 size 분리 (PF0 64KB / PF1~127 32KB) + default/option mux"
area: CAREER
project: project_milano
component: "[[component_milano_pcie]]"
status: todo
priority: high
progress: 0
tags: [milano, pcie, multi_pf, pf, bar0, bar_size, mux, configurable, requirement, rtl]
related_tasks: ["[[task_milano_mse_pf_bar0_overlap_guard]]"]
evidence: [source_milano_conversation_20260624_multi_pf_separated_bar0_size_mux]
confidence: high
needs_user_review: true
updated: 2026-06-25
---
# Milano multi-PF BAR0 size 분리 (PF0 64KB / PF1~127 32KB) + default/option mux

> [!summary] Status
> **todo · high priority · 0%**

## Requirement
- **scope:** BAR0 only; all other BARs keep their existing sizes.

**bar0 size map:**

| pf | size |
|---|---|
| PF0 | 64KB |
| PF1..PF127 | 32KB |
- **pf range assumption:** PF0..PF127 = 128 PFs total; confirm exact PF count and that PF127 is the last.

**selectability:**
- mechanism: muxing
- modes: default, option
- note: default and option BAR0-size configs must be selectable; which config maps to default vs option needs confirmation.

## Context
- Milano multi-PF needs per-PF separated BAR0 sizing instead of one uniform BAR0 size.
- PF0 should expose a 64KB BAR0; PF1 through PF127 should expose a 32KB BAR0.
- Only BAR0 is in scope.
- The sizing must be muxable so a default config and an option config can be selected.
- Brian wants this checked meticulously at the requirement level through implementation.
- Same PCIe component as the existing MSE-linked PF BAR0 overlap-prevention task.

## Expected outputs
- Requirement entry capturing BAR0-only scope, the PF0=64KB / PF1-127=32KB size map, and the default/option mux.
- Per-PF BAR0 size table plus address-map/alignment/overlap implication review.
- RTL/config implementation of the muxed separated BAR0 sizing.
- Requirement-level verification evidence per PF group and per mux mode.

## Failure modes to avoid
- Changing BAR sizes other than BAR0.
- Off-by-one in the PF range (PF127 missing, or PF0 wrongly grouped with PF1-127).
- Mux wired so the unintended config (default vs option) is active.
- Address-map/overlap breakage because PF0 BAR0 (64KB) is larger than PF1-127 BAR0 (32KB).

## Acceptance criteria
- [ ] PF0 BAR0 decodes as 64KB and PF1 through PF127 BAR0 decode as 32KB in the separated config.
- [ ] Only BAR0 is affected; other BARs keep their existing sizes.
- [ ] default and option configs are both selectable via the mux and produce the intended BAR0 sizing.
- [ ] Exact PF count/range and the default-vs-option mapping are confirmed with owner/requirement before closure.
- [ ] Build/lint/requirement-check evidence is captured before marking complete.

## Next actions
- [ ] Confirm PF count/range (exactly PF0-PF127 / 128 PFs?) and which mode is default vs option.
- [ ] Locate the Milano PCIe multi-PF BAR0 size config/decode path.
- [ ] Define the per-PF BAR0 size requirement table and address-map/alignment implications.
- [ ] Add the mux select for default vs option BAR0 sizing.
- [ ] Implement and verify each PF-group size and each mux mode at the requirement level.
- [ ] Record Issue/Resolution evidence after implementation and verification artifacts exist.

## Links
- Component: [[component_milano_pcie]]
- Related: [[task_milano_mse_pf_bar0_overlap_guard]]
- Index: [[index]]

## History
- **2026-06-25** — Generated from `life/tasks/milano_active_tasks.yaml`.

