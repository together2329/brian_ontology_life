#!/usr/bin/env python3
"""Audit global data-center research coverage against the OSM location baseline.

This builder does not turn OpenStreetMap objects into a world facility census.
It makes the remaining work reproducible: every non-empty OSM operator label is
counted, selected aliases are joined to reviewed profiles, unreviewed operators
are ranked, and country-level operator-tag gaps remain visible.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def canonical_label(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", folded.lower())


def entity(
    name: str,
    aliases: list[str],
    status: str,
    profile_refs: list[str],
    boundary: str,
) -> dict:
    return {
        "canonical_entity": name,
        "aliases": aliases,
        "research_status": status,
        "profile_refs": profile_refs,
        "coverage_boundary": boundary,
    }


PROFILED = [
    entity("Amazon_Web_Services", ["Amazon Web Services", "Amazon"], "reviewed_hyperscaler_profile", ["dc_aws_global_infrastructure_portfolio", "company_amazon", "aws_official_region_registry.jsonl"], "Cloud Regions, AZs and OSM objects are not one-to-one buildings."),
    entity("Microsoft", ["Microsoft"], "reviewed_hyperscaler_profile", ["dc_microsoft_global_datacenter_portfolio", "company_microsoft", "microsoft_official_region_registry.jsonl"], "Cloud Regions, AZs and OSM objects are not one-to-one buildings."),
    entity("Google", ["Google"], "reviewed_hyperscaler_profile", ["dc_google_global_data_center_portfolio", "company_alphabet", "google_official_location_registry.jsonl"], "Provider location labels and OSM objects can each cover different physical scopes."),
    entity("Meta", ["Meta", "Facebook"], "reviewed_hyperscaler_profile", ["dc_meta_global_data_center_portfolio", "company_meta", "meta_official_location_registry.jsonl"], "Owned-online, announced, leased and OSM scopes remain separate."),
    entity("Apple", ["Apple", "Apple Inc."], "reviewed_hyperscaler_profile", ["dc_apple_global_data_center_portfolio", "company_apple", "apple_official_location_registry.jsonl"], "Owned campuses, individual buildings and third-party capacity remain separate."),
    entity("Oracle", ["Oracle"], "reviewed_hyperscaler_profile", ["dc_oracle_oci_global_region_portfolio", "company_oracle", "oracle_official_region_registry.jsonl"], "OCI Regions and OSM physical objects use different granularities."),
    entity("Alibaba_Cloud", ["Alibaba", "Alibaba Cloud"], "reviewed_hyperscaler_profile", ["dc_alibaba_cloud_global_region_portfolio", "company_alibaba", "alibaba_official_region_registry.jsonl"], "A published zone can contain one or multiple scattered data centers."),
    entity("Tencent_Cloud", ["Tencent", "Tencent Cloud"], "reviewed_hyperscaler_profile", ["dc_tencent_cloud_global_region_portfolio", "company_tencent", "tencent_official_region_registry.jsonl"], "Region, AZ, owned, leased and OSM scopes remain separate."),
    entity("ByteDance_Volcano_Engine", ["ByteDance", "Volcano Engine"], "reviewed_hyperscaler_profile", ["dc_bytedance_volcano_engine_infrastructure_portfolio", "company_bytedance", "volcengine_official_region_registry.jsonl"], "Product endpoints and Region/AZ labels do not prove physical buildings."),
    entity("Equinix", ["Equinix"], "reviewed_physical_operator_profile", ["dc_equinix_global_ibx_xscale_portfolio", "company_equinix"], "OSM objects, IBX facilities and xScale programs are not automatically the same scope."),
    entity("Digital_Realty", ["Digital Realty", "Interxion"], "reviewed_physical_operator_profile", ["dc_digital_realty_global_portfolio", "company_digital_realty"], "Legacy Interxion labels are joined to the current parent only for research routing."),
    entity("NTT_Global_Data_Centers", ["NTT", "NTT Global Data Centers", "NTT Global Data Centres"], "reviewed_physical_operator_profile", ["dc_ntt_global_data_centers_portfolio", "company_ntt_data_group"], "OSM labels do not prove a current owned, operated or revenue-generating building."),
    entity("QTS", ["QTS", "Quality Technology Services"], "reviewed_physical_operator_profile", ["dc_qts_global_data_centers_portfolio", "company_qts", "qts_official_location_pages.jsonl"], "Official page candidates and OSM objects mix campuses, buildings and lifecycle."),
    entity("CyrusOne", ["CyrusOne"], "reviewed_physical_operator_profile", ["dc_cyrusone_global_portfolio", "company_cyrusone", "cyrusone_official_location_pages.jsonl"], "Published facility identifiers can share one official page or campus."),
    entity("Vantage_Data_Centers", ["Vantage", "Vantage Data Centers", "Vantage Data Centres"], "reviewed_physical_operator_profile", ["dc_vantage_global_data_centers_portfolio", "company_vantage_data_centers"], "Mixed-lifecycle campus design MW is not current utilized load."),
    entity("CoreSite", ["CoreSite"], "reviewed_physical_operator_profile", ["dc_coresite_american_tower_us_portfolio", "company_american_tower"], "Parent segment, facility card and OSM object scopes remain separate."),
    entity("EdgeConneX", ["EdgeConneX"], "reviewed_physical_operator_profile", ["dc_edgeconnex_global_portfolio", "company_edgeconnex"], "Public solution ranges do not disclose fleet operating MW."),
    entity("STACK_Infrastructure", ["Stack Infrastructure", "STACK Infrastructure"], "reviewed_physical_operator_profile", ["dc_stack_global_data_center_portfolio", "company_stack_infrastructure"], "Built, under-development, planned and potential capacity remain separate."),
    entity("Iron_Mountain_Data_Centers", ["Iron Mountain"], "reviewed_physical_operator_profile", ["dc_iron_mountain_global_data_centers_portfolio", "company_iron_mountain"], "Developable and potential capacity is not operating load."),
    entity("DataBank", ["DataBank"], "reviewed_physical_operator_profile", ["dc_databank_north_america_uk_portfolio", "company_databank_holdings"], "Current cards include explicit development and future facilities."),
    entity("NEXTDC", ["NextDC", "NEXTDC", "NEXTDC Sdn Bhd"], "reviewed_physical_operator_profile", ["dc_nextdc_apac_portfolio", "company_nextdc", "nextdc_official_facility_registry.jsonl"], "Provider labels and OSM points or footprints are not one-to-one physical buildings."),
    entity("Flexential", ["Flexential"], "reviewed_physical_operator_profile", ["dc_flexential_us_portfolio", "company_flexential", "flexential_official_facility_registry.jsonl"], "Current cards, OSM objects, physical buildings and the 28-asset securitized pool use different scopes."),
    entity("Lumen_Technologies", ["Lumen Technologies"], "reviewed_physical_operator_profile", ["dc_lumen_north_america_colocation_network_portfolio", "company_lumen_technologies", "lumen_colocation_market_registry.jsonl"], "Current web, 2025 market rows, OSM objects, divested overseas labels and third-party network reach use different scopes."),
    entity("DATA4", ["Data4", "data4", "Data4 Italia", "DATA4"], "reviewed_physical_operator_profile", ["dc_data4_european_portfolio", "company_data4"], "Published power terms vary between IT, reserve, total and available energy."),
    entity("AirTrunk", ["AirTrunk"], "reviewed_physical_operator_profile", ["dc_airtrunk_apac_portfolio", "company_airtrunk"], "Campus design capacity is not current live load."),
    entity("Aligned_Data_Centers", ["Aligned", "Aligned Data Centers", "Aligned Data Centres", "ODATA"], "reviewed_physical_operator_profile", ["dc_aligned_north_america_public_directory", "dc_odata_aligned_latam_portfolio", "company_aligned_data_centers"], "ODATA and Aligned labels are joined at current platform level, not treated as identical facility brands historically."),
    entity("Africa_Data_Centres", ["Africa Data Centres", "Africa Data Centers"], "reviewed_physical_operator_profile", ["dc_africa_data_centres_current_core_portfolio", "company_africa_data_centres"], "Official cards mix critical IT, available and completion measures."),
    entity("Khazna_Data_Centers", ["Khazna", "Khazna Data Centers", "Khazna Data Centres"], "reviewed_physical_operator_profile", ["dc_khazna_global_portfolio", "company_khazna_data_centers"], "Visible markers do not allocate the entire company portfolio headline."),
    entity("Gulf_Data_Hub", ["Gulf Data Hub"], "reviewed_physical_operator_profile", ["dc_gulf_data_hub_gcc_portfolio", "company_gulf_data_hub"], "Website visibility, ownership and lifecycle are different scopes."),
    entity("Ascenty", ["Ascenty"], "reviewed_physical_operator_profile", ["dc_ascenty_latam_portfolio", "company_ascenty"], "Per-building active load and economics remain undisclosed."),
    entity("Scala_Data_Centers", ["Scala Data Centers", "Scala Data Centres"], "reviewed_physical_operator_profile", ["dc_scala_latam_portfolio", "company_scala_data_centers"], "Future land and power announcements are not current capacity."),
    entity("DayOne_Firmus", ["DayOne", "DayOne Data Centers", "DayOne Data Centres", "Firmus"], "reviewed_physical_operator_profile", ["dc_firmus_dayone_batam_dsx", "company_dayone"], "Announced accelerator and capacity ceilings are not installed inventory."),
    entity("GDS_Holdings", ["GDS", "GDS Holdings"], "reviewed_physical_operator_profile", ["dc_gds_china_portfolio", "company_gds_holdings"], "Area utilization and powered-land capacity use different denominators."),
    entity("VNET_Group", ["VNET", "VNET Group", "21Vianet"], "reviewed_physical_operator_profile", ["dc_vnet_china_portfolio", "company_vnet_group"], "Wholesale MW and retail cabinets are not additive."),
    entity("Chindata", ["Chindata"], "reviewed_physical_operator_profile", ["dc_chindata_china_portfolio", "company_chindata_china"], "The reviewed company snapshot is dated and predates ownership changes."),
    entity("STT_GDC_India", ["STT GDC", "STT GDC India"], "reviewed_physical_operator_profile", ["dc_stt_gdc_india_portfolio", "company_stt_gdc_india"], "Operating, development and investment-plan scopes remain separate."),
    entity("CtrlS", ["CtrlS", "CtrlS Datacenters", "CtrlS Datacentres"], "reviewed_physical_operator_profile", ["dc_ctrls_india_portfolio", "company_ctrls_datacenters"], "Company and credit-analysis facility and MW scopes conflict."),
    entity("Yotta", ["Yotta", "Yotta Data Services"], "reviewed_physical_operator_profile", ["dc_yotta_india_portfolio", "company_nidar_yotta"], "Owned, operated and future facilities remain separate."),
    entity("Sify", ["Sify", "Sify Technologies"], "reviewed_physical_operator_profile", ["dc_sify_india_portfolio", "company_sify_technologies"], "Installed, sold and revenue-generating MW remain separate."),
    entity("xAI", ["xAI"], "reviewed_neocloud_profile", ["neocloud_disclosure_registry.jsonl"], "OSM facility objects and GPU-service disclosures require an object-level join."),
]


PRIORITY_GAPS = {
    canonical_label(name): (entity_name, priority)
    for entity_name, priority, names in [
        ("Centersquare", "P1", ["Centersquare", "CenterSquare"]),
        ("atNorth", "P1", ["atNorth"]),
        ("Switch", "P1", ["Switch"]),
        ("NorthC", "P1", ["NorthC"]),
        ("Telehouse", "P1", ["Telehouse"]),
        ("CDC_Data_Centres", "P1", ["CDC", "Canberra Data Centres"]),
        ("Cologix", "P1", ["Cologix"]),
        ("CloudHQ", "P1", ["CloudHQ"]),
        ("Sabey_Data_Centers", "P1", ["Sabey", "Sabey Data Centers"]),
        ("Global_Switch", "P1", ["Global Switch"]),
        ("KDDI", "P1", ["KDDI"]),
        ("OVHcloud", "P1", ["OVHcloud"]),
        ("Bouygues_Telecom", "P2", ["Bouygues Telecom", "Bouygues Télécom"]),
        ("SFR", "P2", ["SFR"]),
        ("Verizon", "P2", ["Verizon"]),
        ("Datacenter_United", "P2", ["Datacenter United"]),
        ("Ark_Data_Centres", "P2", ["Ark Data Centres"]),
        ("Pulsant", "P2", ["Pulsant"]),
        ("OPCORE", "P2", ["OPCORE"]),
        ("Orange", "P2", ["Orange"]),
        ("KIO", "P2", ["KIO"]),
        ("Teraco", "P2", ["Teraco"]),
        ("Colt", "P2", ["Colt"]),
        ("Redcentric", "P2", ["Redcentric"]),
        ("Virtus", "P2", ["Virtus"]),
        ("Spark_New_Zealand", "P2", ["Spark New Zealand"]),
        ("DataPro", "P2", ["DataPro"]),
        ("Rostelecom", "P2", ["Rostelecom"]),
        ("Selectel", "P2", ["Selectel"]),
        ("TierPoint", "P2", ["TierPoint"]),
        ("IDC_Frontier", "P2", ["IDCフロンティア"]),
        ("Leading_Edge_Data_Centres", "P2", ["Leading Edge Data Centres"]),
        ("DigiCo", "P2", ["DigiCo"]),
        ("IXcellerate", "P2", ["IXcellerate"]),
        ("Kao_Data", "P2", ["Kao Data"]),
        ("Prime_Data_Centers", "P2", ["Prime"]),
        ("Verne_Global", "P2", ["Verne Global"]),
    ]
    for name in names
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_alias_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for item in PROFILED:
        for alias in item["aliases"]:
            key = canonical_label(alias)
            assert key not in index or index[key]["canonical_entity"] == item["canonical_entity"], (alias, index[key]["canonical_entity"])
            index[key] = item
    return index


def country_codes(row: dict) -> list[str]:
    return sorted({candidate.get("iso2") for candidate in row.get("country_candidates", []) if candidate.get("iso2")})


def build_operator_records(rows: list[dict], accessed_on: str) -> list[dict]:
    alias_index = build_alias_index()
    counts = Counter()
    countries: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        label = (row.get("operator") or "").strip()
        if not label:
            continue
        counts[label] += 1
        countries[label].update(country_codes(row))
    output = []
    for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())):
        key = canonical_label(label)
        match = alias_index.get(key)
        gap = PRIORITY_GAPS.get(key)
        if match:
            status = match["research_status"]
            canonical_entity = match["canonical_entity"]
            priority = "covered_current_profile"
            profile_refs = match["profile_refs"]
            boundary = match["coverage_boundary"]
        elif gap:
            canonical_entity, priority = gap
            status = "priority_operator_profile_gap"
            profile_refs = []
            boundary = "OSM count establishes mapped objects only; official roster, lifecycle, MW, GPU, equipment and financial evidence still require review."
        else:
            canonical_entity = None
            priority = "untriaged"
            status = "raw_operator_label_not_yet_entity_resolved"
            profile_refs = []
            boundary = "The raw OSM operator label may be an owner, tenant, telecom, enterprise, public institution, legacy brand or spelling variant."
        output.append({
            "id": f"osm_operator_label_{hashlib.sha256(label.encode()).hexdigest()[:16]}",
            "object_type": "OSMOperatorLabelCoverageAudit",
            "raw_operator_label": label,
            "normalized_label": key,
            "canonical_entity": canonical_entity,
            "mapped_object_count": count,
            "country_codes": sorted(countries[label]),
            "country_count": len(countries[label]),
            "research_status": status,
            "research_priority": priority,
            "profile_refs": profile_refs,
            "coverage_boundary": boundary,
            "accessed_on": accessed_on,
        })
    return output


def build_country_records(rows: list[dict], accessed_on: str) -> list[dict]:
    totals = Counter()
    operator_tagged = Counter()
    construction = Counter()
    for row in rows:
        codes = country_codes(row)
        for code in codes:
            totals[code] += 1
            if row.get("operator"):
                operator_tagged[code] += 1
            if row.get("tags", {}).get("construction"):
                construction[code] += 1
    return [{
        "id": f"osm_country_{code.lower()}",
        "object_type": "OSMCountryCoverageAudit",
        "iso2": code,
        "mapped_object_count": totals[code],
        "operator_tagged_object_count": operator_tagged[code],
        "operator_untagged_object_count": totals[code] - operator_tagged[code],
        "operator_tag_coverage_percent": round(operator_tagged[code] / totals[code] * 100, 2),
        "construction_tagged_object_count": construction[code],
        "research_priority_signal": "high_object_count_or_low_operator_tag_coverage" if totals[code] >= 50 or operator_tagged[code] / totals[code] < 0.5 else "standard",
        "coverage_boundary": "Country assignment and object count are OSM-derived; neither proves a complete national facility roster or operating status.",
        "accessed_on": accessed_on,
    } for code in sorted(totals, key=lambda code: (-totals[code], code))]


def build_summary(rows: list[dict], operator_records: list[dict], country_records: list[dict], accessed_on: str) -> dict:
    with_operator = sum(1 for row in rows if row.get("operator"))
    reviewed_objects = sum(row["mapped_object_count"] for row in operator_records if row["research_status"].startswith("reviewed_"))
    priority_rows = [row for row in operator_records if row["research_status"] == "priority_operator_profile_gap"]
    priority_entities: dict[str, dict] = {}
    for row in priority_rows:
        item = priority_entities.setdefault(row["canonical_entity"], {"canonical_entity": row["canonical_entity"], "priority": row["research_priority"], "mapped_object_count": 0, "raw_labels": [], "country_codes": set()})
        item["mapped_object_count"] += row["mapped_object_count"]
        item["raw_labels"].append(row["raw_operator_label"])
        item["country_codes"].update(row["country_codes"])
    ranked = sorted(priority_entities.values(), key=lambda item: (item["priority"], -item["mapped_object_count"], item["canonical_entity"]))
    for rank, item in enumerate(ranked, 1):
        item["rank"] = rank
        item["raw_labels"] = sorted(item["raw_labels"])
        item["country_codes"] = sorted(item["country_codes"])
    objects_without_iso2 = sum(1 for row in rows if not country_codes(row))
    summary = {
        "schema_version": 1,
        "registry": "Global data-center research coverage and gap audit",
        "accessed_on": accessed_on,
        "baseline": {
            "osm_mapped_objects": len(rows),
            "iso2_country_records": len(country_records),
            "objects_with_operator_label": with_operator,
            "objects_without_operator_label": len(rows) - with_operator,
            "distinct_nonempty_raw_operator_labels": len(operator_records),
            "objects_without_resolved_iso2": objects_without_iso2,
        },
        "review_join": {
            "mapped_objects_whose_raw_operator_label_routes_to_a_reviewed_profile": reviewed_objects,
            "percent_of_all_mapped_objects": round(reviewed_objects / len(rows) * 100, 2),
            "percent_of_operator_tagged_mapped_objects": round(reviewed_objects / with_operator * 100, 2),
            "boundary": "Routing a raw label to a reviewed company or portfolio profile does not prove every OSM object was individually reconciled to an official facility record.",
        },
        "priority_unreviewed_operator_entities": ranked,
        "priority_method": "P1 core physical operators first, then P2 operators and telecom platforms; mapped-object count breaks ties but is not market share.",
        "next_sequence": [
            "Complete P1 official facility roster, lifecycle and scale profiles in ranked order.",
            "Join site-level power, cooling and accelerator evidence without converting readiness into installed inventory.",
            "Join audited company or parent financials and preserve segment boundaries.",
            "Resolve high-count raw labels and legacy subsidiaries before expanding low-count country tails.",
            "Refresh the OSM baseline separately; never describe it as every physical data center worldwide.",
        ],
        "non_completion_statement": "Public sources do not expose every physical building, GPU, utility feed, equipment BOM, customer contract or site profit. Unknown fields remain explicit research results.",
    }
    summary["operator_records_sha256"] = canonical_hash(operator_records)
    summary["country_records_sha256"] = canonical_hash(country_records)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--input", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    rows = load_rows(args.input)
    operator_records = build_operator_records(rows, args.accessed_on)
    country_records = build_country_records(rows, args.accessed_on)
    summary = build_summary(rows, operator_records, country_records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    operator_path = args.output_dir / "global_data_center_operator_coverage_audit.jsonl"
    country_path = args.output_dir / "global_data_center_country_coverage_audit.jsonl"
    summary_path = args.output_dir / "global_data_center_coverage_audit_summary.json"
    operator_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in operator_records), encoding="utf-8")
    country_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in country_records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"operator_labels": len(operator_records), "countries": len(country_records), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
