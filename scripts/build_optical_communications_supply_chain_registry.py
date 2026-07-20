#!/usr/bin/env python3
"""Build deterministic optical-communications company and supply-chain registries.

The YAML research artifact is the human-readable evidence ledger. These JSONL
outputs make companies, value-chain roles, facilities and named relationships
searchable while retaining financial, lifecycle, capacity and customer-allocation
boundaries.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


COMPANY_COMPARISON_CONTRACT = {
    "financial": "Preserve currency, period and accounting boundary; group revenue is not optical-only revenue.",
    "commercial": "Partnership, sample, qualification, order, commitment, shipment and recognized revenue remain separate.",
    "capacity": "Wafer diameter, floor area, fibre-km, unit output, revenue capacity and jobs use different denominators.",
    "architecture": "Pluggable, LPO, NPO, CPO, optical I/O and coherent transport can coexist.",
    "customer": "Product or ecosystem exposure is not customer-specific revenue without named primary evidence.",
    "duplication": "Acquired businesses are represented under their current parent rather than double-counted.",
}

SUPPLY_CHAIN_COMPARISON_CONTRACT = {
    "role": "A company may occur in several stages; repeated stage exposure is not a duplicate company.",
    "bottleneck": "Technical criticality does not by itself establish market share, pricing power or profit.",
    "allocation": "A category route is not a bill of materials or customer allocation.",
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
    assert document["id"] == "global_optical_communications_supply_chain_202607"
    return document


def validate_research(document: dict) -> None:
    companies = document["companies"]
    company_ids = [row["id"] for row in companies]
    assert len(companies) >= 60, len(companies)
    assert len(company_ids) == len(set(company_ids)), company_ids
    company_id_set = set(company_ids)

    for row in companies:
        assert row.get("company"), row.get("id")
        assert row.get("country"), row["id"]
        assert row.get("ownership"), row["id"]
        assert row.get("roles"), row["id"]
        assert row.get("core_products"), row["id"]
        assert row.get("evidence_state"), row["id"]
        assert collect_urls(row.get("sources", [])), row["id"]

    stage_ids = [row["id"] for row in document["supply_chain_stages"]]
    assert len(stage_ids) == len(set(stage_ids)), stage_ids
    assert len(stage_ids) == 10
    for stage in document["supply_chain_stages"]:
        assert stage.get("bottleneck"), stage["id"]
        assert stage.get("supplier_refs"), stage["id"]
        missing = sorted(set(stage["supplier_refs"]) - company_id_set)
        assert not missing, (stage["id"], missing)

    snapshots = document["financial_snapshots"]
    assert len({row["company_ref"] for row in snapshots}) == len(snapshots)
    missing_snapshot_refs = sorted({row["company_ref"] for row in snapshots} - company_id_set)
    assert not missing_snapshot_refs, missing_snapshot_refs

    for facility in document["facility_and_capacity_records"]:
        assert facility["company_ref"] in company_id_set, facility["id"]
        assert collect_urls(facility.get("source")), facility["id"]

    for relationship in document["explicit_relationships"]:
        for party in relationship.get("parties", []):
            assert party in company_id_set, (relationship["id"], party)
        assert collect_urls(relationship.get("source")), relationship["id"]

    holdings = document["investment_exposure"]["holdings"]
    assert round(sum(row["weight_percent"] for row in holdings), 2) == 100.00
    assert round(sum(row["weight_percent"] for row in holdings[:3]), 2) == 59.73
    assert round(sum(row["weight_percent"] for row in holdings[:5]), 2) == 73.98
    for holding in holdings:
        assert holding["company_ref"] in company_id_set, holding

    lineage_former = [row["former_entity"] for row in document["acquisition_and_lineage_register"]]
    assert len(lineage_former) == len(set(lineage_former)), lineage_former
    for row in document["acquisition_and_lineage_register"]:
        assert row["current_parent_ref"] in company_id_set, row


def build_companies(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    snapshots = {row["company_ref"]: row for row in document["financial_snapshots"]}
    stage_membership: dict[str, list[str]] = {row["id"]: [] for row in document["companies"]}
    for stage in document["supply_chain_stages"]:
        for company_ref in stage["supplier_refs"]:
            stage_membership[company_ref].append(stage["id"])

    holdings = {
        row["company_ref"]: row["weight_percent"]
        for row in document["investment_exposure"]["holdings"]
    }
    records = []
    for position, company in enumerate(document["companies"], start=1):
        urls = collect_urls(company["sources"])
        records.append({
            "id": company["id"],
            "object_type": "OpticalCommunicationsCompanyProfile",
            "source_order": position,
            "company": company["company"],
            "ticker": company.get("ticker"),
            "country": company["country"],
            "ownership": company["ownership"],
            "roles": company["roles"],
            "core_products": company["core_products"],
            "evidence_state": company["evidence_state"],
            "lineage": company.get("lineage"),
            "linked_profile_ref": company.get("financial_profile_ref") or company.get("related_profile_ref"),
            "latest_financial_snapshot": snapshots.get(company["id"]),
            "supply_chain_stage_refs": stage_membership[company["id"]],
            "KODEX_AI_optical_weight_percent_2026_05_31": holdings.get(company["id"]),
            "official_evidence_urls": urls,
            "official_evidence_url_count": len(urls),
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_profile_sha256": canonical_hash(company),
            "comparison_contract": COMPANY_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })
    return records


def build_supply_chain(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    companies = {row["id"]: row for row in document["companies"]}
    records = []
    position = 0
    for stage_order, stage in enumerate(document["supply_chain_stages"], start=1):
        for supplier_order, company_ref in enumerate(stage["supplier_refs"], start=1):
            position += 1
            company = companies[company_ref]
            records.append({
                "id": f"optical_supply_{stage['id'].removeprefix('stage_')}_{company_ref.removeprefix('optical_company_')}",
                "object_type": "OpticalCommunicationsSupplyChainExposure",
                "source_order": position,
                "stage_order": stage_order,
                "supplier_order_within_stage": supplier_order,
                "stage_id": stage["id"],
                "stage": stage["stage"],
                "bottleneck": stage["bottleneck"],
                "company_ref": company_ref,
                "company": company["company"],
                "country": company["country"],
                "matching_company_roles": company["roles"],
                "core_products": company["core_products"],
                "evidence_state": company["evidence_state"],
                "not_customer_allocation": True,
                "research_artifact_ref": document["id"],
                "research_artifact_path": research_path.as_posix(),
                "source_stage_sha256": canonical_hash(stage),
                "comparison_contract": SUPPLY_CHAIN_COMPARISON_CONTRACT,
                "accessed_on": accessed_on,
            })
    ids = [row["id"] for row in records]
    assert len(ids) == len(set(ids)), ids
    return records


def build_facilities(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    companies = {row["id"]: row for row in document["companies"]}
    records = []
    for position, facility in enumerate(document["facility_and_capacity_records"], start=1):
        company = companies[facility["company_ref"]]
        records.append({
            **facility,
            "object_type": "OpticalCommunicationsFacilityCapacityRecord",
            "source_order": position,
            "company": company["company"],
            "metric_count": len(facility.get("measures", [])),
            "capacity_denominators_not_summed": True,
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_record_sha256": canonical_hash(facility),
            "comparison_contract": COMPANY_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })
    return records


def build_relationships(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    companies = {row["id"]: row for row in document["companies"]}
    records = []
    for position, relationship in enumerate(document["explicit_relationships"], start=1):
        internal_refs = relationship.get("parties", [])
        records.append({
            **relationship,
            "object_type": "OpticalCommunicationsNamedRelationship",
            "source_order": position,
            "internal_party_names": [companies[ref]["company"] for ref in internal_refs],
            "named_relationship_not_revenue_allocation": True,
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_record_sha256": canonical_hash(relationship),
            "comparison_contract": COMPANY_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })
    return records


def build_summary(
    document: dict,
    companies: list[dict],
    supply_chain: list[dict],
    facilities: list[dict],
    relationships: list[dict],
    accessed_on: str,
) -> dict:
    repeated = Counter(row["company_ref"] for row in supply_chain)
    source_urls = collect_urls(document)
    ETF = document["investment_exposure"]
    return {
        "registry": "Global optical communications companies and supply chain",
        "as_of": str(document["as_of"]),
        "accessed_on": accessed_on,
        "company_records": len(companies),
        "public_company_records": sum(row["ownership"] == "public" for row in companies),
        "country_counts": dict(sorted(Counter(row["country"] for row in companies).items())),
        "supply_chain_stages": len(document["supply_chain_stages"]),
        "supply_chain_exposure_records": len(supply_chain),
        "stage_counts": dict(sorted(Counter(row["stage_id"] for row in supply_chain).items())),
        "companies_present_in_multiple_stages": dict(sorted((key, value) for key, value in repeated.items() if value > 1)),
        "financial_snapshot_records": len(document["financial_snapshots"]),
        "facility_capacity_records": len(facilities),
        "named_relationship_records": len(relationships),
        "architecture_routes": len(document["architecture_routes"]),
        "bottlenecks": len(document["bottleneck_register"]),
        "lineage_records": len(document["acquisition_and_lineage_register"]),
        "official_and_primary_source_url_count": len(source_urls),
        "KODEX_AI_optical_snapshot": {
            "date": str(ETF["holding_snapshot_date"]),
            "holding_count": len(ETF["holdings"]),
            "weight_sum_percent": ETF["checks"]["weights_sum_percent"],
            "top_three_percent": ETF["checks"]["top_three_percent"],
            "top_five_percent": ETF["checks"]["top_five_percent"],
            "direct_gaps": ETF["interpretation"]["direct_gaps"],
        },
        "quality_gates": document["quality_gates"],
        "company_record_ids": [row["id"] for row in companies],
        "facility_record_ids": [row["id"] for row in facilities],
        "relationship_record_ids": [row["id"] for row in relationships],
        "company_records_sha256": canonical_hash(companies),
        "supply_chain_records_sha256": canonical_hash(supply_chain),
        "facility_records_sha256": canonical_hash(facilities),
        "relationship_records_sha256": canonical_hash(relationships),
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
        default=Path("life/finance/global_optical_communications_supply_chain_202607.yaml"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("life/imports/optical_communications_20260719"),
    )
    args = parser.parse_args()

    document = load_research(args.research)
    validate_research(document)
    companies = build_companies(document, args.research, args.accessed_on)
    supply_chain = build_supply_chain(document, args.research, args.accessed_on)
    facilities = build_facilities(document, args.research, args.accessed_on)
    relationships = build_relationships(document, args.research, args.accessed_on)
    summary = build_summary(document, companies, supply_chain, facilities, relationships, args.accessed_on)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "optical_company_registry.jsonl", companies)
    write_jsonl(args.output_dir / "optical_supply_chain_registry.jsonl", supply_chain)
    write_jsonl(args.output_dir / "optical_facility_registry.jsonl", facilities)
    write_jsonl(args.output_dir / "optical_relationship_registry.jsonl", relationships)
    (args.output_dir / "optical_communications_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "companies": len(companies),
        "supply_chain_exposures": len(supply_chain),
        "facilities": len(facilities),
        "relationships": len(relationships),
        "source_urls": summary["official_and_primary_source_url_count"],
        "output_dir": args.output_dir.as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
