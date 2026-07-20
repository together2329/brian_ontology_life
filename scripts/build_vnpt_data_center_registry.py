#!/usr/bin/env python3
"""Build a scope-preserving VNPT data-center registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


VNPT_2025_PRESENTATION_URL = "https://vnpt.com.vn/file/808080809b97b1bb019b9b3d370b02a9/upload/xdata/202602/20260225103734vnpt_presentation_update_112025_eng.pdf"
VNPT_HOA_LAC_URL = "https://danang.vnpt.com.vn/tin-tuc-su-kien/hoat-dong-vnpt/202311/khai-truong-trung-tam-du-lieu-vnpt-idc-hoa-lac-lon-nhat-hien-ai-nhat-viet-nam-f62011d/"
VNPT_CLOUD_2024_URL = "https://vnpt.com.vn/gioi-thieu/tin-tuc/he-sinh-thai-vnpt-cloud-huong-toi-tuong-lai-ket-noi-toan-dien.html"
VNPT_2025_RESULTS_URL = "https://vnpt.com.vn/tin-tuc/thong-tin-bao-chi-pr/202512/vnpt-hoan-thanh-toan-dien-ke-hoach-giai-doan-20212025-tao-da-but-pha-voi-nhieu-dau-an-noi-bat-trong-nam-2025-bb23e59/"
VNPT_2025_FINANCIAL_URL = "https://vnpt.com.vn/file/808080809b97b1bb019b9b3d370b02a9/upload/xdata/202605/20260529144839bctc_hop_nhat_31.12.25.pdf"
VNPT_2026_PLAN_URL = "https://vnpt.com.vn/file/808080809b97b1bb019b9b3d370b02a9/upload/xdata/202604/20260423110355bieu_2_bc_muc_tieu_tong_quat_khkd_2026.pdf"
VNPT_ABOUT_URL = "https://vnpt.com.vn/ve-vnpt/"


OSM_CROSSWALK = {
    "osm_way_1175244806": ("TAN_THUAN", "current_provider_named_site_and_2026_expansion_project_name_locality_match"),
    "osm_node_13813612110": (None, "Cau_Giay_OSM_point_not_reconciled_to_a_complete_current_eight_site_provider_roster"),
    "osm_way_1511262966": ("HOA_LAC", "exact_current_operating_site_name_and_locality_match"),
    "osm_way_1511262965": ("NAM_THANG_LONG", "current_provider_named_site_and_2026_expansion_project_name_locality_match"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] in OSM_CROSSWALK:
            rows[row["id"]] = row
    assert set(rows) == set(OSM_CROSSWALK)
    return rows


def build_records(osm_rows: dict[str, dict], accessed_on: str) -> list[dict]:
    records = [
        {
            "id": "vnpt_current_portfolio_scale_2025",
            "object_type": "CurrentPortfolioOperatingScaleDisclosure",
            "operator": "Vietnam_Posts_and_Telecommunications_Group_VNPT",
            "country": "Vietnam",
            "as_of": "2025",
            "large_scale_data_centers": 8,
            "total_operating_capacity_racks_approx": 11_000,
            "geographic_wording": {"area_count": 4, "named_cities": ["Ha_Noi", "Ho_Chi_Minh_City", "Da_Nang"]},
            "certification_wording": "eight_large_scale_data_centers_achieved_Uptime_Tier_III_certification",
            "boundary": "The presentation says four areas but names only three cities. Eight centers and approximately 11,000 operating-capacity racks do not disclose the complete site roster, building count, installed or occupied racks, IT MW, live load or utilization.",
            "source_url": VNPT_2025_PRESENTATION_URL,
            "accessed_on": accessed_on,
        },
        {
            "id": "vnpt_dated_portfolio_scale_2024",
            "object_type": "DatedPortfolioScaleDisclosure",
            "operator": "Vietnam_Posts_and_Telecommunications_Group_VNPT",
            "country": "Vietnam",
            "as_of": "2024",
            "data_centers": 8,
            "total_area_m2_more_than": 58_000,
            "total_racks": 4_700,
            "network_max_Gbps": 100,
            "cloud_service_commitment_percent": 99.99,
            "boundary": "This dated page is retained rather than treated as the same denominator as the later approximately 11,000-rack operating-capacity statement. It does not allocate area, racks, power or utilization by site.",
            "source_url": VNPT_CLOUD_2024_URL,
            "accessed_on": accessed_on,
        },
        {
            "id": "vnpt_provider_site_hoa_lac",
            "object_type": "CurrentProviderNamedOperatingDataCenter",
            "operator": "Vietnam_Posts_and_Telecommunications_Group_VNPT",
            "site_code": "HOA_LAC",
            "provider_site_name": "VNPT IDC Hoa Lac",
            "country": "Vietnam",
            "locality": "Hoa_Lac_High_Tech_Park_Ha_Noi",
            "opened_on": "2023-10-25",
            "provider_fleet_ordinal_at_opening": 8,
            "usable_floor_area_m2_up_to": 23_000,
            "rack_capacity_up_to": 2_000,
            "certification_at_opening": ["Uptime_Tier_III_TCDD", "Uptime_Tier_III_TCCF"],
            "certification_not_yet_current_at_opening": ["Uptime_Tier_III_TCOS_upcoming_as_of_2023_10_25"],
            "redundancy": "N_plus_1",
            "security_layers": 6,
            "connectivity_average_Gbps_per_rack": {"domestic": 2.0, "international": 0.5},
            "named_equipment_suppliers_exact_provider_spelling": ["Cumin", "Hitachi", "Siemens"],
            "OSM_refs": ["osm_way_1511262966"],
            "equipment_boundary": "The provider names supplier brands but not equipment category, model, count, rating, installed state or ownership. The exact spelling Cumin is preserved and not silently corrected or mapped to a specific manufacturer.",
            "capacity_boundary": "Up-to floor area and rack capacity are design or service ceilings, not current installed, occupied, sold, billed or utilized capacity. No utility, facility or IT MW is disclosed.",
            "source_url": VNPT_HOA_LAC_URL,
            "accessed_on": accessed_on,
        },
    ]

    for osm_id, source in osm_rows.items():
        code, classification = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"vnpt_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityLocationEvidence",
            "country": "Vietnam",
            "OSM_ref": osm_id,
            "matched_provider_code": code,
            "match_classification": classification,
            "raw_name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_building_levels": source.get("building_levels"),
            "source_url": source["source_url"],
            "count_boundary": "An OSM point or geometry is location evidence, not proof of the provider's complete current roster, building title, gross or usable floor area, rack or IT load, equipment, GPU inventory or financial contribution.",
            "accessed_on": accessed_on,
        })

    assert len(records) == 7
    assert sum(row["object_type"] == "OSMFacilityLocationEvidence" for row in records) == 4
    assert sum(row.get("matched_provider_code") is not None for row in records if row["object_type"] == "OSMFacilityLocationEvidence") == 3
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    osm = [row for row in records if row["object_type"] == "OSMFacilityLocationEvidence"]
    matched = [row for row in osm if row["matched_provider_code"]]
    footprint_all = round(sum(row["OSM_footprint_area_m2"] or 0 for row in osm), 3)
    footprint_matched = round(sum(row["OSM_footprint_area_m2"] or 0 for row in matched), 3)
    assert footprint_all == 5_924.731
    assert footprint_matched == 5_924.731

    return {
        "id": "vnpt_data_center_summary_2026_07_19",
        "operator_boundary": "Vietnam_Posts_and_Telecommunications_Group_VNPT_100_percent_state_owned_unlisted_group",
        "accessed_on": accessed_on,
        "portfolio_scale": {
            "current_2025_presentation": {"large_scale_data_centers": 8, "operating_capacity_racks_approx": 11_000, "area_count_claim": 4, "named_cities": ["Ha_Noi", "Ho_Chi_Minh_City", "Da_Nang"]},
            "dated_2024_cloud_page": {"data_centers": 8, "area_m2_more_than": 58_000, "racks": 4_700},
            "complete_current_eight_site_name_address_building_ownership_and_lifecycle_roster": "undisclosed_or_unestablished",
            "boundary": "The later approximately 11,000-rack operating-capacity statement is not backcast into the dated 4,700-rack page. The provider says four areas but names only three cities, so no fourth area is invented.",
        },
        "Hoa_Lac": {
            "opened_on": "2023_10_25",
            "fleet_ordinal_at_opening": 8,
            "usable_floor_area_m2_up_to": 23_000,
            "rack_capacity_up_to": 2_000,
            "redundancy": "N_plus_1",
            "security_layers": 6,
            "connectivity_average_Gbps_per_rack": {"domestic": 2.0, "international": 0.5},
            "Uptime_at_opening": {"TCDD": "achieved", "TCCF": "achieved", "TCOS": "upcoming_not_current_evidence"},
            "boundary": "No current installed, occupied, sold, billed or utilized rack figure, utility power, facility power, critical IT load, live load, measured PUE or WUE is disclosed.",
        },
        "power_cooling_and_equipment": {
            "Hoa_Lac_disclosed": {"redundancy": "N_plus_1", "named_supplier_strings": ["Cumin", "Hitachi", "Siemens"], "security_layers": 6},
            "dated_Hoa_Lac_power_project_title": {"wording": "construction_of_two_underground_22KVA_power_lines_at_Hoa_Lac_High_Tech_Park", "total_investment_VND_m_including_VAT": 82_865, "implementation_to_end_2024_VND_m": 62_000, "project_period": "2019_to_2024"},
            "exact_current_per_site_grid_voltage_contract_substation_transformer_switchgear_busway_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_equipment_category_OEM_model_count_rating_loading_test_state_age_and_remaining_life": "undisclosed_or_unestablished",
            "current_measured_site_PUE_WUE_energy_water_emissions_and_live_liquid_cooled_MW": "undisclosed",
            "boundary": "The dated project title's 22KVA wording is preserved without engineering correction. Supplier names and N+1 architecture do not establish an as-built equipment bill, site power or current loading.",
        },
        "AI_GPU_and_cloud": {
            "cloud_evidence": {"2024_OpenStack": True, "network_max_Gbps": 100, "service_commitment_percent": 99.99},
            "partner_page_data_center_category": ["NTT_Data", "Next_DC", "SambaNova"],
            "exact_current_VNPT_customer_or_partner_physical_GPU_accelerator_model_count_owner_site_delivery_acceptance_server_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "boundary": "Cloud and AI services plus a partner listing do not prove a VNPT-owned or deployed accelerator inventory. No SambaNova, NVIDIA or other accelerator quantity or data-center allocation is inferred.",
        },
        "financial_and_investability": {
            "VNPT_Group_2025_audited_VND": {
                "gross_revenue": 57_947_384_233_282,
                "revenue_deductions": 4_339_610_972,
                "net_revenue": 57_943_044_622_310,
                "gross_profit": 14_946_930_453_580,
                "net_profit_from_business_operations": 5_656_509_181_996,
                "profit_before_tax": 6_568_657_049_305,
                "profit_after_tax": 5_233_493_887_015,
                "profit_after_tax_attributable_to_parent": 5_164_402_197_849,
            },
            "VNPT_Group_2024_restated_VND": {"net_revenue": 56_090_143_847_570, "net_profit_from_business_operations": 6_132_537_042_360, "profit_before_tax": 6_925_491_831_080, "profit_after_tax": 5_318_496_737_880},
            "2025_press_total_revenue_VND_b": 61_246,
            "ownership": "100_percent_Vietnamese_state_owned_unlisted_group",
            "direct_public_equity_security": "none_established",
            "data_center_or_cloud_segment_revenue_operating_profit_EBITDA_cash_flow_capex_assets_debt_customer_concentration_utilization_and_ROIC": "not_separately_disclosed",
            "boundary": "The press total-revenue measure is not substituted for audited net revenue. Consolidated telecom and digital-service results cannot be attributed to data centers, cloud, AI or named sites.",
        },
        "outlook": {
            "2026_consolidated_targets_VND_b": {"revenue": 64_564, "profit_before_tax": 7_255, "profit_after_tax": 5_804},
            "2026_parent_targets_VND_b": {"revenue": 59_810, "profit_before_tax": 7_068, "profit_after_tax": 5_654, "total_investment": 15_773, "digital_services_customer_revenue": 11_054},
            "2026_data_center_projects_total_investment_VND_m_including_VAT": {
                "Nam_Thang_Long_data_center_and_broadband_expansion": 174_652,
                "Tan_Thuan_data_center_and_broadband_expansion": 222_905,
                "Tan_Thuan_IDC_expansion_equipment": 695_921,
            },
            "project_amount_boundary": "The two Tan Thuan entries may overlap or use different project scopes and are not summed. Total-investment values including VAT are not 2026 cash spend, vendor revenue, commissioned capacity or operating returns.",
            "positive_signals": ["eight_large_scale_Tier_III_centers", "approximately_11000_racks_operating_capacity", "Hoa_Lac_2000_rack_ceiling", "2026_Nam_Thang_Long_and_Tan_Thuan_expansion_projects", "2026_group_growth_targets", "cloud_and_AI_strategy"],
            "conversion_tests": ["publish_complete_current_eight_site_roster", "allocate_11000_racks_to_installed_occupied_and_billed_site_capacity", "disclose_utility_and_IT_MW", "identify_GPU_model_count_owner_and_site", "commission_2026_expansions", "disclose_data_center_and_cloud_revenue_profit_cash_flow_and_ROIC", "publish_current_site_PUE_WUE_and_equipment_inventory"],
            "risks": ["state_owned_unlisted_no_direct_security", "capital_intensity", "no_site_power_or_live_load", "no_GPU_inventory", "no_segment_profitability", "mixed_dated_rack_scopes", "supplier_and_project_award_opacity"],
            "analytical_view": "VNPT is evidence of rising Vietnamese rack, electrical, cooling, connectivity and cloud demand, but not a direct listed data-center investment. The investable read-through remains indirect until project awards, vendor revenue and data-center economics are disclosed.",
        },
        "OSM_crosswalk": {
            "operator_labeled_objects": len(osm),
            "provider_reconciled_objects": len(matched),
            "unreconciled_objects": [row["OSM_ref"] for row in osm if not row["matched_provider_code"]],
            "mapped_footprint_area_m2_sum_not_floor_area": footprint_all,
            "provider_reconciled_footprint_area_m2_sum_not_floor_area": footprint_matched,
            "Tan_Thuan_OSM_building_levels": 7,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Three footprint geometries and one point cover four operator-tagged objects. The footprints are not provider floor area, and the seven-level Tan Thuan tag is not a verified current data-hall count.",
        },
        "records": records,
        "sources": [VNPT_2025_PRESENTATION_URL, VNPT_HOA_LAC_URL, VNPT_CLOUD_2024_URL, VNPT_2025_RESULTS_URL, VNPT_2025_FINANCIAL_URL, VNPT_2026_PLAN_URL, VNPT_ABOUT_URL],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()

    osm_rows = load_osm(args.osm)
    records = build_records(osm_rows, args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "vnpt_data_center_registry.jsonl"
    summary_path = args.output_dir / "vnpt_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "OSM_objects": 4,
        "OSM_provider_reconciled": 3,
        "OSM_footprint_sum_m2_not_floor_area": 5_924.731,
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
