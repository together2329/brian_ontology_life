#!/usr/bin/env python3
"""Build Flexential's current provider-card facility registry.

The current directory mixes operating and development cards and a card is not
necessarily one physical building.  This builder preserves those boundaries,
maps public OSM objects separately, and records GPU/equipment disclosures without
turning hosting capability or customer deployments into Flexential-owned GPUs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY_URL = "https://www.flexential.com/data-centers"
NORCROSS2_RELEASE = "https://www.flexential.com/resources/press-release/flexential-adding-fifth-atlanta-area-data-center"
HILLSBORO_PROPERTY_RELEASE = "https://www.flexential.com/resources/press-release/flexential-secures-strategic-real-estate-ownership-hillsboro-oregon"
HILLSBORO6_RELEASE = "https://www.flexential.com/resources/press-release/flexential-acquires-prime-property-hillsboro-plans-new-data-center"
PARKER_RELEASE = "https://www.flexential.com/resources/press-release/flexential-announces-flexanywhere-platform-expansion-new-state-art-data"
ESG_RELEASE = "https://www.flexential.com/resources/press-release/flexentials-2025-esg-report-details-progress-sustainable-data-center"
DGX_URL = "https://www.flexential.com/products-services/high-density-colocation/nvidia-dgx-ready-data-centers"
DIGITALOCEAN_RELEASE = "https://www.flexential.com/resources/press-release/flexential-support-digitaloceans-gpu-infrastructure-expansion-high-density"
DIGITALOCEAN_CASE = "https://www.flexential.com/system/files/file/2025-08/digitalocean-customer-case-study.pdf"
APPLIED_DIGITAL_RELEASE = "https://www.flexential.com/resources/press-release/flexential-empowers-applied-digitals-high-performance-computing-solutions"
COREWEAVE_MEDIA = "https://www.flexential.com/resources/media-coverage/inside-flexential-coreweave-alliance-scaling-ai-infrastructure-high"
LIQUID_COOLING_GUIDE = "https://www.flexential.com/resources/brochure/liquid-cooling-applications"


def site(site_id: str, name: str, market: str, area_sq_ft: int, critical_power_mw: float,
         lifecycle: str, page_url: str, **extra: object) -> dict:
    return {
        "site_id": site_id,
        "provider_label": name,
        "market": market,
        "country_code": "US",
        "directory_area_sq_ft": area_sq_ft,
        "directory_critical_power_mw": critical_power_mw,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "facility_page_url": page_url,
        **extra,
    }


OPERATIONAL = "current_directory_card_without_reviewed_development_language_exact_energization_lease_utilization_and_billing_not_individually_reverified"

FACILITIES = [
    site("atl_alpharetta", "Atlanta - Alpharetta", "Atlanta", 142475, 6, OPERATIONAL, "https://www.flexential.com/data-centers/ga/atlanta/alpharetta-data-center"),
    site("atl_douglasville_1", "Atlanta - Douglasville 1", "Atlanta", 205000, 22.5, OPERATIONAL, "https://www.flexential.com/data-centers/ga/atlanta/douglasville-data-center", area_qualifier="published_lower_bound"),
    site("atl_douglasville_2", "Atlanta - Douglasville 2", "Atlanta", 358000, 36, "under_construction_and_on_target_for_completion_not_yet_proven_operating", "https://www.flexential.com/data-centers/ga/atlanta/douglasville-2-data-center"),
    site("atl_norcross_1", "Atlanta - Norcross 1", "Atlanta", 32740, 1.8, OPERATIONAL, "https://www.flexential.com/data-centers/ga/atlanta/norcross-data-center"),
    site("atl_norcross_2", "Atlanta - Norcross 2", "Atlanta", 48000, 4.5, "planned_expected_online_first_half_2028", "https://www.flexential.com/data-centers/ga/atlanta/norcross-2-data-center", official_address="2755 Northwoods Parkway, Norcross, GA"),
    site("clt_north", "Charlotte - North", "Charlotte", 62589, 3.3, OPERATIONAL, "https://www.flexential.com/data-centers/nc/charlotte/north-data-center"),
    site("clt_south", "Charlotte - South", "Charlotte", 66666, 2.36, OPERATIONAL, "https://www.flexential.com/data-centers/nc/charlotte/south-data-center"),
    site("cvg", "Cincinnati", "Cincinnati", 43551, 3.8, OPERATIONAL, "https://www.flexential.com/data-centers/oh/cincinnati/data-center", official_address="5307 Muhlhauser Rd, West Chester, OH 45011"),
    site("dfw_downtown", "Dallas - Downtown Dallas", "Dallas", 80447, 6.66, OPERATIONAL, "https://www.flexential.com/data-centers/tx/dallas/downtown-data-center", physical_scope_note="Facility page says five data centers in one location; one directory card is not one building."),
    site("dfw_plano", "Dallas - Plano", "Dallas", 261425, 18, OPERATIONAL, "https://www.flexential.com/data-centers/tx/dallas/plano-data-center"),
    site("dfw_richardson", "Dallas - Richardson", "Dallas", 100807, 3.75, OPERATIONAL, "https://www.flexential.com/data-centers/tx/dallas/richardson-data-center"),
    site("den_aurora", "Denver - Aurora", "Denver", 171289, 6.75, OPERATIONAL, "https://www.flexential.com/data-centers/co/denver/aurora-data-center"),
    site("den_centennial", "Denver - Centennial", "Denver", 43294, 1.6, OPERATIONAL, "https://www.flexential.com/data-centers/co/denver/centennial-data-center"),
    site("den_englewood", "Denver - Englewood", "Denver", 240549, 18, OPERATIONAL, "https://www.flexential.com/data-centers/co/denver/englewood-data-center"),
    site("den_parker", "Denver - Parker", "Denver", 249000, 22.5, "under_development_scheduled_to_open_later_in_2026", "https://www.flexential.com/data-centers/co/denver/parker-data-center", land_acres=17, electric_utility="CORE Electric Cooperative"),
    site("fll", "Fort Lauderdale", "Fort Lauderdale", 64164, 3.15, OPERATIONAL, "https://www.flexential.com/data-centers/fl/fort-lauderdale/data-center"),
    site("jax", "Jacksonville", "Jacksonville", 35184, 1.39, OPERATIONAL, "https://www.flexential.com/data-centers/fl/jacksonville/data-center"),
    site("las_downtown", "Las Vegas - Downtown", "Las Vegas", 33135, 1.37, OPERATIONAL, "https://www.flexential.com/data-centers/nv/las-vegas/downtown-data-center"),
    site("las_north", "Las Vegas - North", "Las Vegas", 111240, 9, OPERATIONAL, "https://www.flexential.com/data-centers/nv/las-vegas/north-data-center"),
    site("lou_downtown", "Louisville - Downtown", "Louisville", 61080, 3.09, OPERATIONAL, "https://www.flexential.com/data-centers/ky/louisville/downtown-data-center"),
    site("lou_east", "Louisville - East", "Louisville", 35588, 1.46, OPERATIONAL, "https://www.flexential.com/data-centers/ky/louisville/east-data-center"),
    site("msp_chaska", "Minneapolis - Chaska", "Minneapolis", 160838, 9, OPERATIONAL, "https://www.flexential.com/data-centers/mn/minneapolis/chaska-data-center"),
    site("bna_brentwood", "Nashville - Brentwood", "Nashville", 19150, 1.49, OPERATIONAL, "https://www.flexential.com/data-centers/tn/nashville/brentwood-data-center"),
    site("bna_cool_springs", "Nashville - Cool Springs", "Nashville", 80000, 8, OPERATIONAL, "https://www.flexential.com/data-centers/tn/nashville/cool-springs-data-center"),
    site("bna_franklin", "Nashville - Franklin", "Nashville", 80000, 6, OPERATIONAL, "https://www.flexential.com/data-centers/tn/nashville/franklin-data-center"),
    site("tpa_north", "North Tampa", "Tampa", 60166, 3, OPERATIONAL, "https://www.flexential.com/data-centers/fl/tampa/north-data-center"),
    site("phl_collegeville", "Philadelphia - Collegeville", "Philadelphia", 203703, 7.2, OPERATIONAL, "https://www.flexential.com/data-centers/pa/philadelphia/collegeville-data-center"),
    site("phx_deer_valley", "Phoenix - Deer Valley", "Phoenix", 109476, 5.02, OPERATIONAL, "https://www.flexential.com/data-centers/az/phoenix/deer-valley-data-center"),
    site("pdx_hillsboro_1", "Portland - Hillsboro 1", "Portland", 85388, 5.3, OPERATIONAL, "https://www.flexential.com/data-centers/or/portland/hillsboro1-data-center", official_address="3935 NE Aloclek Drive, Hillsboro, OR"),
    site("pdx_hillsboro_2", "Portland - Hillsboro 2", "Portland", 242683, 18, OPERATIONAL, "https://www.flexential.com/data-centers/or/portland/hillsboro2-data-center", official_address="5737 NE Huffman Street, Hillsboro, OR"),
    site("pdx_hillsboro_3", "Portland - Hillsboro 3", "Portland", 358000, 36, OPERATIONAL, "https://www.flexential.com/data-centers/or/portland/hillsboro3-data-center", official_address="5419 NE Starr Boulevard, Hillsboro, OR"),
    site("pdx_hillsboro_4", "Portland - Hillsboro 4", "Portland", 138009, 18, "commissioned_and_fully_leased_by_2026_05", "https://www.flexential.com/data-centers/or/portland/hillsboro4-data-center", official_address="4915 NE Starr Boulevard, Hillsboro, OR"),
    site("pdx_hillsboro_5", "Portland - Hillsboro 5", "Portland", 358000, 36, "under_construction_and_on_target_for_completion_not_yet_proven_operating", "https://www.flexential.com/data-centers/portland-hillsboro-5-data-center", official_address="4975 NE Starr Boulevard, Hillsboro, OR"),
    site("pdx_hillsboro_6", "Portland - Hillsboro 6", "Portland", 350000, 27, "planned_after_2025_property_acquisition", "https://www.flexential.com/data-centers/portland-hillsboro-6-data-center"),
    site("rdu", "Raleigh", "Raleigh", 99976, 4.31, OPERATIONAL, "https://www.flexential.com/data-centers/nc/raleigh/data-center"),
    site("ric", "Richmond", "Richmond", 28594, 2.8, OPERATIONAL, "https://www.flexential.com/data-centers/va/richmond/data-center"),
    site("slc_downtown", "Salt Lake City - Downtown", "Salt Lake City", 44550, 2.65, OPERATIONAL, "https://www.flexential.com/data-centers/ut/salt-lake-city/downtown-data-center"),
    site("slc_fair_park", "Salt Lake City - Fair Park", "Salt Lake City", 22539, 0.49, OPERATIONAL, "https://www.flexential.com/data-centers/ut/salt-lake-city/fair-park-data-center", directory_power_display="490 kW"),
    site("slc_millcreek", "Salt Lake City - Millcreek", "Salt Lake City", 36000, 1.92, OPERATIONAL, "https://www.flexential.com/data-centers/ut/salt-lake-city/millcreek-data-center"),
    site("slc_south_valley", "Salt Lake City - South Valley", "Salt Lake City", 30512, 1.2, OPERATIONAL, "https://www.flexential.com/data-centers/ut/salt-lake-city/south-valley-data-center"),
    site("tpa_west", "West Tampa", "Tampa", 31600, 1.81, OPERATIONAL, "https://www.flexential.com/data-centers/fl/tampa/west-data-center"),
]


EQUIPMENT = {
    "atl_alpharetta": {"power": ["2N UPS topology", "6 MW critical-load UPS"], "cooling": ["N+1 cooling", "hot/cold aisle", "liquid-cooling ready"]},
    "atl_douglasville_1": {"cooling": ["customer deployment supports liquid cooling above 1,500 W/sq ft"], "boundary": "Customer case capability is not measured fleet density or a complete equipment bill of materials."},
    "atl_douglasville_2": {"power": ["distributed 4:3 UPS", "36 MW critical-load UPS"], "cooling": ["N+2 cooling", "up to 80+ kW per cabinet", "target PUE 1.4"]},
    "atl_norcross_1": {"power": ["N+1 UPS", "1.8 MW critical-load UPS"], "cooling": ["N+1 cooling", "150 W/sq ft"]},
    "pdx_hillsboro_3": {"power": ["distributed 4:3 UPS", "36 MW critical-load UPS"], "cooling": ["N+2 cooling", "1,500 W/sq ft", "design PUE 1.3"]},
    "pdx_hillsboro_5": {"cooling": ["liquid-cooling ready", "supports 150+ kW per cabinet"], "boundary": "Published design capability is not commissioned liquid-cooled MW or measured rack draw."},
}


OSM_OBJECT_TO_SITE = {
    "osm_way_826001604": "bna_brentwood", "osm_node_12112295055": "bna_brentwood",
    "osm_node_12112270180": "den_aurora", "osm_node_11400893880": "den_centennial",
    "osm_way_257581364": "ric", "osm_way_39083797": "atl_alpharetta",
    "osm_way_1097502168": "atl_douglasville_1", "osm_way_1258702591": "atl_douglasville_2",
    "osm_way_392324240": "atl_norcross_1", "osm_way_1307920829": "clt_north",
    "osm_way_215630401": "clt_south", "osm_node_12112201416": "cvg",
    "osm_node_12112238944": "dfw_downtown", "osm_way_650412346": "dfw_plano",
    "osm_way_548184239": "dfw_richardson", "osm_way_377545385": "den_englewood",
    "osm_way_741629998": "fll", "osm_node_12112266917": "jax",
    "osm_way_1379421123": "las_downtown", "osm_way_746278786": "las_north",
    "osm_way_330276516": "lou_downtown", "osm_way_329551673": "lou_east",
    "osm_way_52227492": "msp_chaska", "osm_way_1210515186": "bna_cool_springs",
    "osm_way_942604537": "bna_franklin", "osm_way_1178609569": "phl_collegeville",
    "osm_way_157362579": "phx_deer_valley", "osm_way_328703598": "pdx_hillsboro_1",
    "osm_way_328703599": "pdx_hillsboro_1", "osm_way_471691760": "pdx_hillsboro_2",
    "osm_way_918873142": "pdx_hillsboro_3", "osm_way_860433344": "pdx_hillsboro_4",
    "osm_way_1080170579": "pdx_hillsboro_4", "osm_way_1080170580": "pdx_hillsboro_5",
    "osm_node_12112361725": "rdu", "osm_way_729696933": "slc_downtown",
    "osm_way_1121188409": "slc_fair_park", "osm_way_1056658555": "slc_millcreek",
    "osm_way_355926681": "slc_south_valley", "osm_way_1085608797": "tpa_north",
    "osm_node_12112380995": "tpa_west",
}

LEGACY_OR_UNRESOLVED_OSM = {
    "osm_way_296374269": "Allentown label and market filter remain visible, but no current facility card is rendered in the reviewed directory.",
    "osm_node_12112236372": "Denver Downtown appears in OSM but not in the current rendered facility-card roster.",
    "osm_node_12112382397": "Salt Lake City Lindon appears in OSM but not in the current rendered facility-card roster.",
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id, related = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        haystack = " ".join(str(row.get(k, "")) for k in ("name", "operator", "website")).lower()
        if "flexential" in haystack:
            related.append(row)
    return by_id, related


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, related = load_osm(osm_path)
    expected = set(OSM_OBJECT_TO_SITE) | set(LEGACY_OR_UNRESOLVED_OSM)
    assert len(related) == 44, len(related)
    assert expected == {row["id"] for row in related}, sorted(expected ^ {row["id"] for row in related})
    mapped: dict[str, list[dict]] = {}
    for object_id, site_id in OSM_OBJECT_TO_SITE.items():
        row = osm[object_id]
        note = "Public map point or footprint; not provider-certified ownership, lifecycle or building count."
        if object_id == "osm_way_860433344":
            note += " OSM name says Hillsboro 4 while its website tag points to Hillsboro 5; mapping follows the object name."
        if object_id == "osm_way_1080170579":
            note += " The H4 Expansion footprint is nested under the H4 provider-card scope; its website tag points to H5 and remains an identity anomaly."
        mapped.setdefault(site_id, []).append({
            "osm_object_id": object_id,
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "source_url": row["source_url"],
            "boundary": note,
        })
    records = []
    for order, source in enumerate(FACILITIES, 1):
        site_id = source["site_id"]
        sources = [DIRECTORY_URL, source["facility_page_url"]]
        if site_id == "atl_norcross_2": sources.append(NORCROSS2_RELEASE)
        if site_id in {"pdx_hillsboro_4", "pdx_hillsboro_5"}: sources.append(HILLSBORO_PROPERTY_RELEASE)
        if site_id == "pdx_hillsboro_6": sources.append(HILLSBORO6_RELEASE)
        if site_id == "den_parker": sources.append(PARKER_RELEASE)
        if site_id in {"atl_douglasville_2", "pdx_hillsboro_4", "pdx_hillsboro_5", "las_north", "slc_south_valley"}: sources.append(ESG_RELEASE)
        gpu_evidence = []
        if site_id == "atl_douglasville_1":
            gpu_evidence.append({"customer": "DigitalOcean", "accelerators": ["NVIDIA H200", "AMD Instinct"], "ownership": "customer_or_tenant_deployment_not_Flexential_fleet", "exact_count": "undisclosed", "sources": [DIGITALOCEAN_RELEASE, DIGITALOCEAN_CASE]})
            sources.extend([DIGITALOCEAN_RELEASE, DIGITALOCEAN_CASE])
        if site_id == "dfw_plano":
            gpu_evidence.append({"customer": "CoreWeave", "deployment_mw": 13, "rack_density": "more_than_80_kW", "accelerators": ["latest NVIDIA clusters_model_and_count_undisclosed"], "evidence_class": "operator_hosted_media_coverage_not_primary_contract_disclosure", "ownership": "customer_or_tenant_deployment_not_Flexential_fleet", "source": COREWEAVE_MEDIA})
            sources.append(COREWEAVE_MEDIA)
        records.append({
            "id": f"flexential_{site_id}",
            "object_type": "ProviderPublishedDataCenterFacilityCard",
            "source_order": order,
            "operator": "Flexential",
            **source,
            "record_granularity": "provider_directory_card_not_proven_one_to_one_physical_building",
            "power_measure_boundary": "Directory critical-power MW is a marketed card value across mixed lifecycle; it is not automatically operating, energized, leased, utilized, billed or actual load.",
            "public_power_and_cooling_equipment": EQUIPMENT.get(site_id),
            "osm_map_evidence": mapped.get(site_id, []),
            "gpu_deployment_evidence": gpu_evidence,
            "gpu_inventory": {"exact_model_count_owner_site_allocation_delivery_installation_utilization_power_draw_revenue_and_margin": "undisclosed", "boundary": "DGX-ready certification, liquid-cooling capability and customer deployments do not establish a Flexential-owned GPU fleet."},
            "source_urls": list(dict.fromkeys(sources)),
            "accessed_on": accessed_on,
        })
    return records, related


def build_summary(records: list[dict], related: list[dict], accessed_on: str) -> dict:
    mapped_labels = {site_id for site_id in OSM_OBJECT_TO_SITE.values()}
    current_ids = {row["site_id"] for row in records}
    development = [row for row in records if row["lifecycle_as_of_2026_07_19"] != OPERATIONAL and not row["lifecycle_as_of_2026_07_19"].startswith("commissioned")]
    return {
        "schema_version": 1,
        "registry": "Flexential current official facility-card registry",
        "accessed_on": accessed_on,
        "official_directory_cards": len(records),
        "directory_market_headline": 18,
        "visible_market_filter_labels": 19,
        "visible_market_filter_without_current_card": ["Allentown, PA"],
        "topline_data_center_headline": "40+",
        "topline_area_headline_sq_ft": "3M+",
        "directory_card_area_sum_sq_ft_lower_bound_mixed_lifecycle": sum(row["directory_area_sq_ft"] for row in records),
        "directory_card_critical_power_sum_mw_mixed_lifecycle": round(sum(row["directory_critical_power_mw"] for row in records), 2),
        "current_company_capacity_headline_mw_online_or_under_development_lower_bound": 360,
        "scope_conflict_boundary": "The 41 rendered cards, 40+ headline, 18-market headline, 19 visible filters, 3M+ top-line area, 4.985407M card checksum, more-than-360-MW company headline and 372.17-MW card checksum use incompatible granularity or lifecycle scopes and are not silently reconciled.",
        "lifecycle_counts": {"current_cards_without_reviewed_development_language": sum(row["lifecycle_as_of_2026_07_19"] == OPERATIONAL for row in records), "commissioned_and_fully_leased": sum(row["lifecycle_as_of_2026_07_19"].startswith("commissioned") for row in records), "under_construction_or_planned": len(development)},
        "development_card_labels": [row["provider_label"] for row in development],
        "osm_flexential_related_objects": len(related),
        "osm_objects_with_operator_label_flexential": sum(row.get("operator") == "Flexential" for row in related),
        "crosswalked_osm_objects": len(OSM_OBJECT_TO_SITE),
        "crosswalked_current_provider_labels": len(mapped_labels),
        "current_provider_labels_without_osm_crosswalk": sorted(current_ids - mapped_labels),
        "legacy_or_unresolved_osm_objects": LEGACY_OR_UNRESOLVED_OSM,
        "osm_boundary": "OSM points and footprints are public map evidence. Duplicate footprints, legacy labels and provider cards that cover multiple buildings prevent an object/card/building count equivalence.",
        "site_specific_power_or_cooling_evidence_cards": sum(row["public_power_and_cooling_equipment"] is not None for row in records),
        "fleet_power_and_cooling": {
            "published_density_claims": ["80+ kW per cabinet on directory", "up to 150+ kW per cabinet on high-density or selected facility pages", "50 kW air and 80+ kW liquid or immersion in liquid-cooling guide"],
            "liquid_cooling": ["direct-to-chip", "rear-door heat exchanger", "CDU", "immersion", "facility chilled-water loop"],
            "power_note": "Direct-to-chip pumps may use a dedicated UPS or critical IT UPS.",
            "equipment_boundary": "Individual pages disclose selected UPS/cooling topology and density, but no complete fleet or per-site OEM/model/count/rating bill of materials is public.",
        },
        "sustainability": {"renewable_energy_consumed_across_operating_footprint_gwh_2025": 402, "new_facility_design_PUE": 1.4, "new_facility_design_WUE": 0, "capacity_supported_by_closed_loop_cooling_percent": 84, "air_handling_retrofits_sites": 14, "projected_annual_savings_gwh": 7.1},
        "gpu_and_AI": {
            "DGX_ready": "certification_and_capacity_not_GPU_ownership_or_count",
            "DigitalOcean": "Douglasville 1, H200 and AMD Instinct, exact counts undisclosed",
            "Applied_Digital": "7.5 MW across three undisclosed markets, NVIDIA H100, exact sites and counts undisclosed",
            "CoreWeave": "operator-hosted media says 13 MW Plano and prior Oregon/Georgia rollouts; exact counts and full site/model allocation undisclosed",
            "exact_installed_GPU_fleet_count": "undisclosed",
            "sources": [DGX_URL, DIGITALOCEAN_RELEASE, APPLIED_DIGITAL_RELEASE, COREWEAVE_MEDIA],
        },
        "financial_profile_ref": "company_flexential",
        "portfolio_profile_ref": "dc_flexential_us_portfolio",
        "source_urls": [DIRECTORY_URL, NORCROSS2_RELEASE, HILLSBORO_PROPERTY_RELEASE, HILLSBORO6_RELEASE, PARKER_RELEASE, ESG_RELEASE, DGX_URL, DIGITALOCEAN_RELEASE, DIGITALOCEAN_CASE, APPLIED_DIGITAL_RELEASE, COREWEAVE_MEDIA, LIQUID_COOLING_GUIDE],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    assert len(FACILITIES) == 41
    assert sum(row["directory_area_sq_ft"] for row in FACILITIES) == 4_985_407
    assert round(sum(row["directory_critical_power_mw"] for row in FACILITIES), 2) == 372.17
    records, related = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, related, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "flexential_official_facility_registry.jsonl"
    summary_path = args.output_dir / "flexential_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
