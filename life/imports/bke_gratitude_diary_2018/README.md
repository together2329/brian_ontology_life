# BKE Gratitude Diary 2018

Ontology import for Brian's 2018 BKE Group gratitude diary campaign document.

Raw source stays under `raw_data/documents/bke_gratitude_campaign_2018/`.

Generated files:

- `manifest.yaml`: source and parser metadata.
- `source.md`: locally normalized, human-readable DOCX text.
- `normalized_entries.jsonl`: one `GratitudeEntry` per dated gratitude paragraph.
- `entity_linked_entries.jsonl`: gratitude entries with semantic object links.
- `daily_summary.jsonl`: one row per diary date.
- `summary.yaml`: aggregate counts for querying.

Pattern candidates are written to `life/patterns/bke_gratitude_diary_2018_pattern_candidates.yaml`.
