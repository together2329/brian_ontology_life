#!/usr/bin/env python3
"""Classify GasLINE-tagged OSM objects without inventing data centers.

The global OSM baseline contains eight tiny buildings tagged as data centers.
Their enclosing OSM sites are named GasLINE amplifier locations, while GasLINE's
official business description is a dark-fibre network that connects third-party
data centers.  This registry preserves the map tags but does not promote the
objects into a physical data-center, MW, GPU or financial operator profile.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


GASLINE_HOME = "https://www.gasline.de/"
DARK_FIBRE = "https://www.gasline.de/dark-fibre/"
SUSTAINABILITY_2024 = "https://www.gasline.de/wp-content/uploads/Nachhaltigkeitsbericht_Zusammenfassung.pdf"
DERNBACH_1_ENCLOSURE = "https://www.openstreetmap.org/way/130064182"
DERNBACH_23_ENCLOSURE = "https://www.openstreetmap.org/way/129919020"


OBJECTS = {
    "osm_way_130064180": ("Dernbach_1", DERNBACH_1_ENCLOSURE),
    "osm_way_130064188": ("Dernbach_1", DERNBACH_1_ENCLOSURE),
    "osm_way_130064190": ("Dernbach_1", DERNBACH_1_ENCLOSURE),
    "osm_way_129919027": ("Dernbach_2_and_3", DERNBACH_23_ENCLOSURE),
    "osm_way_129919031": ("Dernbach_2_and_3", DERNBACH_23_ENCLOSURE),
    "osm_way_129919032": ("Dernbach_2_and_3", DERNBACH_23_ENCLOSURE),
    "osm_way_129919033": ("Dernbach_2_and_3", DERNBACH_23_ENCLOSURE),
    "osm_way_129919034": ("Dernbach_2_and_3", DERNBACH_23_ENCLOSURE),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    rows = []
    for order, (osm_ref, (site_group, enclosure_url)) in enumerate(OBJECTS.items(), 1):
        source = osm[osm_ref]
        rows.append({
            "id": f"gasline_classification_{osm_ref}",
            "object_type": "OSMDataCenterClassificationEvidence",
            "source_order": order,
            "osm_ref": osm_ref,
            "osm_url": source["source_url"],
            "raw_name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_tags": source.get("tags", {}),
            "site_group": site_group,
            "enclosing_site_url": enclosure_url,
            "enclosing_site_classification": "GasLINE Verstärkerstandort (telecommunications amplifier site)",
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "reviewed_classification": "telecommunications_amplifier_site_component_not_established_as_physical_data_center",
            "physical_data_center_count_contribution": 0,
            "power_capacity_contribution_mw": 0,
            "GPU_or_accelerator_inventory": "not_applicable_and_not_disclosed",
            "classification_boundary": "The raw building=data_center and telecom=data_center tags remain preserved. The named enclosing amplifier site and official dark-fibre business description are stronger classification evidence, so the object is excluded from physical data-center totals unless primary operator evidence later proves a server or colocation function.",
            "accessed_on": accessed_on,
        })
    assert len(rows) == 8
    assert len({row["id"] for row in rows}) == 8
    assert Counter(row["site_group"] for row in rows) == {"Dernbach_2_and_3": 5, "Dernbach_1": 3}
    assert round(sum(row["footprint_area_m2"] for row in rows), 3) == 484.899
    return rows


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    by_site = {}
    for site in sorted({row["site_group"] for row in records}):
        selected = [row for row in records if row["site_group"] == site]
        by_site[site] = {
            "component_building_footprints": len(selected),
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] for row in selected), 3),
            "enclosing_site_url": selected[0]["enclosing_site_url"],
            "classification": selected[0]["enclosing_site_classification"],
        }
    return {
        "id": "gasline_osm_classification_summary_2026_07_19",
        "operator_label": "GasLINE",
        "accessed_on": accessed_on,
        "reviewed_company_boundary": {
            "legal_name": "GasLINE Telekommunikationsnetzgesellschaft deutscher Gasversorgungsunternehmen mbH & Co. KG",
            "official_business": "wireline telecommunications and dark-fibre infrastructure",
            "NACE": "61.10_wireline_telecommunications",
            "official_fibre_route_km": 65000,
            "additional_route_km_under_expansion_to_2029": 5000,
            "official_data_centers_reachable_more_than": 350,
            "ownership_boundary": "Reachable or connected third-party data centers are not GasLINE-owned or operated data centers.",
        },
        "OSM_reconciliation": {
            "raw_GasLINE_tagged_buildings": len(records),
            "named_enclosing_amplifier_site_groups": 2,
            "named_amplifier_labels_within_groups": ["Dernbach 1", "Dernbach 2", "Dernbach 3"],
            "component_footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] for row in records), 3),
            "by_site": by_site,
            "classification": "telecommunications_amplifier_site_components_not_established_as_physical_data_centers",
            "physical_data_center_count_contribution": 0,
            "power_capacity_contribution_mw": 0,
            "boundary": "Eight component footprints are not eight facilities. The classification can be reopened if GasLINE or another primary source publishes a server-room, colocation or IT-load role for the Dernbach sites.",
        },
        "power_cooling_GPU_and_financial_boundary": {
            "site_input_power_UPS_generation_cooling_and_IT_load": "not_disclosed_or_established_as_data_center_infrastructure",
            "GPU_inventory": "not_applicable_and_not_disclosed",
            "third_party_5MW_per_object_claims": "not_adopted_without_primary_source_or_defined_denominator",
            "company_revenue_and_operating_profit": "not_added_to_the_physical_operator_financial_ledger_because_the_reviewed_objects_are_network_amplifier_sites_and_GasLINE_is_private",
        },
        "sources": [GASLINE_HOME, DARK_FIBRE, SUSTAINABILITY_2024, DERNBACH_1_ENCLOSURE, DERNBACH_23_ENCLOSURE],
        "source_file": str(osm_path),
        "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(load_osm(args.osm), args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "gasline_osm_classification_registry.jsonl"
    summary_path = args.output_dir / "gasline_osm_classification_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
