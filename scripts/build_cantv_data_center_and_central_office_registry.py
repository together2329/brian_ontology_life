#!/usr/bin/env python3
"""Build a scope-safe CANTV data-center and central-office registry.

Current public-service evidence names Data Center El Hatillo, while seven CANTV
objects in the OSM baseline are named central offices or local telecom buildings.
This builder preserves all eight evidence rows but does not turn a telecom tag,
building footprint or shared operator name into seven additional commercial data
centers.  Facility engineering, GPUs, operating load and company financials keep
their original disclosure boundaries.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


EL_HATILLO_RELEASE = "https://www.ciudadccs.info/publicacion/43407"
EL_HATILLO_REPUBLICATION = "https://www.estamosenlinea.com.ve/2026/04/25/cantv-y-cavecom-e-articulan-acciones-para-impulsar-la-economia-digital-en-venezuela/"
EL_HATILLO_REPUBLICATION_2 = "https://www.laiguana.tv/articulos/1512810-cantv-cavecom-economia-digital/"
FY2023_AUDITED_COPY = "https://es.scribd.com/document/730255998/INFORMACION-FINANCIERA-DE-LA-EMPRESA-CANTV-AUDITADOS-AL-CIERRE-DICIEMBRE-2023-2022"
H1_2024_UNAUDITED_COPY = "https://es.scribd.com/document/756288762/COMPANIA-ANONIMA-NACIONAL-TELEFONOS-DE-VENEZUELA-Cantv-Estados-Financieros-Trimestral-Jun24-vs-Jun23"
Q1_2024_UNAUDITED_COPY = "https://es.scribd.com/document/732100506/INFORMACION-FINANCIERA-DE-LA-EMPRESA-CANTV-CORRESPONDIENTE-AL-1er-TRIMESTRE-MARZO-2024"
PROSPECTUS_2022 = "https://www.ratiocb.com/wp-content/uploads/2022/09/CANTV-Prospecto.pdf"
BVC_MARKET = "https://market.bolsadecaracas.com/es"
OWNERSHIP_TRANSFER_2025 = "https://dplnews.com/venezuela-aprueban-traspaso-de-acciones-clase-b-de-cantv-al-ministerio-para-ciencia-y-tecnologia/"


EL_HATILLO = {
    "id": "cantv_el_hatillo_data_center",
    "object_type": "DataCenterFacilityEvidence",
    "operator": "Compañía Anónima Nacional Teléfonos de Venezuela (CANTV)",
    "facility_label": "Data Center El Hatillo",
    "city_or_municipality": "El Hatillo",
    "state": "Miranda",
    "country": "Venezuela",
    "country_code": "VE",
    "address": "El Hatillo, Miranda; exact street address not established in reviewed current sources",
    "lifecycle": "current_commercial_service_evidence_as_of_2026_04",
    "current_provider_named_data_center_count_inclusion": True,
    "service_evidence": [
        "data_storage",
        "digital_security",
        "business_continuity",
        "high_speed_connectivity",
        "web_hosting",
        "database_hosting",
        "dedicated_servers",
    ],
    "network_context": "supported_by_CANTV_fiber_network",
    "technical_disclosure": {
        "operating_energized_available_contracted_leased_utilized_and_billed_IT_MW": "undisclosed",
        "gross_or_IT_area_racks_and_building_count": "undisclosed",
        "grid_substation_transformer_switchgear_PDU_UPS_battery_generator_and_fuel": "undisclosed",
        "cooling_topology_chiller_CRAH_CRAC_CDU_liquid_cooled_MW_PUE_WUE_and_water": "undisclosed",
        "certifications": "not_established_in_reviewed_current_sources",
    },
    "installed_GPU_inventory": "not_disclosed_or_established",
    "source_urls": [EL_HATILLO_RELEASE, EL_HATILLO_REPUBLICATION, EL_HATILLO_REPUBLICATION_2],
}


OSM_REFS = [
    "osm_way_523833987",
    "osm_way_900502564",
    "osm_way_889177821",
    "osm_way_1348743262",
    "osm_way_1524226648",
    "osm_way_1079323317",
    "osm_way_260351760",
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    records = [{"source_order": 1, **EL_HATILLO, "accessed_on": accessed_on}]
    for position, osm_ref in enumerate(OSM_REFS, start=2):
        source = osm[osm_ref]
        records.append({
            "id": f"cantv_{osm_ref}_central_office_candidate",
            "object_type": "TelecommunicationsCentralOfficeCandidate",
            "operator": "CANTV",
            "facility_label": source.get("name"),
            "country": "Venezuela",
            "country_code": "VE",
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_building_tag": source.get("tags", {}).get("building"),
            "OSM_telecom_tag": source.get("tags", {}).get("telecom"),
            "OSM_ref": osm_ref,
            "OSM_source_url": source.get("source_url"),
            "lifecycle": "current_OSM_public_location_evidence_without_provider_data_center_confirmation",
            "classification": "telecommunications_central_office_or_exchange_unverified_as_current_commercial_data_center",
            "current_provider_named_data_center_count_inclusion": False,
            "installed_GPU_inventory": "not_disclosed_or_established",
            "counting_boundary": "The OSM telecom=data_center tag and building footprint do not establish a provider-marketed data center, IT load, racks, equipment, GPUs or site economics.",
            "source_order": position,
            "accessed_on": accessed_on,
        })
    assert len(records) == 8
    assert sum(bool(row["current_provider_named_data_center_count_inclusion"]) for row in records) == 1
    assert sum(row["object_type"] == "TelecommunicationsCentralOfficeCandidate" for row in records) == 7
    assert all(osm_ref in osm for osm_ref in OSM_REFS)
    assert Counter(osm[osm_ref].get("operator") for osm_ref in OSM_REFS) == {"CANTV": 7}
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    osm_rows = [row for row in records if row["object_type"] == "TelecommunicationsCentralOfficeCandidate"]
    return {
        "id": "cantv_data_center_and_central_office_summary_2026_07_19",
        "operator": "Compañía Anónima Nacional Teléfonos de Venezuela (CANTV)",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "current_provider_named_data_center_records": 1,
            "current_provider_named_data_center_labels": ["Data Center El Hatillo"],
            "OSM_operator_tagged_objects": 7,
            "OSM_objects_confirmed_as_current_commercial_data_centers": 0,
            "OSM_objects_matching_Data_Center_El_Hatillo": 0,
            "registry_rows": len(records),
            "boundary": "El Hatillo is preserved as the only current provider-named service facility established in reviewed sources. Seven separately located OSM buildings are central-office or exchange candidates and are excluded from verified data-center counts unless provider, permit or audited asset evidence later confirms their role.",
        },
        "El_Hatillo_services": {
            "services": EL_HATILLO["service_evidence"],
            "network_context": EL_HATILLO["network_context"],
            "source_boundary": "The current service evidence is a CANTV announcement reproduced by Venezuelan press; no reviewed provider facility directory or technical sheet established a complete national roster.",
        },
        "power_cooling_and_operating_load": {
            "El_Hatillo_site_MW_area_racks_grid_transformers_switchgear_UPS_batteries_generators_fuel_cooling_PUE_WUE_water_and_live_liquid_cooling": "undisclosed",
            "H1_2024_company_investment_language": ["modernization_of_power_plants", "data_center_adaptations"],
            "investment_language_boundary": "Companywide investment descriptions do not identify a site, OEM, model, unit count, rating, delivery, acceptance, loading, redundancy or remaining life.",
        },
        "GPU_and_AI": {
            "CANTV_or_customer_GPU_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_and_margin": "not_disclosed_or_established",
            "boundary": "Hosting, databases and dedicated-server services do not prove an accelerator fleet or GPU service.",
        },
        "ownership_and_listing": {
            "public_market": "Caracas_Stock_Exchange",
            "class_D_ticker": "TDV.D",
            "2022_prospectus_state_class_B_share_percent": 91.02,
            "2022_state_holders": ["CORPOSTEL", "BANDES"],
            "2025_legal_custodian_change": "Class_B_shares_held_through_dissolved_CORPOSTEL_transferred_to_Ministry_for_Science_and_Technology",
            "current_exact_post_transfer_share_class_and_free_float_reconciliation": "not_established",
            "boundary": "The 2025 custodian change is not treated as a change in the 91.02 percent ownership percentage without a current cap table.",
        },
        "financials": {
            "currency_boundary": "Exact Venezuelan-bolivar figures are retained without USD conversion. Nominal growth is not real growth because inflation and exchange-rate regimes make cross-period and cross-company comparison unsafe.",
            "FY2023_audited_consolidated": {
                "source_boundary": "Reviewed through a user-uploaded copy of audited statements dated 2024-04-12; the original issuer or exchange filing was not independently reviewed.",
                "revenue_VES": 7459399503,
                "prior_year_revenue_VES": 1697577481,
                "nominal_revenue_growth_percent_derived": 339.414,
                "fixed_telephony_revenue_VES": 4927579236,
                "internet_revenue_VES": 2531820267,
                "operating_expenses_VES": 7353989813,
                "accounting_operating_profit_VES": 105409690,
                "operating_margin_percent_derived": 1.413,
                "other_income_and_expense_net_VES": -1232788602,
                "net_financial_income_VES": 1673963091,
                "foreign_exchange_gain_VES": 1707290782,
                "pre_tax_result_VES": 546584179,
                "income_tax_VES": 429769492,
                "net_income_VES": 116814687,
                "net_margin_percent_derived": 1.566,
                "total_assets_VES": 53956143325,
                "equity_VES": 19147149521,
                "liabilities_VES": 34808993804,
                "cash_VES": 188936048,
                "operating_cash_flow_VES": 1908934792,
                "operating_cash_flow_margin_percent_derived": 25.591,
                "PPE_acquisitions_VES": 1578930642,
                "intangible_acquisitions_VES": 72862144,
                "investing_acquisition_outflow_VES": 1651792786,
                "free_cash_flow_proxy_VES": 257142006,
                "free_cash_flow_proxy_boundary": "Operating cash flow minus PPE and intangible acquisitions; not provider-reported free cash flow.",
            },
            "H1_2024_unaudited_consolidated": {
                "source_boundary": "Reviewed through a user-uploaded copy; the original issuer or exchange filing was not independently reviewed and total revenue was not visible in the reviewed extract.",
                "revenue_VES": "not_visible_in_reviewed_extract",
                "accounting_operating_profit_VES": 809404949,
                "operating_margin_percent_reported": 14.2,
                "pre_tax_result_VES": 198968837,
                "income_tax_expense_VES": 289759310,
                "net_loss_VES": 90790473,
            },
            "latest_2025_or_2026_revenue_operating_profit_cash_flow_capex_and_debt": "not_found_in_reviewed_sources",
            "data_center_segment_and_site_revenue_operating_profit_cash_flow_capex_customer_concentration_and_ROIC": "undisclosed",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "raw_operator_counts": dict(Counter("CANTV" for _ in osm_rows)),
            "object_refs": [row["OSM_ref"] for row in osm_rows],
            "footprint_area_m2_checksum": round(sum(row.get("OSM_footprint_area_m2") or 0 for row in osm_rows), 3),
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "counting_boundary": "Footprints are OSM geometry evidence, not data-hall area, gross facility area, IT load or a verified facility count.",
        },
        "outlook": {
            "positive_signals": ["current_El_Hatillo_enterprise_hosting_services", "national_fiber_and_GPON_modernization", "H1_2024_accounting_operating_profit", "minority_public_listing"],
            "risk_signals": ["state_control_and_governance", "inflation_and_currency_translation", "2023_thin_operating_margin_and_FX_driven_net_result", "H1_2024_net_loss", "no_current_audited_2024_or_2025_results_reviewed", "no_complete_facility_roster_or_site_MW_equipment_GPU_and_economics", "OSM_central_office_false_positive_risk", "local_market_liquidity_and_convertibility"],
            "analytical_view": "CANTV may benefit from sovereign hosting and fiber modernization, but it is a state-controlled diversified telecom rather than a disclosed data-center pure play. The 2023 result was supported by foreign-exchange gains and current underwriting is blocked by stale audited accounts, nominal-currency comparability, an incomplete facility roster and absent site-level engineering and economics.",
        },
        "sources": [EL_HATILLO_RELEASE, EL_HATILLO_REPUBLICATION, EL_HATILLO_REPUBLICATION_2, FY2023_AUDITED_COPY, H1_2024_UNAUDITED_COPY, Q1_2024_UNAUDITED_COPY, PROSPECTUS_2022, BVC_MARKET, OWNERSHIP_TRANSFER_2025],
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
    registry_path = args.output_dir / "cantv_data_center_and_central_office_registry.jsonl"
    summary_path = args.output_dir / "cantv_data_center_and_central_office_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
