# Obsidian Daily Import

This folder contains ontology-friendly indexes generated from Brian's Obsidian `01_Daily` raw snapshot.

Raw source files are preserved in the repository under:

- `raw_data/obsidian/01_Daily/`

Generated files:

- `manifest.yaml`: source file inventory with path, role, size, and sha256.
- `summary.yaml`: aggregate import summary, area totals, energy stats, emotion tags, and semantic link counts.
- `normalized_records.jsonl`: parsed `TimeBlock` and `DailySection` records from dated Daily notes.
- `entity_linked_records.jsonl`: normalized records with semantic links to ontology objects.
- `daily_summary.jsonl`: day-level aggregates for time blocks, sections, areas, emotions, and entity refs.

Regenerate with:

```bash
python3 tools/import_obsidian_daily.py
```

Semantic links are candidates when their source entity is marked `needs_user_review` in `life/entities/semantic_entity_catalog.yaml`.
Daily note time blocks come from the `### Day planner` section and should be treated as mixed planned/actual unless Brian confirms otherwise.
