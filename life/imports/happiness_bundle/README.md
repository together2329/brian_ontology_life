# Happiness Bundle Import

This directory contains derived indexes from Brian's local `행복꾸러미` PDF.

Generated files:

- `manifest.yaml`: source path, sha256, page count, text count, and generated file refs.
- `page_index.jsonl`: page-level text hash, short excerpt, tags, and linked entity candidates.
- `image_index.jsonl`: page-level image/visual evidence index with image counts, visual categories, and linked entities.
- `parsed_items.yaml`: structured happiness trigger list extracted from PDF text.

The canonical concept object is stored at:

- `life/concepts/happiness_bundle.yaml`

Regenerate with:

```bash
python3 tools/import_happiness_bundle.py
```

The raw PDF stays at its original local Google Drive path. This repo stores only source metadata, page refs, short excerpts, image hashes/metadata, and structured ontology objects.
