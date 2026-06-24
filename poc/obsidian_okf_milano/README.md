---
type: index
title: Milano Tasks — Obsidian + OKF POC
description: Proof-of-concept rendering of the Milano task ontology as OKF-style Markdown for Obsidian.
tags: [poc, okf, obsidian, milano]
updated: 2026-06-25
---

# Milano Tasks — Obsidian + OKF POC

This folder is a **proof of concept** for managing `BRIAN_ONTOLOGY_AGENT` on top of
**Obsidian** using a **Google OKF-style** file shape, driven by the readability pain of raw YAML.
See the thought thread `thought_thread_20260625_obsidian_okf_readable_management`.

> [!warning] This is a generated VIEW, not the source of truth
> The canonical ontology still lives in `life/tasks/milano_active_tasks.yaml`.
> These notes were generated from it on 2026-06-25 as a readability experiment.
> Only **5 representative tasks** are converted here, not all 23.

## What the POC demonstrates

| Brian's want | How it shows up here |
|---|---|
| YAML frontmatter on top | every note's `--- ... ---` block (structured/machine layer) |
| Readable Markdown body below | the `#` headings, tables, callouts under the frontmatter |
| Follow a record's history | the `## History` section in each note |
| Obsidian tasks | `- [ ]` checkboxes in **Next actions** / **Acceptance criteria** |
| Obsidian Bases | [`milano_tasks.base`](milano_tasks.base) — filterable table/card view |
| Graph via backlinks | `[[wikilinks]]` to tasks, [[component_milano_pcie]], etc. |
| git trackability | this whole folder is committed to the repo `.git` |

## Structure

```
poc/obsidian_okf_milano/
├── README.md            ← you are here
├── index.md             ← OKF index / map of content
├── log.md               ← OKF-style update log
├── milano_tasks.base    ← Obsidian Base (table + card views)
├── tasks/               ← one OKF note per task
└── entities/            ← backlink hubs (component, …)
```

## How to view in Obsidian
1. Open this `poc/obsidian_okf_milano/` folder as an Obsidian vault (or a folder inside one).
2. Open `milano_tasks.base` for the filterable task table.
3. Open Graph view to see the `[[backlink]]` connections between tasks and [[component_milano_pcie]].
4. Enable the Tasks plugin to roll up the `- [ ]` checkboxes across notes.

## Mapping back to canonical YAML
Each note's frontmatter `id` is the canonical ontology id. To regenerate, re-run the
conversion from `life/tasks/milano_active_tasks.yaml`. If this POC is accepted, the next
step is deciding whether OKF becomes the canonical store or stays a generated view layer
(see the thought thread's `open_questions`).
