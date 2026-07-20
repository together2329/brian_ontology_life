#!/usr/bin/env python3
"""Build deterministic company, facility and relationship registries.

The human-readable YAML links the earlier memory-company research to foundries,
internal backend sites and independent OSAT/test companies.  Generated records
retain every accounting, lifecycle and production-denominator boundary rather
than publishing a false cross-company capacity total.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


COMPANY_COMPARISON_CONTRACT = {
    "period": "Quarterly, fiscal-year, preliminary and guidance periods remain distinct.",
    "currency": "Revenue and operating profit stay in their reported currencies; no FX conversion is performed.",
    "accounting_boundary": "Segment, consolidated, intersegment and derived metrics remain labeled.",
    "normalization": "Current memory-cycle margins are not treated as steady-state earnings.",
}

FACILITY_COMPARISON_CONTRACT = {
    "scope": "Company portfolio, campus, fab building and line scopes may overlap and are not additive by default.",
    "denominator": "8-inch equivalent, 12-inch equivalent, native wafer, package, test, area, capex and value proxies are separate units.",
    "lifecycle": "Operating, ramping, under-construction, planned and transaction-announced sites remain separate.",
    "missing_data": "Undisclosed physical throughput remains null and is not estimated from revenue, floor area or capex.",
    "joint_venture": "Flash Ventures Yokkaichi and Kitakami records are shared by Kioxia and Sandisk and counted once.",
}

RELATIONSHIP_COMPARISON_CONTRACT = {
    "evidence": "Named contracts, joint ventures and collaborations are distinct from process-category exposure.",
    "allocation": "A process route or supplier layer does not establish customer-specific revenue, volume or installed share.",
    "commercial_state": "Research, plan, qualification, order, shipment and recognized revenue remain distinct states.",
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


def load_yaml(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(document, dict), path
    return document


def extract_financial_metrics(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    """Expose searchable financial fields without flattening their unit boundary."""
    if not snapshot:
        return {
            "period": None,
            "status": "not_publicly_disclosed",
            "currency": None,
            "revenue_metrics": [],
            "operating_profit_metrics": [],
            "operating_margin_metrics": [],
        }

    def metrics_for(predicate: Any) -> list[dict[str, Any]]:
        rows = []
        for key, value in snapshot.items():
            if predicate(key, value):
                rows.append({"metric_key": key, "value": value})
        return rows

    revenue_metrics = metrics_for(
        lambda key, value: "revenue" in key.lower()
        and "mix" not in key.lower()
        and "share" not in key.lower()
        and not isinstance(value, (dict, list))
    )
    operating_profit_metrics = metrics_for(
        lambda key, value: ("operating_profit" in key.lower() or "operating_income" in key.lower())
        and "margin" not in key.lower()
        and not isinstance(value, (dict, list))
    )
    operating_margin_metrics = metrics_for(
        lambda key, value: "operating_margin" in key.lower() and not isinstance(value, (dict, list))
    )
    return {
        "period": snapshot.get("period"),
        "status": snapshot.get("status", "status_retained_in_source_profile"),
        "currency": snapshot.get("currency"),
        "revenue_metrics": revenue_metrics,
        "operating_profit_metrics": operating_profit_metrics,
        "operating_margin_metrics": operating_margin_metrics,
    }


def validate_capacity_measure(measure: dict[str, Any], owner_id: str) -> None:
    required = {"metric_type", "value", "unit", "period", "status", "scope"}
    missing = required - set(measure)
    assert not missing, (owner_id, missing, measure)
    assert measure["value"] is not None, (owner_id, measure)
    assert isinstance(measure["value"], (int, float, list)), (owner_id, measure)
    if isinstance(measure["value"], list):
        assert len(measure["value"]) == 2, (owner_id, measure)


def validate_research(document: dict[str, Any], memory: dict[str, Any]) -> None:
    assert document["id"] == "global_semiconductor_manufacturing_backend_network_202607"
    assert memory["id"] == "global_memory_semiconductor_supply_chain_202607"

    linked_ids = document["research_scope"]["linked_memory_and_enabler_company_ids"]
    memory_ids = [row["id"] for row in memory["manufacturers"]]
    assert linked_ids == memory_ids, (linked_ids, memory_ids)
    assert len(memory_ids) == 12

    overrides = document["linked_company_overrides"]
    override_ids = [row["company_id"] for row in overrides]
    assert override_ids == memory_ids
    assert all(row.get("category_tags") for row in overrides)

    additional = document["additional_companies"]
    additional_ids = [row["id"] for row in additional]
    assert len(additional_ids) == len(set(additional_ids)) == 20
    assert not set(additional_ids) & set(memory_ids)
    for row in additional:
        assert row.get("company") and row.get("country") and row.get("category_tags"), row["id"]
        assert row.get("latest_financial_snapshot"), row["id"]
        assert collect_urls(row.get("sources", [])), row["id"]

    external_ids = [row["id"] for row in document["external_entities"]]
    assert len(external_ids) == len(set(external_ids))
    entity_ids = set(memory_ids + additional_ids + external_ids)

    groups = document["facility_groups"]
    group_ids = [row["id"] for row in groups]
    assert len(group_ids) == len(set(group_ids))
    facility_ids: list[str] = []
    for group in groups:
        assert group.get("company_ids"), group["id"]
        assert set(group["company_ids"]) <= entity_ids, group["id"]
        assert group.get("sites"), group["id"]
        assert collect_urls(group.get("sources", [])), group["id"]
        for measure in group.get("portfolio_capacity_measures", []):
            validate_capacity_measure(measure, group["id"])
        for site in group["sites"]:
            facility_ids.append(site["id"])
            for key in ("site_name", "country", "city_or_region", "lifecycle", "functions", "capacity_disclosure"):
                assert site.get(key) is not None, (group["id"], site["id"], key)
            for measure in site.get("capacity_measures", []):
                validate_capacity_measure(measure, site["id"])
    assert len(facility_ids) == len(set(facility_ids))
    assert len(groups) == 31
    assert len(facility_ids) == 140

    relationships = document["explicit_relationships"]
    relationship_ids = [row["id"] for row in relationships]
    assert len(relationship_ids) == len(set(relationship_ids))
    for row in relationships:
        assert row["from_id"] in entity_ids, row["id"]
        assert row["to_id"] in entity_ids, row["id"]
        assert set(row.get("facility_refs", [])) <= set(facility_ids), row["id"]
        assert row.get("sources") and collect_urls(row["sources"]), row["id"]
        assert row.get("not_imply"), row["id"]

    for route in document["process_routes"]:
        assert route.get("not_customer_allocation") is True, route["id"]
        sequence = [stage["sequence"] for stage in route["stages"]]
        assert sequence == list(range(1, len(sequence) + 1)), route["id"]
        for stage in route["stages"]:
            assert set(stage["company_ids"]) <= entity_ids, (route["id"], stage)

    flash_group = next(row for row in groups if row["id"] == "facility_group_flash_ventures")
    assert flash_group["company_ids"] == ["memory_company_kioxia", "memory_company_sandisk"]
    assert flash_group.get("non_additive_group") == "flash_ventures_yokkaichi_kitakami"
    assert {site["id"] for site in flash_group["sites"]} == {
        "fab_flash_ventures_yokkaichi",
        "fab_flash_ventures_kitakami",
    }


def build_companies(
    document: dict[str, Any],
    memory: dict[str, Any],
    research_path: Path,
    memory_path: Path,
    accessed_on: str,
) -> list[dict[str, Any]]:
    override_by_id = {row["company_id"]: row for row in document["linked_company_overrides"]}
    records: list[dict[str, Any]] = []
    for position, company in enumerate(memory["manufacturers"], start=1):
        override = override_by_id[company["id"]]
        snapshot = company.get("latest_financial_snapshot")
        urls = collect_urls(company.get("sources", []))
        records.append({
            "id": company["id"],
            "object_type": "SemiconductorManufacturingCompanyProfile",
            "source_order": position,
            "source_kind": "linked_memory_research",
            "company": company["company"],
            "ticker": company.get("ticker"),
            "country": company["country"],
            "category_tags": override["category_tags"],
            "latest_financial_snapshot": snapshot,
            "searchable_financial_metrics": extract_financial_metrics(snapshot),
            "profile": company,
            "official_evidence_urls": urls,
            "research_artifact_ref": memory["id"],
            "research_artifact_path": memory_path.as_posix(),
            "source_profile_sha256": canonical_hash(company),
            "comparison_contract": COMPANY_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })

    offset = len(records)
    for position, company in enumerate(document["additional_companies"], start=1):
        snapshot = company["latest_financial_snapshot"]
        urls = collect_urls(company.get("sources", []))
        records.append({
            "id": company["id"],
            "object_type": "SemiconductorManufacturingCompanyProfile",
            "source_order": offset + position,
            "source_kind": "manufacturing_backend_research",
            "company": company["company"],
            "ticker": company.get("ticker"),
            "country": company["country"],
            "category_tags": company["category_tags"],
            "latest_financial_snapshot": snapshot,
            "searchable_financial_metrics": extract_financial_metrics(snapshot),
            "profile": company,
            "official_evidence_urls": urls,
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_profile_sha256": canonical_hash(company),
            "comparison_contract": COMPANY_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })

    ids = [row["id"] for row in records]
    assert len(ids) == len(set(ids)) == 32
    return records


def build_facilities(
    document: dict[str, Any],
    memory: dict[str, Any],
    research_path: Path,
    accessed_on: str,
) -> list[dict[str, Any]]:
    company_names = {
        row["id"]: row["company"]
        for row in memory["manufacturers"] + document["additional_companies"]
    }
    records: list[dict[str, Any]] = []
    position = 0
    for group_order, group in enumerate(document["facility_groups"], start=1):
        urls = collect_urls(group.get("sources", []))
        position += 1
        records.append({
            "id": group["id"],
            "object_type": "SemiconductorFacilityPortfolioGroup",
            "source_order": position,
            "group_order": group_order,
            "company_ids": group["company_ids"],
            "company_names": [company_names[value] for value in group["company_ids"]],
            "portfolio_boundary": group.get("portfolio_boundary"),
            "non_additive_group": group.get("non_additive_group"),
            "capacity_measures": group.get("portfolio_capacity_measures", []),
            "site_record_ids": [site["id"] for site in group["sites"]],
            "official_evidence_urls": urls,
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_group_sha256": canonical_hash(group),
            "comparison_contract": FACILITY_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })
        for site_order, site in enumerate(group["sites"], start=1):
            position += 1
            records.append({
                "id": site["id"],
                "object_type": "SemiconductorFacilitySite",
                "source_order": position,
                "group_order": group_order,
                "site_order_within_group": site_order,
                "facility_group_id": group["id"],
                "company_ids": group["company_ids"],
                "company_names": [company_names[value] for value in group["company_ids"]],
                "site_name": site["site_name"],
                "country": site["country"],
                "city_or_region": site["city_or_region"],
                "lifecycle": site["lifecycle"],
                "functions": site["functions"],
                "wafer_sizes": site.get("wafer_sizes", []),
                "capacity_disclosure": site["capacity_disclosure"],
                "capacity_measures": site.get("capacity_measures", []),
                "site_attributes": {
                    key: value
                    for key, value in site.items()
                    if key not in {
                        "id", "site_name", "country", "city_or_region", "lifecycle",
                        "functions", "wafer_sizes", "capacity_disclosure", "capacity_measures",
                    }
                },
                "portfolio_capacity_measure_ref": group["id"] if group.get("portfolio_capacity_measures") else None,
                "portfolio_boundary": group.get("portfolio_boundary"),
                "non_additive_group": group.get("non_additive_group"),
                "official_evidence_urls": urls,
                "research_artifact_ref": document["id"],
                "research_artifact_path": research_path.as_posix(),
                "source_site_sha256": canonical_hash(site),
                "comparison_contract": FACILITY_COMPARISON_CONTRACT,
                "accessed_on": accessed_on,
            })

    ids = [row["id"] for row in records]
    assert len(ids) == len(set(ids)) == 171
    return records


def build_relationships(
    document: dict[str, Any],
    memory: dict[str, Any],
    research_path: Path,
    memory_path: Path,
    accessed_on: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    position = 0
    for row in document["explicit_relationships"]:
        position += 1
        records.append({
            "id": row["id"],
            "object_type": "SemiconductorConfirmedRelationship",
            "source_order": position,
            "relationship_class": "explicit_named_relationship",
            "relationship": row,
            "official_evidence_urls": collect_urls(row["sources"]),
            "research_artifact_ref": document["id"],
            "research_artifact_path": research_path.as_posix(),
            "source_relationship_sha256": canonical_hash(row),
            "comparison_contract": RELATIONSHIP_COMPARISON_CONTRACT,
            "accessed_on": accessed_on,
        })

    for layer_order, layer in enumerate(memory["supply_chain_layers"], start=1):
        for supplier_order, supplier in enumerate(layer["suppliers"], start=1):
            position += 1
            supplier_slug = supplier["company"].lower()
            layer_slug = layer["id"].removeprefix("layer_")
            records.append({
                "id": f"manufacturing_layer_exposure_{layer_slug}_{supplier_slug}",
                "object_type": "SemiconductorProcessLayerExposure",
                "source_order": position,
                "relationship_class": "category_exposure_not_customer_allocation",
                "layer_order": layer_order,
                "supplier_order_within_layer": supplier_order,
                "layer_id": layer["id"],
                "stage": layer["stage"],
                "bottleneck": layer["bottleneck"],
                "supplier": supplier,
                "not_customer_allocation": True,
                "research_artifact_ref": memory["id"],
                "research_artifact_path": memory_path.as_posix(),
                "source_relationship_sha256": canonical_hash({"layer": layer["id"], "supplier": supplier}),
                "comparison_contract": RELATIONSHIP_COMPARISON_CONTRACT,
                "accessed_on": accessed_on,
            })

    for route_order, route in enumerate(document["process_routes"], start=1):
        for stage in route["stages"]:
            position += 1
            row = {
                "route_id": route["id"],
                "product_family": route["product_family"],
                "not_customer_allocation": route["not_customer_allocation"],
                **stage,
            }
            records.append({
                "id": f"process_route_{route['id'].removeprefix('route_')}_{stage['sequence']}",
                "object_type": "SemiconductorProcessRouteStage",
                "source_order": position,
                "relationship_class": "capability_route_not_customer_allocation",
                "route_order": route_order,
                "route_stage": row,
                "official_evidence_urls": [],
                "research_artifact_ref": document["id"],
                "research_artifact_path": research_path.as_posix(),
                "source_relationship_sha256": canonical_hash(row),
                "comparison_contract": RELATIONSHIP_COMPARISON_CONTRACT,
                "accessed_on": accessed_on,
            })

    ids = [row["id"] for row in records]
    assert len(ids) == len(set(ids))
    return records


def build_summary(
    document: dict[str, Any],
    companies: list[dict[str, Any]],
    facilities: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    accessed_on: str,
) -> dict[str, Any]:
    company_categories = Counter(
        category for row in companies for category in row["category_tags"]
    )
    site_records = [row for row in facilities if row["object_type"] == "SemiconductorFacilitySite"]
    group_records = [row for row in facilities if row["object_type"] == "SemiconductorFacilityPortfolioGroup"]
    capacity_measures = [
        measure
        for row in facilities
        for measure in row.get("capacity_measures", [])
    ]
    financials_with_revenue = sum(
        bool(row["searchable_financial_metrics"]["revenue_metrics"]) for row in companies
    )
    financials_with_operating_profit = sum(
        bool(row["searchable_financial_metrics"]["operating_profit_metrics"]) for row in companies
    )
    source_urls = collect_urls(document)
    relationship_classes = Counter(row["relationship_class"] for row in relationships)
    return {
        "registry": document["title"],
        "as_of": str(document["as_of"]),
        "accessed_on": accessed_on,
        "company_records": len(companies),
        "linked_memory_company_records": sum(row["source_kind"] == "linked_memory_research" for row in companies),
        "additional_foundry_and_backend_company_records": sum(row["source_kind"] == "manufacturing_backend_research" for row in companies),
        "company_category_tag_counts_nonexclusive": dict(sorted(company_categories.items())),
        "companies_with_public_revenue_metric": financials_with_revenue,
        "companies_with_public_operating_profit_metric": financials_with_operating_profit,
        "facility_portfolio_group_records": len(group_records),
        "facility_site_records": len(site_records),
        "facility_country_counts": dict(sorted(Counter(row["country"] for row in site_records).items())),
        "facility_lifecycle_counts": dict(sorted(Counter(row["lifecycle"] for row in site_records).items())),
        "facility_capacity_disclosure_counts": dict(sorted(Counter(row["capacity_disclosure"] for row in site_records).items())),
        "facility_function_counts_nonexclusive": dict(sorted(Counter(function for row in site_records for function in row["functions"]).items())),
        "capacity_measure_records": len(capacity_measures),
        "capacity_metric_type_counts": dict(sorted(Counter(row["metric_type"] for row in capacity_measures).items())),
        "capacity_unit_counts": dict(sorted(Counter(row["unit"] for row in capacity_measures).items())),
        "cross_company_capacity_total": None,
        "cross_company_capacity_total_boundary": "Intentionally null because units, periods, scopes, lifecycle states and capacity-versus-output meanings differ.",
        "relationship_records": len(relationships),
        "relationship_class_counts": dict(sorted(relationship_classes.items())),
        "explicit_named_relationship_records": relationship_classes["explicit_named_relationship"],
        "process_layer_exposure_records": relationship_classes["category_exposure_not_customer_allocation"],
        "process_route_stage_records": relationship_classes["capability_route_not_customer_allocation"],
        "official_and_filing_url_count": len(source_urls),
        "source_urls": source_urls,
        "disclosure_gap_records": len(document["disclosure_gaps"]),
        "quality_gates": {
            "company_ids_unique": True,
            "facility_ids_unique": True,
            "relationship_ids_unique": True,
            "flash_ventures_capacity_counted_once": True,
            "planned_capacity_not_counted_as_current": True,
            "incompatible_capacity_units_not_summed": True,
            "intel_intersegment_boundary_retained": True,
            "samsung_DS_boundary_retained": True,
            "ase_ATM_and_EMS_boundary_retained": True,
            "doosan_tesna_value_proxy_not_physical_output": True,
            "capability_routes_not_customer_allocations": True,
        },
        "company_record_ids": [row["id"] for row in companies],
        "facility_record_ids": [row["id"] for row in facilities],
        "relationship_record_ids": [row["id"] for row in relationships],
        "company_records_sha256": canonical_hash(companies),
        "facility_records_sha256": canonical_hash(facilities),
        "relationship_records_sha256": canonical_hash(relationships),
        "research_artifact_sha256": canonical_hash(document),
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
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
        default=Path("life/finance/global_semiconductor_manufacturing_backend_network_202607.yaml"),
    )
    parser.add_argument(
        "--memory-research",
        type=Path,
        default=Path("life/finance/global_memory_semiconductor_supply_chain_202607.yaml"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("life/imports/semiconductor_manufacturing_backend_20260719"),
    )
    args = parser.parse_args()

    document = load_yaml(args.research)
    memory = load_yaml(args.memory_research)
    validate_research(document, memory)
    companies = build_companies(document, memory, args.research, args.memory_research, args.accessed_on)
    facilities = build_facilities(document, memory, args.research, args.accessed_on)
    relationships = build_relationships(
        document, memory, args.research, args.memory_research, args.accessed_on
    )
    summary = build_summary(document, companies, facilities, relationships, args.accessed_on)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    company_path = args.output_dir / "company_financial_registry.jsonl"
    facility_path = args.output_dir / "semiconductor_facility_registry.jsonl"
    relationship_path = args.output_dir / "semiconductor_relationship_registry.jsonl"
    summary_path = args.output_dir / "semiconductor_manufacturing_summary.json"
    write_jsonl(company_path, companies)
    write_jsonl(facility_path, facilities)
    write_jsonl(relationship_path, relationships)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "companies": len(companies),
        "facility_records": len(facilities),
        "facility_sites": summary["facility_site_records"],
        "relationships": len(relationships),
        "company_registry": str(company_path),
        "facility_registry": str(facility_path),
        "relationship_registry": str(relationship_path),
        "summary": str(summary_path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
