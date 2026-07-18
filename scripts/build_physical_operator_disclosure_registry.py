#!/usr/bin/env python3
"""Build a crosswalk for major physical data-center operators.

The detailed evidence already lives in the landscape and financial ledgers.  This
builder validates and joins those records without flattening facility, campus,
market, design-capacity, operating-capacity and financial reporting scopes into a
false league table.  URLs and hashes are copied from the reviewed local evidence,
so the output is a reproducible index rather than a second hand-maintained ledger.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


def spec(
    company: str,
    financial_ref: str,
    portfolio_refs: list[str],
    geography: str,
    disclosure_class: str,
    scale_headline: str,
    scale_boundary: str,
    page_registry_refs: list[str] | None = None,
) -> dict:
    return {
        "company": company,
        "financial_profile_ref": financial_ref,
        "portfolio_profile_refs": portfolio_refs,
        "geography": geography,
        "financial_disclosure_class": disclosure_class,
        "scale_headline": scale_headline,
        "scale_boundary": scale_boundary,
        "page_registry_refs": page_registry_refs or [],
    }


SPECS = [
    spec("Aligned_Data_Centers", "company_aligned_data_centers", ["dc_aligned_north_america_public_directory", "dc_odata_aligned_latam_portfolio"], "Americas", "private_or_unlisted", "39 visible North/Latin America identifiers versus an 87 data-centers-under-management-and-future-development headline", "The 48-unit gap may include managed, private-customer or future assets; neither count is an operating-building total."),
    spec("Africa_Data_Centres", "company_africa_data_centres", ["dc_africa_data_centres_current_core_portfolio"], "Africa", "private_or_unlisted", "five current marketed facility cards in South Africa, Kenya and Nigeria", "The 92.15 MW card checksum mixes upon-completion, available and critical-IT measures and is not current live load."),
    spec("Khazna_Data_Centers", "company_khazna_data_centers", ["dc_khazna_global_portfolio"], "UAE_plus_international_pipeline", "private_or_unlisted", "30 live UAE facility markers and a separate 673 MW portfolio headline", "Visible marker design values sum to 298.51 MW, leaving a 374.49 MW scope difference that is not allocated to projects."),
    spec("Gulf_Data_Hub", "company_gulf_data_hub", ["dc_gulf_data_hub_gcc_portfolio"], "GCC_and_MENA", "private_or_unlisted", "six visible operating markers, four construction markers and 55 pipeline markers versus a seven-owned-facility transaction scope", "Ownership, website visibility and lifecycle are different scopes; pipeline pins are not permits or operating sites."),
    spec("Ascenty", "company_ascenty", ["dc_ascenty_latam_portfolio"], "Latin_America", "public_parent_with_segment_or_platform_boundary", "27 operating and 13 under-development facilities in the reviewed portfolio snapshot", "Parent and regional portfolio disclosures do not provide per-building active load, utilization or returns."),
    spec("Scala_Data_Centers", "company_scala_data_centers", ["dc_scala_latam_portfolio"], "Latin_America", "private_or_unlisted", "operating portfolio plus a large future power-and-land pipeline", "Campus and future-power announcements are not current energized, leased, utilized or billed IT load."),
    spec("DATA4", "company_data4", ["dc_data4_european_portfolio"], "Europe", "private_or_unlisted", "more than 1.5 GW marketed portfolio context with 1,252 MW of reviewed city headlines", "Pages use total power, available energy, electrical reserve and IT power language that cannot be ranked as one capacity metric."),
    spec("CoreSite", "company_american_tower", ["dc_coresite_american_tower_us_portfolio", "dc_coresite_ch2_chicago"], "United_States", "public_parent_with_segment_or_platform_boundary", "30 operating facilities in 11 markets in the latest SEC ledger", "SEC NRSF, market gross-area headlines and visible-card area have different denominators; CoreSite segment profit is company-defined."),
    spec("Iron_Mountain_Data_Centers", "company_iron_mountain", ["dc_iron_mountain_global_data_centers_portfolio"], "Global", "public_parent_with_segment_or_platform_boundary", "approximately 1.4 GW developable-capacity marketing context", "Developable and potential capacity plus a 400 MW pipeline are not operating capacity or current revenue."),
    spec("NTT_Global_Data_Centers", "company_ntt_data_group", ["dc_ntt_global_data_centers_portfolio", "dc_ntt_india_portfolio"], "Global", "public_parent_with_segment_or_platform_boundary", "more than 2,000 MW of current marketing critical-IT-load scope and a greater-than-3 GW FY2030 target", "The current headline, dated 1,630 MW management measure and target are different timing and lifecycle scopes."),
    spec("CyrusOne", "company_cyrusone", ["dc_cyrusone_global_portfolio"], "North_America_Europe_and_Japan", "private_or_unlisted", "66 published facility identifiers across 46 unique official location pages and more than 1 GW companywide critical-load claim", "Shared pages and mixed lifecycle prevent identifier count or marketed capacity from becoming an operating-building or utilized-load total.", ["life/imports/global_data_centers_20260717/cyrusone_official_location_pages.jsonl", "life/imports/global_data_centers_20260717/cyrusone_official_location_summary.json"]),
    spec("Equinix", "company_equinix", ["dc_equinix_global_ibx_xscale_portfolio"], "Global", "public_standalone_or_listed_operator", "global IBX retail portfolio plus xScale, with 52 major development projects at 2025 year-end", "Retail cabinets, xScale MW, land-supported capacity and development projects are distinct measures."),
    spec("Digital_Realty", "company_digital_realty", ["dc_digital_realty_global_portfolio"], "Global", "public_standalone_or_listed_operator", "approximately 2.9 GW in-place IT capacity, 769 MW under development and more than 5 GW future-development capacity", "In-place, under-construction and future land or space capacity cannot be added as current operating load."),
    spec("QTS", "company_qts", ["dc_qts_global_data_centers_portfolio"], "North_America_and_Europe", "private_or_unlisted", "49 canonical current official location candidates and more than 3 GW critical power under customer contract in the dated 2024 scope", "Contracted power, public-card capacity, commissioned facilities and concept-stage gross capacity are not interchangeable.", ["life/imports/global_data_centers_20260717/qts_official_location_pages.jsonl", "life/imports/global_data_centers_20260717/qts_official_location_summary.json"]),
    spec("Vantage_Data_Centers", "company_vantage_data_centers", ["dc_vantage_global_data_centers_portfolio"], "Global", "private_or_unlisted", "approximately 5.9 GW summed from current regional or campus design and full-buildout pages", "The sum mixes operating sites and development projects and is not operating, energized, leased or utilized load."),
    spec("AirTrunk", "company_airtrunk", ["dc_airtrunk_apac_portfolio"], "Asia_Pacific", "private_or_unlisted", "22 disclosed campuses with a derived design-capacity lower bound above 3.153 GW", "Campus design capacity is not current operating load; the separate dated 800 MW customer-commitment measure is not added."),
    spec("NEXTDC", "company_nextdc", ["dc_nextdc_apac_portfolio"], "Australia_and_Asia_Pacific", "public_standalone_or_listed_operator", "29 current provider facility labels across Australia, Japan, Malaysia and New Zealand", "Twenty-eight published card values sum to a 1.82055-GW mixed-lifecycle lower bound; this is not operating, energized, leased, utilized or billed load.", ["life/imports/global_data_centers_20260717/nextdc_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/nextdc_official_facility_summary.json"]),
    spec("Flexential", "company_flexential", ["dc_flexential_us_portfolio"], "United_States", "private_or_unlisted", "41 current provider cards and more than 360 MW online or under development", "The card checksum is 372.17 MW across mixed lifecycle, one card can cover multiple buildings, and the 28-asset KBRA pool uses a separate 199-MW financial boundary.", ["life/imports/global_data_centers_20260717/flexential_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/flexential_official_facility_summary.json"]),
    spec("Lumen_Technologies", "company_lumen_technologies", ["dc_lumen_north_america_colocation_network_portfolio"], "North_America_current_colocation_plus_legacy_OSM_divestiture_boundary", "public_parent_with_segment_or_platform_boundary", "current web page says 200+ North American locations and 120+ cities while the 2025 PDF says 175+ data centers and exposes 120 city/state market rows", "No current official building/address roster reconciles the scopes; 2,200+ third-party data centers are network reach, and six overseas OSM objects retain legacy labels after divestiture.", ["life/imports/global_data_centers_20260717/lumen_colocation_market_registry.jsonl", "life/imports/global_data_centers_20260717/lumen_colocation_market_summary.json"]),
    spec("Csquare", "company_csquare", ["dc_csquare_north_america_uk_portfolio"], "United_States_Canada_and_United_Kingdom", "public_standalone_or_listed_operator", "64 final-prospectus site rows, including three slated closures, versus 36 current reviewed spec-sheet facility groups", "The SEC rows, marketed groups, physical buildings and 22 operator-tagged OSM objects use different granularities; 389 MW sellable and 392 MW contracted power are not actual metered load.", ["life/imports/global_data_centers_20260717/csquare_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/csquare_official_facility_summary.json"]),
    spec("CDC_Data_Centres", "company_cdc_data_centres", ["dc_cdc_australia_new_zealand_portfolio"], "Australia_and_New_Zealand", "private_with_public_shareholder_look_through_metrics", "30 facility codes on the dated investor map across five regions, with 19 operating and six under construction in the later FY2026 portfolio table", "The dated map reconstructs 18 operating, 5 construction and 7 future codes; the later portfolio totals are not allocated to codes, and 671 MW operating capacity is not actual customer load.", ["life/imports/global_data_centers_20260717/cdc_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/cdc_official_facility_summary.json"]),
    spec("Switch", "company_switch", ["dc_switch_us_portfolio"], "United_States", "private_or_unlisted", "20 current owner-published operating data centers across five exascale campuses, plus a planned 382-acre Pennsylvania campus", "The aggregate 20-asset count is not allocated to a complete public building roster; campus full-build MW, OSM footprints and customer-hosted GPU milestones are different scopes.", ["life/imports/global_data_centers_20260717/switch_official_campus_registry.jsonl", "life/imports/global_data_centers_20260717/switch_official_campus_summary.json"]),
    spec("atNorth", "company_atnorth", ["dc_atnorth_nordic_portfolio"], "Nordics", "private_or_unlisted", "8 operating data centers, 13 current site codes and 1 GW of secured power", "Operating sites, development codes, site-page MW, secured power and 16 Iceland-only OSM objects use different scopes.", ["life/imports/global_data_centers_20260717/atnorth_official_site_registry.jsonl", "life/imports/global_data_centers_20260717/atnorth_official_site_summary.json"]),
    spec("NorthC", "company_northc", ["dc_northc_northwest_europe_portfolio"], "Netherlands_Germany_and_Switzerland", "private_or_unlisted", "25 current-network data centers versus 27 directory labels and more than 140 MW secured gross grid capacity", "Shared pages, 82.88 MW of current-card installed electrical capacity, upgrades, greenfields, 21 OSM objects and customer-owned GPUs use different scopes.", ["life/imports/global_data_centers_20260717/northc_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/northc_official_facility_summary.json"]),
    spec("Telehouse", "company_kddi", ["dc_telehouse_global_connectivity_portfolio", "dc_kddi_japan_data_center_portfolio"], "North_America_Europe_Asia_and_KDDI_Japan", "public_parent_with_segment_or_platform_boundary", "31 global brochure labels aggregating more than 45 sites plus a 22-label KDDI Japan WVS product roster and separately sourced AI projects", "City, campus and product labels, physical buildings, Osaka Sakai operation, Tama construction, design or receiving power, current load, AI systems and OSM objects use different scopes.", ["life/imports/global_data_centers_20260717/telehouse_official_location_registry.jsonl", "life/imports/global_data_centers_20260717/telehouse_official_location_summary.json", "life/imports/global_data_centers_20260717/kddi_japan_data_center_registry.jsonl", "life/imports/global_data_centers_20260717/kddi_japan_data_center_summary.json"]),
    spec("Sabey_Data_Centers", "company_sabey_data_centers", ["dc_sabey_us_portfolio"], "United_States", "private_or_unlisted", "six energized campuses with approximately 251 MW operating capacity including 76 MW of built powered shell at 2026-03-31", "Seven current location pages, North Texas pipeline, 21 historical buildings, campus design values, 11 OSM objects and customer-owned Horizon GPUs use different scopes.", ["life/imports/global_data_centers_20260717/sabey_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/sabey_official_facility_summary.json"]),
    spec("Cologix", "company_cologix", ["dc_cologix_north_america_portfolio"], "United_States_and_Canada", "private_or_unlisted", "49 current provider facility-code pages across 13 markets versus a 45-plus data-center headline", "Shared addresses, market-count conflicts, site power measures, 11 OSM objects, customer GPUaaS and private financing use different physical, operating and financial scopes.", ["life/imports/global_data_centers_20260717/cologix_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/cologix_official_facility_summary.json"]),
    spec("CloudHQ", "company_cloudhq", ["dc_cloudhq_global_portfolio"], "Global", "private_or_unlisted", "20 current campus pages versus a 23-campus headline and 5.2-GW-plus mixed-lifecycle inventory", "The 5,136.4-MW card checksum mixes operating, available, contracted, construction and future capacity; only the two-asset ABS pool confirms 160 MW leased and ramped operating load.", ["life/imports/global_data_centers_20260717/cloudhq_official_campus_registry.jsonl", "life/imports/global_data_centers_20260717/cloudhq_official_campus_summary.json"]),
    spec("Global_Switch", "company_global_switch", ["dc_global_switch_europe_apac_portfolio"], "Europe_and_Asia_Pacific", "private_or_unlisted_with_audited_bondholder_financials", "16 numeric directory labels plus two coming-soon markets, eight ESG data-centres or campuses and 252 MW saleable capacity", "Directory card MW, utility MVA, saleable MW, legal properties, OSM objects and customer GPUs use different scopes.", ["life/imports/global_data_centers_20260717/global_switch_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/global_switch_official_facility_summary.json"]),
    spec("OVHcloud", "company_ovhcloud", ["dc_ovhcloud_global_owned_and_shared_portfolio"], "Global", "public_standalone_or_listed_operator", "19 current region rows and 46 datacenters versus 44 datacenters at 18 sites in FY2025, including 31 directly held facilities", "Region rows, availability zones, directly held and shared facilities, OSM objects, servers, GPU services and physical accelerators use different scopes.", ["life/imports/global_data_centers_20260717/ovhcloud_official_location_registry.jsonl", "life/imports/global_data_centers_20260717/ovhcloud_official_location_summary.json"]),
    spec("Bouygues_Telecom", "company_bouygues_telecom", ["dc_bouygues_telecom_french_network_data_center_and_towerlink_boundary"], "France", "public_parent_with_segment_or_platform_boundary", "three provider-named historical data centers, 22 passive-asset transfers to Towerlink and 31 related OSM objects", "The 2021 named roster, transaction batches, current Vauban-owned Towerlink platform, continuing Bouygues tenancy or services and map objects do not form one current physical-building count.", ["life/imports/global_data_centers_20260717/bouygues_telecom_data_center_evidence_registry.jsonl", "life/imports/global_data_centers_20260717/bouygues_telecom_data_center_evidence_summary.json"]),
    spec("UltraEdge_SFR_legacy", "company_ultraedge", ["dc_ultraedge_french_edge_portfolio_and_sfr_legacy_boundary"], "France", "private_with_public_parent_associate_look_through", "248 current owned-and-operated sites, 30-plus data centers, 200-plus POPs and 51 MW deployed IT power versus 251 current mixed edge cards and 257 source transaction assets", "The current provider headline, directory cards, Datapole summaries, source transaction assets and 17 legacy SFR OSM objects use different granularity; none is a verified current physical-building or utilized-load total.", ["life/imports/global_data_centers_20260717/ultraedge_current_region_directory_source.json", "life/imports/global_data_centers_20260717/ultraedge_current_region_directory_registry.jsonl", "life/imports/global_data_centers_20260717/ultraedge_current_region_directory_summary.json"]),
    spec("Verizon", "company_verizon", ["dc_verizon_network_colocation_and_legacy_data_center_boundary"], "United_States_France_and_global_service_reach", "public_parent_with_segment_or_platform_boundary", "200-plus global service locations, 350-plus U.S. technology facilities with 200-plus MW available power, nine available-capacity cities, 12 external on-net partner sites and one exact Saint-Denis regulatory structure", "Service, technology-facility, city, external-partner, regulatory, historical-sale and OSM scopes do not form a current Verizon-owned physical-building or utilized-load count.", ["life/imports/global_data_centers_20260717/verizon_data_center_evidence_registry.jsonl", "life/imports/global_data_centers_20260717/verizon_data_center_evidence_summary.json"]),
    spec("Datacenter_United", "company_datacenter_united", ["dc_datacenter_united_belgium_portfolio"], "Belgium", "private_with_investor_reported_financials", "13 current investor-basis facilities across 11 locations and 24.1 MW built-and-secured IT capacity versus a 14-label mixed-lifecycle directory", "Facility labels, shared-site locations, physical buildings, development labels, OSM objects, built IT, secured expansion and utilized load use different scopes.", ["life/imports/global_data_centers_20260717/datacenter_united_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/datacenter_united_official_facility_summary.json"]),
    spec("DayOne_Data_Centers", "company_dayone", ["dc_firmus_dayone_batam_dsx"], "Asia_Pacific", "private_or_unlisted", "Batam 360 MW Firmus partnership plus the wider DayOne expansion platform", "The Batam capacity and up-to-170,000 accelerator ceiling are announced through 2027-2028, not live infrastructure."),
    spec("STACK_Infrastructure", "company_stack_infrastructure", ["dc_stack_global_data_center_portfolio"], "Global", "private_or_unlisted", "more than 8.5 GW built or under development plus more than 8.5 GW planned and potential in current marketing", "Regional headlines and market cards conflict; built, development, planned and potential scopes are never summed into operating load."),
    spec("GDS_Holdings", "company_gds_holdings", ["dc_gds_china_portfolio"], "Mainland_China", "public_standalone_or_listed_operator", "1,538 MW in service and 77.3% utilized area at Q1 2026, with 3.7 GW powered land and reservations", "Area utilization is not power utilization; powered land and reservations are future resources."),
    spec("VNET_Group", "company_vnet_group", ["dc_vnet_china_portfolio"], "Mainland_China", "public_standalone_or_listed_operator", "907 wholesale MW in service with 75.7% utilized MW plus a separate 50,170-cabinet retail fleet at Q1 2026", "Wholesale MW utilization and retail cabinet counts use different denominators and are not combined."),
    spec("Chindata_China", "company_chindata_china", ["dc_chindata_china_portfolio"], "Mainland_China", "private_or_unlisted", "dated Q2 2024 operating-plus-construction IT capacity of 1.64 GW and 1,355 MVA operating-substation nameplate", "The snapshot predates ownership changes; MVA, IT MW, construction and operating load are different measures."),
    spec("EdgeConneX", "company_edgeconnex", ["dc_edgeconnex_global_portfolio"], "Global", "private_or_unlisted", "40 kW to 500 MW-plus solution range with more than 80% of deployed MW described as build-to-suit", "Design range and build-to-suit share do not disclose current fleet MW, utilization or per-site capacity."),
    spec("STT_GDC_India", "company_stt_gdc_india", ["dc_stt_gdc_india_portfolio"], "India", "private_or_unlisted", "operating and under-development marketed portfolio with a separate 550 MW plan", "Dated operating, investment and planned-capacity snapshots are kept separate."),
    spec("CtrlS_Datacenters", "company_ctrls_datacenters", ["dc_ctrls_india_portfolio"], "India", "private_or_unlisted", "company headline of 19 live facilities and more than 370 MW versus ICRA's 17 operating facilities and 150 MW", "The 220-plus-MW difference may reflect marketed versus analytical or revenue-generating scope; it remains unresolved."),
    spec("Yotta_Data_Services", "company_nidar_yotta", ["dc_yotta_india_portfolio"], "India", "private_or_unlisted", "six reviewed operating or operated facility labels plus future campus programs", "Owned, government-operated, marketed-live and future facilities are distinct asset and lifecycle classes."),
    spec("Sify_Infinit_Spaces", "company_sify_technologies", ["dc_sify_india_portfolio"], "India", "public_standalone_or_listed_operator", "14 operating data centers and a 188.05 MW site-card sum reconciling to the rounded 188 MW headline", "Only 129 MW was cumulatively sold at FY2026 year-end; marketed live, installed, sold and revenue-generating MW differ."),
    spec("DataBank", "company_databank_holdings", ["dc_databank_north_america_uk_portfolio"], "United_States_and_United_Kingdom", "private_or_unlisted", "76 current marketing cards summing to 1.023179 GW of mixed-lifecycle critical IT load", "Eleven cards are explicitly development or future; the full checksum is not operating, energized, leased, utilized or billed load."),
    spec("Ark_Data_Centres", "company_ark_data_centres", ["dc_ark_data_centres_uk_europe_portfolio"], "United_Kingdom_Belgium_and_Spain", "private_with_statutory_operating_company_financials", "27-data-centre and 9-location headline versus eight visible pages with at least 29 card labels, a 108.42-MW statutory built-capacity reconstruction and approximately 549 MW of mixed-lifecycle page capacity", "Location cards, physical buildings, statutory operating-company sites, group developments, OSM footprints, built MW, contracted power, customer-owned GPUs and utilized load use different scopes.", ["life/imports/global_data_centers_20260717/ark_data_centres_official_location_registry.jsonl", "life/imports/global_data_centers_20260717/ark_data_centres_official_location_summary.json"]),
    spec("Orange_Group_and_Orange_Business", "company_orange_group", ["dc_orange_group_data_center_cloud_and_network_portfolio"], "Global_with_selected_France_Norway_Sweden_and_Germany_detail", "public_parent_with_segment_or_platform_boundary", "70 Orange Business infrastructure data centers versus 10-plus European Cloud Avenue locations including four in France and three selected French colocation campuses", "Group infrastructure, cloud service locations, campuses, physical buildings, legacy telecom sites, OSM objects, IT MW, generators, chillers and GPUaaS models use different scopes.", ["life/imports/global_data_centers_20260717/orange_data_center_evidence_registry.jsonl", "life/imports/global_data_centers_20260717/orange_data_center_evidence_summary.json"]),
    spec("Pulsant", "company_pulsant", ["dc_pulsant_uk_regional_edge_portfolio"], "United_Kingdom", "private_with_statutory_operating_and_group_financials", "fourteen current operating facility codes with a 22.12-MW IT-card checksum and 45.1-MVA incoming-power-sheet checksum", "Facility codes, buildings, OSM objects, IT MW, incoming MVA, available high-density MW, utilization, private-group financials and GPU-service capability use different scopes.", ["life/imports/global_data_centers_20260717/pulsant_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/pulsant_official_facility_summary.json"]),
    spec("KIO_Data_Centers", "company_kio_data_centers", ["dc_kio_latin_america_portfolio"], "Mexico_Colombia_Guatemala_Panama_and_Dominican_Republic", "private_with_sponsor_and_IFC_investment_disclosure", "fifteen current location pages across five Latin American countries with 28,490 square metres of published data-hall area", "Current location pages, historical portfolio headlines, page and PDF engineering values, expansion projects, OSM objects, live load, utilization, sponsor economics and partner GPU services use different scopes.", ["life/imports/global_data_centers_20260717/kio_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/kio_official_facility_summary.json"]),
    spec("Kumo_Networks", "company_kumo_networks", ["dc_kumo_spain_legacy_kio_portfolio"], "Spain", "private_subsidiary_with_parent_segment_look_through", "two current operating Tier IV sites in Murcia and Paterna under El Corte Ingles ownership", "Current Kumo facilities, legacy KIO Networks Espana OSM labels, published equipment ratings and the wider parent Surface Commercialization segment use different physical, ownership and financial scopes.", ["life/imports/global_data_centers_20260717/kio_official_facility_summary.json"]),
    spec("OPCORE", "company_opcore", ["dc_opcore_france_poland_and_paris_area_portfolio"], "France_and_Poland", "private_joint_venture_with_public_parent_affiliate_look_through", "seven current French provider pages, five Polish marketed addresses with at least six physical buildings, two separately scoped development records and 730 MW secured or under construction in the Paris area", "Provider pages, marketed addresses, physical buildings, legal establishments, OSM objects, utility feeds, IT load, development power, affiliate financials and installed GPUs use different scopes.", ["life/imports/global_data_centers_20260717/opcore_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/opcore_official_facility_summary.json"]),
    spec("SoftBank_inherited_IDCF_data_centers", "company_softbank_corp", ["dc_softbank_inherited_idcf_japan_data_center_portfolio"], "Japan", "public_parent_with_segment_and_transferred_business_boundary", "nine current provider location labels comprising eight operating labels and one Tomakomai development after SoftBank's 2026-04-01 succession", "Provider labels, physical buildings, expansion ceilings, OSM footprints, SoftBank group and Enterprise financials, transferred-division revenue and companywide GPUs use different scopes.", ["life/imports/global_data_centers_20260717/softbank_idcf_data_center_registry.jsonl", "life/imports/global_data_centers_20260717/softbank_idcf_data_center_summary.json"]),
    spec("VIRTUS_Data_Centres", "company_virtus_data_centres", ["dc_virtus_europe_portfolio"], "United_Kingdom_Germany_and_Italy", "private_with_statutory_consolidated_group_financials", "32 current facility codes with a 647.9-MW mixed-lifecycle checksum versus 11 fully live UK sites and 179.3 MW billable at FY2024 year-end", "Facility codes, OSM objects, operating sites, design IT MW, grid MVA, billable and contracted MW, customer GPUs and statutory group financials use different scopes.", ["life/imports/global_data_centers_20260717/virtus_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/virtus_official_facility_summary.json"]),
    spec("DigiCo_Infrastructure_REIT", "company_digico_infrastructure_reit", ["dc_digico_australia_north_america_portfolio"], "Australia_and_United_States", "public_listed_REIT_with_statutory_and_management_reporting", "13 legally held properties versus 11 current directory labels, nine source-established operating property labels and 238 MW of HY2026 planned IT capacity", "Legal properties, operating facilities, phased delivery, development land, signed asset sales, OSM objects, billing, contracted and planned IT MW, hosted customer GPUs and statutory or underlying financial measures use different scopes.", ["life/imports/global_data_centers_20260717/digico_official_property_registry.jsonl", "life/imports/global_data_centers_20260717/digico_official_property_summary.json"]),
    spec("Teraco", "company_teraco", ["dc_teraco_south_africa_portfolio"], "South_Africa", "private_subsidiary_with_public_parent_transaction_metrics", "eight operating facility codes, one under-construction code and 126 MW in-place plus 41 MW under-construction in Digital Realty's transaction scope", "Facility codes, physical buildings, campuses, a satellite earth station, 188/189/191/228-MW provider scopes, 12 OSM objects, GPUs and private-company financials use different boundaries.", ["life/imports/global_data_centers_20260717/teraco_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/teraco_official_facility_summary.json"]),
    spec("Colt_DCS", "company_colt_dcs", ["dc_colt_dcs_global_portfolio"], "United_Kingdom_Europe_India_and_Japan", "private_with_UK_statutory_entity_and_parent_segment_revenue", "15 operational data-centres headline, 13 current operating page groups, 18 split development labels and a 655.5-MW development-page checksum", "Current DCS facilities, partially operating phases, legacy datasheets, former AtlasEdge or Templus assets, Colt Technology Services nodes, OSM objects, mixed MW measures and financial perimeters use different boundaries.", ["life/imports/global_data_centers_20260717/colt_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/colt_official_facility_summary.json"]),
    spec("DataPro", "company_datapro", ["dc_datapro_moscow_portfolio"], "Russia_Moscow_region", "private_Russian_legal_entity_with_public_statutory_BFO", "four current-directory facilities, 6,550/6,553 current rack scopes and two deferred future projects yielding a 25,800 projected-rack page checksum", "Current racks, projected racks, gross facility power, provider certification claims, Uptime's current public roster, former assets, OSM footprints and legal-entity financials use different boundaries.", ["life/imports/global_data_centers_20260717/datapro_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/datapro_official_facility_summary.json"]),
    spec("Stellanor_and_legacy_Redcentric", "company_stellanor", ["dc_stellanor_uk_portfolio_and_legacy_redcentric_boundary"], "United_Kingdom", "private_newly_formed_operator_with_former_owner_segment_financial_proxy", "11 current operating sites and 39 MVA secured grid capacity versus a 68.5-MVA checksum of ten site-page maximum values", "Current Stellanor sites, three acquisition lineages, legacy Redcentric OSM labels, secured grid, site maxima, UPS, generation, cooling, former-owner financials and transaction consideration use different scopes.", ["life/imports/global_data_centers_20260717/stellanor_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/stellanor_official_facility_summary.json"]),
]


COMMON_GAPS = [
    "exact current physical building roster with ownership, lease and lifecycle",
    "operating, energized, leased, utilized, billed and customer-accepted IT load by site",
    "site-level customer concentration, revenue, operating profit and return on invested capital",
    "GPU model, count, owner, delivery state, site allocation and utilization",
    "grid feeds, substations, transformers, switchgear, UPS, batteries and backup generation",
    "cooling equipment, live liquid-cooled MW, measured PUE, WUE and absolute water",
]


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


def collect_urls(value: object) -> list[str]:
    found: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, str) and item.startswith(("https://", "http://")):
            found.append(item)
        elif isinstance(item, dict):
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return list(dict.fromkeys(found))


def load_index(path: Path, key: str) -> dict[str, dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = document[key]
    return {row["id"]: row for row in rows}


def build_records(finance_path: Path, landscape_path: Path, accessed_on: str) -> list[dict]:
    finance = load_index(finance_path, "financial_profiles")
    landscape = load_index(landscape_path, "campus_profiles")
    assert len(SPECS) == 58
    assert len({row["company"] for row in SPECS}) == len(SPECS)
    records = []
    for position, source in enumerate(SPECS, start=1):
        financial = finance[source["financial_profile_ref"]]
        portfolios = [landscape[ref] for ref in source["portfolio_profile_refs"]]
        for file_ref in source["page_registry_refs"]:
            assert Path(file_ref).exists(), file_ref
        urls = collect_urls(financial.get("sources", []))
        for portfolio in portfolios:
            urls.extend(collect_urls(portfolio.get("sources", [])))
        urls = list(dict.fromkeys(urls))
        records.append({
            "id": f"physical_operator_{source['company'].lower()}",
            "object_type": "PhysicalOperatorDisclosureCrosswalk",
            "source_order": position,
            **source,
            "official_evidence_urls": urls,
            "official_evidence_url_count": len(urls),
            "financial_profile_sha256": canonical_hash(financial),
            "portfolio_profile_sha256": canonical_hash(portfolios),
            "comparison_contract": {
                "location": "facility, building, campus, market, Region and service AZ remain separate granularities",
                "power": "utility, apparent-power, gross facility, critical IT, contracted, live and utilized values remain separate",
                "lifecycle": "operating, construction, announced, planned and potential values remain separate",
                "economics": "funding, valuation, capex plans, bookings and contract values are not revenue or operating profit",
            },
            "common_unresolved_gaps": COMMON_GAPS,
            "accessed_on": accessed_on,
        })
    return records


def build_summary(records: list[dict], accessed_on: str) -> dict:
    classes = Counter(row["financial_disclosure_class"] for row in records)
    return {
        "registry": "Major physical data-center operator disclosure crosswalk",
        "accessed_on": accessed_on,
        "operator_records": len(records),
        "financial_disclosure_class_counts": dict(sorted(classes.items())),
        "operators_with_machine_generated_page_registries": [row["company"] for row in records if row["page_registry_refs"]],
        "operators_with_reviewed_portfolio_profiles": len(records),
        "no_cross_operator_capacity_sum": True,
        "no_facility_or_building_count_ranking": True,
        "comparison_gate": [
            "Choose one physical granularity.",
            "Choose one lifecycle date and state.",
            "Choose one power denominator.",
            "Choose one financial reporting boundary.",
            "Only then compare growth, utilization, margin or returns.",
        ],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--finance", type=Path, default=Path("life/finance/ai_data_center_supply_chain_financials_202607.yaml"))
    parser.add_argument("--landscape", type=Path, default=Path("life/knowledge/global_ai_data_center_landscape_202607.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.finance, args.landscape, args.accessed_on)
    summary = build_summary(records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "physical_operator_disclosure_registry.jsonl"
    summary_path = args.output_dir / "physical_operator_disclosure_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
