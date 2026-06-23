# Project Instructions

This repository is Brian's local life ontology profile. It is operated by AI coding
agents — both **Codex** (entry point: `AGENTS.md`) and **Claude Code** (entry point:
this file). Both share the same operating brain in `.codex/`, so behavior stays
identical no matter which agent is running.

## Operating brain

Read the shared operating model first. It is imported below so it is always in context:

@.codex/AGENTS.md

The canonical files (all under `.codex/`):

- `life_ontology.yaml`: object / link / action / query type definitions (v1).
- `identity_profile.yaml`: identity, family/project context, patterns, operating rules.
- `import_rules.yaml`: how to absorb past records without losing raw data.

`life/` holds the living records (BODY, MIND, CAREER, FINANCE, RELATION, MAINTENANCE,
FUN); `raw_data/` preserves original sources verbatim; `tools/` has the Python
import/query scripts.

## Repository rules

- Treat `.codex/life_ontology.yaml` as the canonical v1 ontology draft.
- Keep the setup lightweight. Do not scaffold an app, database, or service unless Brian asks.
- Keep personal records local. Do not send private life records to external services unless Brian explicitly asks.
- Prefer small, reviewable edits and commit meaningful checkpoints to Git.
- Reply in Korean.
