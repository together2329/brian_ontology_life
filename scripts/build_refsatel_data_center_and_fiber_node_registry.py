#!/usr/bin/env python3
"""Build a scope-safe REFSA Telecomunicaciones facility and fiber-node registry.

Ten OSM rows mention REFSA.  The official Formosa Digital map classifies their
matching locations as network nodes, while provincial government reports and the
provider site separately establish a data-center shelter at Parque Industrial.
This builder therefore counts one current data-center candidate and preserves the
other nine rows as fiber-network nodes rather than multiplying the facility count.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


REFSATEL_HOME = "https://www.refsatel.com.ar/"
CDT_2022 = "https://www.refsatel.com.ar/?access=noticia&id=7"
FORMOSA_DIGITAL_MAP = "https://fd.formosa.gob.ar/mapa"
GOVERNMENT_REPORT_2023 = "https://archivos.formosa.gob.ar/media/uploads/obras_acciones/pdf_1709291983.pdf"
GOVERNMENT_REPORT_2022 = "https://archivos.formosa.gob.ar/media/uploads/obras_acciones/pdf_1677679927.pdf"
GOVERNMENT_REPORT_2020 = "https://archivos.formosa.gob.ar/media/uploads/obras_acciones/pdf_1614568663.pdf"
REFSA_ENERGY_HOME = "https://www.recursosyenergia.com.ar/"
ELECTRICITY_DISTRIBUTOR_RESOLUTION = "https://www.boletinoficial.gob.ar/detalleAviso/primera/71799/20120702"


OFFICIAL_MAP_MATCHES = {
    "osm_node_7034711942": ("Nodo REFSA Telecomunicaciones NODO PARQUE INDUSTRIAL", -26.205722346733452, -58.207155615091324, "data_center_shelter_and_network_node"),
    "osm_node_7034739991": ("Nodo REFSA Telecomunicaciones Tatané", -26.393695675407635, -58.3444748371403, "fiber_network_node"),
    "osm_node_7034747256": ("Nodo REFSA Telecomunicaciones El Colorado", -26.308342424274976, -59.37098573147978, "fiber_network_node"),
    "osm_node_7034744730": ("Nodo REFSA Telecomunicaciones General Lucio Victorio Mansilla", -26.659273447885617, -58.63063082098961, "fiber_network_node"),
    "osm_node_6519075547": ("Nodo REFSA Telecomunicaciones Villa Dos Trece", -26.18411082863653, -59.36329047381605, "fiber_network_node"),
    "osm_node_7034753291": ("Nodo REFSA Telecomunicaciones Villa Escolar", -26.621404531124682, -58.67066413164139, "fiber_network_node"),
    "osm_node_7034742245": ("Nodo REFSA Telecomunicaciones Colonia Mayor Villafañe", -26.203350500321555, -59.07971124346659, "fiber_network_node"),
    "osm_node_7034745400": ("Nodo REFSA Telecomunicaciones Herradura", -26.488428387941973, -58.311425149440765, "fiber_network_node"),
    "osm_node_7034694131": ("Nodo REFSA Telecomunicaciones Presidente Irigoyen", -26.175418961838208, -58.83395236729484, "fiber_network_node"),
    "osm_node_7034746627": ("Nodo REFSA Telecomunicaciones Misión San Francisco de Laishí", -26.239996717614844, -58.63028030097212, "fiber_network_node"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for position, (osm_ref, (official_label, official_lat, official_lon, classification)) in enumerate(OFFICIAL_MAP_MATCHES.items(), 1):
        source = osm[osm_ref]
        separation = round(distance_m(source["latitude"], source["longitude"], official_lat, official_lon), 1)
        base = {
            "id": f"refsatel_{osm_ref}",
            "operator": "REFSA Telecomunicaciones",
            "country": "Argentina",
            "country_code": "AR",
            "province": "Formosa",
            "OSM_ref": osm_ref,
            "OSM_name": source.get("name"),
            "OSM_raw_operator": source.get("operator"),
            "OSM_latitude": source.get("latitude"),
            "OSM_longitude": source.get("longitude"),
            "OSM_telecom_tag": source.get("tags", {}).get("telecom"),
            "OSM_source_url": source.get("source_url"),
            "official_map_label": official_label,
            "official_map_latitude": official_lat,
            "official_map_longitude": official_lon,
            "OSM_to_official_map_distance_m": separation,
            "classification": classification,
            "source_order": position,
            "accessed_on": accessed_on,
        }
        if classification == "data_center_shelter_and_network_node":
            base.update({
                "object_type": "DataCenterFacilityEvidence",
                "facility_label": "REFSA Telecomunicaciones Parque Industrial data-center shelter",
                "lifecycle": "current_provider_marketed_service_and_2023_government_operating_evidence",
                "current_verified_data_center_count_inclusion": True,
                "services": ["housing", "hosting", "connectivity", "public_and_private_customer_network_services"],
                "equipment_evidence": {
                    "2020": ["PLC_monitoring_for_UPS_and_cooling_systems", "shared_reported_generator_maintenance", "air_conditioner_maintenance", "10_Gbps_edge_and_20_Gbps_service_trunk_context"],
                    "2022": ["generator_maintenance", "air_conditioner_maintenance", "ASN_communications_equipment_maintenance"],
                    "2023": ["shelter_connectivity_work", "FreeNAS_06_server_racked_and_placed_in_production", "two_IBM_servers_installed", "Huawei_S6730_switch_installed"],
                    "complete_as_built_BOM": "undisclosed",
                },
                "installed_GPU_inventory": "not_disclosed_or_established",
                "counting_boundary": "The government reports establish the Parque Industrial shelter as one data-center location. They do not disclose gross or IT MW, rack count, equipment ownership, utilization or site economics.",
            })
        else:
            base.update({
                "object_type": "FiberOpticNetworkNodeEvidence",
                "lifecycle": "current_official_map_network_node",
                "current_verified_data_center_count_inclusion": False,
                "installed_GPU_inventory": "not_disclosed_or_established",
                "counting_boundary": "The official provincial map classifies this location as a network node. Its OSM telecom=data_center tag adds no verified data-center facility, rack, MW, equipment, GPU or revenue count.",
            })
        records.append(base)
    assert len(records) == 10
    assert sum(bool(row["current_verified_data_center_count_inclusion"]) for row in records) == 1
    assert sum(row["object_type"] == "FiberOpticNetworkNodeEvidence" for row in records) == 9
    assert max(row["OSM_to_official_map_distance_m"] for row in records) < 100
    assert Counter(row["OSM_raw_operator"] for row in records) == {"REFSA": 7, None: 2, "REFSA TELECOMUNICACIONES": 1}
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    data_centers = [row for row in records if row["current_verified_data_center_count_inclusion"]]
    fiber_nodes = [row for row in records if row["object_type"] == "FiberOpticNetworkNodeEvidence"]
    return {
        "id": "refsatel_data_center_and_fiber_node_summary_2026_07_19",
        "operator": "REFSA Telecomunicaciones",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "related_OSM_rows": len(records),
            "current_verified_data_center_candidates": len(data_centers),
            "current_data_center_label": data_centers[0]["facility_label"],
            "fiber_network_nodes_excluded_from_data_center_count": len(fiber_nodes),
            "OSM_operator_tagged_rows": 8,
            "OSM_name_only_rows": 2,
            "maximum_OSM_to_official_map_distance_m": max(row["OSM_to_official_map_distance_m"] for row in records),
            "boundary": "The OSM modular-center point aligns within 16.5 metres of the official Parque Industrial node and government reports identify a REFSA Telecomunicaciones data-center shelter there. The other nine OSM rows align to official map network nodes and add no data-center count.",
        },
        "provider_current_business_scale": {
            "fiber_route_km_more_than": 2000,
            "connected_points": 1729,
            "connected_education_centers": 725,
            "connected_government_organizations_and_services": 731,
            "data_center_services": ["housing", "hosting"],
            "scale_boundary": "These are current homepage claims on a site whose visible news feed and copyright date remain 2022; they are network and customer-point measures, not current physical data-center scale.",
        },
        "data_center_engineering": {
            "location": "Parque_Industrial_Formosa",
            "site_role": "data_center_shelter_and_fiber_network_node",
            "2020_evidence": {
                "energy_and_cooling_monitoring": "PLC_monitoring_for_UPS_and_cooling_systems_at_Parque_Industrial_and_UPSTI",
                "generator": "maintenance_reported_for_both_Parque_Industrial_and_UPSTI_data_centers_without_unit_allocation_or_rating",
                "cooling": "air_conditioner_maintenance_at_Parque_Industrial",
                "network": "10_Gbps_edge_and_20_Gbps_service_trunk_context",
                "CDN_services": ["Google_GGC", "Facebook_FBN_implementation_started"],
            },
            "2022_evidence": ["generator_maintenance", "air_conditioner_maintenance", "ASN_communications_equipment_maintenance"],
            "2023_evidence": ["shelter_connectivity_work", "FreeNAS_06_server_racked_and_in_production", "two_IBM_servers_installed", "Huawei_S6730_switch_installed"],
            "complete_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_cooling_OEM_model_count_rating_redundancy_loading_acceptance_age_and_remaining_life": "undisclosed",
            "operating_energized_available_contracted_customer_accepted_leased_utilized_billed_peak_and_actual_IT_MW": "undisclosed",
            "gross_or_IT_area_racks_and_measured_PUE_WUE_water": "undisclosed",
            "equipment_ownership_boundary": "Government reports do not consistently distinguish REFSA, UPSTI, hosted customer and shared provincial equipment ownership.",
        },
        "CDTREFSA_2022": {
            "announcement_state": "planned_or_launch_language_not_proven_as_separate_current_physical_facility",
            "described_resources": ["cutting_edge_servers", "IT_infrastructure", "hosting", "storage", "data_transmission"],
            "planned_cloud_services": ["PaaS", "IaaS", "SaaS", "Apps"],
            "physical_identity_to_Parque_Industrial_or_another_site": "undisclosed",
            "boundary": "The 2022 announcement does not add a facility, building, MW, rack, GPU or revenue count.",
        },
        "GPU_and_AI": {
            "REFSA_or_customer_GPU_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_and_margin": "not_disclosed_or_established",
            "boundary": "High-density servers, IBM servers, virtual machines, cloud plans and CDN services do not prove physical accelerators.",
        },
        "ownership_and_financials": {
            "ownership": "created_by_Government_of_Formosa_according_to_provider_homepage",
            "public_listing": "none_established",
            "exact_legal_entity_parent_subsidiary_division_and_share_capital_perimeter": "undisclosed",
            "latest_revenue_operating_profit_cash_flow_capex_debt_and_balance_sheet": "not_found_in_reviewed_public_sources",
            "data_center_segment_and_site_economics": "undisclosed",
            "boundary": "REFSA Energía's electricity-distribution role and the REFSA Telecomunicaciones brand are kept separate; no financial consolidation or allocation is inferred.",
        },
        "OSM_crosswalk": {
            "related_objects": len(records),
            "raw_operator_counts": dict(Counter(str(row["OSM_raw_operator"]) for row in records)),
            "records": [{key: row[key] for key in ["OSM_ref", "OSM_name", "official_map_label", "OSM_to_official_map_distance_m", "classification", "current_verified_data_center_count_inclusion"]} for row in records],
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "outlook": {
            "positive_signals": ["provincial_state_mandate", "more_than_2000_km_fiber_network", "Parque_Industrial_housing_and_hosting_site", "public_and_private_customer_connectivity", "Red_Capricornio_reach"],
            "risk_signals": ["single_verified_data_center", "homepage_metrics_visibly_stale", "no_current_MW_area_racks_utilization_or_site_economics", "legal_and_financial_perimeter_undisclosed", "no_GPU_inventory", "public_sector_customer_and_governance_concentration", "Argentina_inflation_and_currency_risk"],
            "analytical_view": "REFSA Telecomunicaciones is useful evidence of provincial edge and sovereign-service demand, not an investable data-center pure play. Its one verified shelter and broad fiber network may support regional digital services, but current capacity, utilization, equipment ownership, financial results and returns remain unavailable.",
        },
        "sources": [REFSATEL_HOME, CDT_2022, FORMOSA_DIGITAL_MAP, GOVERNMENT_REPORT_2023, GOVERNMENT_REPORT_2022, GOVERNMENT_REPORT_2020, REFSA_ENERGY_HOME, ELECTRICITY_DISTRIBUTOR_RESOLUTION],
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
    registry_path = args.output_dir / "refsatel_data_center_and_fiber_node_registry.jsonl"
    summary_path = args.output_dir / "refsatel_data_center_and_fiber_node_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
