# BKE Gratitude Diary 2019

Ontology import for Brian's 2019 BKE Group gratitude diary campaign document.

Raw source stays under `raw_data/documents/bke_gratitude_campaign_2019/`.

Generated files:

- `manifest.yaml`: source and parser metadata.
- `normalized_entries.jsonl`: one `GratitudeEntry` per dated gratitude paragraph.
- `entity_linked_entries.jsonl`: gratitude entries with semantic object links.
- `daily_summary.jsonl`: one row per diary date.
- `summary.yaml`: aggregate counts for querying.

Pattern candidates are written to `life/patterns/bke_gratitude_diary_pattern_candidates.yaml`.
