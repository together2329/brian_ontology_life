#!/usr/bin/env python3
"""Build NEXTDC's current official facility-label registry.

The registry keeps provider facility labels, mapped OSM objects, marketed or
planned IT-capacity cards, fitted-out capacity, contracted capacity, billing
capacity and actual load as different measures.  It also preserves public
equipment details without treating DGX certification or cooling capability as
evidence of an installed GPU fleet.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


ROSTER_URL = "https://www.nextdc.com/solutions/mission-critical-spaces"
RESULTS_URL = "https://www.nextdc.com/hubfs/ASX%20Announcements/1H26%20Results%20Presentation.pdf"
APRIL_URL = "https://www.nextdc.com/news/record-contracted-growth-and-a2.2bn-capital-plan-to-scale-ai-ready-infrastructure"
MAY_URL = "https://www.nextdc.com/news/nextdc-bolsters-liquidity-to-a8.4-billion-to-accelerate-ai-infrastructure-rollout"
KL1_LAUNCH_URL = "https://www.nextdc.com/news/nextdc-goes-live-with-kl1-kuala-lumpur-launching-strategic-ai-ready-data-centre-in-southeast-asia"
DGX_URL = "https://www.nextdc.com/news/nextdc-secures-certification-in-the-nvidia-dgx-ready-data-center-program"
AI_PLAYBOOK_URL = "https://nextdc.com/hubfs/NEXTDC-AI-Playbook.pdf"


def site(
    site_id: str,
    market: str,
    locality: str,
    country_code: str,
    technical_space_m2: float | None,
    card_power_mw: float | None,
    power_qualifier: str,
    lifecycle: str,
    page_url: str,
    **extra: object,
) -> dict:
    return {
        "site_id": site_id,
        "market": market,
        "locality": locality,
        "country_code": country_code,
        "technical_space_m2": technical_space_m2,
        "portfolio_card_power_mw": card_power_mw,
        "portfolio_card_power_qualifier": power_qualifier,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "facility_page_url": page_url,
        **extra,
    }


FACILITIES = [
    site("S1", "Sydney", "Macquarie Park", "AU", 5800, 16, "published_value", "operational", "https://www.nextdc.com/data-centres/sydney-data-centres/s1-sydney"),
    site("S2", "Sydney", "Macquarie Park", "AU", 8700, 30, "published_value", "operational", "https://www.nextdc.com/data-centres/sydney-data-centres/s2-sydney"),
    site("S3", "Sydney", "Artarmon", "AU", 20000, 80, "published_value", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/sydney-data-centres/s3-sydney", dated_1h26_built_mw=60, dated_1h26_in_progress_mw=20),
    site("S4", "Sydney", "Horsley Park", "AU", 124000, 350, "published_value", "development_approval_obtained_and_construction_in_progress", "https://www.nextdc.com/data-centres/sydney-data-centres/s4-sydney", dated_2026_05_in_progress_mw_approximate=250),
    site("S5", "Sydney", "Macquarie Park", "AU", 16000, 80, "published_value", "design_and_town_planning", "https://www.nextdc.com/data-centres/sydney-data-centres/s5-sydney", dated_1h26_initial_capacity_mw_approximate=20),
    site("S6", "Sydney", "Artarmon", "AU", 4000, 13.5, "published_target_it_capacity", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/sydney-data-centres/s6-sydney", dated_1h26_built_mw=2.7, dated_1h26_in_progress_mw=10.8),
    site("S7", "Sydney", "Eastern Creek", "AU", None, 550, "published_lower_bound", "design_and_town_planning", "https://www.nextdc.com/data-centres/sydney-data-centres-colocation"),
    site("M1", "Melbourne", "Port Melbourne", "AU", 6000, 16, "published_value", "operational", "https://www.nextdc.com/data-centres/melbourne-data-centres/m1-melbourne"),
    site("M2", "Melbourne", "Tullamarine", "AU", 15000, 120, "published_value", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/melbourne-data-centres/m2-melbourne", dated_1h26_built_mw=51, dated_1h26_in_progress_mw=30),
    site("M3", "Melbourne", "West Footscray", "AU", 41000, 225, "published_value", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/melbourne-data-centres/m3-melbourne", dated_1h26_built_mw=40, dated_1h26_in_progress_mw=185),
    site("GE1", "Geelong", "Geelong", "AU", 2100, 4.4, "published_value", "under_development_target_practical_completion_2H_FY27", "https://www.nextdc.com/data-centres/geelong-data-centres/ge1-geelong", dated_1h26_initial_capacity_mw_approximate=1),
    site("M4", "Melbourne", "Port Melbourne", "AU", 26400, 150, "published_value", "development_approval_obtained", "https://www.nextdc.com/data-centres/melbourne-data-centres/m4-melbourne", dated_1h26_phase_1_initial_capacity_mw_approximate=10),
    site("B1", "Brisbane", "Brisbane CBD", "AU", 1650, 2.25, "published_value", "operational", "https://www.nextdc.com/data-centres/brisbane-data-centres/b1-brisbane"),
    site("B2", "Brisbane", "Fortitude Valley", "AU", 6000, 12, "published_value", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/brisbane-data-centres/b2-brisbane", dated_1h26_built_mw=6, dated_1h26_in_progress_mw=2),
    site("GC1", "Gold Coast", "Gold Coast", "AU", 4600, 6, "published_value", "design_and_town_planning", "https://www.nextdc.com/data-centres/gold-coast-data-centres/gc1-gold-coast", dated_1h26_initial_capacity_mw_approximate=1),
    site("P1", "Perth", "Malaga", "AU", 3000, 10, "published_lower_bound", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/perth-data-centres/p1-perth", dated_1h26_built_mw=5.5, dated_1h26_in_progress_mw=2),
    site("P2", "Perth", "Perth CBD", "AU", 12000, 20, "published_lower_bound", "operational_with_fitout_in_progress", "https://www.nextdc.com/data-centres/perth-data-centres/p2-perth", dated_1h26_built_mw=6, dated_1h26_in_progress_mw=4),
    site("PH1", "Port Hedland", "Pilbara", "AU", 727, 1, "published_value", "operational", "https://www.nextdc.com/data-centres/port-hedland-data-centre-colocation", official_address="17 Loreto Circuit, Port Hedland, WA 6721"),
    site("A1", "Adelaide", "Central CBD", "AU", 2922, 5, "published_value", "operational", "https://www.nextdc.com/data-centres/adelaide-data-centre/a1-adelaide"),
    site("C1", "Canberra", "Bruce", "AU", 2260, 4.4, "published_value", "operational", "https://www.nextdc.com/data-centres/canberra-data-centres/c1-canberra"),
    site("D1", "Darwin", "Darwin CBD", "AU", 3000, 1, "published_value", "operational", "https://www.nextdc.com/data-centres/darwin-data-centres/d1-darwin"),
    site("D2", "Darwin", "Darwin CBD", "AU", None, 6, "published_value", "under_development_target_practical_completion_1H_FY27", "https://www.nextdc.com/data-centres/darwin-data-centres-colocation", dated_1h26_initial_capacity_mw_approximate=1.5),
    site("SC1", "Sunshine Coast", "Maroochydore", "AU", 290, 1, "published_value", "operational", "https://www.nextdc.com/data-centres/sunshine-coast-data-centres/sc1-sunshine-coast"),
    site("SC2", "Sunshine Coast", "Sunshine Coast", "AU", None, 6, "published_value", "under_development_target_practical_completion_2H_FY27", "https://www.nextdc.com/data-centres/sunshine-coast-data-centres-colocation", dated_1h26_initial_capacity_mw_approximate=1),
    site("NE1", "Newman", "Pilbara", "AU", 560, 1, "published_value", "operational", "https://www.nextdc.com/data-centres/newman-data-centre-colocation", official_address="Cnr Pardoo St and Woodstock St, Newman, WA 6753"),
    site("TK1", "Tokyo", "Tokyo", "JP", None, 30, "published_value", "in_planning_target_practical_completion_FY30", "https://www.nextdc.com/data-centres/japan-data-centres-colocation"),
    site("TK2", "Tokyo", "Tokyo", "JP", None, None, "undisclosed", "published_current_card_lifecycle_not_disclosed_in_reviewed_sources", "https://www.nextdc.com/data-centres/japan-data-centres-colocation"),
    site("KL1", "Kuala Lumpur", "Petaling Jaya", "MY", 18250, 65, "published_design_it_capacity", "operational_launched_2026_05_14_with_full_65MW_buildout_not_proven_live", "https://www.nextdc.com/data-centres/malaysia-data-centres-colocation", official_address="1, Jln 51a/229, Seksyen 51a, Petaling Jaya, 46100 Selangor", dated_1h26_initial_capacity_in_progress_mw_lower_bound=15),
    site("AK1", "Auckland", "Auckland", "NZ", 3000, 15, "published_value", "design_and_town_planning", "https://www.nextdc.com/data-centres/new-zealand-data-centres-colocation", dated_1h26_initial_capacity_mw_approximate=1.7),
]


EQUIPMENT = {
    "S1": {"power": ["N+1 supply and N+N rack delivery", "670kVA Piller diesel rotary UPS units on isolated parallel bus", "24-hour onsite fuel"], "cooling": ["N+1 high-efficiency water-cooled chillers", "dual primary pipework", "N+2 CRAC units per hall", "cold-aisle containment"]},
    "S2": {"power": ["isolated parallel bus", "1.5MW Piller rotary UPS with MTU engines", "24-hour fuel", "whole-site UPS including mechanical cooling"], "cooling": ["Stulz indirect free-cooling CRACs and modular cooling towers", "N+1 independent cooling", "24-hour water", "published PUE 1.29 annual average and 1.15 annual low"]},
    "S3": {"power": ["2.7MW Piller rotary UPS with MTU engines", "isolated parallel bus", "24-hour fuel", "whole-site UPS including mechanical cooling"], "cooling": ["Vertiv indirect free-cooling CRACs and modular cooling towers", "N+1 independent cooling", "24-hour water", "PUE targets 1.20 annual average and 1.15 annual low"]},
    "S6": {"power": ["site marketed for up to 600kW per rack in AI playbook"], "cooling": ["customer-specific direct-to-chip, rear-door heat exchanger and immersion-cooling designs"], "boundary": "Design capability is not installed rack draw or a complete as-built equipment bill of materials."},
    "M1": {"power": ["isolated parallel bus", "N+1 supply and N+N rack delivery", "1.336MW Piller DRUPS with MTU engines", "minimum 12-hour fuel"], "cooling": ["N+1 water-cooled chillers, cooling towers and pumps", "dual primary pipework", "secure CRAC corridors", "mixed hot- and cold-aisle containment"]},
    "M2": {"power": ["isolated parallel bus", "N+1 supply and N+N rack delivery", "1.5MW Piller rotary UPS with MTU engines", "12-hour fuel", "whole-site UPS including mechanical cooling"], "cooling": ["Vertiv evaporative free-cooling units", "N+1 independent cooling", "24-hour water", "published PUE 1.28 annual average and 1.10 annual low"]},
    "M3": {"power": ["redundant 2.7MW Piller UPS with MTU engines", "24-hour fuel", "whole-site UPS including mechanical cooling"], "cooling": ["Stulz fan walls with indirect/direct economy-cycle free cooling", "magnetic-bearing high-efficiency chillers", "N+1 independent cooling", "24-hour water", "PUE targets 1.29 annual average and 1.15 winter"]},
    "B1": {"power": ["N+N rack delivery", "1MW Schneider UPS units with 20-minute battery autonomy", "1.6MW prime-rated generators"], "cooling": ["N+1 air-cooled UNIFLAIR chillers", "dual chilled-water risers and buffer tank", "N+1 CRAC units", "published approximate 1,400W/m2 server heat load"]},
    "B2": {"power": ["isolated parallel bus and N+N rack delivery", "1.5MW Piller rotary UPS with Penske engines", "24-hour fuel"], "cooling": ["Stulz indirect free-cooling CRACs and modular cooling towers", "N+1 independent cooling", "24-hour water", "published PUE 1.34 annual average and 1.25 annual low"]},
    "P1": {"power": ["isolated parallel bus and N+N rack delivery", "6+1 1670kVA diesel rotary UPS", "N+1 supply", "24-hour fuel"], "cooling": ["N+1 high-efficiency chillers and pumps", "dual chilled-water risers and dual-path pipework", "N+2 CRAC units per hall", "published approximate 2,000W/m2 server heat load"]},
    "P2": {"power": ["isolated parallel bus and N+N rack delivery", "1.5MW Piller rotary UPS with Penske engines", "24-hour fuel"], "cooling": ["Stulz indirect free-cooling and DX CRACs", "N+1 cooling circuits and N+2 CRAC units per hall", "24-hour design water storage", "published 4,000W/m2 peak design heat load"]},
    "PH1": {"power": ["N+1 main electrical infrastructure and N+N power rail", "two 400kVA MTU backup diesel generators", "minimum 18-hour fuel"], "cooling": ["cold-aisle containment", "N+1 condenser and in-row cooling with UPS redundancy", "leak detection"]},
    "A1": {"power": ["distributed-redundant N+1 2MW static battery UPS", "MTU generator engines", "48-hour fuel", "whole-site UPS including mechanical systems"], "cooling": ["direct and indirect free-air economisation", "Vertiv indirect free-cooling CRACs and modular cooling towers", "N+1 independent cooling and N+2 CRACs per hall", "PUE targets 1.25 annual average and 1.15-1.20 annual low"]},
    "C1": {"power": ["two independent onsite substations", "N+1 RUPS and main electrical infrastructure", "N+N final rack circuits", "minimum 24-hour fuel"], "cooling": ["N+1 water-cooled chillers, cooling towers and pumps", "water buffer tank", "N+2 CRAC units per hall", "published approximate 2,000W/m2 server heat load"]},
    "SC1": {"power": ["N+1 main electrical infrastructure and N+N power rail", "two FG Wilson backup diesel generators with space for a third", "minimum 18-hour fuel"], "cooling": ["cold-aisle containment", "N+1 roof condenser and in-row cooling with UPS redundancy", "leak detection"]},
    "NE1": {"power": ["N+1 main electrical infrastructure and N+N power rail", "two 400kVA MTU backup diesel generators", "minimum 18-hour fuel"], "cooling": ["cold-aisle containment", "N+1 condenser and in-row cooling with UPS redundancy", "leak detection"]},
}


SAME_PAGE_SCOPE_CONFLICTS = {
    "A1": ["portfolio card and page narrative say 5MW; current page stat says 6MW"],
    "D1": ["portfolio card says 1MW and page stat says 1MW+; page narrative describes a 7+MW facility"],
    "PH1": ["portfolio card and page IT-capacity stat say 1MW; page narrative describes 1.5MW"],
    "NE1": ["portfolio card and page IT-capacity stat say 1MW; page narrative describes 1.5MW"],
    "P1": ["portfolio card says 10+MW; detailed power specification says approximately 6MW IT load"],
}


OSM_OBJECT_TO_SITE = {
    "osm_way_77626243": "C1",
    "osm_way_394251157": "S1",
    "osm_way_750706229": "S2",
    "osm_way_1225879499": "S3",
    "osm_way_889434872": "S6",
    "osm_way_1307941180": "D1",
    "osm_way_1303950840": "M3",
    "osm_way_117986093": "A1",
    "osm_way_333179191": "M1",
    "osm_way_812825291": "P2",
    "osm_way_908492330": "SC1",
    "osm_way_1026603690": "KL1",
    "osm_way_881960579": "KL1",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id = {}
    nextdc_rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        haystack = " ".join(str(row.get(k, "")) for k in ("name", "operator", "website")).lower().replace(" ", "")
        if "nextdc" in haystack:
            nextdc_rows.append(row)
    return by_id, nextdc_rows


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, nextdc_osm = load_osm(osm_path)
    missing = sorted(set(OSM_OBJECT_TO_SITE) - set(osm))
    assert not missing, missing
    site_osm: dict[str, list[dict]] = {}
    for object_id, site_id in OSM_OBJECT_TO_SITE.items():
        source = osm[object_id]
        site_osm.setdefault(site_id, []).append({
            "osm_object_id": object_id,
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "source_url": source["source_url"],
            "boundary": "Public map object or footprint, not provider-certified building count, address, ownership or lifecycle.",
        })
    records = []
    for position, source in enumerate(FACILITIES, start=1):
        record = {
            "id": f"nextdc_{source['site_id'].lower()}",
            "object_type": "ProviderPublishedDataCenterFacilityLabel",
            "source_order": position,
            "operator": "NEXTDC",
            **source,
            "record_granularity": "provider_facility_label_not_proven_one_to_one_physical_building",
            "power_measure_boundary": "Portfolio-card MW is marketed IT capacity or planned power depending on lifecycle; it is not automatically built, energized, leased, utilized, billing or actual load.",
            "public_power_and_cooling_equipment": EQUIPMENT.get(source["site_id"]),
            "same_page_or_same_roster_scope_conflicts": SAME_PAGE_SCOPE_CONFLICTS.get(source["site_id"], []),
            "osm_map_evidence": site_osm.get(source["site_id"], []),
            "gpu_inventory": {
                "installed_model_count_owner_site_allocation_utilization_power_draw_revenue_and_margin": "undisclosed",
                "boundary": "NVIDIA DGX-Ready certification, AI-ready marketing, supported A100/H100/GB200 platforms and liquid-cooling density are hosting capabilities, not proof of physical GPU installation or NEXTDC ownership.",
            },
            "source_urls": list(dict.fromkeys([ROSTER_URL, source["facility_page_url"], RESULTS_URL, DGX_URL])),
            "accessed_on": accessed_on,
        }
        if source["site_id"] == "S4":
            record["source_urls"].extend([APRIL_URL, MAY_URL])
        if source["site_id"] == "KL1":
            record["source_urls"].append(KL1_LAUNCH_URL)
        if source["site_id"] == "S6":
            record["source_urls"].append(AI_PLAYBOOK_URL)
        records.append(record)
    return records, nextdc_osm


def build_summary(records: list[dict], nextdc_osm: list[dict], accessed_on: str) -> dict:
    lifecycle = Counter()
    for row in records:
        state = row["lifecycle_as_of_2026_07_19"]
        lifecycle["operational"] += int(state.startswith("operational"))
        lifecycle["development_or_planning"] += int(any(term in state for term in ("development", "planning", "in_planning")))
        lifecycle["published_card_lifecycle_undisclosed"] += int("lifecycle_not_disclosed" in state)
    disclosed_power = [row for row in records if row["portfolio_card_power_mw"] is not None]
    operational_power = [row for row in disclosed_power if row["lifecycle_as_of_2026_07_19"].startswith("operational")]
    mapped_ids = set(OSM_OBJECT_TO_SITE)
    unresolved = [row["id"] for row in nextdc_osm if row["id"] not in mapped_ids]
    return {
        "registry": "NEXTDC current official facility-label registry",
        "accessed_on": accessed_on,
        "official_facility_labels": len(records),
        "country_counts": dict(sorted(Counter(row["country_code"] for row in records).items())),
        "lifecycle_counts": dict(lifecycle),
        "technical_space_disclosed_labels": sum(row["technical_space_m2"] is not None for row in records),
        "portfolio_card_power_disclosed_labels": len(disclosed_power),
        "portfolio_card_power_lower_bound_mw_mixed_lifecycle": round(sum(row["portfolio_card_power_mw"] for row in disclosed_power), 3),
        "operational_label_card_power_lower_bound_mw_not_live_load": round(sum(row["portfolio_card_power_mw"] for row in operational_power), 3),
        "dated_1h26_portfolio_total_it_power_mw": 1814.6,
        "dated_1h26_built_capacity_mw": 240.9,
        "dated_1h26_in_progress_mw": 272.9,
        "dated_1h26_contracted_utilisation_mw": 416.6,
        "dated_1h26_billing_utilisation_mw": 119.8,
        "dated_1h26_forward_order_book_mw": 296.8,
        "dated_2026_04_pro_forma_contracted_utilisation_mw": 667,
        "dated_2026_04_forward_order_book_mw": 544,
        "power_comparison_boundary": "Current card totals mix operating, fit-out, approved, planning and unknown lifecycle. The 1H26 portfolio measures have different dates and denominators and are not added to card totals.",
        "site_specific_power_or_cooling_disclosure_labels": sum(row["public_power_and_cooling_equipment"] is not None for row in records),
        "labels_with_published_scope_conflicts": [row["site_id"] for row in records if row["same_page_or_same_roster_scope_conflicts"]],
        "labels_with_exact_installed_gpu_inventory": 0,
        "osm_nextdc_related_objects": len(nextdc_osm),
        "osm_crosswalked_objects": len(mapped_ids),
        "osm_crosswalked_provider_labels": len(set(OSM_OBJECT_TO_SITE.values())),
        "unresolved_nextdc_related_osm_objects": unresolved,
        "osm_boundary": "OSM objects may be points or building footprints and can be multiple objects for one provider label; provider labels may also be campuses or planned sites.",
        "financial_profile_ref": "company_nextdc",
        "portfolio_profile_ref": "dc_nextdc_apac_portfolio",
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records, nextdc_osm = build_records(args.osm, args.accessed_on)
    assert len(records) == 29
    assert len({row["site_id"] for row in records}) == 29
    summary = build_summary(records, nextdc_osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "nextdc_official_facility_registry.jsonl"
    summary_path = args.output_dir / "nextdc_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
