#!/usr/bin/env python3
"""Build a scope-safe TelemaxX facility, engineering, finance and OSM registry.

TelemaxX currently describes four high-security data centers used for housing,
while its directory also retains POP Technologiepark Karlsruhe (former IPC2).
This builder keeps the five named locations and their OSM objects, but excludes
the former IPC2 network POP from the current data-center count.  Published
usable-area, energy, equipment and financial values retain their original
portfolio, site-group and legal-entity boundaries.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://www.telemaxx.de/"
DIRECTORY = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentren-der-telemaxx"
DATACENTER = "https://www.telemaxx.de/services/rechenzentrum/datacenter"
CERTIFICATIONS = "https://www.telemaxx.de/services/rechenzentrum/datacenter/zertifizierungen"
INFRASTRUCTURE = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentrum-infrastruktur"
IPC1 = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentren-der-telemaxx/ipc-1"
IPC2 = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentren-der-telemaxx/ipc-2"
IPC3 = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentren-der-telemaxx/ipc-3"
IPC4 = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentren-der-telemaxx/ipc-4"
IPC5 = "https://www.telemaxx.de/services/rechenzentrum/datacenter/rechenzentren-der-telemaxx/ipc-5"
IPC4_ADDRESS = "https://www.telemaxx.de/ueber-uns/aktuelles/veranstaltungen/07052026-customer-excellence-forum-mit-rechenzentrumsfuehrung"
FACTSHEET = "https://www.telemaxx.de/fileadmin/docs/Flyer/TelemaxX_Factsheet_Rechenzentren.pdf"
EMAS_2026 = "https://www.telemaxx.de/fileadmin/docs/EMAS/TXX_Umwelterklaerung_2026_01.pdf"
SHAREHOLDERS = "https://www.telemaxx.de/ueber-uns/unternehmen/gesellschafter"
PARTNERS = "https://www.telemaxx.de/ueber-uns/partner"
OPEN_CLOUD = "https://www.telemaxx.de/services/cloud/telemaxx-opencloud/opencloud-kosten"
AI_EVENT = "https://www.telemaxx.de/ueber-uns/aktuelles/veranstaltungen/25072025-ki-anwendungen-auf-telemaxx-opencloud-mit-rechenzentrumsfuehrung"
LIQUID_COOLING_EDUCATION = "https://www.telemaxx.de/academy/wissen/rechenzentrum/klimatisierung"
FINANCE_EXTRACT = "https://handelsregister.ai/de/organizations/karlsruhe/bau-von-versorgungseinrichtungen-fuer-elektrizitaet-und-telekommunikation/telemaxx-telekommunikation-gmbh-2ee96e3e04be3411618451185817e3ef"
OPEN_REGISTER = "https://openregister.de/company/DE-HRB-B1601-108481"


FACILITIES = [
    {
        "id": "telemaxx_ipc1",
        "object_type": "DataCenterFacilityEvidence",
        "operator": "TelemaxX Telekommunikation GmbH",
        "facility_label": "IPC1",
        "city": "Karlsruhe",
        "country": "Germany",
        "country_code": "DE",
        "address": "Karlsruhe 76189; exact street address not established in reviewed official sources",
        "lifecycle": "current_housing_scope_certified_but_not_actively_marketed_for_new_colocation",
        "current_high_security_data_center_count_inclusion": True,
        "active_new_colocation_marketing": False,
        "published_data_center_usable_area_m2": 1200,
        "published_rack_ceiling": None,
        "availability_percent": 99.65,
        "electrical_and_cooling_redundancy": "N_plus_1",
        "equipment_evidence": {
            "fire_compartments": 4,
            "UPS_emergency_power_and_cooling": "present_without_reviewed_site_specific_model_count_or_rating",
            "complete_as_built_BOM": "undisclosed",
        },
        "certifications": ["ISO_27001_2024_colocation_scope"],
        "source_urls": [IPC1, CERTIFICATIONS, DATACENTER],
    },
    {
        "id": "telemaxx_pop_tpk_former_ipc2",
        "object_type": "NetworkPointOfPresenceEvidence",
        "operator": "TelemaxX Telekommunikation GmbH",
        "facility_label": "POP Technologiepark Karlsruhe (former IPC2)",
        "city": "Karlsruhe",
        "country": "Germany",
        "country_code": "DE",
        "address": "Karlsruhe 76131; exact street address not established in reviewed official sources",
        "lifecycle": "current_network_POP_former_data_center_not_current_housing_facility",
        "current_high_security_data_center_count_inclusion": False,
        "active_new_colocation_marketing": False,
        "historical_role": "former_redundancy_data_center_for_IPC1",
        "current_role": "network_point_of_presence",
        "certifications": [],
        "counting_boundary": "The provider directory retains this named location, but the current page identifies a network POP and does not market housing or list a current data-center certification.",
        "source_urls": [IPC2, DIRECTORY, CERTIFICATIONS, DATACENTER],
    },
    {
        "id": "telemaxx_ipc3",
        "object_type": "DataCenterFacilityEvidence",
        "operator": "TelemaxX Telekommunikation GmbH",
        "facility_label": "IPC3",
        "city": "Karlsruhe",
        "country": "Germany",
        "country_code": "DE",
        "address": "Karlsruhe 76227; exact street address not established in reviewed official sources",
        "lifecycle": "current_active_colocation_data_center",
        "current_high_security_data_center_count_inclusion": True,
        "active_new_colocation_marketing": True,
        "published_data_center_usable_area_m2": 1600,
        "published_rack_ceiling": 600,
        "rack_boundary": "Approximately 600 racks at full occupancy is a design or fit-out ceiling, not a current installed, leased or utilized rack count.",
        "availability_percent": 99.9,
        "electrical_and_cooling_redundancy": "N_plus_1",
        "equipment_evidence": {
            "build_sections": 4,
            "build_section_area_m2": 400,
            "floors": 2,
            "raised_floor_cm": 70,
            "medium_voltage": "one_20kV_ring_simple",
            "transformers": "N_plus_1; infrastructure page describes 2000_kVA_transformer_units_without_complete_site_unit_count",
            "emergency_generation": "simple_topology_with_96_hour_fuel_autonomy",
            "UPS_full_load_autonomy_minutes_up_to": 30,
            "cooling": "cold_and_hot_aisles_cold_aisle_containment_N_plus_1_chillers_physically_ringed_glycol_water_network_and_supply_exhaust_air",
            "chiller_buildout": "5_plus_1_with_up_to_five_440_kW_chillers",
            "climate_units": "up_to_10_units_and_850_kW_total_per_section_as_page_worded",
            "complete_as_built_BOM": "undisclosed",
        },
        "certifications": ["ISO_27001_2024_colocation_scope", "ISAE_3402_Type_2_portfolio_scope"],
        "source_urls": [IPC3, FACTSHEET, INFRASTRUCTURE, CERTIFICATIONS],
    },
    {
        "id": "telemaxx_ipc4",
        "object_type": "DataCenterFacilityEvidence",
        "operator": "TelemaxX Telekommunikation GmbH",
        "facility_label": "IPC4",
        "city": "Karlsruhe",
        "country": "Germany",
        "country_code": "DE",
        "address": "Ohmstrasse 1, 76229 Karlsruhe",
        "lifecycle": "current_active_colocation_data_center",
        "current_high_security_data_center_count_inclusion": True,
        "active_new_colocation_marketing": True,
        "published_data_center_usable_area_m2": 3000,
        "published_rack_ceiling": None,
        "availability_percent": 99.99,
        "electrical_and_cooling_redundancy": "N_plus_1",
        "equipment_evidence": {
            "fire_compartments": 4,
            "medium_voltage": "one_20kV_ring_with_redundant_transfer_and_metering",
            "transformers": "N_plus_1; infrastructure page describes 2000_kVA_transformer_units_without_complete_site_unit_count",
            "emergency_generation": "N_plus_1_with_96_hour_fuel_autonomy",
            "UPS_full_load_autonomy_minutes_up_to": 30,
            "cooling": "cold_and_hot_aisles_cold_aisle_containment_N_plus_1_chillers_air_handling_and_water_ring",
            "2025_efficiency_upgrade": "two_new_efficient_chillers_installed_at_end_2025_with_more_planned",
            "complete_as_built_BOM": "undisclosed",
        },
        "certifications": ["ISO_27001_2024_colocation_scope", "ISAE_3402_Type_2_portfolio_scope"],
        "source_urls": [IPC4, IPC4_ADDRESS, FACTSHEET, INFRASTRUCTURE, CERTIFICATIONS, EMAS_2026],
    },
    {
        "id": "telemaxx_ipc5",
        "object_type": "DataCenterFacilityEvidence",
        "operator": "TelemaxX Telekommunikation GmbH",
        "facility_label": "IPC5",
        "city": "Stutensee",
        "country": "Germany",
        "country_code": "DE",
        "address": "Stutensee 76297; Friedrich-List-Strasse 12 appears in OSM or third-party records but was not established by a reviewed provider page",
        "lifecycle": "current_active_colocation_data_center",
        "current_high_security_data_center_count_inclusion": True,
        "active_new_colocation_marketing": True,
        "published_data_center_usable_area_m2": 2000,
        "published_rack_ceiling": None,
        "availability_percent": 99.99,
        "electrical_and_cooling_redundancy": "2N_or_1_plus_1_as_component_worded",
        "equipment_evidence": {
            "fire_compartments": 4,
            "medium_voltage": "two_20kV_rings_with_redundant_transfer_and_metering",
            "transformers": "1_plus_1",
            "emergency_generation": "1_plus_1_with_120_hour_fuel_autonomy",
            "UPS_full_load_autonomy_minutes_up_to": 30,
            "cooling": "cold_and_hot_aisles_cold_aisle_containment_1_plus_1_chillers_air_handling_and_water_ring",
            "onsite_solar_pv_kWp": 130,
            "onsite_solar_generation_2025_MWh": 114,
            "complete_as_built_BOM": "undisclosed",
        },
        "certifications": ["ISO_27001_2024_colocation_scope", "ISAE_3402_Type_2_portfolio_scope", "TUEV_TSI_Level_3_extended", "EN_50600_availability_class_3"],
        "source_urls": [IPC5, FACTSHEET, CERTIFICATIONS, EMAS_2026],
    },
]


OSM_CROSSWALK = {
    "osm_way_51763539": ("telemaxx_ipc1", "current_housing_facility_exact_name_and_locality_candidate"),
    "osm_node_4231017085": ("telemaxx_pop_tpk_former_ipc2", "current_network_POP_with_legacy_data_center_tag"),
    "osm_way_334161493": ("telemaxx_ipc3", "current_active_colocation_facility_exact_name_candidate"),
    "osm_way_258148708": ("telemaxx_ipc4", "current_active_colocation_facility_exact_name_candidate"),
    "osm_way_549728082": ("telemaxx_ipc5", "current_active_colocation_facility_exact_name_and_locality_candidate"),
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = [{"source_order": position, **row, "installed_GPU_inventory": "not_disclosed_or_established", "accessed_on": accessed_on} for position, row in enumerate(FACILITIES, 1)]
    assert len(records) == 5
    assert sum(bool(row["current_high_security_data_center_count_inclusion"]) for row in records) == 4
    assert sum(row.get("published_data_center_usable_area_m2") or 0 for row in records) == 7800
    assert sum(row.get("published_rack_ceiling") or 0 for row in records) == 600
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (registry_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "registry_ref": registry_ref,
            "classification": classification,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "start_date": source.get("tags", {}).get("start_date"),
            "counting_rule": "OSM preserves public location evidence but adds no facility, usable-area, rack, MW or GPU count. The IPC2 point is a current network POP, not a fifth current housing data center.",
        })
    assert len(rows) == 5
    assert Counter(row["raw_operator"] for row in rows) == {"TelemaxX Telekommunikation GmbH": 5}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    current = [row for row in records if row["current_high_security_data_center_count_inclusion"]]
    marketed = [row for row in current if row["active_new_colocation_marketing"]]
    return {
        "id": "telemaxx_official_facility_summary_2026_07_19",
        "operator": "TelemaxX Telekommunikation GmbH",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "provider_directory_rows": len(records),
            "current_high_security_data_centers": len(current),
            "current_housing_scope_codes": [row["facility_label"] for row in current],
            "active_new_colocation_marketing_codes": [row["facility_label"] for row in marketed],
            "network_POP_former_data_center_rows": 1,
            "current_page_numeric_usable_area_checksum_m2": sum(row.get("published_data_center_usable_area_m2") or 0 for row in current),
            "homepage_colocation_area_claim_m2": "more_than_8000",
            "publication_conflict": "The four current facility pages sum to 7,800 square metres, while current company material says more than 8,000 square metres. No hidden area is invented to reconcile the 200-plus-square-metre gap.",
            "boundary": "Facility-page usable area, homepage colocation area, EMAS scoped usable area, land area, OSM footprints and available or utilized whitespace are different measures.",
        },
        "engineering": {
            "factsheet_detailed_site_scope": ["IPC3", "IPC4", "IPC5"],
            "medium_voltage": {"IPC3": "one_simple_20kV_ring", "IPC4": "one_20kV_ring_redundant_transfer_metering", "IPC5": "two_20kV_rings_redundant_transfer_metering"},
            "transformers": {"IPC3": "N_plus_1", "IPC4": "N_plus_1", "IPC5": "1_plus_1", "published_unit_rating_kVA_without_complete_site_count": 2000},
            "emergency_generation": {"IPC3": "simple_96_hours", "IPC4": "N_plus_1_96_hours", "IPC5": "1_plus_1_120_hours"},
            "EMAS_generator_count": {"company_scope_total": 11, "A41_group_IPC1_IPC3_IPC5": 6, "O1_group_IPC4": 5, "site_allocation_inside_A41_group": "undisclosed"},
            "UPS_full_load_autonomy_minutes_up_to": 30,
            "IPC3_chillers": "5_plus_1_buildout_with_up_to_five_440_kW_units",
            "complete_as_built_per_site_grid_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_loading_acceptance_and_remaining_life": "undisclosed",
        },
        "environment_and_operating_energy_2025": {
            "reporting_scope": "four_data_centers_plus_offices_unless_more_narrowly_labeled",
            "total_scoped_usable_area_m2": 9993,
            "data_center_electricity_MWh": 29487,
            "customer_IT_energy_MWh": 19860,
            "cooling_energy_MWh": 5164,
            "emergency_generator_preheat_energy_MWh": 243,
            "customer_IT_share_percent_derived": 67.352,
            "cooling_share_percent_derived": 17.513,
            "customer_IT_energy_growth_2024_to_2025_percent_derived": 4.554,
            "annual_average_customer_IT_load_MW_derived": 2.267,
            "annual_energy_ratio_total_DC_electricity_to_customer_IT_energy_derived": 1.485,
            "ratio_boundary": "The average load and energy ratio are analyst calculations from annual MWh. The ratio is not provider-reported PUE and neither value is installed, peak, available or billable MW.",
            "electricity_procurement": "100_percent_renewable_electricity_since_2024_via_TUEV_certified_guarantees_of_origin",
            "total_energy_renewable_share_percent": 98,
            "IPC5_solar": {"nameplate_kWp": 130, "generation_2025_MWh": 114},
            "additional_PV_end_2025": {"systems_kWp": [120, 130], "commissioning": "start_2026", "portfolio_total_after_expansion_kWp": 380},
            "total_water_m3_including_offices": 1114,
            "office_water_m3": 848,
            "non_office_residual_m3_derived": 266,
            "water_boundary": "The residual is not assigned to cooling or individual facilities because the declaration perimeter does not support that allocation.",
            "PUE_target": "less_than_or_equal_to_1.3_by_2030_not_current_measured_PUE",
            "A41_2025_estimation_boundary": "A41 electricity values were estimated while bills were pending.",
        },
        "GPU_AI_and_liquid_cooling": {
            "AI_workload_evidence": "A 2025 event demonstrated LLM and RAG applications on TelemaxX OpenCloud.",
            "OpenCloud_public_SKUs": "vCPU_and_vRAM_without_reviewed_GPU_SKU",
            "TelemaxX_owned_installed_GPU_model_count_owner_site_delivery_rack_fabric_power_utilization_revenue_and_margin": "not_disclosed_or_established",
            "customer_GPU_inventory": "undisclosed",
            "liquid_cooling": "reviewed_provider_article_is_educational_not_deployment_evidence",
            "reviewed_live_facility_cooling": "factsheet_describes_air_and_chilled_or_glycol_water_systems_for_IPC3_IPC4_IPC5",
        },
        "ownership": {
            "publicly_listed_security": False,
            "shareholders_percent": {
                "Stadtwerke_Karlsruhe": 42.0,
                "Stadtwerke_Baden_Baden": 9.1,
                "Stadtwerke_Rastatt": 9.1,
                "Stadtwerke_Ettlingen": 8.0,
                "Energie_und_Wasserversorgung_Bruchsal": 8.0,
                "Stadtwerke_Bretten": 6.8,
                "Stadtwerke_Gaggenau": 6.8,
                "Stadtwerke_Buehl": 5.7,
                "Stadt_Stutensee": 4.5,
            },
            "shareholder_percent_checksum": 100.0,
            "Breitbandkabel_Landkreis_Karlsruhe_interest_percent": 49,
        },
        "financials": {
            "legal_entity": "TelemaxX Telekommunikation GmbH",
            "FY2024_audited_source_boundary": "Original report text reproduced by commercial extractor, identifying Bundesanzeiger as source and an unqualified audit opinion.",
            "FY2024": {
                "revenue_EUR_million": 41.298298,
                "data_center_revenue_EUR_million": 14.774,
                "data_center_revenue_growth_percent_derived": 5.071,
                "data_center_revenue_share_percent_derived": 35.774,
                "EBITDA_EUR_million": 8.073,
                "EBITDA_margin_percent_derived": 19.548,
                "EBIT_EUR_million": 1.552,
                "EBIT_margin_percent_derived": 3.758,
                "EBT_EUR_million": -0.765,
                "net_result_EUR_million": -1.361,
                "investments_EUR_million": 5.814,
                "bank_debt_EUR_million": 21.561,
                "cash_EUR_million": 5.475,
                "equity_EUR_million": 27.649,
                "impairment_of_Phone_maxX_interest_or_loan_EUR_million": 2.074,
            },
            "FY2025_latest_extracted_summary": {
                "filing_publication_date": "2026-04-10",
                "revenue_EUR_million_rounded": 41.80,
                "revenue_growth_percent_derived_approximate": 1.215,
                "net_result_EUR_million": 0.765532,
                "net_margin_percent_derived_approximate": 1.831,
                "balance_sheet_total_EUR_million": 54.54,
                "equity_EUR_million": 28.03,
                "liabilities_EUR_million": 22.04,
                "operating_result_EUR_million_analyst_derived_from_rounded_summary_lines": 2.4542,
                "operating_margin_percent_analyst_derived_approximate": 5.871,
                "EBITDA": "not_established_from_reviewed_latest_free_summary",
                "latest_data_center_segment_revenue_and_profit": "not_disclosed_in_reviewed_free_summary",
                "boundary": "The 2025 values are a commercial extracted summary; the original filing was not reviewed. The operating result is an analyst calculation from rounded lines and is not a provider-reported metric.",
            },
            "business_boundary": "TelemaxX also sells telecommunications and IT services; data-center revenue is not standalone site economics or segment operating profit.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "raw_operator_counts": dict(Counter(row["raw_operator"] for row in osm_rows)),
            "current_data_center_candidates": 4,
            "current_network_POP_former_data_center_objects": 1,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "outlook": {
            "positive_signals": ["municipal_and_regional_shareholder_base", "four_site_sovereign_regional_colocation_position", "2024_data_center_revenue_growth", "2025_company_net_profit_recovery", "customer_IT_energy_growth_and_efficiency_modernization"],
            "risk_signals": ["small_Karlsruhe_and_Stutensee_geographic_concentration", "no_current_site_MW_occupancy_or_billable_load", "no_latest_detailed_data_center_segment_profit", "telecom_price_pressure_and_customer_consolidation", "no_installed_GPU_inventory_or_live_liquid_cooling_evidence", "7800_versus_more_than_8000_square_metre_conflict"],
            "analytical_view": "TelemaxX is a compact municipally anchored regional fiber, colocation and cloud platform with positive 2024 data-center growth and 2025 company profit recovery. It is not a listed pure play, and a valuation case still requires current segment profit, occupancy, billable load, capex, cash flow and equipment-level evidence.",
        },
        "sources": [HOME, DIRECTORY, DATACENTER, CERTIFICATIONS, INFRASTRUCTURE, IPC1, IPC2, IPC3, IPC4, IPC5, IPC4_ADDRESS, FACTSHEET, EMAS_2026, SHAREHOLDERS, PARTNERS, OPEN_CLOUD, AI_EVENT, LIQUID_COOLING_EDUCATION, FINANCE_EXTRACT, OPEN_REGISTER],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_rows = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_rows, args.osm, args.accessed_on)
    summary["records_sha256"] = canonical_hash(records)
    summary["OSM_crosswalk"]["records"] = osm_rows
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "telemaxx_official_facility_registry.jsonl"
    summary_path = args.output_dir / "telemaxx_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_rows": len(osm_rows), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
