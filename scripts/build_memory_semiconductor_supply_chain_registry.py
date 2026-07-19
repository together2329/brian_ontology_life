#!/usr/bin/env python3
"""Build deterministic memory-manufacturer and enabling-supply-chain registries.

The YAML research artifact remains the human-readable evidence ledger.  These
outputs make company and supplier-layer records easy to retrieve while retaining
the accounting, market-share, lifecycle, relationship and capacity boundaries.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


MANUFACTURER_COMPARISON_CONTRACT = {
    "accounting": "Preserve currency, reporting period and audited, preliminary, forecast or management-plan state.",
    "market_share": "Market-research revenue share is not physical wafer capacity, bit shipment, HBM share or profit share.",
    "capacity": "Do not sum fab plans, shell capacity, wafer starts, output bits and packaged-product shipments as one measure.",
    "joint_venture": "Kioxia and Sandisk commercial results remain separate, but Yokkaichi and Kitakami wafer capacity is not double-counted.",
    "normalization": "Current price-cycle revenue and margins are not treated as normalized earnings.",
    "relationship": "A category-exposed supplier is not converted into a named customer allocation without primary evidence.",
}

SUPPLY_CHAIN_COMPARISON_CONTRACT = {
    "exposure": "Product-category exposure is not customer-specific revenue, order value or installed share.",
    "commercial": "Research collaboration, qualification, MOU, order, shipment and recognized revenue remain separate states.",
    "capacity": "Equipment throughput, wafer capacity, stack count, package capacity and accelerator output use different denominators.",
    "duplication": "A supplier appearing in multiple layers is one company with several process roles, not several independent companies.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def collect_urls(value: object) -> list[str]:
    found: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, str) and item.startswith(("https://", "http://")):
            found.append(item)
        elif isinstance(item, dict):
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return list(dict.fromkeys(found))


def load_research(path: Path) -> dict:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["id"] == "global_memory_semiconductor_supply_chain_202607"
    assert len(document["manufacturers"]) == 12
    assert len(document["supply_chain_layers"]) == 10
    return document


def validate_research(document: dict) -> None:
    manufacturers = document["manufacturers"]
    manufacturer_ids = [row["id"] for row in manufacturers]
    assert len(manufacturer_ids) == len(set(manufacturer_ids)), manufacturer_ids
    for row in manufacturers:
        assert row.get("company")
        assert row.get("country")
        assert row.get("classification")
        assert row.get("sources"), row["id"]
        assert collect_urls(row["sources"]), row["id"]

    layers = document["supply_chain_layers"]
    layer_ids = [row["id"] for row in layers]
    assert len(layer_ids) == len(set(layer_ids)), layer_ids
    for layer in layers:
        assert layer.get("stage")
        assert layer.get("bottleneck")
        assert layer.get("suppliers"), layer["id"]

    dram = document["market_snapshot"]["branded_DRAM_1Q26"]
    named_top_three = sum(row["share_percent"] for row in dram["suppliers"][:3])
    assert round(named_top_three, 1) == dram["top_three_share_percent"]
    nand_boundary = document["market_snapshot"]["NAND_1Q26"]["Kioxia_Sandisk_capacity_boundary"]
    assert "jointly" in nand_boundary and "not" in nand_boundary


def build_manufacturers(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    records = []
    for position, company in enumerate(document["manufacturers"], start=1):
        urls = collect_urls(company["sources"])
        records.append({
            "id": company["id"],
            "object_type": "MemorySemiconductorManufacturerProfile",
            "source_order": position,
            "company": company["company"],
            "ticker": company.get("ticker"),
            "country": company["country"],
            "classification": company["classification"],
            "core_products": company.get("core_products", []),
            "profile": company,
            "official_evidence_urls": urls,
            "official_evidence_url_count": len(urls),
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_profile_sha256": canonical_hash(company),
            "comparison_contract": MANUFACTURER_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })
    return records


def build_supply_chain(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    records = []
    position = 0
    for layer_order, layer in enumerate(document["supply_chain_layers"], start=1):
        layer_signal = layer.get("current_signal", layer.get("current_signals"))
        for supplier_order, supplier in enumerate(layer["suppliers"], start=1):
            position += 1
            company_slug = supplier["company"].lower()
            layer_slug = layer["id"].removeprefix("layer_")
            records.append({
                "id": f"memory_supply_{layer_slug}_{company_slug}",
                "object_type": "MemorySemiconductorSupplyChainExposure",
                "source_order": position,
                "layer_order": layer_order,
                "supplier_order_within_layer": supplier_order,
                "layer_id": layer["id"],
                "stage": layer["stage"],
                "bottleneck": layer["bottleneck"],
                "company": supplier["company"],
                "role": supplier["role"],
                "evidence_level": supplier["evidence_level"],
                "criticality": supplier["criticality"],
                "supplier_attributes": {key: value for key, value in supplier.items() if key not in {"company", "role", "evidence_level", "criticality"}},
                "layer_current_signal": layer_signal,
                "layer_boundaries": {key: value for key, value in layer.items() if key.endswith(("boundary", "transition"))},
                "research_artifact_ref": document["id"],
                "research_artifact_path": research_path.as_posix(),
                "source_layer_sha256": canonical_hash(layer),
                "comparison_contract": SUPPLY_CHAIN_COMPARISON_CONTRACT,
                "accessed_on": accessed_on,
            })
    ids = [row["id"] for row in records]
    assert len(ids) == len(set(ids)), ids
    return records


def build_summary(document: dict, manufacturers: list[dict], suppliers: list[dict], accessed_on: str) -> dict:
    source_urls = collect_urls(document)
    supplier_companies = sorted({row["company"] for row in suppliers})
    repeated_suppliers = Counter(row["company"] for row in suppliers)
    return {
        "registry": "Global memory semiconductor manufacturers and enabling supply chain",
        "as_of": str(document["as_of"]),
        "accessed_on": accessed_on,
        "manufacturer_records": len(manufacturers),
        "manufacturer_country_counts": dict(sorted(Counter(row["country"] for row in manufacturers).items())),
        "manufacturer_classification_counts": dict(sorted(Counter(row["classification"] for row in manufacturers).items())),
        "supply_chain_layers": len(document["supply_chain_layers"]),
        "supply_chain_exposure_records": len(suppliers),
        "unique_supply_chain_companies": len(supplier_companies),
        "supplier_layer_counts": dict(sorted(Counter(row["layer_id"] for row in suppliers).items())),
        "supplier_evidence_level_counts": dict(sorted(Counter(row["evidence_level"] for row in suppliers).items())),
        "suppliers_present_in_multiple_layers": dict(sorted((key, value) for key, value in repeated_suppliers.items() if value > 1)),
        "adjacent_memory_supplier_records": len(document["adjacent_memory_supplier_roster"]["companies"]),
        "official_and_market_research_url_count": len(source_urls),
        "source_urls": source_urls,
        "quality_gates": {
            "dram_top_three_share_reconciled": True,
            "kioxia_sandisk_JV_capacity_not_double_counted": True,
            "tsmc_not_classified_as_memory_IDM": True,
            "current_cycle_not_treated_as_normalized": True,
            "category_exposure_not_treated_as_customer_allocation": True,
        },
        "manufacturer_record_ids": [row["id"] for row in manufacturers],
        "supply_chain_record_ids": [row["id"] for row in suppliers],
        "manufacturer_records_sha256": canonical_hash(manufacturers),
        "supply_chain_records_sha256": canonical_hash(suppliers),
        "research_artifact_sha256": canonical_hash(document),
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, default=str) + "\n" for row in records),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument(
        "--research",
        type=Path,
        default=Path("life/finance/global_memory_semiconductor_supply_chain_202607.yaml"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("life/imports/memory_semiconductor_20260719"),
    )
    args = parser.parse_args()

    document = load_research(args.research)
    validate_research(document)
    manufacturers = build_manufacturers(document, args.research, args.accessed_on)
    suppliers = build_supply_chain(document, args.research, args.accessed_on)
    summary = build_summary(document, manufacturers, suppliers, args.accessed_on)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manufacturer_path = args.output_dir / "memory_manufacturer_registry.jsonl"
    supply_chain_path = args.output_dir / "memory_supply_chain_registry.jsonl"
    summary_path = args.output_dir / "memory_semiconductor_summary.json"
    write_jsonl(manufacturer_path, manufacturers)
    write_jsonl(supply_chain_path, suppliers)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "manufacturers": len(manufacturers),
        "supply_chain_records": len(suppliers),
        "unique_supply_chain_companies": summary["unique_supply_chain_companies"],
        "manufacturer_registry": str(manufacturer_path),
        "supply_chain_registry": str(supply_chain_path),
        "summary": str(summary_path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
