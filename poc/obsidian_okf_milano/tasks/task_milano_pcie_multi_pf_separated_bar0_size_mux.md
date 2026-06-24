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
tags: [milano, pcie, multi_pf, bar0, bar_size, mux, requirement, rtl]
related_tasks: ["[[task_milano_mse_pf_bar0_overlap_guard]]"]
evidence: [source_milano_conversation_20260624_multi_pf_separated_bar0_size_mux]
confidence: high
needs_user_review: true
updated: 2026-06-25
---

# multi-PF BAR0 size 분리 (PF0 64KB / PF1~127 32KB)

> [!summary] One-liner
> multi-PF에 **BAR0 한정** per-PF 크기 분리 — **PF0 = 64KB, PF1~127 = 32KB** — 를 넣고,
> **default / option** 을 mux로 선택할 수 있게. requirement 수준에서 꼼꼼히 검증.

## Requirement
- **Scope:** BAR0 only — all other BARs keep their existing sizes.

| PF | BAR0 size |
|----|-----------|
| PF0 | **64KB** |
| PF1 .. PF127 | **32KB** |

- **PF range:** PF0..PF127 = 128 PFs total → ⚠️ exact count needs confirmation.
- **Selectability:** `muxing`, modes = `default` / `option` (which maps to which ⚠️ needs confirmation).

## Context
- multi-PF needs per-PF separated BAR0 sizing instead of one uniform size.
- Only BAR0 is in scope; muxable so a default and an option config can be selected.
- Brian wants this checked meticulously at the requirement level through implementation.
- Same PCIe block as [[task_milano_mse_pf_bar0_overlap_guard]].

## Failure modes to avoid
- Changing BAR sizes other than BAR0.
- Off-by-one in the PF range (PF127 missing, or PF0 grouped with PF1-127).
- Mux wired so the unintended config is active.
- Address-map/overlap breakage because PF0 BAR0 (64KB) > PF1-127 BAR0 (32KB).

## Acceptance criteria
- [ ] PF0 BAR0 decodes as 64KB and PF1–PF127 BAR0 decode as 32KB in the separated config.
- [ ] Only BAR0 is affected; other BARs unchanged.
- [ ] `default` and `option` both selectable via the mux with intended sizing.
- [ ] Exact PF count/range and default-vs-option mapping confirmed with owner before closure.
- [ ] Build/lint/requirement-check evidence captured before complete.

## Next actions
- [ ] Confirm PF count/range and which mode is default vs option.
- [ ] Locate the Milano PCIe multi-PF BAR0 size config/decode path.
- [ ] Define the per-PF BAR0 size requirement table + address-map/alignment implications.
- [ ] Add the mux select for default vs option BAR0 sizing.
- [ ] Implement and verify each PF-group size and each mux mode at the requirement level.
- [ ] Record Issue/Resolution evidence after implementation + verification artifacts exist.

## Links
- Component: [[component_milano_pcie]]
- Related: [[task_milano_mse_pf_bar0_overlap_guard]]
- Index: [[index]]

## History
- **2026-06-24** — Recorded as a requirement from a dawn conversation; status `todo`. PF0=64KB / PF1-127=32KB, BAR0-only, default/option mux.
- **2026-06-25** — Converted to OKF/Obsidian POC note.
