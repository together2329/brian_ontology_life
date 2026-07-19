#!/usr/bin/env python3
"""Build a scope-safe ETIX facility, transition, and OSM registry.

ETIX's current homepage still presents a 15-site portfolio, while a June 2026
Eurofiber transaction announced four additional Occitanie locations and public
French registry evidence subsequently shows a legal-control transition.  The
Bangkok page also markets a second facility outside the older 15-site directory.
This builder preserves those three lifecycle/count scopes instead of inventing a
single current operating total.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://www.etixeverywhere.com/"
LILLE = "https://www.etixeverywhere.com/fr/centres-de-donnees-a-lille/"
NANTES = "https://www.etixeverywhere.com/fr/centres-de-donnees-a-nantes/"
PARIS = "https://www.etixeverywhere.com/fr/centres-de-donnees-a-paris/"
LYON = "https://www.etixeverywhere.com/fr/centres-de-donnees-a-lyon/"
TOULOUSE = "https://www.etixeverywhere.com/fr/centres-de-donnees-a-toulouse/"
MONTPELLIER = "https://www.etixeverywhere.com/fr/centres-de-donnees-a-montpellier/"
LIEGE = "https://www.etixeverywhere.com/data-centers-in-liege/"
BANGKOK = "https://www.etixeverywhere.com/data-centers-in-bangkok/"
BANGKOK_2024 = "https://apac.etixeverywhere.com/2024/09/19/bknix-choosing-etix-bangkok-1-for-its-6th-pop/"
EUROFIBER = "https://www.eurofiber.com/press/etix--enters-into-exclusive-negotiations-for-the-acquisition-of--four-eurofiber-datacenters-in-occitanie-region-cementing-its-position-as-frances-leading-sovereign-operator/"
EUROFIBER_FR = "https://www.eurofiber.com/fr-fr/actualites/etix-entre-en-negociation-exclusive-pour-l-acquisition-de-quatre-datacenters"
EUROFIBER_PDF = "https://assets.ctfassets.net/l0t3dj9b53n9/5jTr9epigstiuWaRPd8WvD/8df0437d710e7668602117b62a18b9cd/2026_06_-_ETIX_in_exclusive_talks_to_acquire_four_Eurofiber_data_centers_in_Occitanie.pdf"
EUROFIBER_HDS = "https://eurofibercloudinfra.fr/wp-content/uploads/2025/06/2025_certificat_HDS.pdf"
LEGAL_REGISTRY = "https://entreprises.lefigaro.fr/eurofiber-dc-92/entreprise-829079912"
SUSTAINABILITY = "https://www.etixeverywhere.com/sustainable-data-centers-esg/"
VISION = "https://www.etixeverywhere.com/our-vision/"
INFRANITY = "https://infranity.com/wp-content/uploads/2024/05/2024-05-Etix-Press-Release-EN_vF.pdf"
EURAZEO_2025 = "https://www.eurazeo.com/sites/default/files/2026-04/Eurazeo_Universal_Registration_Document_2025_EN_260402_MEL_0.pdf"
ZCOLO = "https://www.etixeverywhere.com/etix-everywhere-renforce-sa-position-de-leader-en-france-avec-lintegration-de-cinq-nouveaux-data-centers/"
CIV = "https://www.etixeverywhere.com/etix-everywhere-accelerates-its-development-and-integrates-civ-france-into-its-network-of-data-centers/"
PAPPERS_HOLDING = "https://www.pappers.fr/entreprise/etix-everywhere-holding-france-891040958"
PAPPERS_FRANCE = "https://www.pappers.fr/entreprise/etix-everywhere-france-809711856"
PAPPERS_OUEST = "https://www.pappers.fr/entreprise/etix-everywhere-ouest-523491256"
DATASHEET_LILLE = "https://app-na1.hubspotdocuments.com/documents/4292166/view/1709975116?accessId=410616"
DATASHEET_NANTES = "https://app-na1.hubspotdocuments.com/documents/4292166/view/1709976437?accessId=1d007f"
DATASHEET_PARIS = "https://app-na1.hubspotdocuments.com/documents/4292166/view/1709978204?accessId=2d5ba2"


def site(
    row_id: str,
    label: str,
    city: str,
    country: str,
    country_code: str,
    address: str | None,
    web_capacity_kw: int | None,
    web_racks: int | None,
    city_source: str,
    *,
    lifecycle: str = "base_fifteen_current_directory_site",
    equipment: dict | None = None,
    conflicts: list[str] | None = None,
    extra_sources: list[str] | None = None,
) -> dict:
    return {
        "id": row_id,
        "object_type": "DataCenterFacilityEvidence",
        "operator_or_marketer": "ETIX Everywhere",
        "facility_label": label,
        "city_or_market": city,
        "country": country,
        "country_code": country_code,
        "address": address,
        "lifecycle": lifecycle,
        "website_card_capacity_kw": web_capacity_kw,
        "website_card_racks": web_racks,
        "capacity_boundary": "Provider card capacity is a published design or facility value, not proven operating, energized, leased, utilized, billed or actual IT load.",
        "equipment_evidence": equipment or {"complete_as_built_BOM": "undisclosed"},
        "publication_conflicts": conflicts or [],
        "installed_GPU_inventory": "not_disclosed_or_established",
        "source_urls": [city_source, *(extra_sources or [])],
    }


BASE_SITES = [
    site("etix_lille_1", "Lille #1", "Tourcoing / Lille", "France", "FR", "101 Boulevard Constantin Descat, Tourcoing", 600, 100, LILLE),
    site("etix_lille_2", "Lille #2", "Sainghin-en-Melantois / Lille", "France", "FR", "1681 Rue des Saules, Sainghin-en-Melantois", 3200, 810, LILLE, extra_sources=[CIV]),
    site("etix_lille_3", "Lille #3", "Anzin / Lille", "France", "FR", "486 Avenue Augusta Ada-King, Anzin", 1500, 496, LILLE, extra_sources=[CIV]),
    site("etix_lille_4", "Lille #4", "Fretin / Lille", "France", "FR", "28 Rue des Famards, Fretin", 3200, 810, LILLE, equipment={"AI_ready_marketing": True, "complete_as_built_BOM": "undisclosed"}, conflicts=["Four website cards sum to 8.5MW while the city headline states 5.3MW."], extra_sources=[DATASHEET_LILLE]),
    site("etix_nantes_1", "Nantes #1", "Saint-Herblain / Nantes", "France", "FR", "2 Impasse Josephine Baker, Saint-Herblain", 350, 140, NANTES, equipment={"datasheet_total_IT_energy_kVA": 200, "UPS_and_boards": "2N", "generator": "N_plus_mobile", "cooling": "N_plus_1_free_cooling", "PUE": 1.4, "WUE_l_per_kWh": "less_than_0.01", "rack_density_ceiling_kw": 20}, conflicts=["Website states 350kW while datasheet states 200kVA."], extra_sources=[DATASHEET_NANTES]),
    site("etix_nantes_2", "Nantes #2", "Carquefou / Nantes", "France", "FR", "14 Rue Vega, Carquefou", 900, 300, NANTES, equipment={"datasheet_total_IT_energy_kVA": 900, "diesel_generators_UPS_and_boards": "distributed_2N", "cooling": "distributed_2N_free_cooling", "PUE": 1.3, "WUE_l_per_kWh": "less_than_0.01", "rack_density_ceiling_kw": 20}, extra_sources=[DATASHEET_NANTES]),
    site("etix_nantes_3", "Nantes #3", "Coueron / Nantes", "France", "FR", "1 Rue des Forgerons, Coueron", 1200, 372, NANTES, equipment={"datasheet_total_IT_energy_kVA": 1200, "diesel_generators_UPS_and_boards": "2N", "cooling": "2N_free_cooling", "PUE": 1.4, "WUE_l_per_kWh": "less_than_0.01", "rack_density_ceiling_kw": 20}, conflicts=["Website states 372 racks while datasheet states 400 racks."], extra_sources=[DATASHEET_NANTES]),
    site("etix_vendee_1", "Vendee #1", "La Roche-sur-Yon", "France", "FR", "4 Impasse Philippe Gozola, La Roche-sur-Yon", 240, 80, NANTES, equipment={"datasheet_total_IT_energy_kVA": 200, "UPS_and_boards": "2N", "generators": "N_current_and_2N_planned_2026", "cooling": "distributed_2N_free_cooling", "PUE": 1.4, "WUE_l_per_kWh": "less_than_0.01", "rack_density_ceiling_kw": 20}, conflicts=["Website states 240kW and 80 racks while datasheet states 200kVA and 120 racks."], extra_sources=[DATASHEET_NANTES]),
    site("etix_paris_1", "Paris #1", "Paris", "France", "FR", "19-21 Rue Poissonniere, Paris", 500, 200, PARIS, equipment={"datasheet_total_IT_energy_kVA": 500, "UPS_and_boards": "distributed_2N", "generator": "N_plus_mobile", "cooling": "N_plus_1_Catcher_free_cooling", "PUE": 1.5, "WUE_l_per_kWh": "less_than_0.01", "rack_density_ceiling_kw": 20}, extra_sources=[DATASHEET_PARIS]),
    site("etix_paris_3", "Paris #3", "Velizy-Villacoublay / Paris", "France", "FR", "16-18 Avenue de l'Europe, Velizy-Villacoublay", 4400, 800, PARIS, equipment={"datasheet_total_IT_energy_kVA": 4000, "UPS_and_boards": "2N", "generators": "N_plus_1_Catcher", "cooling": "N_plus_1_Catcher_free_cooling", "PUE": 1.25, "WUE_l_per_kWh": "less_than_0.01", "rack_density_ceiling_kw": 30, "direct_liquid_cooling_configuration_ceiling_kw": 150}, conflicts=["Website card states 4,400kW while official datasheet states 4,000kVA; the datasheet value reconciles the 4.5MW city headline.", "City page markets more than 50kW per rack while datasheet states 150kW in a DLC configuration; both are capability ceilings, not live density."], extra_sources=[DATASHEET_PARIS]),
    site("etix_lyon_1", "Lyon #1", "Lyon", "France", "FR", "81 Boulevard du Parc d'Artillerie, Lyon", 240, 80, LYON, conflicts=["Website card states 240kW while the city headline states 630kW."], extra_sources=[ZCOLO]),
    site("etix_toulouse_1", "Toulouse #1", "Balma / Toulouse", "France", "FR", "10 Rue des Freres Peugeot, Balma", 300, 100, TOULOUSE),
    site("etix_montpellier_1", "Montpellier #1", "Montpellier", "France", "FR", "143 Rue Emile Julien, Montpellier", 300, 100, MONTPELLIER),
    site("etix_liege_1", "Liege #1", "Villers-le-Bouillet / Liege", "Belgium", "BE", "3 Rue de la Science, Villers-le-Bouillet", 1160, 360, LIEGE, conflicts=["Website city headline rounds the 1,160kW card to 1.2MW."]),
    site("etix_bangkok_1", "Bangkok #1", "Bang Chalong / Bangkok", "Thailand", "TH", "111 Subdistrict 11 12 Bang Chalong, Samut Prakan", 5000, 850, BANGKOK, conflicts=["Current page states 5MW and 850 racks, while a 2024 official release stated 4MW and more than 1,000 racks during expansion."], extra_sources=[BANGKOK_2024]),
]


TRANSITION_SITES = [
    site("etix_occitanie_toulouse_acquired", "Eurofiber Toulouse", "Toulouse", "France", "FR", "131 Chemin du Sang de Serp, Toulouse", None, None, EUROFIBER, lifecycle="legal_control_transition_supported_by_public_registry_after_exclusive_talks", conflicts=["June 1 release described exclusive talks and expected June closing; later registry evidence supports control transition but no reviewed post-close ETIX asset roster was found."], extra_sources=[EUROFIBER_PDF, EUROFIBER_HDS, LEGAL_REGISTRY]),
    site("etix_occitanie_auch_acquired", "Eurofiber Auch", "Auch", "France", "FR", None, None, None, EUROFIBER, lifecycle="legal_control_transition_supported_by_public_registry_after_exclusive_talks", conflicts=["Official sources name Auch but do not provide an exact facility address in the reviewed evidence."], extra_sources=[EUROFIBER_PDF, LEGAL_REGISTRY]),
    site("etix_occitanie_nimes_acquired", "Eurofiber Nimes", "Bouillargues / Nimes", "France", "FR", "13-15 Rue Etienne Velay, Bouillargues", None, None, EUROFIBER, lifecycle="legal_control_transition_supported_by_public_registry_after_exclusive_talks", extra_sources=[EUROFIBER_PDF, EUROFIBER_HDS, LEGAL_REGISTRY]),
    site("etix_occitanie_labege_colocation_acquired", "Eurofiber Labege colocation unit", "Labege / Toulouse", "France", "FR", None, None, None, EUROFIBER, lifecycle="legal_control_transition_of_colocation_unit_supported_by_public_registry_after_exclusive_talks", conflicts=["Official transaction sources name a colocation unit in Labege but do not establish its exact building address or legal-title perimeter."], extra_sources=[EUROFIBER_PDF, LEGAL_REGISTRY]),
]


BANGKOK_EXPANSION = site(
    "etix_bangkok_2",
    "Bangkok #2",
    "Bang Chalong / Bangkok",
    "Thailand",
    "TH",
    "Bang Chalong, Samut Prakan",
    23000,
    2200,
    BANGKOK,
    lifecycle="currently_marketed_expansion_outside_older_fifteen_site_count",
    conflicts=["Bangkok page says ETIX operates two centers and gives a combined 28MW headline, but the homepage still states 15 sites and exact energized, customer-ready and billing state is not reconciled."],
)


OSM_CROSSWALK = {
    "osm_way_757483478": ("etix_lille_1", "same_complex_address_candidate_about_224m_from_provider_geocode"),
    "osm_way_540389197": ("etix_nantes_1", "current_base_site_exact_address_candidate"),
    "osm_way_525667518": ("etix_nantes_2", "current_base_site_address_candidate_about_60m_from_provider_geocode"),
    "osm_way_84917665": ("etix_nantes_3", "current_base_site_exact_road_and_building_candidate"),
    "osm_way_64108260": ("etix_toulouse_1", "current_base_site_exact_address_candidate"),
    "osm_way_76329433": ("etix_occitanie_toulouse_acquired", "newly_acquired_or_transition_Toulouse_site_exact_address_candidate"),
    "osm_node_6213121089": (None, "legacy_Vendee_2_point_not_current_Vendee_1_directory_site"),
    "osm_way_313238933": (None, "legacy_Vendee_2_building_not_current_Vendee_1_directory_site"),
    "osm_way_67893730": ("etix_occitanie_labege_colocation_acquired", "geographic_candidate_for_Labege_colocation_unit_without_official_address_bridge"),
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [*BASE_SITES, *TRANSITION_SITES, BANGKOK_EXPANSION]
    assert len(BASE_SITES) == 15
    assert len(TRANSITION_SITES) == 4
    assert len(rows) == 20
    assert sum(row["website_card_capacity_kw"] or 0 for row in BASE_SITES) == 23090
    assert sum(row["website_card_capacity_kw"] or 0 for row in rows) == 46090
    return [{"source_order": position, **row, "accessed_on": accessed_on} for position, row in enumerate(rows, 1)]


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
            "counting_rule": "OSM is a partial crosswalk and does not add a facility, MW or GPU count. Legacy and candidate rows remain outside the verified current base-site count.",
        })
    assert len(rows) == 9
    assert Counter(row["raw_operator"] for row in rows) == {"ETIX": 5, None: 4}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "etix_official_facility_summary_2026_07_19",
        "operator": "ETIX Everywhere",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "older_homepage_and_directory_base_sites": 15,
            "base_France_sites": 13,
            "base_Belgium_sites": 1,
            "base_Thailand_sites": 1,
            "June_2026_Occitanie_transaction_sites": 4,
            "transaction_implied_global_sites": 19,
            "separately_marketed_Bangkok_2_rows": 1,
            "registry_rows": len(records),
            "base_website_card_checksum_mw": 23.09,
            "all_numeric_website_card_checksum_mw": 46.09,
            "boundary": "The 15-site directory, four-site legal-control transition and Bangkok #2 marketing expansion are separate count and lifecycle scopes. Neither MW checksum is operating, energized, leased, utilized, billed or actual IT load.",
            "cumulative_delivery_claim": "50MW_IT_load_capacity_delivered_since_2012_not_current_portfolio_capacity",
        },
        "publication_conflicts": {
            "Lille": "5.3MW city headline versus 8.5MW sum of four cards",
            "Paris": "4.5MW city headline versus 4.9MW web cards; official datasheet's 4.0MVA Paris #3 reconciles to 4.5MW",
            "Lyon": "630kW city headline versus 240kW card",
            "Bangkok_1": "current 5MW and 850 racks versus 2024 official 4MW and more than 1,000 racks",
            "acquisition_count": "English release and PDF move global count from 15 to 19; French page says the pre-deal French network had 15 rather than the homepage's 13",
            "acquisition_capacity_graphic": "Official PDF simultaneously shows plus 40MW and plus 1.2MW capacity without defined denominators; neither is allocated or added",
            "homepage_staleness": "Homepage still states 15 sites after the June transaction and Bangkok page says two centers",
        },
        "transaction_and_legal_control": {
            "announcement_date": "2026-06-01",
            "announced_state": "exclusive_negotiations_with_closing_expected_June_2026",
            "sites": ["Toulouse_owned_facility", "Auch_owned_facility", "Nimes_owned_facility", "Labege_colocation_unit"],
            "subsequent_registry_evidence": "ETIX Everywhere Holding France became president of EUROFIBER DC on 2026-06-16; registered office moved to Toulouse on 2026-06-26; BODACC administrative modification published 2026-07-07.",
            "classification": "legal_control_transition_supported_by_public_registry_after_exclusive_talks",
            "boundary": "Legal-control evidence does not by itself establish property title, closing consideration, exact asset perimeter or a refreshed post-close ETIX operating roster.",
        },
        "power_cooling_and_density": {
            "Nantes_and_Paris_datasheets": "Selected official datasheets disclose 2N or distributed-2N UPS/boards, generator topologies, free-cooling, PUE 1.25-1.5, WUE below 0.01L/kWh and density ceilings of 20-30kW/rack.",
            "Paris_3_DLC_configuration_ceiling_kw": 150,
            "Bangkok_2_published_capacity_mw": 23,
            "complete_per_site_grid_transformer_switchgear_PDU_UPS_battery_generator_fuel_cooling_OEM_model_count_rating_loading_acceptance_and_remaining_life": "undisclosed",
            "boundary": "Datasheet ratings and AI-ready or DLC ceilings are design capabilities, not proof of current deployment, load or customer acceptance.",
        },
        "GPU_and_AI_boundary": {
            "AI_ready_labels": ["Lille_4", "Paris_high_density_and_DLC_configuration"],
            "ETIX_owned_installed_GPU_count": "not_disclosed_or_established",
            "customer_GPU_model_count_owner_site_delivery_rack_fabric_power_utilization_revenue_and_margin": "undisclosed",
        },
        "sustainability": {
            "EcoVadis_2026": "Gold_81_of_100",
            "Scope_1_and_2_reduction_2023_to_2025_percent": 70,
            "renewable_energy_percent": 75,
            "certified_sites": 15,
            "certification_boundary": "ESG page footnote excludes Lyon from ISO 14001 and ISO 50001 scope.",
            "homepage_conflict": "Homepage FAQ separately states 60% Scope 2 reduction and 57% renewable energy in 2025; publication date and scope are not reconciled.",
        },
        "ownership_and_finance": {
            "investors": ["Eurazeo", "Infranity"],
            "standalone_consolidated_ETIX_revenue_operating_profit_EBITDA_cash_flow_capex_debt_and_ROIC": "not_publicly_disclosed_in_reviewed_sources",
            "French_social_accounts_non_additive": {
                "ETIX_Everywhere_Holding_France_FY2024": {"revenue_EUR_thousand": 347, "EBITDA_EUR_thousand": -620, "operating_result_EUR_thousand": -752, "net_result_EUR_thousand": -3950, "debt_EUR_million": 77.9, "cash_EUR_million": 15.6, "equity_EUR_million": 123},
                "ETIX_Everywhere_France_FY2024": {"revenue_EUR_million": 6.66, "net_result_EUR_thousand": 127, "operating_result": "not_published_in_reviewed_summary"},
                "ETIX_Everywhere_Ouest_FY2024": {"revenue_EUR_million": 3.11, "EBITDA_EUR_thousand": 683, "operating_result_EUR_thousand": 419, "net_result_EUR_thousand": 347, "period_comparability": "reporting_date_or_period_changed_and_original_filing_period_length_not_reconciled"},
            },
            "boundary": "These are separate French legal-entity social accounts and must not be added or treated as consolidated ETIX fleet economics.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "raw_operator_counts": {str(key): value for key, value in sorted(Counter(row["raw_operator"] for row in osm_rows).items(), key=lambda item: str(item[0]))},
            "mapped_current_base_candidates": 5,
            "mapped_transaction_site_candidates": 1,
            "legacy_Vendee_2_objects": 2,
            "Labege_geographic_candidate": 1,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "outlook": {
            "positive_signals": ["regional_edge_density_in_France", "Occitanie_cluster_expansion", "Eurazeo_and_Infranity_long_term_capital", "selected_low_WUE_free_cooling_and_high_density_design", "Bangkok_growth_option"],
            "risk_signals": ["stale_and_conflicting_site_counts", "mixed_capacity_and_lifecycle_scopes", "private_consolidated_financials_undisclosed", "acquisition_property_and_closing_perimeter_not_fully_bridged", "no_installed_GPU_inventory_or_site_economics"],
            "analytical_view": "ETIX is a credible sovereign regional-edge consolidator with growing French density and a Thailand expansion option, but its public pages currently lag transaction state and mix design, card and cumulative-delivery measures. The investment case is private and requires a consolidated financial, legal-asset and live-load bridge before valuation or returns can be underwritten.",
        },
        "remaining_material_gaps": [
            "exact_post_close_non_overlapping_site_building_address_title_lease_operator_and_lifecycle_roster",
            "15_to_19_site_transaction_bridge_and_Bangkok_2_current_count_and_delivery_state",
            "per_site_operating_energized_customer_accepted_leased_utilized_billed_and_actual_IT_load",
            "per_site_complete_as_built_electrical_and_cooling_equipment_ledger",
            "per_site_live_liquid_cooled_MW_rack_density_measured_PUE_WUE_energy_water_and_emissions",
            "GPU_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_and_margin",
            "consolidated_revenue_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_ROIC_and_valuation",
            "Eurofiber_transaction_consideration_financing_exact_property_and_colocation_contract_perimeter",
        ],
        "sources": [HOME, LILLE, NANTES, PARIS, LYON, TOULOUSE, MONTPELLIER, LIEGE, BANGKOK, BANGKOK_2024, EUROFIBER, EUROFIBER_FR, EUROFIBER_PDF, EUROFIBER_HDS, LEGAL_REGISTRY, SUSTAINABILITY, VISION, INFRANITY, EURAZEO_2025, ZCOLO, CIV, PAPPERS_HOLDING, PAPPERS_FRANCE, PAPPERS_OUEST, DATASHEET_LILLE, DATASHEET_NANTES, DATASHEET_PARIS],
        "records_sha256": canonical_hash(records),
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
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "etix_official_facility_registry.jsonl"
    summary_path = args.output_dir / "etix_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
