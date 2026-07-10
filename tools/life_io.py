#!/usr/bin/env python3
"""Shared loading and traversal helpers for life ontology tools.

The repository intentionally stores records as plain YAML and JSONL.  This
module keeps file discovery, parsing, record traversal, and reference detection
consistent across the validator and query CLI without introducing a database.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Literal
from urllib.parse import urlparse

import yaml

Namespace = Literal["life", "templates", "schema"]

YAML_SUFFIXES = {".yaml", ".yml"}
DATA_SUFFIXES = YAML_SUFFIXES | {".jsonl"}
FILE_EXTENSIONS = {
    ".yaml",
    ".yml",
    ".jsonl",
    ".json",
    ".md",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".html",
    ".txt",
    ".csv",
    ".tsv",
    ".docx",
    ".xlsx",
}
DEFAULT_AREA_IDS = {
    "MIND",
    "BODY",
    "CAREER",
    "FINANCE",
    "RELATION",
    "MAINTENANCE",
    "FUN",
}


@dataclass(frozen=True)
class SourceDocument:
    """One parsed YAML document or one parsed JSONL line."""

    path: Path
    relative_path: str
    namespace: Namespace
    data: Any
    line: int | None = None

    @property
    def label(self) -> str:
        return f"{self.relative_path}:{self.line}" if self.line else self.relative_path


@dataclass(frozen=True)
class LoadError:
    relative_path: str
    namespace: Namespace
    message: str
    line: int | None = None

    @property
    def label(self) -> str:
        return f"{self.relative_path}:{self.line}" if self.line else self.relative_path


@dataclass(frozen=True)
class LoadResult:
    documents: tuple[SourceDocument, ...]
    errors: tuple[LoadError, ...]
    files: tuple[Path, ...]


@dataclass(frozen=True)
class RecordNode:
    document: SourceDocument
    object_path: str
    record_type: str
    value: dict[str, Any]

    @property
    def record_id(self) -> str | None:
        value = self.value.get("id")
        return value if isinstance(value, str) and value else None

    @property
    def area(self) -> str | None:
        value = self.value.get("area")
        return value if isinstance(value, str) and value else None


@dataclass(frozen=True)
class ReferenceValue:
    key: str
    object_path: str
    value: Any
    expects_many: bool


@dataclass(frozen=True)
class IdValue:
    object_path: str
    value: Any


def _namespace_for(relative_path: Path) -> Namespace:
    first = relative_path.parts[0] if relative_path.parts else ""
    if first == "life":
        return "life"
    if first == "templates":
        return "templates"
    return "schema"


def discover_files(
    root: Path,
    *,
    include_life: bool = True,
    include_templates: bool = False,
    include_schema: bool = False,
) -> list[Path]:
    """Return supported data files under the selected repository namespaces."""

    root = root.resolve()
    candidates: list[Path] = []
    if include_life:
        life_dir = root / "life"
        if life_dir.is_dir():
            candidates.extend(path for path in life_dir.rglob("*") if path.suffix.lower() in DATA_SUFFIXES)
    if include_templates:
        template_dir = root / "templates"
        if template_dir.is_dir():
            candidates.extend(path for path in template_dir.glob("*") if path.suffix.lower() in DATA_SUFFIXES)
    if include_schema:
        schema_dir = root / ".codex"
        if schema_dir.is_dir():
            candidates.extend(path for path in schema_dir.glob("*") if path.suffix.lower() in YAML_SUFFIXES)

    return sorted({path for path in candidates if path.is_file()}, key=lambda path: path.as_posix())


def load_documents(
    root: Path,
    *,
    include_life: bool = True,
    include_templates: bool = False,
    include_schema: bool = False,
) -> LoadResult:
    """Parse selected YAML and JSONL files while preserving source locations."""

    root = root.resolve()
    files = discover_files(
        root,
        include_life=include_life,
        include_templates=include_templates,
        include_schema=include_schema,
    )
    documents: list[SourceDocument] = []
    errors: list[LoadError] = []

    for path in files:
        relative = path.relative_to(root)
        relative_path = relative.as_posix()
        namespace = _namespace_for(relative)

        if path.suffix.lower() == ".jsonl":
            try:
                with path.open(encoding="utf-8") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                        except (json.JSONDecodeError, ValueError) as exc:
                            errors.append(
                                LoadError(
                                    relative_path=relative_path,
                                    namespace=namespace,
                                    line=line_number,
                                    message=str(exc),
                                )
                            )
                            continue
                        documents.append(
                            SourceDocument(
                                path=path,
                                relative_path=relative_path,
                                namespace=namespace,
                                data=data,
                                line=line_number,
                            )
                        )
            except (OSError, UnicodeError) as exc:
                errors.append(
                    LoadError(
                        relative_path=relative_path,
                        namespace=namespace,
                        message=str(exc),
                    )
                )
            continue

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            line = None
            mark = getattr(exc, "problem_mark", None)
            if mark is not None:
                line = mark.line + 1
            errors.append(
                LoadError(
                    relative_path=relative_path,
                    namespace=namespace,
                    line=line,
                    message=str(exc),
                )
            )
            continue

        documents.append(
            SourceDocument(
                path=path,
                relative_path=relative_path,
                namespace=namespace,
                data=data,
            )
        )

    return LoadResult(tuple(documents), tuple(errors), tuple(files))


def load_area_ids(root: Path) -> set[str]:
    """Load canonical area IDs, falling back to the documented defaults."""

    ontology_path = root.resolve() / ".codex" / "life_ontology.yaml"
    try:
        document = yaml.safe_load(ontology_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return set(DEFAULT_AREA_IDS)

    areas = document.get("areas") if isinstance(document, dict) else None
    if not isinstance(areas, list):
        return set(DEFAULT_AREA_IDS)

    found = {
        item["id"]
        for item in areas
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
    }
    return found or set(DEFAULT_AREA_IDS)


def iter_id_values(value: Any, object_path: str = "$") -> Iterator[IdValue]:
    """Yield every mapping key named ``id`` with its structural path."""

    if isinstance(value, dict):
        if "id" in value:
            yield IdValue(f"{object_path}.id", value.get("id"))
        for key, child in value.items():
            yield from iter_id_values(child, f"{object_path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_id_values(child, f"{object_path}[{index}]")


def is_reference_key(key: str) -> bool:
    """Return whether a field follows the repository's reference convention."""

    return key == "ref" or key.endswith("_ref") or key.endswith("_refs")


def iter_reference_values(value: Any, object_path: str = "$") -> Iterator[ReferenceValue]:
    """Yield reference fields without normalizing malformed shapes away."""

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{object_path}.{key}"
            if is_reference_key(key):
                yield ReferenceValue(
                    key=key,
                    object_path=child_path,
                    value=child,
                    expects_many=key.endswith("_refs"),
                )
            yield from iter_reference_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_reference_values(child, f"{object_path}[{index}]")


def iter_area_values(value: Any, object_path: str = "$") -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{object_path}.{key}"
            if key == "area":
                yield child_path, child
            yield from iter_area_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_area_values(child, f"{object_path}[{index}]")


def _singularize(token: str) -> str:
    irregular = {
        "people": "person",
        "children": "child",
        "men": "man",
        "women": "woman",
        "data": "datum",
        "statuses": "status",
    }
    if token in irregular:
        return irregular[token]
    if token.endswith("ies") and len(token) > 3:
        return token[:-3] + "y"
    if token.endswith("sses"):
        return token[:-2]
    if token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def type_name(collection_name: str | None) -> str:
    if not collection_name:
        return "Record"
    tokens = collection_name.strip("[]").split("_")
    if tokens:
        tokens[-1] = _singularize(tokens[-1])
    return "".join(token[:1].upper() + token[1:] for token in tokens if token) or "Record"


def iter_record_nodes(document: SourceDocument) -> Iterator[RecordNode]:
    """Yield logical record mappings instead of treating an entire file as one hit.

    Top-level collection containers are skipped, while their child mappings are
    yielded individually. Nested mappings and list items remain searchable.
    """

    def walk(
        value: Any,
        object_path: str,
        collection_name: str | None,
    ) -> Iterator[RecordNode]:
        if isinstance(value, dict):
            is_jsonl_root = document.path.suffix.lower() == ".jsonl" and object_path == "$"
            meaningful_root_scalars = object_path == "$" and any(
                key not in {"schema_version", "status"}
                and isinstance(child, (str, int, float, bool))
                for key, child in value.items()
            )
            is_record = is_jsonl_root or object_path != "$" or meaningful_root_scalars
            if is_record:
                explicit_type = value.get("type") or value.get("record_type")
                record_type = explicit_type if isinstance(explicit_type, str) and explicit_type else type_name(collection_name)
                yield RecordNode(document, object_path, record_type, value)
            for key, child in value.items():
                if isinstance(child, list):
                    for index, item in enumerate(child):
                        yield from walk(item, f"{object_path}.{key}[{index}]", key)
                elif isinstance(child, dict):
                    yield from walk(child, f"{object_path}.{key}", key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from walk(child, f"{object_path}[{index}]", collection_name)

    yield from walk(document.data, "$", None)


def _scalar_fragments(value: Any) -> Iterable[str]:
    """Flatten direct scalar content while leaving nested records to their own node."""

    if value is None:
        return []
    if isinstance(value, (str, int, float, bool)):
        return [str(value)]
    if isinstance(value, list) and all(not isinstance(item, (dict, list)) for item in value):
        return [str(item) for item in value if item is not None]
    return []


def record_search_text(record: dict[str, Any]) -> str:
    fragments: list[str] = []
    for key, value in record.items():
        scalar_values = list(_scalar_fragments(value))
        if scalar_values:
            fragments.append(f"{key}=" + " ".join(scalar_values))
    return " | ".join(fragments)


def compact_snippet(text: str, start: int, end: int, radius: int = 90) -> str:
    """Return a normalized context snippet guaranteed to include the match."""

    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return ""

    # Whitespace normalization changes offsets. Locate the matched literal again
    # when possible, otherwise use the original offsets as a safe approximation.
    matched = re.sub(r"\s+", " ", text[start:end]).strip()
    if matched:
        normalized_start = normalized.casefold().find(matched.casefold())
        if normalized_start >= 0:
            start = normalized_start
            end = normalized_start + len(matched)

    left = max(0, start - radius)
    right = min(len(normalized), end + radius)
    prefix = "…" if left else ""
    suffix = "…" if right < len(normalized) else ""
    return f"{prefix}{normalized[left:right].strip()}{suffix}"


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def looks_like_path(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if stripped.startswith(("./", "../", "/", "~")):
        return True
    if "/" in stripped or "\\" in stripped:
        return True
    return Path(stripped).suffix.lower() in FILE_EXTENSIONS


def resolve_repo_relative_path(root: Path, value: str) -> tuple[Path | None, str | None]:
    """Resolve a file reference and reject absolute or escaping paths."""

    candidate = Path(value)
    windows_absolute = bool(re.match(r"^[A-Za-z]:[\\/]", value))
    if candidate.is_absolute() or windows_absolute or value.startswith("~"):
        return None, "absolute paths and home-directory expansion are not allowed"

    root = root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, "path escapes the repository root"
    return resolved, None
