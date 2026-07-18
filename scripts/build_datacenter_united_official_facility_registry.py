#!/usr/bin/env python3
"""Build Datacenter United's facility, portfolio and OSM evidence registry.

The current provider directory, current investor portfolio scope, acquisition
documents and public map use different denominators.  This builder preserves
the 13-operating-facility investor basis, the 14-label mixed-lifecycle provider
directory and the 12 related OSM objects without turning any of them into a
false building, live-load or GPU census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DCU_DIRECTORY = "https://datacenterunited.com/en/our-datacenters/"
CORDIANT_CURRENT = "https://www.cordiantdigitaltrust.com/investments/current-assets/datacenter-united-dcu/"
CORDIANT_ACQUISITION = "https://www.cordiantdigitaltrust.com/cordiant-digital-infrastructure-limited-to-acquire-stakes-in-two-belgian-data-centre-providers-expanding-its-presence-in-western-europe/"
CORDIANT_ACQUISITION_DECK = "https://wp-cordiantdigitaltrust-2022.s3.eu-west-2.amazonaws.com/media/2024/10/CDIL-Acquisition-of-DCCO-DCU-vF.pdf"
CORDIANT_2026_ANNUAL = "https://wp-cordiantdigitaltrust-2022.s3.eu-west-2.amazonaws.com/media/2026/06/CORDIANT-AR-PROOF-09-18.06.26-FINAL.pdf"
PROXIMUS_SALE = "https://www.proximus.com/news/2024/20241025-proximus-sells-its-datacenters.html"
PROXIMUS_COMPLETION = "https://www.proximus.com/nl/news/2025/202503-news-proximus-datacenter-sale-completed.html"
DCU_COMPLETION = "https://datacenterunited.com/en/datacenter-united-finalizes-acquisition-of-proximus-data-centers/"
DCU_FUNDING = "https://datacenterunited.com/en/datacenter-united-announces-eur-120-million-funding-to-enable-sustainable-ai-ready-growth-2/"
DCU_ROADMAP = "https://datacenterunited.com/en/infrastructure-development/"
DCU_AI = "https://datacenterunited.com/en/dcu-future-ready-infrastructuur-gebouwd-voor-ai-geoptimaliseerd-voor-duurzaamheid-2/"
DCU_TIER_IV = "https://datacenterunited.com/en/tier-iv-more-than-just-a-unique-certificate-2/"
DCU_INTEGRATOR = "https://datacenterunited.com/en/de-infrastructuurpartner-voor-it-integrators-die-bouwen-aan-digitale-voorsprong-3/"
ISO_27001 = "https://datacenterunited.com/media/uploads/pdf/1/8/18_iso-iec-27001-eng-c671504-2-20250813.pdf"
ISO_9001 = "https://datacenterunited.com/media/uploads/pdf/1/9/19_iso-9001-eng-c671505-1-20250815.pdf"
ISO_14001 = "https://datacenterunited.com/media/uploads/pdf/1/7/17_iso-14001-certificate-ems-821167.pdf"


def site_page(slug: str) -> str:
    return f"https://datacenterunited.com/en/our-datacenters/{slug}/"


FACILITIES = [
    {
        "id": "dcu_antwerp_1",
        "provider_label": "Antwerp 1",
        "facility_code": "ANTW1",
        "location_key": "antwerp_haifastraat",
        "city": "Antwerp",
        "address": "Haifastraat 6, 2030 Antwerp, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-antwerp"),
        "shared_site_facility_labels": ["Antwerp 1", "Antwerp 2"],
        "OSM_refs": ["osm_node_13614915734"],
        "site_evidence": ["Tier_IV_certified", "carrier_neutral", "high_density_supported", "solar_panels", "cooling_upgrade_underway"],
    },
    {
        "id": "dcu_antwerp_2",
        "provider_label": "Antwerp 2",
        "facility_code": "ANTW2",
        "location_key": "antwerp_haifastraat",
        "city": "Antwerp",
        "address": "Haifastraat 6, 2030 Antwerp, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-antwerp"),
        "shared_site_facility_labels": ["Antwerp 1", "Antwerp 2"],
        "OSM_refs": ["osm_node_13614915734"],
        "site_evidence": ["Tier_IV_certified", "carrier_neutral", "high_density_supported", "solar_panels", "cooling_upgrade_underway"],
    },
    {
        "id": "dcu_antwerp_3",
        "provider_label": "Antwerp 3",
        "legacy_label": "DC Flanders",
        "location_key": "antwerp_noorderlaan",
        "city": "Antwerp",
        "address": "Noorderlaan 147, 2030 Antwerp, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-flanders"),
        "shared_site_facility_labels": ["Antwerp 3"],
        "OSM_refs": ["osm_node_12637347290"],
        "site_evidence": ["compact_connectivity_and_network_hub_site"],
    },
    {
        "id": "dcu_brussels_zaventem",
        "provider_label": "Brussels",
        "location_key": "zaventem_excelsiorlaan",
        "city": "Zaventem",
        "address": "Excelsiorlaan 15, 1930 Zaventem, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-brussels"),
        "shared_site_facility_labels": ["Brussels"],
        "OSM_refs": ["osm_way_29417840"],
        "site_evidence": ["provider_current_location_page"],
    },
    {
        "id": "dcu_burcht",
        "provider_label": "Burcht",
        "location_key": "burcht_antwerpsesteenweg",
        "city": "Burcht",
        "address": "Antwerpsesteenweg 221-223, 2070 Burcht, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-burcht"),
        "shared_site_facility_labels": ["Burcht"],
        "OSM_refs": ["osm_way_389875923"],
        "site_evidence": ["provider_current_location_page", "legacy_DCstar_label_in_OSM"],
    },
    {
        "id": "dcu_ghent",
        "provider_label": "Ghent",
        "location_key": "ghent_poortakkerstraat",
        "city": "Ghent",
        "address": "Poortakkerstraat 33, 9051 Ghent, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-ghent"),
        "shared_site_facility_labels": ["Ghent"],
        "OSM_refs": ["osm_way_368995283"],
        "site_evidence": ["cooling_infrastructure_upgrade"],
    },
    {
        "id": "dcu_hasselt_1",
        "provider_label": "Hasselt 1",
        "location_key": "hasselt_veldstraat",
        "city": "Hasselt",
        "address": "Veldstraat 101, 3500 Hasselt, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-hasselt-1"),
        "shared_site_facility_labels": ["Hasselt 1"],
        "OSM_refs": ["osm_way_746200227"],
        "site_evidence": ["provider_current_location_page"],
    },
    {
        "id": "dcu_hasselt_2",
        "provider_label": "Hasselt 2",
        "location_key": "hasselt_trichterheideweg",
        "city": "Hasselt",
        "address": "Trichterheideweg 2, 3500 Hasselt, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": False,
        "official_page": "https://datacenterunited.com/datacenters/datacenter-hasselt-2",
        "shared_site_facility_labels": ["Hasselt 2"],
        "OSM_refs": ["osm_way_822844088"],
        "site_evidence": ["current_separate_provider_page", "included_in_2025_ISO_certification", "omitted_from_current_14_label_directory"],
    },
    {
        "id": "dcu_oostkamp",
        "provider_label": "Oostkamp",
        "location_key": "oostkamp",
        "city": "Oostkamp",
        "address": "address_conflict_retained",
        "address_variants": {
            "current_operator_page_and_job_listing": "Brugsestraat 196/1, 8200 Oostkamp, Belgium",
            "2025_ISO_certificates": "Zwartegatstraat 7, 8020 Oostkamp, Belgium",
        },
        "lifecycle": "operating",
        "portfolio_origin": "legacy_Datacenter_United",
        "provider_directory_2026": True,
        "official_page": site_page("dc-oostkamp-bruges"),
        "shared_site_facility_labels": ["Oostkamp"],
        "OSM_refs": ["osm_way_139586790"],
        "site_evidence": ["cooling_access_and_technical_space_upgrade", "high_density_readiness", "operator_vs_certificate_address_conflict"],
    },
    {
        "id": "dcu_evere_1",
        "provider_label": "Evere 1",
        "location_key": "evere_carlistraat",
        "city": "Evere",
        "address": "Carlistraat 2, 1140 Evere, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "Proximus_carveout",
        "provider_directory_2026": True,
        "official_page": site_page("dc-evere"),
        "shared_site_facility_labels": ["Evere 1", "Evere 2"],
        "OSM_refs": ["osm_node_13320005875"],
        "site_evidence": ["one_location_page_for_two_acquired_facility_labels", "integration_completed"],
    },
    {
        "id": "dcu_evere_2",
        "provider_label": "Evere 2",
        "location_key": "evere_carlistraat",
        "city": "Evere",
        "address": "Carlistraat 2, 1140 Evere, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "Proximus_carveout",
        "provider_directory_2026": True,
        "official_page": site_page("dc-evere"),
        "shared_site_facility_labels": ["Evere 1", "Evere 2"],
        "OSM_refs": ["osm_node_13320005875"],
        "site_evidence": ["one_location_page_for_two_acquired_facility_labels", "integration_completed"],
    },
    {
        "id": "dcu_machelen",
        "provider_label": "Machelen",
        "location_key": "machelen_rittwegerlaan",
        "city": "Machelen",
        "address": "Rittwegerlaan 15, 1830 Machelen, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "Proximus_carveout",
        "provider_directory_2026": True,
        "official_page": site_page("dc-machelen"),
        "shared_site_facility_labels": ["Machelen"],
        "OSM_refs": ["osm_way_35130174"],
        "site_evidence": ["power_intensive_and_high_density_marketing", "available_power_and_space", "liquid_cooling_deployment_roadmap_2026"],
    },
    {
        "id": "dcu_mechelen",
        "provider_label": "Mechelen",
        "location_key": "mechelen_stationsstraat",
        "city": "Mechelen",
        "address": "Stationsstraat 58-59, 2800 Mechelen, Belgium",
        "lifecycle": "operating",
        "portfolio_origin": "Proximus_carveout",
        "provider_directory_2026": True,
        "official_page": site_page("dc-mechelen"),
        "shared_site_facility_labels": ["Mechelen"],
        "OSM_refs": ["osm_node_12633325927"],
        "site_evidence": ["provider_current_location_page"],
    },
    {
        "id": "dcu_mouscron",
        "provider_label": "Mouscron",
        "alternate_label": "Moeskroen",
        "location_key": "mouscron_slachthuisstraat",
        "city": "Mouscron",
        "address": "Slachthuisstraat 31, 7700 Mouscron, Belgium",
        "lifecycle": "development",
        "portfolio_origin": "organic_expansion",
        "provider_directory_2026": True,
        "official_page": site_page("dc-moeskroen"),
        "shared_site_facility_labels": ["Mouscron"],
        "OSM_refs": ["osm_way_148845282"],
        "site_evidence": ["provider_page_explicitly_currently_under_development", "coming_soon"],
    },
    {
        "id": "dcu_ghent_2",
        "provider_label": "Ghent 2",
        "location_key": "ghent_2_undisclosed",
        "city": "Ghent",
        "address": "undisclosed",
        "lifecycle": "development",
        "portfolio_origin": "organic_expansion",
        "provider_directory_2026": True,
        "official_page": site_page("dc-ghent"),
        "shared_site_facility_labels": ["Ghent 2"],
        "OSM_refs": [],
        "site_evidence": ["planning_and_site_preparation_2026", "construction_2026_2027", "capacity_availability_after_2027"],
    },
]


OSM_CROSSWALK = {
    "osm_way_139586790": (["dcu_oostkamp"], "site_match_with_unresolved_operator_vs_certificate_address_conflict"),
    "osm_way_29417840": (["dcu_brussels_zaventem"], "site_match"),
    "osm_node_13614915734": (["dcu_antwerp_1", "dcu_antwerp_2"], "shared_site_point_not_facility_specific"),
    "osm_node_13320005875": (["dcu_evere_1", "dcu_evere_2"], "shared_site_point_not_facility_specific"),
    "osm_node_12637347290": (["dcu_antwerp_3"], "site_match"),
    "osm_way_746200227": (["dcu_hasselt_1"], "site_match"),
    "osm_way_822844088": (["dcu_hasselt_2"], "site_match"),
    "osm_way_35130174": (["dcu_machelen"], "site_match"),
    "osm_node_12633325927": (["dcu_mechelen"], "site_match"),
    "osm_way_148845282": (["dcu_mouscron"], "development_site_match_not_operating"),
    "osm_way_368995283": (["dcu_ghent"], "site_match"),
    "osm_way_389875923": (["dcu_burcht"], "site_match_with_legacy_DCstar_operator_label"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(FACILITIES, start=1):
        row = dict(source)
        row.update({
            "object_type": "DatacenterUnitedOfficialFacilityLabelRecord",
            "source_order": order,
            "country_code": "BE",
            "investor_operating_scope_2026": source["lifecycle"] == "operating",
            "physical_granularity_boundary": "A facility label may share an address and provider page with another label; it is not automatically a separately verified building or meter.",
            "power_boundary": "No reviewed source allocates built, secured, operating, energized, leased, utilized or billed IT MW to this facility label.",
            "GPU_boundary": "No reviewed source identifies operator- or customer-owned GPU model, count, delivery state, power draw, utilization or economics at this facility label.",
            "source_urls": sorted(set([source["official_page"], DCU_DIRECTORY, CORDIANT_CURRENT, ISO_27001, ISO_9001, ISO_14001])),
            "accessed_on": accessed_on,
        })
        records.append(row)

    assert len(records) == 15
    assert len({row["id"] for row in records}) == 15
    assert Counter(row["lifecycle"] for row in records) == {"operating": 13, "development": 2}
    assert sum(row["provider_directory_2026"] for row in records) == 14
    assert len({row["location_key"] for row in records if row["investor_operating_scope_2026"]}) == 11
    assert Counter(row["portfolio_origin"] for row in records if row["lifecycle"] == "operating") == {
        "legacy_Datacenter_United": 9,
        "Proximus_carveout": 4,
    }
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_id, (facility_refs, status) in OSM_CROSSWALK.items():
        source = osm[osm_id]
        assert source.get("operator") in {"Data Center United", "Datacenter United", "Datacenter United / DCstar nv"}
        rows.append({
            "osm_ref": osm_id,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "country_codes": sorted({candidate["iso2"] for candidate in source.get("country_candidates", [])}),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_refs": facility_refs,
            "crosswalk_status": status,
            "boundary": "OSM points and footprint polygons are public-map evidence, not provider-verified ownership, gross floor area, data-hall area, lifecycle, power, utilization or financial records.",
            "source_url": source["source_url"],
        })
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_crosswalk: list[dict], accessed_on: str) -> dict:
    operating = [row for row in records if row["lifecycle"] == "operating"]
    directory = [row for row in records if row["provider_directory_2026"]]
    summary = {
        "id": "datacenter_united_official_facility_summary_2026_07_19",
        "object_type": "DatacenterUnitedFacilityPortfolioReconciliation",
        "accessed_on": accessed_on,
        "operator": "Datacenter United",
        "country_code": "BE",
        "reconstructed_registry": {
            "facility_label_records": len(records),
            "operating_facility_labels": len(operating),
            "operating_location_keys": len({row["location_key"] for row in operating}),
            "development_facility_labels": sum(row["lifecycle"] == "development" for row in records),
            "current_provider_directory_labels": len(directory),
            "directory_operating_labels": sum(row["lifecycle"] == "operating" and row["provider_directory_2026"] for row in records),
            "directory_development_labels": sum(row["lifecycle"] == "development" and row["provider_directory_2026"] for row in records),
            "operating_label_omitted_from_directory": [row["provider_label"] for row in operating if not row["provider_directory_2026"]],
            "current_provider_directory_label_names": [row["provider_label"] for row in directory],
        },
        "published_roster_denominators": {
            "latest_Cordiant_investment_page": {"facilities": 13, "locations": 11, "built_and_secured_IT_capacity_MW_rounded": 24, "scope": "current_operating_investor_basis"},
            "legacy_DCU_pre_acquisition": {"facilities": 9, "locations": 8},
            "Proximus_carveout": {"facilities": 4, "locations": 3},
            "provider_directory": {"labels": 14, "scope": "mixed_operating_and_development_with_Hasselt_2_omitted"},
            "conflicting_provider_marketing_articles": {"data_centers": 16, "locations": 13, "status": "unreconciled_marketing_denominator_not_used_as_operating_baseline"},
            "boundary": "The 13/11 investor basis, 14-label directory and 16/13 article claims are retained separately. Labels, locations and physical buildings are not interchangeable.",
        },
        "portfolio_power": {
            "legacy_DCU": {"built_IT_MW": 1.7, "secured_expansion_MW": 7.1, "accessible_total_MW": 8.8},
            "Proximus_carveout": {"built_IT_MW": 4.0, "secured_expansion_MW": 11.3, "accessible_total_MW": 15.3},
            "combined": {"built_IT_MW_derived": 5.7, "secured_expansion_MW_derived": 18.4, "built_and_secured_accessible_MW": 24.1},
            "Proximus_sale_announcement_capacity_MW_approximate": 11,
            "additional_Antwerp_power_secured_MW": 17,
            "boundary": "The 11-MW Proximus transaction statement and 4.0/15.3-MW investor buckets use different timing or power scopes. The later 17 MW secured in Antwerp is a future power foundation and is not added to 24.1 MW without a dated bridge. None is current utilized load.",
        },
        "acquisition_and_ownership": {
            "Proximus_sale_enterprise_value_EUR_million": 128,
            "Proximus_completion_date": "2025-02-28",
            "Proximus_real_estate_included_locations": ["Evere", "Mechelen"],
            "Proximus_MSA": "10_year_index_linked_plus_two_5_year_extension_options",
            "combined_transaction_enterprise_value_EUR_million": 200.5,
            "original_equity_investment_EUR_million": 92.3,
            "current_economic_interests_percent": {"Cordiant_Digital_Infrastructure_Limited": 37.4, "other_Cordiant_managed_co_investor": 10.1, "TINC": 47.5, "CEO_Friso_Haringsma_non_voting": 5.0},
            "current_voting_interests_percent": {"Cordiant_managed_interests": 50, "TINC": 50},
            "boundary": "Cordiant-managed vehicles collectively retain 47.5% economics and 50% voting; CDIL's own indirect economic interest is 37.4% after the July 2025 syndication.",
        },
        "financials": {
            "FY2023A_transaction_basis_EUR_million": {
                "legacy_DCU": {"revenue": 10.0, "adjusted_EBITDA": 3.8},
                "Proximus_carveout": {"revenue": 30.3, "adjusted_EBITDA": 11.3, "includes_annual_Proximus_office_lease_revenue": 3.0},
                "combined_pre_synergy": {"revenue": 40.3, "adjusted_EBITDA": 15.1},
            },
            "FY2025_first_combined_year_EUR_million": {"revenue": 36.1, "EBITDA": 11.3, "EBITDA_margin_percent_derived": 31.30, "boundary": "Acquisition completed at end-February, so reported results are not a full twelve-month combined period."},
            "FY2025_pro_forma_12_month_EUR_million": {"revenue": 41.3, "EBITDA": 13.2, "EBITDA_margin_percent_derived": 31.96},
            "FY2025_audited_Belgian_GAAP_GBP_million": {"turnover": 30.9, "pre_tax_loss": -10.0, "net_assets": 76.3},
            "standalone_accounting_operating_profit": "not_disclosed_in_reviewed_source",
            "boundary": "EBITDA, adjusted EBITDA and pre-tax loss are not accounting operating profit. GBP audited totals, EUR management reporting and transaction-basis FY2023 numbers use different periods, currencies and perimeters.",
        },
        "financing_and_orders": {
            "senior_package_EUR_million": 120,
            "maturity": "2030-09",
            "drawn_term_loan_EUR_million": 50,
            "capex_facility_EUR_million": 50,
            "revolving_and_ancillary_facility_EUR_million": 20,
            "margin_over_Euribor_percent_at_current_leverage": 2.25,
            "hedged_notional_EUR_million": 55,
            "four_year_swap_rate_percent": 2.42,
            "all_in_fixed_rate_percent_at_current_margin": 4.67,
            "cash_at_2026_03_31_EUR_million": 1.7,
            "unused_facilities_at_2026_03_31_EUR_million": 56.5,
            "net_leverage_at_2026_03_31_times": 3.9,
            "top_30_customer_contracted_order_book_EUR_million": 83.4,
            "named_customers": ["Proximus", "Pfizer", "Telenet", "Atos"],
            "operator_release_accordion_potential_EUR_million": 50,
            "boundary": "Facility commitments, unused debt capacity and accordion potential are not drawn debt, incurred capex, revenue or free cash flow.",
        },
        "AI_GPU_power_and_cooling": {
            "capabilities": ["heavy_GPU_workload_support", "liquid_cooling", "high_efficiency_chillers", "optimized_thermal_management", "advanced_free_air_cooling", "high_density_readiness"],
            "Machelen_2026": "liquid_cooling_and_high_density_design_Q2_deployment_Q3_commissioning_Q4",
            "Antwerp_2026": "cooling_efficiency_design_Q2_components_Q3_activation_Q4",
            "Oostkamp_2026": "cooling_access_and_technical_space_expansion_Q2_to_Q4",
            "Ghent_2": "site_preparation_2026_construction_2026_2027_capacity_after_2027",
            "operator_marketing_redundancy_claim": "2N_plus_1",
            "Tier_IV_boundary": "Only the Antwerp Haifastraat site is explicitly identified as Tier IV; portfolio-wide redundancy is not inferred from that certification.",
            "GPU_model_count_owner_site_utilization_power_and_economics": "undisclosed",
            "GPU_ownership_boundary": "Colocation readiness and customer workload support do not establish Datacenter United ownership of accelerators.",
            "undisclosed_equipment": ["utility_feeds", "substation_transformer_switchgear_counts_and_ratings", "UPS_battery_generator_counts_ratings_topology_and_OEMs", "chiller_CRAH_CDU_and_heat_rejection_counts_ratings_and_OEMs", "site_level_live_liquid_cooled_MW"],
        },
        "sustainability": {
            "FY2025_operational_electricity_covered_by_renewable_electricity_percent": 82,
            "coverage_instruments": ["PPAs", "Guarantees_of_Origin"],
            "operator_marketing_all_data_centers_renewable_percent": 100,
            "operator_marketing_PUE_claim": "less_than_1.2",
            "operator_marketing_solar_capacity_as_published": "3500Wp",
            "SBTi_scope_1_and_2_reduction_target_percent": 46.2,
            "SBTi_target_year": 2031,
            "boundary": "The measured 82% investor disclosure and 100% operator marketing claim are not silently reconciled. The published 3500Wp string is preserved without converting it to 3.5 MW, and sub-1.2 PUE is not treated as a per-site measured portfolio value.",
        },
        "address_conflict": {
            "site": "Oostkamp",
            "operator_page_and_job_listing": "Brugsestraat 196/1, 8200 Oostkamp",
            "2025_ISO_certificates": "Zwartegatstraat 7, 8020 Oostkamp",
            "status": "unresolved_possible_office_facility_address_change_or_separate_property",
        },
        "OSM_crosswalk": osm_crosswalk,
        "OSM_crosswalk_count": len(osm_crosswalk),
        "OSM_operator_label_counts": dict(sorted(Counter(row["raw_operator"] for row in osm_crosswalk).items())),
        "comparison_gate": "Do not add facility labels, provider directory labels, investor locations, OSM objects, built IT MW, secured expansion MW, grid power, customer GPUs, financing or revenue into one league-table metric.",
        "sources": [
            DCU_DIRECTORY,
            CORDIANT_CURRENT,
            CORDIANT_ACQUISITION,
            CORDIANT_ACQUISITION_DECK,
            CORDIANT_2026_ANNUAL,
            PROXIMUS_SALE,
            PROXIMUS_COMPLETION,
            DCU_COMPLETION,
            DCU_FUNDING,
            DCU_ROADMAP,
            DCU_AI,
            DCU_TIER_IV,
            DCU_INTEGRATOR,
            ISO_27001,
            ISO_9001,
            ISO_14001,
        ],
        "registry_sha256": canonical_hash(records),
    }
    assert summary["reconstructed_registry"] == {
        "facility_label_records": 15,
        "operating_facility_labels": 13,
        "operating_location_keys": 11,
        "development_facility_labels": 2,
        "current_provider_directory_labels": 14,
        "directory_operating_labels": 12,
        "directory_development_labels": 2,
        "operating_label_omitted_from_directory": ["Hasselt 2"],
        "current_provider_directory_label_names": [row["provider_label"] for row in directory],
    }
    assert len(osm_crosswalk) == 12
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()

    records = build_records(args.accessed_on)
    osm_crosswalk = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_crosswalk, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "datacenter_united_official_facility_registry.jsonl"
    summary_path = args.output_dir / "datacenter_united_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_crosswalk": len(osm_crosswalk), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
