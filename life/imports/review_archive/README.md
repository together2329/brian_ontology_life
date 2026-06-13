# Review Archive Import

This folder contains ontology-friendly indexes generated from Brian's historical `_Review` archive.

Raw source files are preserved in the repository under:

- `raw_data/review_archive/`

Their original source roots were:

- `/Users/brian/Desktop/_Review/2018`
- `/Users/brian/Desktop/_Review/2019`
- `/Users/brian/Desktop/_Review/2020`
- `/Users/brian/Desktop/_Review/2021`
- `/Users/brian/Desktop/_Review/2023`

Generated files:

- `manifest.yaml`: source file inventory with path, role, size, and sha256.
- `summary.yaml`: aggregate import summary, area totals, metric counts, and ontology mapping.
- `normalized_records.jsonl`: row-level historical index with date, area, duration, metrics, emotion tags, source row, and raw text hash/excerpt.
- `entity_linked_records.jsonl`: row-level historical index plus semantic links to ontology objects.
- `entity_link_summary.yaml`: aggregate semantic link summary.
- `daily_summary.jsonl`: day-level area, emotion, and metric aggregates.

The generated pattern candidates are stored at:

- `life/patterns/review_archive_pattern_candidates.yaml`

Regenerate with:

```bash
python3 tools/import_review_archive.py
python3 tools/link_semantic_entities.py
```

The generated pattern candidates are not confirmed identity statements. Treat them as evidence-backed hypotheses until Brian reviews them.

Semantic links are also candidates when their source entity is marked `needs_user_review` in `life/entities/semantic_entity_catalog.yaml`.
