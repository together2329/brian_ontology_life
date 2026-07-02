# Life Ontology Skeleton

This repository is a lightweight starting point for a local, ontology-backed
personal operating system.

It intentionally contains only:

- ontology schema
- agent operating instructions
- empty local record directories
- templates
- read-only validation/query helpers

It does not contain actual personal records, raw source files, identity details,
financial data, health records, or relationship history.

## Structure

```text
.codex/
  AGENTS.md              Agent operating rules
  life_ontology.yaml     Canonical schema draft
  import_rules.yaml      Local import and privacy rules
life/
  body/                  Body, health, workout records
  mind/                  Mood, reflection, identity records
  tasks/                 Career and personal task records
  finance/               Assets, decisions, spending records
  relation/              People and social interaction records
  maintenance/           Admin, errands, household records
  fun/                   Enjoyment and recovery records
  concepts/              Stable personal concepts
  entities/              Entity catalogs and alias rules
  imports/               Normalized local import indexes
  patterns/              Pattern candidates and confirmed patterns
  knowledge/             Thought threads and knowledge notes
raw_data/
  README.md              Raw data policy; raw files stay local
templates/
  *.template.yaml        Copy locally before filling with real data
tools/
  validate_life.py       Parse and reference validation
  query_life.py          Simple local search helper
```

## Quick Start

1. Copy a template from `templates/` into the relevant `life/` folder.
2. Replace placeholder IDs and values with local records.
3. Keep raw files under `raw_data/`; they are ignored by git by default.
4. Run validation before committing:

```bash
python3 tools/validate_life.py
```

Search local records:

```bash
python3 tools/query_life.py search "keyword"
python3 tools/query_life.py ids
```

## Privacy Rules

- Keep raw personal records local.
- Do not commit real identity, health, finance, relationship, or source files to
  a public repository.
- Prefer append-only records and stable IDs.
- Use `needs_user_review: true` and `confidence` for uncertain interpretations.
- Do not claim causality from correlation; preserve evidence links.

