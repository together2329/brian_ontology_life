#!/usr/bin/env python3
"""Build a scope-preserving data-center power and cooling supply-chain index.

The financial research file remains the canonical evidence ledger.  This builder
joins its industrial and utility profiles into one deterministic comparison layer
while keeping group revenue, segment results, backlog, agreements, equipment
nameplate and physical data-center load as different measures.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


def spec(
    financial_ref: str,
    primary_category: str,
    value_pool: str,
    bottleneck: str,
    exposure_boundary: str,
) -> dict:
    return {
        "financial_profile_ref": financial_ref,
        "primary_category": primary_category,
        "value_pool": value_pool,
        "bottleneck": bottleneck,
        "exposure_boundary": exposure_boundary,
    }


SPECS = [
    spec("company_vertiv", "critical_power_and_electrical", "UPS, switchgear, power distribution, racks and liquid or air thermal systems", "high-density capacity depends on integrated power delivery and heat removal", "Broad critical-infrastructure exposure is not disclosed data-center-only revenue or profit."),
    spec("company_schneider_electric", "critical_power_and_electrical", "energy management, switchgear, UPS, prefabricated modules, controls and cooling", "electrical architecture and cooling controls must scale together", "Group, Energy Management and backlog totals include non-data-center demand; a customer case does not quantify vendor revenue."),
    spec("company_eaton", "critical_power_and_electrical", "switchgear, busway, breakers, UPS, power distribution and thermal systems", "electrical interconnection and distribution capacity constrain delivery", "Electrical segment orders and company results are not a separately reported data-center P&L."),
    spec("company_abb", "critical_power_and_electrical", "medium-voltage equipment, switchgear, automation and direct-current architecture", "grid-to-rack conversion and protection must support larger, denser loads", "Data-center order growth is a demand signal; it is not disclosed recognized revenue, margin or installed load."),
    spec("company_siemens_energy", "critical_power_and_electrical", "grid equipment, transformers, substations and generation systems", "long-lead grid and transformer supply can gate campus energization", "Grid Technologies and group results cover many end markets; backlog is not data-center revenue."),
    spec("company_ls_electric", "critical_power_and_electrical", "transformers, switchgear, distribution and automation", "North American transformer and switchgear availability gates utility and campus expansion", "Company backlog and product backlog are not site allocations, shipments, accepted equipment or revenue."),
    spec("company_hd_hyundai_electric", "critical_power_and_electrical", "power transformers, distribution transformers and switchgear", "large-transformer manufacturing capacity is a long-cycle grid bottleneck", "North American demand and total backlog do not disclose a data-center-specific order book or site bill of materials."),
    spec("company_ge_vernova", "onsite_and_backup_generation", "gas turbines, transformers, substations, switchgear and grid integration", "campuses require both bulk grid capacity and resilient on-site generation", "Company revenue is not data-center revenue; equipment orders are not recognized revenue, and turbine nameplate is not IT load."),
    spec("company_caterpillar", "onsite_and_backup_generation", "large reciprocating engines, turbines and generator systems", "backup and prime-power availability can gate campus commissioning", "Power and Energy segment results include non-data-center markets; equipment capacity is not facility IT capacity."),
    spec("company_cummins", "onsite_and_backup_generation", "generator sets, engines, alternators and power systems", "large-load sites require dispatchable backup or bridge power", "Power Systems results include diverse applications and do not disclose data-center-only revenue or margins."),
    spec("company_bloom_energy", "onsite_and_backup_generation", "solid-oxide fuel-cell generation and on-site power systems", "behind-the-meter generation can bridge slow grid interconnection", "Master-agreement and backlog ceilings are not delivered systems or revenue; generation nameplate is not critical IT load."),
    spec("company_lg_electronics", "cooling_and_thermal", "chillers, coolant distribution units and HVAC systems", "high-density AI racks move the bottleneck from room cooling to liquid heat rejection", "The DataVolt relationship is an MOU, not an order, backlog, shipment or recognized revenue; group and Eco Solution results remain broader."),
    spec("company_modine", "cooling_and_thermal", "Airedale chillers, cooling systems and coolant distribution units", "liquid-cooled deployments need scalable heat rejection and distribution", "Data-center sales growth does not establish site allocations or a complete data-center segment P&L."),
    spec("company_trane_technologies", "cooling_and_thermal", "chillers, applied equipment and thermal-management services", "large-campus thermal plants must be delivered before dense compute ramps", "Applied-equipment bookings and group backlog span multiple building markets and are not recognized data-center revenue."),
    spec("company_johnson_controls", "cooling_and_thermal", "chillers, building automation, controls and liquid-cooling integration", "cooling plant, controls and commissioning determine usable high-density capacity", "Large-project orders and total backlog are not data-center-only revenue, margin or installed equipment."),
    spec("company_prysmian", "cable_and_connectivity", "high-voltage cable, building wire and fiber connectivity", "grid expansion and intra-campus power or optical links require cable capacity", "Industrial, construction and Digital Solutions results include many applications; growth attribution does not yield a data-center P&L."),
    spec("company_nexans", "cable_and_connectivity", "transmission, distribution and building electrification cable", "grid reinforcement and campus distribution depend on long-lead cable systems", "Standard-metal and current-metal sales use different accounting presentations and do not isolate data-center revenue."),
    spec("company_constellation_energy", "utilities_and_generation", "firm generation, retail supply and clean-energy contracting", "round-the-clock large-load supply needs dispatchable generation and market access", "Generation fleet scale and customer agreements are not dedicated data-center capacity or site-level revenue without allocation evidence."),
    spec("company_dte_energy", "utilities_and_generation", "regulated electric delivery, generation and storage obligations", "utility interconnection, substation construction and cost recovery gate energization", "Contracted load is not current energized, utilized or billed demand; regulatory and construction milestones remain required."),
    spec("company_wec_energy_group", "utilities_and_generation", "regulated generation, transmission interface and electric delivery", "multi-gigawatt campuses require staged utility buildout and rate-base approval", "Critical-IT design, projected load and long-term potential use different scopes and are not added as current demand."),
    spec("company_dominion_energy", "utilities_and_generation", "regulated generation, transmission and distribution service", "Northern Virginia delivery is constrained by substations, transmission and generation", "Substation nameplate is not campus IT load, and the proposed NextEra transaction remains pending rather than consolidated."),
    spec("company_tenaga_nasional", "utilities_and_generation", "national-grid supply, transmission and data-center interconnection", "Malaysia's campus pipeline depends on grid connection and generation availability", "Planned supply and maximum demand are not current energized or utilized IT load; group results are not data-center earnings."),
    spec("company_nextera_energy", "utilities_and_generation", "generation, renewables, storage, transmission and large-load development", "large-load hubs need generation and transmission buildout ahead of demand", "Development pipelines and a proposed Dominion combination are forward-looking; they are not current site supply or combined financials."),
    spec("company_evergy", "utilities_and_generation", "regulated electric service and large-load interconnection", "new campuses require interconnection, approved tariffs and timely capacity additions", "Commercial-load growth and service agreements do not establish current campus demand, revenue or asset returns."),
    spec("company_entergy", "utilities_and_generation", "regulated electric service, generation and transmission", "large Gulf-region campuses require generation, transmission and regulatory cost recovery", "Service agreements and announced projects are not energized demand, billed revenue or completed rate-base assets."),
]


SNAPSHOT_KEYS = (
    "fiscal_baseline",
    "latest_update",
    "FY2025_results",
    "Q1_2026_results",
    "Q2_2026_preliminary_results",
)

COMPARISON_CONTRACT = {
    "financial": "Preserve currency, fiscal period and GAAP, IFRS, K-IFRS or adjusted basis; do not sum currencies without an explicit FX date.",
    "revenue": "Group and segment revenue are not data-center revenue unless the company reports that boundary.",
    "commercial": "Orders, backlog, pipeline, MOU, master agreement and service agreement are not recognized revenue.",
    "power": "Generation, transformer, substation, utility-service and equipment nameplate are not critical IT load.",
    "lifecycle": "Planned, contracted, ordered, shipped, installed, energized, accepted, utilized and billed remain separate states.",
}

COMMON_GAPS = [
    "data-center-specific revenue, operating profit, cash flow and return on invested capital",
    "order and backlog allocation by customer, campus, equipment model and delivery state",
    "site-level transformer, switchgear, UPS, battery, generator, chiller and CDU bill of materials",
    "current energized, accepted, utilized and billed IT load linked to utility and equipment records",
    "supplier capacity, lead time, price, cancellation rights, warranty and commissioning evidence",
    "utility interconnection, permit, tariff, cost-recovery and in-service milestones",
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


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


def load_index(path: Path, key: str) -> dict[str, dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {row["id"]: row for row in document[key]}


def financial_snapshots(profile: dict) -> dict:
    return {key: profile[key] for key in SNAPSHOT_KEYS if key in profile}


def build_records(finance_path: Path, landscape_path: Path, accessed_on: str) -> list[dict]:
    finance = load_index(finance_path, "financial_profiles")
    landscape = load_index(landscape_path, "campus_profiles")
    assert len(SPECS) == 25
    assert len({row["financial_profile_ref"] for row in SPECS}) == len(SPECS)
    records = []
    for position, source in enumerate(SPECS, start=1):
        profile = finance[source["financial_profile_ref"]]
        exposure = profile.get("data_center_exposure", {})
        campus_refs = exposure.get("confirmed_campus_refs", [])
        missing_campuses = [ref for ref in campus_refs if ref not in landscape]
        assert not missing_campuses, (profile["id"], missing_campuses)
        urls = collect_urls(profile.get("sources", []))
        assert urls, profile["id"]
        records.append({
            "id": f"supply_chain_{profile['id'].removeprefix('company_')}",
            "object_type": "DataCenterPowerCoolingSupplyChainProfile",
            "source_order": position,
            "company": profile["company"],
            **source,
            "financial_snapshots": financial_snapshots(profile),
            "data_center_exposure": exposure,
            "management_outlook": profile.get("management_outlook"),
            "watch_items": profile.get("watch_items", []),
            "confirmed_campus_refs": campus_refs,
            "official_evidence_urls": urls,
            "official_evidence_url_count": len(urls),
            "financial_profile_sha256": canonical_hash(profile),
            "comparison_contract": COMPARISON_CONTRACT,
            "common_unresolved_gaps": COMMON_GAPS,
            "accessed_on": accessed_on,
        })
    return records


def build_summary(records: list[dict], accessed_on: str) -> dict:
    categories = Counter(row["primary_category"] for row in records)
    return {
        "registry": "Data-center power, electrical, cooling, cable and utility supply-chain crosswalk",
        "accessed_on": accessed_on,
        "company_records": len(records),
        "primary_category_counts": dict(sorted(categories.items())),
        "companies_with_confirmed_campus_refs": [row["company"] for row in records if row["confirmed_campus_refs"]],
        "official_evidence_url_count": len({url for row in records for url in row["official_evidence_urls"]}),
        "no_group_revenue_sum": True,
        "no_backlog_or_agreement_to_revenue_conversion": True,
        "no_equipment_or_utility_nameplate_to_IT_load_conversion": True,
        "comparison_gate": [
            "Choose one accounting and currency basis.",
            "Choose one product or utility-service value pool.",
            "Choose one commercial and delivery lifecycle.",
            "Require a site or segment allocation before claiming data-center economics.",
        ],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--finance", type=Path, default=Path("life/finance/ai_data_center_supply_chain_financials_202607.yaml"))
    parser.add_argument("--landscape", type=Path, default=Path("life/knowledge/global_ai_data_center_landscape_202607.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.finance, args.landscape, args.accessed_on)
    summary = build_summary(records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "power_cooling_supply_chain_registry.jsonl"
    summary_path = args.output_dir / "power_cooling_supply_chain_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
