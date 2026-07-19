#!/usr/bin/env python3
"""Build deterministic AI power-infrastructure research registries.

The YAML ledger preserves evidence and comparison boundaries. The JSONL outputs
make companies, stage exposures, facilities and named relationships searchable
without converting plans, contracts, backlog or nameplate ratings into current
data-center load or recognized revenue.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml


COMPANY_COMPARISON_CONTRACT = {
    "financial": "Preserve currency, period and group or segment boundary; group revenue is not AI revenue.",
    "power": "IT MW, utility MW, generator MW, transformer MVA and battery MW/MWh are different denominators.",
    "lifecycle": "Planned, requested, contracted, permitted, built, energized and billed remain separate.",
    "commercial": "Partnership, MSA, order, backlog, shipment and recognized revenue remain separate.",
    "ownership": "Subsidiary and parent revenue are not double-counted.",
}

SUPPLY_CHAIN_COMPARISON_CONTRACT = {
    "role": "A company may occur in multiple stages; repeated exposure is not a duplicate company.",
    "bottleneck": "Technical scarcity does not prove pricing power, market share or profit.",
    "allocation": "Stage membership is not a customer bill of materials or revenue allocation.",
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
    assert document["id"] == "global_ai_power_infrastructure_supply_chain_202607"
    return document


def iter_investment_holdings(document: dict):
    for fund in document["investment_exposure"]["funds"]:
        for key in ("holdings", "holdings_partial_top_ten"):
            for holding in fund.get(key, []):
                yield fund, key, holding


def validate_research(document: dict) -> None:
    quality = document["quality_gates"]
    companies = document["companies"]
    company_ids = [row["id"] for row in companies]
    company_id_set = set(company_ids)
    assert len(companies) >= quality["minimum_company_records"], len(companies)
    assert len(company_ids) == len(company_id_set), company_ids

    for company in companies:
        assert company.get("company"), company.get("id")
        assert company.get("country"), company["id"]
        assert company.get("ownership"), company["id"]
        assert company.get("roles"), company["id"]
        assert company.get("core_products"), company["id"]
        assert company.get("evidence_state"), company["id"]
        assert collect_urls(company.get("sources", [])), company["id"]

    stages = document["supply_chain_stages"]
    stage_ids = [row["id"] for row in stages]
    assert len(stages) == quality["exact_supply_chain_stage_count"], len(stages)
    assert len(stage_ids) == len(set(stage_ids)), stage_ids
    for stage in stages:
        assert stage.get("bottleneck"), stage["id"]
        assert stage.get("supplier_refs"), stage["id"]
        missing = sorted(set(stage["supplier_refs"]) - company_id_set)
        assert not missing, (stage["id"], missing)

    snapshots = document["financial_snapshots"]
    snapshot_refs = [row["company_ref"] for row in snapshots]
    assert len(snapshot_refs) == len(set(snapshot_refs)), snapshot_refs
    assert not (set(snapshot_refs) - company_id_set), sorted(set(snapshot_refs) - company_id_set)

    for facility in document["facility_and_capacity_records"]:
        assert facility["company_ref"] in company_id_set, facility["id"]
        assert facility.get("measures"), facility["id"]
        assert collect_urls(facility.get("source")), facility["id"]

    relationship_ids = [row["id"] for row in document["explicit_relationships"]]
    assert len(relationship_ids) == len(set(relationship_ids)), relationship_ids
    for relationship in document["explicit_relationships"]:
        missing = sorted(set(relationship.get("parties", [])) - company_id_set)
        assert not missing, (relationship["id"], missing)
        assert relationship.get("lifecycle"), relationship["id"]
        assert relationship.get("boundary"), relationship["id"]
        assert collect_urls(relationship.get("source")), relationship["id"]

    for fund, _, holding in iter_investment_holdings(document):
        company_ref = holding.get("company_ref")
        if company_ref:
            assert company_ref in company_id_set, (fund["id"], company_ref)

    KODEX = document["investment_exposure"]["funds"][0]
    weights = [row["weight_percent"] for row in KODEX["holdings"]]
    assert round(sum(weights[:3]), 2) == quality["ETF_checks"]["KODEX_top_three_percent"]
    assert round(sum(weights[:5]), 2) == quality["ETF_checks"]["KODEX_top_five_percent"]
    assert round(sum(weights), 2) == KODEX["checks"]["rounding_weight_sum_percent"]

    lineage_entities = [row["operating_entity"] for row in document["lineage_register"]]
    assert len(lineage_entities) == len(set(lineage_entities)), lineage_entities
    for row in document["lineage_register"]:
        assert row["current_parent_ref"] in company_id_set, row


def build_companies(document: dict, research_path: Path, accessed_on: str) -> list[dict]:
    snapshots = {row["company_ref"]: row for row in document["financial_snapshots"]}
    stages_by_company: dict[str, list[str]] = defaultdict(list)
    for stage in document["supply_chain_stages"]:
        for company_ref in stage["supplier_refs"]:
            stages_by_company[company_ref].append(stage["id"])

    investment_by_company: dict[str, list[dict]] = defaultdict(list)
    for fund, holding_set, holding in iter_investment_holdings(document):
        company_ref = holding.get("company_ref")
        if company_ref:
            investment_by_company[company_ref].append({
                "fund_id": fund["id"],
                "holding_snapshot_date": str(fund["holding_snapshot_date"]),
                "holding_set": holding_set,
                "weight_percent": holding["weight_percent"],
                "full_or_partial_boundary": fund.get("boundary", "full_published_snapshot_with_rounding"),
            })

    records = []
    for position, company in enumerate(document["companies"], start=1):
        urls = collect_urls(company["sources"])
        records.append({
            "id": company["id"],
            "object_type": "AIPowerInfrastructureCompanyProfile",
            "source_order": position,
            "company": company["company"],
            "ticker": company.get("ticker"),
            "country": company["country"],
            "ownership": company["ownership"],
            "roles": company["roles"],
            "core_products": company["core_products"],
            "evidence_state": company["evidence_state"],
            "linked_financial_profile_ref": company.get("financial_profile_ref"),
            "latest_financial_snapshot": snapshots.get(company["id"]),
            "supply_chain_stage_refs": stages_by_company[company["id"]],
            "Brian_fund_exposures": investment_by_company[company["id"]],
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
                "id": f"power_supply_{stage['id'].removeprefix('stage_')}_{company_ref.removeprefix('power_company_')}",
                "object_type": "AIPowerInfrastructureSupplyChainExposure",
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
        records.append({
            **facility,
            "object_type": "AIPowerInfrastructureFacilityCapacityRecord",
            "source_order": position,
            "company": companies[facility["company_ref"]]["company"],
            "metric_count": len(facility["measures"]),
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
        records.append({
            **relationship,
            "object_type": "AIPowerInfrastructureNamedRelationship",
            "source_order": position,
            "internal_party_names": [companies[ref]["company"] for ref in relationship.get("parties", [])],
            "commercial_and_power_boundaries_preserved": True,
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
    funds = document["investment_exposure"]["funds"]
    return {
        "registry": "Global AI data-center power infrastructure supply chain",
        "as_of": str(document["as_of"]),
        "accessed_on": accessed_on,
        "company_records": len(companies),
        "public_or_state_controlled_company_records": sum(
            "public" in row["ownership"] or "state" in row["ownership"] for row in companies
        ),
        "country_counts": dict(sorted(Counter(row["country"] for row in companies).items())),
        "supply_chain_stages": len(document["supply_chain_stages"]),
        "supply_chain_exposure_records": len(supply_chain),
        "stage_counts": dict(sorted(Counter(row["stage_id"] for row in supply_chain).items())),
        "companies_present_in_multiple_stages": dict(sorted(
            (company_ref, count) for company_ref, count in repeated.items() if count > 1
        )),
        "financial_snapshot_records": len(document["financial_snapshots"]),
        "facility_capacity_records": len(facilities),
        "named_relationship_records": len(relationships),
        "system_routes": len(document["system_routes"]),
        "bottlenecks": len(document["bottleneck_register"]),
        "lineage_records": len(document["lineage_register"]),
        "official_and_primary_source_url_count": len(source_urls),
        "Brian_portfolio_snapshot": document["investment_exposure"]["portfolio_snapshot"],
        "Brian_fund_reconciliation": [{
            "fund_id": fund["id"],
            "snapshot_date": str(fund["holding_snapshot_date"]),
            "published_company_rows_captured": len(fund.get("holdings", fund.get("holdings_partial_top_ten", []))),
            "boundary": fund.get("boundary", "full_published_snapshot_with_rounding"),
        } for fund in funds],
        "KODEX_concentration": funds[0]["checks"],
        "quality_gates": document["quality_gates"],
        "open_questions": document["open_questions"],
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
        default=Path("life/finance/global_ai_power_infrastructure_supply_chain_202607.yaml"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("life/imports/ai_power_infrastructure_20260719"),
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
    write_jsonl(args.output_dir / "power_company_registry.jsonl", companies)
    write_jsonl(args.output_dir / "power_supply_chain_registry.jsonl", supply_chain)
    write_jsonl(args.output_dir / "power_facility_registry.jsonl", facilities)
    write_jsonl(args.output_dir / "power_relationship_registry.jsonl", relationships)
    (args.output_dir / "power_infrastructure_summary.json").write_text(
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
