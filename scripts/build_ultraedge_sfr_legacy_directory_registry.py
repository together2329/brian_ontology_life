#!/usr/bin/env python3
"""Build UltraEdge's current directory and the legacy SFR OSM crosswalk.

UltraEdge's public pages expose several incompatible scopes: a 248-site
portfolio headline, 30+ data centers, 200+ POPs, 251 region-directory cards,
six Datapole metro summaries and the 257 data-center/office assets transferred
from SFR in 2024.  This builder preserves every denominator and prevents the
directory cards or OSM objects from becoming a false physical-building census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ABOUT = "https://www.ultraedge.com/about"
DIRECTORY = "https://www.ultraedge.com/datacenter"
PRESS = "https://www.ultraedge.com/press"
STANDARDS = "https://www.ultraedge.com/normes"
SERVICES = "https://www.ultraedge.com/offre-services"
PUE = "https://www.ultraedge.com/en/glossary/pue"
GCORE = "https://www.ultraedge.com/en/press/press-release/partenariat-gcore"
SFR_PARTNERSHIP = "https://www.ultraedge.com/press/press-release/partenariat-sfr"
ALTICE_Q2_2024 = "https://alticefrance.com/sites/default/files/pdf/Altice%20France%20Holding%20-%20Q2%202024%20condensed%20interim%20special%20purpose%20financial%20statements.pdf"
ALTICE_FY2024 = "https://alticefrance.com/sites/default/files/pdf/Altice_France_SA_FY_2024_Consolidated_Financial_Statements.pdf"
ALTICE_FY2025 = "https://static.s-sfr.fr/AlticeFrance/investors/financial-documentation/Altice-France-SAS-FY-2025-Consolidated-Financial-Statements.pdf"
ALTICE_FY2025_PRESS = "https://static.s-sfr.fr/AlticeFrance/investors/results-presentation/altice-france-q4-fy2025-press-release.pdf"
ALTICE_Q1_2026 = "https://static.s-sfr.fr/AlticeFrance/investors/results-presentation/260520-altice-france-q1-2026-press-release.pdf"
SFR_MOU = "https://www.corporate.bouyguestelecom.fr/archives-communique-presse/bouygues-telecom-franchit-une-etape-structurante-pour-son-developpement-futur-en-signant-aux-cotes-de-free-groupe-iliad-et-orange-un-protocole-daccord-avec-altice-france-en-vue-de-l/"


DATAPOLES = [
    {"metro": "Bordeaux", "published_power_MW": 5, "hosting_space_m2": 6000, "data_centers": 6},
    {"metro": "Lyon", "published_power_MW": 7, "hosting_space_m2": 12000, "data_centers": 7},
    {"metro": "Strasbourg", "published_power_MW": 3, "hosting_space_m2": 5000, "data_centers": 3},
    {"metro": "Paris", "published_power_MW": 12, "hosting_space_m2": 14000, "data_centers": 9},
    {"metro": "Rennes", "published_power_MW": 2.5, "hosting_space_m2": 3000, "data_centers": 4},
    {"metro": "Lille", "published_power_MW": 1.5, "hosting_space_m2": 1000, "data_centers": 2},
]


EXACT_OSM_CROSSWALK = {
    "osm_way_154149196": "Bordeaux Gabriel Péri",
    "osm_way_81784724": "Rennes",
    "osm_node_6102460998": "Strasbourg",
    "osm_way_80469752": "Vénissieux",
}


COURBEVOIE_CLUSTER_OSM = {"osm_way_700652111", "osm_node_2556825308"}


GEOGRAPHIC_CANDIDATES = {
    "osm_way_134684836": ["Nantes", "Nantes Rezé", "Nantes Rezé TDR", "Nantes-Saint-Herblain"],
    "osm_way_149298432": ["Dijon Longvic", "Dijon Neel"],
    "osm_way_160165248": ["Grenoble Saint-Martin 1", "Grenoble Saint-Martin 2"],
    "osm_way_160165252": ["Grenoble Saint-Martin 1", "Grenoble Saint-Martin 2"],
    "osm_way_75758209": ["Montpellier 1", "Montpellier 2"],
    "osm_way_84699719": ["Nantes", "Nantes Rezé", "Nantes Rezé TDR", "Nantes-Saint-Herblain"],
    "osm_relation_5888279": ["Vélizy"],
    "osm_way_73131890": ["Val-de-Reuil"],
    "osm_way_847106822": ["Trappes 1", "Trappes 2", "Trappes 3", "Trappes 4", "Trappes 5", "Trappes SF"],
    "osm_way_847113959": ["Trappes 1", "Trappes 2", "Trappes 3", "Trappes 4", "Trappes 5", "Trappes SF"],
    "osm_way_847120472": ["Achères 0", "Achères 1", "Achères 2", "Achères 3", "Achères 4"],
}


PORTFOLIO_CONTEXT = {
    "current_provider_headlines": {
        "owned_and_operated_sites": 248,
        "data_centers": "30_plus",
        "telecom_POPs": "200_plus",
        "deployed_IT_power_MW": 51,
        "hosting_space_m2": 35000,
        "Datapoles": 6,
    },
    "current_region_directory": {
        "cards": 251,
        "published_type_counts": {"Data center": 78, "Datacenter": 1, "IX Edge": 11, "POP": 161},
        "non_POP_cards": 90,
        "region_pages": 12,
        "boundary": "Cards are mixed edge-site labels, not a uniform current physical data-center building count.",
    },
    "six_Datapole_page_checksum": {
        "published_power_MW": 31,
        "hosting_space_m2": 41000,
        "data_centers": 31,
        "boundary": "Metro summaries conflict with or use a different scope from the 51-MW, 35,000-m2 and 30-plus portfolio headlines; values are not added or reconciled without a provider bridge.",
    },
    "ownership_and_transaction": {
        "sale_closed": "2024-05-23",
        "source_asset_scope": "257_datacenters_plus_office_space_then_operated_by_SFR",
        "Morgan_Stanley_Infrastructure_Partners_percent": 70,
        "Altice_France_SFR_retained_percent": 30,
        "total_consideration_EUR_million": 500,
        "reported_capital_gain_EUR_million": 313.1,
        "continuing_relationship": "SFR_build_to_suit_agreement_and_operating_or_service_relationship",
        "boundary": "Current UltraEdge ownership, SFR occupancy or service use, provider cards and the original 257-asset transaction perimeter are different scopes.",
    },
    "power_and_cooling": {
        "published": [
            "up_to_15_kW_per_rack_marketed_high_density",
            "direct_liquid_cooling_available_natively_at_selected_sites_depending_on_configuration_and_power",
            "closed_loop_chilled_water_and_water_reuse_where_water_cooling_is_used",
            "ISO_50001_claim",
            "average_PUE_1.5_to_1.9_claim",
            "new_extension_or_building_target_PUE_1.2_to_1.3",
        ],
        "undisclosed": [
            "site_level_live_or_measured_PUE_and_WUE",
            "absolute_energy_water_and_renewable_share",
            "utility_feeds_substations_transformers_switchgear",
            "UPS_battery_and_generator_counts_ratings_topology_and_OEMs",
            "cooling_equipment_counts_ratings_and_OEMs",
            "live_liquid_cooled_MW",
            "energized_leased_utilized_customer_accepted_and_billed_IT_load",
        ],
        "boundary": "Design capability, targets and deployed IT-power headlines are not measured live load or equipment inventory.",
    },
    "GPU_and_AI": {
        "direct_operator_owned_GPU_inventory_by_model_count_site_power_and_utilization": "undisclosed",
        "Gcore_partnership": "access_to_AI_infrastructure_with_NVIDIA_GPU_servers",
        "boundary": "The Gcore partnership and AI-ready design claims do not establish UltraEdge-owned GPUs, a model, count, host site, delivery state, power draw, utilization, revenue or margin.",
    },
    "comparison_boundary": "Do not add or equate 248 current sites, 251 directory cards, 257 transferred assets, 30-plus data centers, 90 non-POP cards, 200-plus POPs, 31 Datapole data centers or 17 SFR-tagged OSM objects.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def load_source(path: Path) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    assert source["accessed_on"]
    assert len(source["region_sources"]) == 12
    cards = source["cards"]
    assert len(cards) == 251
    assert Counter(row["published_type"] for row in cards) == Counter({
        "POP": 161, "Data center": 78, "IX Edge": 11, "Datacenter": 1,
    })
    assert [row["source_order"] for row in cards] == list(range(1, 252))
    return source


def build_records(source: dict, accessed_on: str) -> list[dict]:
    records = []
    for card in source["cards"]:
        records.append({
            "id": f"ultraedge_card_{card['source_order']:03d}_{slug(card['published_name'])}",
            "object_type": "ProviderPublishedMixedEdgeSiteCardRecord",
            **card,
            "provider": "UltraEdge",
            "current_provider_publication_status": "present_on_region_directory_at_access_date",
            "record_granularity": "provider_card_not_confirmed_physical_building",
            "ownership_boundary": "Provider publication supports an UltraEdge-marketed or operated edge-site label, not a property title, SFR tenancy, exact building count, live load or site economics.",
            "accessed_on": accessed_on,
        })
    assert len({row["id"] for row in records}) == len(records)
    return records


def load_sfr_osm(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    candidates = [row for row in rows if row.get("operator") == "SFR"]
    assert len(candidates) == 17, [row["id"] for row in candidates]
    return sorted(candidates, key=lambda row: row["id"])


def build_osm_reviews(osm_rows: list[dict], provider_names: set[str]) -> list[dict]:
    expected = set(EXACT_OSM_CROSSWALK) | COURBEVOIE_CLUSTER_OSM | set(GEOGRAPHIC_CANDIDATES)
    assert expected == {row["id"] for row in osm_rows}
    assert set(EXACT_OSM_CROSSWALK.values()) <= provider_names
    assert all(set(names) <= provider_names for names in GEOGRAPHIC_CANDIDATES.values())
    reviews = []
    for source in osm_rows:
        osm_id = source["id"]
        if osm_id in EXACT_OSM_CROSSWALK:
            disposition = "same_city_and_legacy_Netcenter_name_crosswalk_to_current_UltraEdge_card"
            confidence = "high_name_and_city_crosswalk_not_property_or_building_proof"
            candidates = [EXACT_OSM_CROSSWALK[osm_id]]
        elif osm_id in COURBEVOIE_CLUSTER_OSM:
            disposition = "Courbevoie_cluster_level_crosswalk_not_allocated_to_one_of_five_current_cards"
            confidence = "cluster_level_only"
            candidates = [f"Courbevoie {number}" for number in range(1, 6)]
        else:
            disposition = "geographic_or_legacy_candidate_unresolved_against_current_card_and_physical_building"
            confidence = "unresolved"
            candidates = GEOGRAPHIC_CANDIDATES[osm_id]
        reviews.append({
            "osm_object_id": osm_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "candidate_current_UltraEdge_cards": candidates,
            "disposition": disposition,
            "crosswalk_confidence": confidence,
            "boundary": "A legacy SFR OSM operator tag does not prove current SFR property ownership, UltraEdge ownership, exact building identity, lifecycle, capacity, GPU inventory or economics.",
        })
    return reviews


def build_summary(records: list[dict], source: dict, osm_reviews: list[dict], accessed_on: str) -> dict:
    type_counts = Counter(row["published_type"] for row in records)
    datapole_power = sum(row["published_power_MW"] for row in DATAPOLES)
    datapole_space = sum(row["hosting_space_m2"] for row in DATAPOLES)
    datapole_dcs = sum(row["data_centers"] for row in DATAPOLES)
    assert (datapole_power, datapole_space, datapole_dcs) == (31, 41000, 31)
    return {
        "registry": "UltraEdge current French region directory and SFR legacy OSM crosswalk",
        "accessed_on": accessed_on,
        "provider_directory_cards": len(records),
        "provider_directory_type_counts": dict(sorted(type_counts.items())),
        "provider_directory_region_pages": len(source["region_sources"]),
        "current_provider_headline_sites": 248,
        "current_provider_headline_data_centers": "30_plus",
        "current_provider_headline_telecom_POPs": "200_plus",
        "current_provider_headline_deployed_IT_power_MW": 51,
        "current_provider_headline_hosting_space_m2": 35000,
        "source_transaction_asset_scope": 257,
        "provider_scope_conflict": PORTFOLIO_CONTEXT["comparison_boundary"],
        "Datapoles": DATAPOLES,
        "Datapole_checksum": {
            "published_power_MW": datapole_power,
            "hosting_space_m2": datapole_space,
            "data_centers": datapole_dcs,
            "conflict_boundary": PORTFOLIO_CONTEXT["six_Datapole_page_checksum"]["boundary"],
        },
        "SFR_operator_tagged_OSM_objects": len(osm_reviews),
        "exact_name_and_city_crosswalks": sum(row["crosswalk_confidence"].startswith("high_") for row in osm_reviews),
        "Courbevoie_cluster_crosswalks": sum(row["crosswalk_confidence"] == "cluster_level_only" for row in osm_reviews),
        "unresolved_geographic_or_legacy_candidates": sum(row["crosswalk_confidence"] == "unresolved" for row in osm_reviews),
        "osm_reviews": osm_reviews,
        "portfolio_context": PORTFOLIO_CONTEXT,
        "UltraEdge_financial_snapshots_EUR_million": {
            "provider_press_page_2025_revenue": {
                "revenue": 160,
                "boundary": "Current provider press-page headline; reporting basis and timing are not disclosed sufficiently to reconcile to the associate note.",
            },
            "Altice_30_percent_associate_note_2025_unaudited": {
                "revenue": 140.4,
                "net_income": 0.3,
                "equity": 701.8,
                "cash_negative_or_net_debt_positive": 115.3,
                "total_equity_and_liabilities": 999.0,
                "Altice_carrying_value": 210.5,
            },
            "Altice_30_percent_associate_note_2024_comparative": {
                "revenue": 86.4,
                "net_income": -9.9,
                "equity": 701.6,
                "cash_negative_or_net_debt_positive": 222.9,
                "total_equity_and_liabilities": 927.7,
                "Altice_carrying_value": 211.4,
            },
            "boundary": "The EUR160m provider headline and EUR140.4m unaudited associate-note revenue conflict and remain separate pending a reporting-period and consolidation-basis bridge. Net income is not operating profit.",
        },
        "Altice_France_SFR_FY2025_accounting_EUR_million": {
            "revenue": 9382.4,
            "adjusted_EBITDA": 3071.5,
            "depreciation_amortization_and_impairment": 2975.2,
            "other_expenses_and_income": -553.3,
            "rental_expense_reversal": 1277.2,
            "operating_profit": 820.2,
            "net_income": -1574.6,
            "accrued_capex": 1560.1,
            "cash_payments_for_tangible_intangible_assets_and_contract_costs": 1824.5,
            "boundary": "Audited accounting perimeter; 2024 operating profit included large disposal gains and is not a clean recurring comparator. These figures are not UltraEdge-only economics.",
        },
        "Altice_France_SFR_Q1_2026_investor_pro_forma_EUR_million": {
            "revenue": 2164,
            "revenue_change_percent": -9.1,
            "adjusted_EBITDA": 583,
            "adjusted_EBITDA_change_percent": -13.1,
            "adjusted_EBITDA_margin_percent": 26.9,
            "accrued_capex": 323,
            "OpFCF": 260,
            "business_services_revenue": 705,
            "pro_forma_net_debt": 15542,
            "actual_net_debt": 15603,
            "weighted_average_cost_of_debt_percent": 7.7,
            "last_twelve_months_pro_forma_EBITDA": 2845,
            "net_leverage_multiple": 5.5,
            "boundary": "Investor pro-forma restricted-group measures are not the audited accounting presentation and are not UltraEdge-only results.",
        },
        "announced_SFR_acquisition_MOU": {
            "consortium": ["Bouygues_Telecom", "Orange", "Free_Groupe_iliad"],
            "enterprise_value_EUR_billion": 20.35,
            "earnout_up_to_EUR_million": 650,
            "expected_close": "H2_2027_subject_to_conditions_and_approvals",
            "UltraEdge": "explicitly_excluded",
        },
        "official_sources": [
            ABOUT, DIRECTORY, PRESS, STANDARDS, SERVICES, PUE, GCORE,
            SFR_PARTNERSHIP, ALTICE_Q2_2024, ALTICE_FY2024, ALTICE_FY2025,
            ALTICE_FY2025_PRESS, ALTICE_Q1_2026, SFR_MOU,
            *[row["source_url"] for row in source["region_sources"]],
        ],
        "source_snapshot_sha256": canonical_hash(source),
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("life/imports/global_data_centers_20260717/ultraedge_current_region_directory_source.json"))
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/ultraedge_current_region_directory_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/ultraedge_current_region_directory_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    source = load_source(args.source)
    records = build_records(source, args.accessed_on)
    osm_rows = load_sfr_osm(args.osm)
    osm_reviews = build_osm_reviews(osm_rows, {row["published_name"] for row in records})
    summary = build_summary(records, source, osm_reviews, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_reviews": len(osm_reviews), "registry": str(args.registry), "summary": str(args.summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
