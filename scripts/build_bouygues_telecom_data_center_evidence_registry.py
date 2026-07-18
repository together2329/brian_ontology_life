#!/usr/bin/env python3
"""Build Bouygues Telecom's data-center, asset-transfer and OSM evidence registry.

Bouygues Telecom's public evidence spans several incompatible scopes: a 2021
page naming three operated data centers, 2021-2025 sales of the buildings and
passive infrastructure of 22 mobile switching centres/data centers to
Towerlink, continuing service and lease relationships, and 31 related OSM map
objects.  This builder preserves those scopes instead of presenting any one of
them as a current physical-building census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import unicodedata
from pathlib import Path


ENERGY_PAGE = "https://www.corporate.bouyguestelecom.fr/nos-engagements/demarche-societale-environnementale/numerique-positif-pour-la-planete/des-installations-performantes/"
CSR_2021 = "https://www.corporate.bouyguestelecom.fr/wp-content/uploads/2022/06/RapportRSE-2021-Partie2-BouyguesTelecom-Juin2022.pdf"
URD_2025 = "https://www.bouygues.com/app/uploads/2026/03/bouygues_deu_2025_uk_web.pdf"
CELLNEX_2018 = "https://informeanual.cellnex.com/2018/2018-crecimiento-consolidacion-y-transformacion.html"
CELLNEX_TOWERLINK_SALE = "https://www.cellnex.com/dk-en/news/cellnex-agreement-towerlink-datacenter-france-vauban-infra/"
CELLNEX_CNMV = "https://www.cellnex.com/es-es/relacion-con-inversores/comunicaciones-cnmv/"
BOUYGUES_Q1_2026 = "https://www.bouygues.com/app/uploads/docs/127403/Press-Release-Q1-2026.pdf"
SFR_MOU = "https://www.corporate.bouyguestelecom.fr/archives-communique-presse/bouygues-telecom-franchit-une-etape-structurante-pour-son-developpement-futur-en-signant-aux-cotes-de-free-groupe-iliad-et-orange-un-protocole-daccord-avec-altice-france-en-vue-de-l/"
AI_FACTORY = "https://www.corporate.bouyguestelecom.fr/nos-activites/strategie-innovation/"
PRISME_AI = "https://www.corporate.bouyguestelecom.fr/archives-communique-presse/bouygues-telecom-choisit-prisme-ai-pour-deployer-son-studio-ia-et-accelerer-sa-transformation-agentique/"
GOOGLE_CLOUD_AI = "https://www.corporate.bouyguestelecom.fr/archives-communique-presse/bouygues-telecom-revolutionne-lexperience-client-en-lancant-le-1er-assistant-de-vente-100-voix-en-france-dote-de-lia-generative-de-google-cloud/"
OVHCLOUD_PARTNERSHIP = "https://www.corporate.bouyguestelecom.fr/archives-communique-presse/bouygues-telecom-entreprises-et-ovhcloud-sassocient-pour-permettre-aux-entreprises-de-taille-intermediaire-dacceder-facilement-au-cloud-hybride/"
NUMSPOT = "https://www.corporate.bouyguestelecom.fr/communique-de-presse-numspot-numspot-repense-le-pilotage-du-cloud-avec-une-plateforme-innovante-nouvelle-generation/"
NUMSPOT_GPU = "https://www.corporate.bouyguestelecom.fr/archives-communique-presse/un-an-apres-sa-creation-numspot-affiche-ses-premiers-resultats-et-annonce-le-lancement-de-sa-plateforme-de-services-manages-en-2024/"


NAMED_LOCATIONS = [
    {
        "id": "bouygues_telecom_bievres",
        "object_type": "ProviderNamedHistoricalDataCenterLocationRecord",
        "provider_location_name": "Bièvres",
        "country_code": "FR",
        "published_operating_evidence": "listed_as_one_of_three_Bouygues_Telecom_data_centers_on_page_last_modified_in_2021",
        "current_2026_property_owner": "undisclosed_at_named_location_level",
        "current_2026_Bouygues_operating_or_tenancy_status": "undisclosed_at_named_location_level",
        "source_urls": [ENERGY_PAGE, CSR_2021, URD_2025],
    },
    {
        "id": "bouygues_telecom_saclay",
        "object_type": "ProviderNamedHistoricalDataCenterLocationRecord",
        "provider_location_name": "Saclay",
        "country_code": "FR",
        "published_operating_evidence": "listed_as_one_of_three_Bouygues_Telecom_data_centers_on_page_last_modified_in_2021",
        "current_2026_property_owner": "undisclosed_at_named_location_level",
        "current_2026_Bouygues_operating_or_tenancy_status": "undisclosed_at_named_location_level",
        "source_urls": [ENERGY_PAGE, CSR_2021, URD_2025],
    },
    {
        "id": "bouygues_telecom_montigny_le_bretonneux",
        "object_type": "ProviderNamedHistoricalDataCenterLocationRecord",
        "provider_location_name": "Montigny-le-Bretonneux",
        "country_code": "FR",
        "opened": 2009,
        "ISO_50001_since": 2012,
        "European_Code_of_Conduct_participant": True,
        "published_operating_evidence": "listed_as_one_of_three_Bouygues_Telecom_data_centers_on_page_last_modified_in_2021",
        "current_2026_property_owner": "undisclosed_at_named_location_level",
        "current_2026_Bouygues_operating_or_tenancy_status": "undisclosed_at_named_location_level",
        "source_urls": [ENERGY_PAGE, CSR_2021, URD_2025],
    },
]


TRANSFER_BATCHES = [
    {
        "id": "bouygues_towerlink_transfer_2021",
        "object_type": "DataCenterPassiveAssetTransferBatchRecord",
        "transaction_year": 2021,
        "transferred_MSC_or_data_center_building_and_passive_infrastructure_count": 13,
        "consideration_EUR_million": 199,
        "disposal_gain_EUR_million": 114,
        "timing_detail": "seven_assets_in_March; eleven_assets_and_EUR168m_in_H1; two_more_and_EUR31m_in_H2",
        "buyer": "Towerlink_France_then_controlled_by_Cellnex",
        "seller_and_continuing_main_user": "Bouygues_Telecom",
        "source_urls": [URD_2025, CELLNEX_2018],
    },
    {
        "id": "bouygues_towerlink_transfer_2022",
        "object_type": "DataCenterPassiveAssetTransferBatchRecord",
        "transaction_year": 2022,
        "transferred_MSC_or_data_center_building_and_passive_infrastructure_count": 4,
        "consideration_EUR_million": 102,
        "disposal_gain_EUR_million": 52,
        "buyer": "Towerlink_France_then_controlled_by_Cellnex",
        "seller_and_continuing_main_user": "Bouygues_Telecom",
        "source_urls": [URD_2025],
    },
    {
        "id": "bouygues_towerlink_core_idf_transfer_2024_2025",
        "object_type": "DataCenterPassiveAssetSaleAndLeasebackBatchRecord",
        "board_authorization_date": "2024-06-20",
        "transferred_core_Ile_de_France_data_center_count": 5,
        "closing_detail": [
            {"date": "2024-12-18", "sites": 2, "consideration_EUR_million": 63, "gain_EUR_million": 7},
            {"date": "2025-01", "sites": 3, "consideration_EUR_million": 87, "gain_EUR_million": 12},
        ],
        "buyer": "Towerlink_France_then_controlled_by_Cellnex",
        "seller_and_lessee_or_continuing_user": "Bouygues_Telecom",
        "IFRS_16_boundary": "sale_and_leaseback; for the three January 2025 sites Bouygues reported EUR39m investing proceeds and EUR48m financing or retained-use lease-liability effects",
        "named_site_identity": "undisclosed",
        "source_urls": [URD_2025],
    },
    {
        "id": "towerlink_cellnex_to_vauban_ownership_transition",
        "object_type": "DataCenterPlatformOwnershipTransitionRecord",
        "platform": "Towerlink_France",
        "seller": "Cellnex",
        "buyer": "Vauban_Infra_Fibre",
        "equity_interest_percent": 99.99,
        "announced_consideration_EUR_million": 391,
        "closing_date": "2026-01-23",
        "continuing_customer_boundary": "Bouygues_Telecom_remains_the_named_main_customer_or_service_counterparty; ownership_transition_does_not_establish_current_site_count",
        "source_urls": [CELLNEX_TOWERLINK_SALE, CELLNEX_CNMV, URD_2025],
    },
]


PORTFOLIO_CONTEXT = {
    "historical_provider_named_data_centers": 3,
    "historical_transferred_MSC_or_data_center_passive_assets_checksum": 22,
    "historical_transfer_consideration_checksum_EUR_million": 451,
    "historical_disposal_gain_checksum_EUR_million": 185,
    "current_exact_physical_building_roster": "undisclosed",
    "current_property_ownership_by_site": "undisclosed",
    "current_Bouygues_operated_or_tenanted_roster": "undisclosed",
    "ownership_operating_boundary": "The transfers covered buildings and passive infrastructure. They do not prove that Bouygues removed its telecom or IT equipment, stopped operating services, or ceased using the locations.",
    "power_and_resilience": {
        "disclosed": ["optimized_UPS_or_inverter_operation", "backup_generator_systems", "reduced_generator_testing_or_use_target", "biofuel_development", "solar_and_hydrogen_hybrid_generator_tests"],
        "undisclosed": ["site_MW_or_MVA", "utility_feeds", "substations", "transformers", "switchgear", "UPS_and_battery_counts_ratings_OEMs_topology", "generator_counts_ratings_OEMs_fuel_and_runtime", "energized_leased_utilized_customer_accepted_and_billed_IT_load"],
    },
    "cooling": {
        "disclosed": ["outside_air_free_cooling_below_9C", "cold_corridor_containment", "airflow_and_hotspot_optimization", "eco_cooling_for_newly_commissioned_sites", "alternative_refrigerants_under_study"],
        "undisclosed": ["site_level_PUE_and_WUE", "absolute_site_energy_and_water", "cooling_equipment_BOM_and_OEMs", "liquid_cooling", "high_density_AI_ready_MW", "fleetwide_eco_cooling_deployment_share"],
    },
    "energy_and_emissions": {
        "2025_scope_1_and_2_network_operations_share_percent": 71,
        "Statkraft_CPPA_term_years": 10,
        "electricity_requirements_covered_by_CPPA_plus_guarantees_of_origin_percent": 82,
        "Suez_PPA_term_years": 15,
        "Suez_PPA_renewable_energy_GWh_per_year": 53,
        "Ecowatt_winter_reduction_commitment_percent": 10,
        "boundary": "Procurement coverage and commitments are not data-center-only consumption, hourly matching, realized savings or per-site efficiency.",
    },
    "GPU_and_AI": {
        "direct_physical_GPU_inventory_by_model_site_count_owner_power_and_utilization": "undisclosed",
        "evidence": ["internal_AI_Factory_at_Meudon_Technopole", "Prisme_ai_studio_on_group_or_chosen_cloud_infrastructure", "Google_Cloud_voice_AI", "OVHcloud_hybrid_cloud_partnership", "NumSpot_consortium_and_OUTSCALE_GPU_service"],
        "boundary": "AI products, partnerships and consortium services do not establish Bouygues-owned GPUs or accelerator deployment inside a named Bouygues data center.",
    },
    "comparison_boundary": "Do not add or equate three 2021 provider-named locations, 22 historical passive-asset transfers, Cellnex's earlier 62-site option or 100-edge-site target, current Towerlink assets, and 31 OSM objects.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def without_accents(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", value.casefold())
        if unicodedata.category(char) != "Mn"
    )


def load_osm_candidates(path: Path) -> list[dict]:
    candidates = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        combined = without_accents(f"{row.get('name') or ''} {row.get('operator') or ''}")
        if "bouygues telecom" in combined:
            candidates.append(row)
    return candidates


def build_osm_reviews(osm_path: Path) -> list[dict]:
    candidates = load_osm_candidates(osm_path)
    assert len(candidates) == 31, [row["id"] for row in candidates]
    exact_montigny = {"osm_node_6174610289", "osm_way_113714402"}
    assert exact_montigny <= {row["id"] for row in candidates}
    reviews = []
    for source in candidates:
        exact = source["id"] in exact_montigny
        reviews.append({
            "osm_object_id": source["id"],
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "provider_record_id": "bouygues_telecom_montigny_le_bretonneux" if exact else None,
            "disposition": "same_named_Montigny_location_duplicate_point_and_footprint_representations_not_two_facilities" if exact else "Bouygues_related_map_object_unresolved_against_current_facility_property_and_tenancy_roster",
            "boundary": "OSM identity, operator tags and footprints do not prove current ownership, operation, lifecycle, capacity, power topology, GPU inventory or facility economics.",
        })
    return sorted(reviews, key=lambda row: row["osm_object_id"])


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for position, source in enumerate([*NAMED_LOCATIONS, *TRANSFER_BATCHES], start=1):
        records.append({
            **source,
            "source_order": position,
            "operator_or_tenant": "Bouygues_Telecom",
            "record_granularity": "named_historical_location_or_transaction_batch_not_current_uniform_physical_building",
            "portfolio_context": PORTFOLIO_CONTEXT,
            "accessed_on": accessed_on,
        })
    assert len(records) == 7
    assert len({row["id"] for row in records}) == len(records)
    return records


def build_summary(records: list[dict], osm_reviews: list[dict], accessed_on: str) -> dict:
    return {
        "registry": "Bouygues Telecom data-center, passive-asset transfer and OSM evidence registry",
        "accessed_on": accessed_on,
        "records": len(records),
        "provider_named_historical_location_records": len(NAMED_LOCATIONS),
        "passive_asset_transfer_batches": 3,
        "platform_ownership_transition_records": 1,
        "historical_transferred_MSC_or_data_center_passive_assets_checksum": sum(
            row.get("transferred_MSC_or_data_center_building_and_passive_infrastructure_count", row.get("transferred_core_Ile_de_France_data_center_count", 0))
            for row in TRANSFER_BATCHES
        ),
        "historical_transfer_consideration_checksum_EUR_million": 451,
        "historical_disposal_gain_checksum_EUR_million": 185,
        "related_OSM_objects": len(osm_reviews),
        "raw_operator_tagged_OSM_objects": sum(bool(row["osm_operator"]) for row in osm_reviews),
        "raw_name_only_OSM_objects": sum(bool(row["osm_name"]) and not row["osm_operator"] for row in osm_reviews),
        "Montigny_duplicate_map_representations": sum(bool(row["provider_record_id"]) for row in osm_reviews),
        "unresolved_OSM_objects": sum(not row["provider_record_id"] for row in osm_reviews),
        "osm_reviews": osm_reviews,
        "portfolio_context": PORTFOLIO_CONTEXT,
        "FY2025_financial_snapshot_EUR_million": {
            "sales": 8100,
            "sales_billed_to_customers": 6500,
            "EBITDA_after_leases": 2042,
            "current_operating_profit_from_activities": 674,
            "current_operating_profit": 639,
            "operating_profit": 648,
            "net_profit_attributable_to_group": 326,
            "gross_capex_excluding_frequencies": 1480,
            "net_debt": 3738,
        },
        "Q1_2026_financial_snapshot_EUR_million": {
            "sales": 2020,
            "sales_from_services": 1602,
            "sales_billed_to_customers": 1619,
            "EBITDA_after_leases": 415,
            "current_operating_profit_from_activities": 82,
            "current_operating_profit": 73,
            "operating_profit": 74,
            "gross_capex": 342,
        },
        "official_sources": [
            ENERGY_PAGE, CSR_2021, URD_2025, CELLNEX_2018,
            CELLNEX_TOWERLINK_SALE, CELLNEX_CNMV, BOUYGUES_Q1_2026, SFR_MOU,
            AI_FACTORY, PRISME_AI, GOOGLE_CLOUD_AI, OVHCLOUD_PARTNERSHIP,
            NUMSPOT, NUMSPOT_GPU,
        ],
        "records_sha256": canonical_hash(records),
        "comparison_boundary": PORTFOLIO_CONTEXT["comparison_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/bouygues_telecom_data_center_evidence_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/bouygues_telecom_data_center_evidence_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_reviews = build_osm_reviews(args.osm)
    summary = build_summary(records, osm_reviews, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_reviews": len(osm_reviews), "registry": str(args.registry), "summary": str(args.summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
