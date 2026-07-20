#!/usr/bin/env python3
"""Build a scope-preserving legacy Euclyde and current nLighten France registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


FRANCE_DIRECTORY_URL = "https://www.nlighten.com/en/locations-detail-pages/france/"
ACQUISITION_URL = "https://www.nlighten.com/en/press-releases/nlighten-acquires-euclyde-data-centers-a-leading-edge-data-center-platform-in-france/"
REBRAND_URL = "https://www.nlighten.com/fr/communiques-de-presse/euclyde-datacenters-annonce-le-rebranding-en-nlighten-france-au-dc-world-de-paris/"
EXA_ACQUISITION_URL = "https://www.nlighten.com/en/press-releases/nlighten-expands-throughout-europe/"
PAR3_ACQUISITION_URL = "https://www.nlighten.com/en/nlighten-expands-french-data-center-footprint-through-paris-site-acquisition/"
SECURITY_URL = "https://www.nlighten.com/en/security-and-compliance/"
NCONNECT_URL = "https://www.nlighten.com/en/nconnect/"
FRANCE_ENERGY_URL = "https://www.nlighten.com/en/press-releases/new-energy-agreement-brings-enhanced-renewable-transparency-to-nlightens-french-data-center-operations/"
ICFEN_URL = "https://www.nlighten.com/en/nlightens-carbon-free-energy-commitment/our-carbon-free-energy-score/"
UK_TOPCO_FILING_URL = "https://find-and-update.company-information.service.gov.uk/company/14348462/filing-history"
UK_TOPCO_2024_ACCOUNTS_URL = "https://find-and-update.company-information.service.gov.uk/company/14348462/filing-history/MzUwNTU1NTc3OGFkaXF6a2N4/document?download=1"
FRANCE_REGISTRY_URL = "https://annuaire-entreprises.data.gouv.fr/entreprise/840088439"
PAPPERS_RE_URL = "https://www.pappers.fr/entreprise/nlighten-france-re-449012913"
PAPPERS_FRANCE_URL = "https://www.pappers.fr/entreprise/nlighten-france-840088439"
PAPPERS_HOLDING_URL = "https://www.pappers.fr/entreprise/nlighten-france-holding-930347521"


FACILITIES = [
    {
        "code": "NCE1",
        "name": "Antibes",
        "city": "Antibes",
        "address": "49 Rue Emile Hugues, 06600 Antibes, Sophia-Antipolis, France",
        "legacy_Euclyde_code": "DC1",
        "lineage": "legacy_Euclyde_six_site_acquisition_2023",
        "space_m2": 1500,
        "site_capacity_end_state_kW": 6000,
        "high_density": "15_to_150_plus_kW_per_cabinet",
        "url": "https://www.nlighten.com/en/edge-location/antibes/",
    },
    {
        "code": "MLH1",
        "name": "Besancon",
        "city": "Besancon",
        "address": "2 Rue Albert Einstein, 25000 Besancon, France",
        "legacy_Euclyde_code": "DC2",
        "lineage": "legacy_Euclyde_six_site_acquisition_2023",
        "space_m2": 300,
        "site_capacity_end_state_kW": 1200,
        "high_density": "15_to_150_plus_kW_per_cabinet_on_request",
        "url": "https://www.nlighten.com/en/edge-location/besancon/",
    },
    {
        "code": "NCE2",
        "name": "Valbonne",
        "city": "Valbonne",
        "address": "930 Route des Dolines, 06560 Valbonne, Sophia Antipolis, France",
        "legacy_Euclyde_code": "DC3",
        "lineage": "legacy_Euclyde_six_site_acquisition_2023",
        "space_m2": 700,
        "site_capacity_end_state_kW": 6000,
        "high_density": "15_to_150_plus_kW_per_cabinet",
        "url": "https://www.nlighten.com/en/edge-location/valbonne/",
    },
    {
        "code": "LYS1",
        "name": "Lyon",
        "city": "Villeurbanne",
        "address": "45-47 Rue Francis de Pressense, 69100 Villeurbanne, France",
        "legacy_Euclyde_code": "DC5",
        "lineage": "legacy_Euclyde_six_site_acquisition_2023",
        "space_m2": 560,
        "site_capacity_end_state_kW": 1200,
        "high_density": "15_to_150_plus_kW_per_cabinet_on_request",
        "url": "https://www.nlighten.com/en/edge-location/lyon/",
    },
    {
        "code": "PAR1",
        "name": "Paris_PAR1",
        "city": "Lognes",
        "address": "3-5 Mail Barthelemy Thimonnier, Newton A, 77185 Lognes, France",
        "legacy_Euclyde_code": "DC6",
        "lineage": "legacy_Euclyde_six_site_acquisition_2023",
        "space_m2": 3300,
        "site_capacity_end_state_kW": 2400,
        "high_density": "15_to_150_plus_kW_per_cabinet_on_request",
        "url": "https://www.nlighten.com/en/edge-location/paris-1/",
    },
    {
        "code": "SXB1",
        "name": "Strasbourg",
        "city": "Illkirch_Graffenstaden",
        "address": "Rue Jean-Dominique Cassini, 67400 Illkirch-Graffenstaden, France",
        "legacy_Euclyde_code": "DC7",
        "lineage": "legacy_Euclyde_six_site_acquisition_2023",
        "space_m2": 600,
        "site_capacity_end_state_kW": 1200,
        "high_density": "15_to_150_plus_kW_per_cabinet_on_request",
        "url": "https://www.nlighten.com/en/edge-location/strasbourg/",
    },
    {
        "code": "PAR2",
        "name": "Paris_PAR2",
        "city": "Aubervilliers",
        "address": "34 Rue des Gardinoux, 93300 Aubervilliers, France",
        "legacy_Euclyde_code": None,
        "lineage": "2024_EXA_Infrastructure_seven_site_related_party_acquisition_addition",
        "space_m2": 1800,
        "site_capacity_end_state_kW": 2200,
        "high_density": "15_to_150_plus_kW_per_cabinet_on_request",
        "url": "https://www.nlighten.com/en/edge-location/paris-2/",
    },
    {
        "code": "PAR3",
        "name": "Paris_PAR3",
        "city": "Emerainville",
        "address": "Rue Vladimir Jankelevitch, 77184 Emerainville, France",
        "legacy_Euclyde_code": None,
        "lineage": "2026_oXya_site_acquisition_with_oXya_as_anchor_customer",
        "space_m2": None,
        "site_capacity_end_state_kW": None,
        "high_density": "AI_ready_scalable_power_and_cooling_claim_without_numeric_capacity",
        "url": "https://www.nlighten.com/en/edge-location/paris-3/",
    },
]


OSM_CROSSWALK = {
    "osm_relation_1074421": ("NCE1", "DC1"),
    "osm_way_843508896": ("NCE2", "DC3"),
    "osm_way_84607738": ("LYS1", "DC5"),
    "osm_way_116116518": ("PAR1", "DC6"),
    "osm_way_1061336199": ("SXB1", "DC7"),
}


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] in OSM_CROSSWALK:
            rows[row["id"]] = row
    assert set(rows) == set(OSM_CROSSWALK)
    return rows


def build_records(osm_rows: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for facility in FACILITIES:
        row = {
            "id": f"nlighten_france_facility_{facility['code'].lower()}",
            "object_type": "ProviderDataCenterFacilityDisclosure",
            "operator": "nLighten_France",
            "country": "France",
            "lifecycle": "current_provider_directory_operating_or_marketed_site",
            **facility,
            "common_design_disclosure": {
                "cabinet_feeds": "independent_A_and_B",
                "standard_air_cooled_density_kW_per_cabinet": "2_to_7_up_to_15",
                "design_PUE": 1.29 if facility["code"] != "PAR3" else None,
                "design_target": "Tier_III" if facility["code"] != "PAR3" else None,
                "cooling_and_humidity_design": "ASHRAE_A1_allowable" if facility["code"] != "PAR3" else None,
            },
            "capacity_boundary": "Space and power are provider page values. Power is explicitly end-state site capacity for the seven numeric cards, not live, energized, contracted, sold, utilized, billed or IT load. PAR3 has no numeric card disclosure.",
            "accessed_on": accessed_on,
        }
        records.append(row)
    for osm_id, source in osm_rows.items():
        current_code, legacy_code = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"nlighten_france_evidence_{osm_id}",
            "object_type": "OSMFacilityEvidence",
            "operator": "nLighten_France",
            "legacy_operator_label": source.get("operator"),
            "legacy_name": source.get("name"),
            "OSM_ref": osm_id,
            "matched_current_facility_code": current_code,
            "matched_legacy_Euclyde_code": legacy_code,
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_building_levels": source.get("building_levels"),
            "source_url": source["source_url"],
            "count_boundary": "The OSM object is a legacy-label location crosswalk, not proof of current title, lifecycle, gross floor area, data-hall area, power, utilization or financial contribution.",
            "accessed_on": accessed_on,
        })
    assert len(records) == 13
    assert sum(row["object_type"] == "ProviderDataCenterFacilityDisclosure" for row in records) == 8
    assert sum(row["object_type"] == "OSMFacilityEvidence" for row in records) == 5
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    numeric = [row for row in FACILITIES if row["site_capacity_end_state_kW"] is not None]
    osm_records = [row for row in records if row["object_type"] == "OSMFacilityEvidence"]
    return {
        "id": "euclyde_nlighten_france_data_center_summary_2026_07_19",
        "current_operator": "nLighten France",
        "legacy_operator": "Euclyde Data Centers",
        "accessed_on": accessed_on,
        "ownership_and_brand_timeline": {
            "2023_06_01": "nLighten, an I Squared Capital ISQ Global Infrastructure Fund III platform, acquired six carrier-neutral Euclyde sites across five French markets; consideration was not disclosed.",
            "2024_04_01": "The audited group accounts record acquisition of EI Data Center France SAS from related-party EXA Infrastructure France SAS for EUR4.696 million; the provider's seven-site European release added a French location now marketed as PAR2.",
            "2024_11_25": "Euclyde was rebranded nLighten France.",
            "2026_02_02": "nLighten acquired the Emerainville site from oXya as PAR3, its eighth French site; oXya remained anchor customer under a long-term master services agreement.",
            "current_shareholder": "I_Squared_Capital_backed_nLighten_platform",
            "transaction_values": {"Euclyde_2023": "undisclosed", "EI_Data_Center_France_2024_EUR_million": 4.696, "PAR3_2026": "undisclosed"},
        },
        "roster_reconciliation": {
            "current_provider_France_site_cards": 8,
            "legacy_Euclyde_sites_acquired_2023": 6,
            "legacy_to_current_codes": {row["legacy_Euclyde_code"]: row["code"] for row in FACILITIES if row["legacy_Euclyde_code"]},
            "post_Euclyde_additions": ["PAR2", "PAR3"],
            "legacy_code_gap": "No DC4 appears in the six-site acquired roster; no missing facility is invented.",
            "boundary": "The current eight-site roster supersedes the legacy six-site brand roster. Codes, markets, legal establishments, physical buildings and OSM objects remain separate granularities.",
        },
        "current_numeric_card_arithmetic_checksum_not_live_capacity": {
            "numeric_sites": [row["code"] for row in numeric],
            "space_m2": sum(row["space_m2"] for row in numeric),
            "site_capacity_end_state_MW": sum(row["site_capacity_end_state_kW"] for row in numeric) / 1000,
            "PAR3_numeric_capacity": "undisclosed",
            "historical_provider_conflicts": {
                "NCE1": "Older July 2024 provider datasheet stated proposed end-state 800kW versus current page 6000kW.",
                "NCE2": "Older July 2024 provider datasheet stated proposed end-state 900kW versus current page 6000kW.",
                "MLH1": "Provider pages or datasheets have shown 1200kW and 1500kW; this registry uses the current edge-location page's 1200kW and preserves the conflict.",
            },
            "boundary": "The 8,760m2 and 20.2MW sums are reproducibility checks across seven current numeric cards. They exclude PAR3 and are not operating, live, IT, energized, sold, occupied, utilized, billed or peak load.",
        },
        "OSM_crosswalk": {
            "raw_operator_labels": ["Euclyde", "Euclyde Datacenters"],
            "matched_objects": len(osm_records),
            "matched_current_codes": [row["matched_current_facility_code"] for row in osm_records],
            "off_sample_current_sites": ["MLH1", "PAR2", "PAR3"],
            "footprint_area_m2_checksum_where_available": round(sum(row.get("OSM_footprint_area_m2") or 0 for row in osm_records), 3),
            "boundary": "Five legacy-label OSM objects route to five current sites. Their footprint checksum is not provider space or gross floor area and does not establish a complete current estate.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "power_cooling_and_equipment_boundary": {
            "published_common_design": {
                "cabinet_power": "independent_A_and_B_feeds",
                "standard_air_cooled_density_kW_per_cabinet": "2_to_7_up_to_15",
                "high_density_AI_ready_kW_per_cabinet": "15_to_150_plus_with_on_request_qualifier_at_five_numeric_sites",
                "design_PUE": 1.29,
                "design_target": "Tier_III",
                "cooling_and_humidity": "ASHRAE_A1_allowable_category",
            },
            "undisclosed": [
                "per_site_grid_feeds_voltage_contract_capacity_current_draw_and_substation",
                "transformer_switchgear_busbar_PDU_UPS_battery_generator_fuel_OEM_model_count_rating_loading_test_age_and_remaining_life",
                "chiller_CRAH_CRAC_CDU_pump_water_loop_OEM_model_count_rating_redundancy_and_loading",
                "measured_site_PUE_WUE_energy_water_emissions_heat_reuse_and_live_liquid_cooled_MW",
                "energized_available_allocated_sold_occupied_billed_peak_and_actual_IT_load",
            ],
            "boundary": "A Tier III design target is not an Uptime certified-design, constructed-facility or operational-sustainability award. AI-ready cabinet density and a design PUE are not installed equipment, liquid load or measured performance.",
        },
        "energy_and_sustainability": {
            "site_page_claim": "100_percent_carbon_free_energy_backed_by_Guarantees_of_Origin_with_PPA_and_ICFEn_calculated",
            "France_supply_agreement_start": "2026-01-01",
            "France_supply_parties": ["nLighten", "Axpo", "independent_wind_power_producer"],
            "hourly_tracking": "contract_announces_granular_hourly_renewable_tracking_across_all_France_locations",
            "France_absolute_energy_PUE_WUE_water_and_emissions": "undisclosed",
            "boundary": "Guarantees of Origin, PPAs, a supply agreement and hourly accounting are distinct. The published group ICFEn average is not allocated to France and is not applied to these sites.",
        },
        "AI_GPU_boundary": {
            "provider_claims": ["AI_ready_15_to_150_plus_kW_per_cabinet", "PAR3_scalable_power_and_cooling_for_AI_ready_workloads"],
            "exact_current_operator_or_customer_GPU_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "live_liquid_cooled_MW": "undisclosed_or_unestablished",
            "boundary": "High-density readiness does not establish installed accelerators or liquid cooling. No GPU total is inferred.",
        },
        "audited_nLighten_UK_TopCo_group_2024_EUR_million": {
            "reporting_period_months": 12,
            "revenue": 59.963,
            "UK_destination_revenue": 29.970,
            "rest_of_Europe_destination_revenue": 29.993,
            "gross_profit": 26.948,
            "operating_loss": -31.957,
            "loss_before_tax": -40.994,
            "net_loss": -39.837,
            "net_cash_used_in_operating_activities": -19.647,
            "purchases_of_property_plant_and_equipment": 74.596,
            "acquisition_of_subsidiaries_net_of_cash": 18.265,
            "property_plant_and_equipment": 322.184,
            "right_of_use_assets": 80.490,
            "cash_and_cash_equivalents_excluding_restricted_cash": 32.297,
            "restricted_cash": 4.284,
            "loans_and_borrowings_including_lease_liabilities": 189.705,
            "net_assets": 269.575,
            "France_PPE_pledged_as_security": 53.201,
            "France_third_party_loans": 15.179,
            "boundary": "These are audited nLighten UK TopCo consolidated European-group results, not France-only or site-level results. Rest of Europe combines France with other countries, acquisitions entered consolidation at different dates and the 2023 comparator is a restated 16-month period.",
        },
        "France_legal_entity_boundary": {
            "nLighten_France_SIREN": "840088439",
            "nLighten_France_RE_SIREN": "449012913",
            "nLighten_France_Holding_SIREN": "930347521",
            "official_registry_active_establishments_for_840088439": 7,
            "secondary_registry_2024": {
                "nLighten_France_net_loss_EUR_million": -1.7,
                "nLighten_France_RE_net_income_EUR_million": 3.94,
                "nLighten_France_Holding_revenue_EUR_million": 1.89,
                "nLighten_France_Holding_operating_loss_EUR_million": -0.0477,
            },
            "boundary": "The French entities are not added or substituted for consolidated group results. Revenue and operating lines are confidential or unavailable for the two operating entities, mergers make periods non-comparable, and the displayed French figures are secondary registry transcriptions rather than reviewed original filings.",
        },
        "outlook": {
            "positive_signals": ["eight_site_current_France_roster", "two_post_Euclyde_additions", "high_density_design_range", "France_hourly_renewable_tracking_contract", "2024_group_revenue_scale_up", "EUR74_596m_group_PPE_investment", "I_Squared_capital_support"],
            "risk_signals": ["2024_group_operating_and_net_losses", "negative_operating_cash_flow", "high_acquisition_and_startup_costs", "EUR189_705m_loans_and_lease_liabilities", "GBP78_684m_facility_due_March_2026_with_replacement_uncertain_at_accounts_authorization", "no_current_refinancing_confirmation_in_reviewed_sources", "end_state_capacity_not_live_load", "no_France_segment_profit_or_GPU_inventory", "power_equipment_and_measured_efficiency_opacity"],
            "analytical_view": "nLighten France has a credible regional edge footprint and visible sponsor-funded expansion, but it is not directly investable and the audited group was loss-making and cash-consuming during rapid acquisition integration. The key conversion tests are refinancing, delivery of end-state power into contracted billed load, measured efficiency, and evidence that high-density readiness produces recurring returns.",
        },
        "records": records,
        "sources": [
            FRANCE_DIRECTORY_URL,
            ACQUISITION_URL,
            REBRAND_URL,
            EXA_ACQUISITION_URL,
            PAR3_ACQUISITION_URL,
            SECURITY_URL,
            NCONNECT_URL,
            FRANCE_ENERGY_URL,
            ICFEN_URL,
            UK_TOPCO_FILING_URL,
            UK_TOPCO_2024_ACCOUNTS_URL,
            FRANCE_REGISTRY_URL,
            PAPPERS_RE_URL,
            PAPPERS_FRANCE_URL,
            PAPPERS_HOLDING_URL,
        ] + [row["url"] for row in FACILITIES],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(load_osm(args.osm), args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    summary["records_sha256"] = canonical_hash(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "euclyde_nlighten_france_data_center_registry.jsonl"
    summary_path = args.output_dir / "euclyde_nlighten_france_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
