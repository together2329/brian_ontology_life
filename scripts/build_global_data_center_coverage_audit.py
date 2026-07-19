#!/usr/bin/env python3
"""Audit global data-center research coverage against the OSM location baseline.

This builder does not turn OpenStreetMap objects into a world facility census.
It makes the remaining work reproducible: every non-empty OSM operator label is
counted, selected aliases are joined to reviewed profiles, unreviewed operators
are ranked, and country-level operator-tag gaps remain visible.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def canonical_label(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", folded.lower())


def entity(
    name: str,
    aliases: list[str],
    status: str,
    profile_refs: list[str],
    boundary: str,
) -> dict:
    return {
        "canonical_entity": name,
        "aliases": aliases,
        "research_status": status,
        "profile_refs": profile_refs,
        "coverage_boundary": boundary,
    }


PROFILED = [
    entity("Amazon_Web_Services", ["Amazon Web Services", "Amazon", "Amazon Web Services us-east-2 datacenter"], "reviewed_hyperscaler_profile", ["dc_aws_global_infrastructure_portfolio", "company_amazon", "aws_official_region_registry.jsonl"], "Cloud Regions, AZs and OSM objects are not one-to-one buildings."),
    entity("Microsoft", ["Microsoft"], "reviewed_hyperscaler_profile", ["dc_microsoft_global_datacenter_portfolio", "company_microsoft", "microsoft_official_region_registry.jsonl"], "Cloud Regions, AZs and OSM objects are not one-to-one buildings."),
    entity("Google", ["Google", "Google LLC"], "reviewed_hyperscaler_profile", ["dc_google_global_data_center_portfolio", "company_alphabet", "google_official_location_registry.jsonl"], "Provider location labels and OSM objects can each cover different physical scopes."),
    entity("Meta", ["Meta", "Facebook"], "reviewed_hyperscaler_profile", ["dc_meta_global_data_center_portfolio", "company_meta", "meta_official_location_registry.jsonl"], "Owned-online, announced, leased and OSM scopes remain separate."),
    entity("Apple", ["Apple", "Apple Inc."], "reviewed_hyperscaler_profile", ["dc_apple_global_data_center_portfolio", "company_apple", "apple_official_location_registry.jsonl"], "Owned campuses, individual buildings and third-party capacity remain separate."),
    entity("Oracle", ["Oracle"], "reviewed_hyperscaler_profile", ["dc_oracle_oci_global_region_portfolio", "company_oracle", "oracle_official_region_registry.jsonl"], "OCI Regions and OSM physical objects use different granularities."),
    entity("Alibaba_Cloud", ["Alibaba", "Alibaba Cloud"], "reviewed_hyperscaler_profile", ["dc_alibaba_cloud_global_region_portfolio", "company_alibaba", "alibaba_official_region_registry.jsonl"], "A published zone can contain one or multiple scattered data centers."),
    entity("Tencent_Cloud", ["Tencent", "Tencent Cloud"], "reviewed_hyperscaler_profile", ["dc_tencent_cloud_global_region_portfolio", "company_tencent", "tencent_official_region_registry.jsonl"], "Region, AZ, owned, leased and OSM scopes remain separate."),
    entity("ByteDance_Volcano_Engine", ["ByteDance", "Volcano Engine"], "reviewed_hyperscaler_profile", ["dc_bytedance_volcano_engine_infrastructure_portfolio", "company_bytedance", "volcengine_official_region_registry.jsonl"], "Product endpoints and Region/AZ labels do not prove physical buildings."),
    entity("Equinix", ["Equinix", "Equinix, Inc."], "reviewed_physical_operator_profile", ["dc_equinix_global_ibx_xscale_portfolio", "company_equinix"], "OSM objects, IBX facilities and xScale programs are not automatically the same scope."),
    entity("Digital_Realty", ["Digital Realty", "Interxion"], "reviewed_physical_operator_profile", ["dc_digital_realty_global_portfolio", "company_digital_realty"], "Legacy Interxion labels are joined to the current parent only for research routing."),
    entity("NTT_Global_Data_Centers", ["NTT", "NTT Global Data Centers", "NTT Global Data Centres", "NTT Global Data Centers EMEA GmbH"], "reviewed_physical_operator_profile", ["dc_ntt_global_data_centers_portfolio", "company_ntt_data_group"], "OSM labels do not prove a current owned, operated or revenue-generating building."),
    entity("QTS", ["QTS", "Quality Technology Services"], "reviewed_physical_operator_profile", ["dc_qts_global_data_centers_portfolio", "company_qts", "qts_official_location_pages.jsonl"], "Official page candidates and OSM objects mix campuses, buildings and lifecycle."),
    entity("CyrusOne", ["CyrusOne"], "reviewed_physical_operator_profile", ["dc_cyrusone_global_portfolio", "company_cyrusone", "cyrusone_official_location_pages.jsonl"], "Published facility identifiers can share one official page or campus."),
    entity("Vantage_Data_Centers", ["Vantage", "Vantage Data Centers", "Vantage Data Centres"], "reviewed_physical_operator_profile", ["dc_vantage_global_data_centers_portfolio", "company_vantage_data_centers"], "Mixed-lifecycle campus design MW is not current utilized load."),
    entity("CoreSite", ["CoreSite", "CoreSite Real Estate 1656 McCarthy, L.P."], "reviewed_physical_operator_profile", ["dc_coresite_american_tower_us_portfolio", "company_american_tower"], "Parent segment, facility card and OSM object scopes remain separate."),
    entity("EdgeConneX", ["EdgeConneX"], "reviewed_physical_operator_profile", ["dc_edgeconnex_global_portfolio", "company_edgeconnex"], "Public solution ranges do not disclose fleet operating MW."),
    entity("STACK_Infrastructure", ["Stack Infrastructure", "STACK Infrastructure", "STACK", "Stack Infrastructure, Incorporated", "STACK Infrastructre"], "reviewed_physical_operator_profile", ["dc_stack_global_data_center_portfolio", "company_stack_infrastructure"], "Built, under-development, planned and potential capacity remain separate."),
    entity("Iron_Mountain_Data_Centers", ["Iron Mountain", "Iron Mountain, Inc."], "reviewed_physical_operator_profile", ["dc_iron_mountain_global_data_centers_portfolio", "company_iron_mountain"], "Developable and potential capacity is not operating load."),
    entity("DataBank", ["DataBank"], "reviewed_physical_operator_profile", ["dc_databank_north_america_uk_portfolio", "company_databank_holdings"], "Current cards include explicit development and future facilities."),
    entity("NEXTDC", ["NextDC", "NEXTDC", "NEXTDC Sdn Bhd"], "reviewed_physical_operator_profile", ["dc_nextdc_apac_portfolio", "company_nextdc", "nextdc_official_facility_registry.jsonl"], "Provider labels and OSM points or footprints are not one-to-one physical buildings."),
    entity("Flexential", ["Flexential"], "reviewed_physical_operator_profile", ["dc_flexential_us_portfolio", "company_flexential", "flexential_official_facility_registry.jsonl"], "Current cards, OSM objects, physical buildings and the 28-asset securitized pool use different scopes."),
    entity("Lumen_Technologies", ["Lumen Technologies"], "reviewed_physical_operator_profile", ["dc_lumen_north_america_colocation_network_portfolio", "company_lumen_technologies", "lumen_colocation_market_registry.jsonl"], "Current web, 2025 market rows, OSM objects, divested overseas labels and third-party network reach use different scopes."),
    entity("Csquare", ["Csquare", "Centersquare", "CenterSquare", "Cyxtera"], "reviewed_physical_operator_profile", ["dc_csquare_north_america_uk_portfolio", "company_csquare", "csquare_official_facility_registry.jsonl"], "Final-prospectus site rows, marketed groups, OSM objects and legacy Cyxtera names use different legal and physical scopes."),
    entity("CDC_Data_Centres", ["CDC", "Canberra Data Centres"], "reviewed_physical_operator_profile", ["dc_cdc_australia_new_zealand_portfolio", "company_cdc_data_centres", "cdc_official_facility_registry.jsonl"], "Dated facility codes, current location pages, portfolio metrics, OSM objects and customer equipment use different scopes."),
    entity("Switch", ["Switch"], "reviewed_physical_operator_profile", ["dc_switch_us_portfolio", "company_switch", "switch_official_campus_registry.jsonl"], "The 20 operating-data-center aggregate, five campuses, named facilities, OSM footprints and hosted customer GPUs use different scopes."),
    entity("atNorth", ["atNorth"], "reviewed_physical_operator_profile", ["dc_atnorth_nordic_portfolio", "company_atnorth", "atnorth_official_site_registry.jsonl"], "Eight operating sites, thirteen codes, site-page MW, secured power and sixteen Iceland-only OSM objects use different scopes."),
    entity("NorthC", ["NorthC", "NorthC Nederland"], "reviewed_physical_operator_profile", ["dc_northc_northwest_europe_portfolio", "company_northc", "northc_official_facility_registry.jsonl"], "Twenty-five current-network data centers, twenty-seven directory labels, shared pages, current installed electrical MW, secured gross grid capacity and twenty-one OSM objects use different scopes."),
    entity("Telehouse", ["Telehouse"], "reviewed_physical_operator_profile", ["dc_telehouse_global_connectivity_portfolio", "company_kddi", "telehouse_official_location_registry.jsonl"], "Thirty-one brochure location labels aggregate more than forty-five sites; city groups, buildings, average MVA, current IT load, AI labs and OSM objects remain separate."),
    entity("KDDI", ["KDDI"], "reviewed_physical_operator_profile", ["dc_kddi_japan_data_center_portfolio", "dc_telehouse_global_connectivity_portfolio", "company_kddi", "kddi_japan_data_center_registry.jsonl"], "Twenty-two domestic WVS product labels, the wider map, Osaka Sakai operation, Tama construction, OSM telecom objects and the global Telehouse portfolio use different scopes."),
    entity("Sabey_Data_Centers", ["Sabey", "Sabey Data Centers"], "reviewed_physical_operator_profile", ["dc_sabey_us_portfolio", "company_sabey_data_centers", "sabey_official_facility_registry.jsonl"], "Six energized campuses, seven current location pages, a North Texas pipeline record, historical building count, campus design values, OSM objects and customer-owned Horizon GPUs use different scopes."),
    entity("Cologix", ["Cologix"], "reviewed_physical_operator_profile", ["dc_cologix_north_america_portfolio", "company_cologix", "cologix_official_facility_registry.jsonl"], "Forty-nine provider codes, shared-address suites, company and market counts, OSM objects, design power, customer GPUs and private financing use different scopes."),
    entity("CloudHQ", ["CloudHQ"], "reviewed_physical_operator_profile", ["dc_cloudhq_global_portfolio", "company_cloudhq", "cloudhq_official_campus_registry.jsonl"], "Twenty current campus pages, a twenty-three-campus headline, mixed-lifecycle card MW, two operating ABS assets and OSM objects use different scopes."),
    entity("Global_Switch", ["Global Switch"], "reviewed_physical_operator_profile", ["dc_global_switch_europe_apac_portfolio", "company_global_switch", "global_switch_official_facility_registry.jsonl"], "Sixteen numeric directory labels, two coming-soon markets, eight ESG campuses, legal properties, OSM objects, utility MVA and saleable MW use different scopes."),
    entity("OVHcloud", ["OVHcloud", "OVH", "OVH GmbH", "OVH Sp. z o.o."], "reviewed_physical_operator_profile", ["dc_ovhcloud_global_owned_and_shared_portfolio", "company_ovhcloud", "ovhcloud_official_location_registry.jsonl"], "Nineteen current region rows, 46 datacenters, 23 availability zones, 31 FY2025 directly held facilities, shared sites, OSM objects, servers and GPUs use different scopes."),
    entity("Bouygues_Telecom", ["Bouygues Telecom", "Bouygues Télécom"], "reviewed_physical_operator_profile", ["dc_bouygues_telecom_french_network_data_center_and_towerlink_boundary", "company_bouygues_telecom", "bouygues_telecom_data_center_evidence_registry.jsonl"], "Three 2021 provider-named data centers, 22 historical passive-asset transfers, current Towerlink property ownership, continuing Bouygues use and 31 OSM objects use different scopes."),
    entity("UltraEdge_SFR_legacy", ["SFR"], "reviewed_physical_operator_profile", ["dc_ultraedge_french_edge_portfolio_and_sfr_legacy_boundary", "company_ultraedge", "company_altice_france_sfr", "ultraedge_current_region_directory_registry.jsonl"], "UltraEdge's 248-site headline, 251 mixed edge cards, 257 source transaction assets, 30-plus data centers, 200-plus POPs and 17 legacy SFR OSM objects use different scopes."),
    entity("Verizon", ["Verizon", "Verizon Wireless", "Verizon Business"], "reviewed_physical_operator_profile", ["dc_verizon_network_colocation_and_legacy_data_center_boundary", "company_verizon", "verizon_data_center_evidence_registry.jsonl"], "The 200-plus global service locations, over-300-plus U.S. locations, 350-plus technology facilities, nine available-capacity cities, 12 external partner sites, one exact French regulatory structure, 29 sold buildings and 13 OSM objects use different scopes."),
    entity("Datacenter_United", ["Datacenter United", "Data Center United", "Datacenter United / DCstar nv"], "reviewed_physical_operator_profile", ["dc_datacenter_united_belgium_portfolio", "company_datacenter_united", "datacenter_united_official_facility_registry.jsonl"], "The 13-facility/11-location investor basis, 14-label mixed-lifecycle directory, shared-site facility labels, 12 OSM objects, 24.1 MW built-and-secured scope and development labels use different denominators."),
    entity("Ark_Data_Centres", ["Ark Data Centres"], "reviewed_physical_operator_profile", ["dc_ark_data_centres_uk_europe_portfolio", "company_ark_data_centres", "ark_data_centres_official_location_registry.jsonl"], "The 27-data-centre/9-location headline, eight visible pages with at least 29 card labels, ten OSM objects, 108.42 MW statutory built scope, approximately 549 MW mixed-lifecycle card capacity and customer-owned Nebius GPUs use different denominators."),
    entity("Orange_Group_and_Orange_Business", ["Orange", "orange", "Orange Business", "Orange Polska S.A.", "Orange România"], "reviewed_physical_operator_profile", ["dc_orange_group_data_center_cloud_and_network_portfolio", "company_orange_group", "orange_data_center_evidence_registry.jsonl"], "The 70-data-center infrastructure headline, 10-plus Cloud Avenue European locations, four French service locations, three selected French campuses, facility buildings, one landing station and eleven OSM objects use different denominators."),
    entity("Pulsant", ["Pulsant"], "reviewed_physical_operator_profile", ["dc_pulsant_uk_regional_edge_portfolio", "company_pulsant", "pulsant_official_facility_registry.jsonl"], "The fourteen current facility codes, 22.12-MW IT-card checksum, 45.1-MVA incoming-power checksum, 1.2-MW available high-density scope and twelve related OSM objects use different denominators."),
    entity("KIO_Data_Centers", ["KIO"], "reviewed_physical_operator_profile", ["dc_kio_latin_america_portfolio", "company_kio_data_centers", "kio_official_facility_registry.jsonl"], "The fifteen current location codes, 28,490-square-metre data-hall checksum, publication-level engineering conflicts, expansion projects and Latin American OSM objects use different scopes."),
    entity("Kumo_Networks", ["KIO Networks España", "KIO Networks Espana", "Kumo Networks"], "reviewed_physical_operator_profile", ["dc_kumo_spain_legacy_kio_portfolio", "company_kumo_networks", "kio_official_facility_summary.json"], "The two Spanish OSM objects retain the former KIO Networks Espana label; the current operator is Kumo Networks under El Corte Ingles ownership."),
    entity("OPCORE", ["OPCORE"], "reviewed_physical_operator_profile", ["dc_opcore_france_poland_and_paris_area_portfolio", "company_opcore", "opcore_official_facility_registry.jsonl"], "Seven current French pages, five Polish marketed addresses, at least six Polish physical buildings, ten open French legal establishments, two development records, 730 MW of Paris-area pipeline and nine OPCORE-labelled OSM objects use different scopes."),
    entity("SoftBank_inherited_IDCF_data_centers", ["IDCフロンティア"], "reviewed_physical_operator_profile", ["dc_softbank_inherited_idcf_japan_data_center_portfolio", "company_softbank_corp", "softbank_idcf_data_center_registry.jsonl"], "The legacy IDC Frontier label routes to SoftBank after the 2026-04-01 succession; nine provider locations, multi-building campuses, one development, eight Kitakyushu OSM footprints and companywide GPUs use different scopes."),
    entity("VIRTUS_Data_Centres", ["VIRTUS", "Virtus"], "reviewed_physical_operator_profile", ["dc_virtus_europe_portfolio", "company_virtus_data_centres", "virtus_official_facility_registry.jsonl"], "Thirty-two provider codes, eleven FY2024 live UK sites, 647.9 MW of mixed-lifecycle design IT capacity, eleven related OSM objects, customer GPUs and group financials use different scopes."),
    entity("DigiCo_Infrastructure_REIT", ["DigiCo"], "reviewed_physical_operator_profile", ["dc_digico_australia_north_america_portfolio", "company_digico_infrastructure_reit", "digico_official_property_registry.jsonl"], "Thirteen legal properties, eleven current directory labels, nine operating property labels, signed asset sales, 238 MW planned, seven OSM objects and hosted-customer GPUs use different scopes."),
    entity("Teraco", ["Teraco", "Terao Data Environments"], "reviewed_physical_operator_profile", ["dc_teraco_south_africa_portfolio", "company_teraco", "teraco_official_facility_registry.jsonl"], "Eight operating facility codes, JB1 East and West buildings, JB7 construction, the Teleport, mixed 126/167/188/189/191/228-MW scopes and twelve related OSM objects use different boundaries."),
    entity("Colt_DCS_and_legacy_Colt_labels", ["Colt", "Colt data centre services", "Colt Technology Services nv"], "reviewed_physical_operator_profile", ["dc_colt_dcs_global_portfolio", "company_colt_dcs", "colt_official_facility_registry.jsonl"], "Sixteen related OSM objects resolve into eight current DCS candidates, three former DCS assets now at AtlasEdge or Templus and five Colt Technology Services network or telecom facilities; the raw operator aliases route eight tagged objects to this boundary profile."),
    entity("DataPro", ["DataPro"], "reviewed_physical_operator_profile", ["dc_datapro_moscow_portfolio", "company_datapro", "datapro_official_facility_registry.jsonl"], "Six Moscow-region OSM objects resolve into four current-directory facilities and two deferred future projects; current racks, projected racks and gross facility power remain separate."),
    entity("Stellanor_and_legacy_Redcentric_labels", ["Redcentric", "Stellanor", "Stellanor Datacenters", "Stellanor Data Centers"], "reviewed_physical_operator_profile", ["dc_stellanor_uk_portfolio_and_legacy_redcentric_boundary", "company_stellanor", "stellanor_official_facility_registry.jsonl"], "Six OSM objects retain the former Redcentric operator label after the eight-site sale; Stellanor's current eleven-site roster, three acquisition lineages, 39-MVA portfolio headline and site-page maximum values use different scopes."),
    entity("Rostelecom_RTK_COD", ["Rostelecom"], "reviewed_physical_operator_profile", ["dc_rostelecom_rtk_cod_russia_portfolio", "company_rostelecom_rtk_cod", "rostelecom_rtk_cod_facility_registry.jsonl"], "Six Rostelecom-tagged OSM objects cover only part of the provider's 26-site portfolio; two Nizhny building footprints are one facility candidate, and rack, MW, GPU-service and financial scopes remain separate."),
    entity("Selectel", ["Selectel"], "reviewed_physical_operator_profile", ["dc_selectel_russia_owned_and_global_service_footprint", "company_selectel", "selectel_official_facility_registry.jsonl"], "Six Selectel-tagged OSM objects plus one name-only building crosswalk to six current own facilities, eight partner or product service locations and one unconfirmed development; physical sites, service domains, connected power, GPU configurations and financial scopes remain separate."),
    entity("TenPeaks_and_legacy_Spark_New_Zealand_labels", ["Spark New Zealand", "Spark", "TenPeaks", "TenPeaks Data Centres"], "reviewed_physical_operator_profile", ["dc_tenpeaks_new_zealand_portfolio_and_legacy_spark_boundary", "company_tenpeaks_and_spark_new_zealand", "tenpeaks_legacy_spark_facility_registry.jsonl"], "Seven operator-tagged OSM objects retain legacy Spark labels after the 2026 transfer, while two Albany objects are name-only; the current eleven-facility headline, nine operating map labels, plausible component reconciliation, development pipeline and pre-sale financials remain separate scopes."),
    entity("IXcellerate", ["IXcellerate"], "reviewed_physical_operator_profile", ["dc_ixcellerate_moscow_campus_portfolio", "company_ixcellerate", "ixcellerate_official_facility_registry.jsonl"], "Five OSM objects crosswalk exactly to MOS1-MOS5, while current full-design cards, the 10,329-rack end-2025 statement, staged MOS3 delivery, grid power and South or Veshki full-build plans retain separate scopes."),
    entity("Leading_Edge_Data_Centres", ["Leading Edge Data Centres", "Leading Edge Data Centre"], "reviewed_physical_operator_profile", ["dc_leading_edge_data_centres_australia_regional_portfolio", "company_leading_edge_data_centres", "leading_edge_official_facility_registry.jsonl"], "Six OSM ways crosswalk to all six current NSW facility cards; the singular Tamworth operator label, current 3.975-MW card checksum, historical 75-rack first-six design, older rollout plans, AI business names and investor financial scopes remain separate."),
    entity("Prime_Data_Centers", ["Prime", "Prime Data Centers"], "reviewed_physical_operator_profile", ["dc_prime_data_centers_north_america_emea_portfolio", "company_prime_data_centers", "prime_data_centers_official_facility_registry.jsonl"], "Six OSM objects cover four current facility candidates plus the historical Saeby plan; two Dallas footprints are one facility, and the current directory, portfolio headlines, pipeline, customer GPUs and private financials remain separate."),
    entity("TierPoint", ["TierPoint"], "reviewed_physical_operator_profile", ["dc_tierpoint_us_enterprise_and_ai_colocation_portfolio", "company_tierpoint", "tierpoint_official_facility_registry.jsonl"], "Five operator-tagged OSM objects plus ten name, owner or website crosswalks cover 15 current facility candidates; 37 page groups, 40 sheet records, 33 collateral assets, power/cooling evidence and customer hardware remain separate scopes."),
    entity("Kao_Data", ["Kao Data"], "reviewed_physical_operator_profile", ["dc_kao_data_uk_ai_and_advanced_computing_portfolio", "company_kao_data", "kao_data_official_facility_registry.jsonl"], "Four operator-tagged OSM ways crosswalk to KLON-01, KLON-02, KLON-05 and KLON-06; seven current codes, Park Royal, mixed MW measures, customer GPUs and statutory or investor financial perimeters remain separate."),
    entity("Verne", ["Verne Global", "Verne"], "reviewed_physical_operator_profile", ["dc_verne_northern_europe_ai_colocation_portfolio", "company_verne", "verne_official_facility_registry.jsonl"], "Four operator-tagged OSM objects plus one name-only campus relation crosswalk to Iceland, Helsinki and transitional London; retained operations, divestments, signed sale, construction, plans, customer GPUs and financial perimeters remain separate."),
    entity("Cogent_Communications", ["Cogent", "Cogent Communications", "Cogent Communications, Inc."], "reviewed_physical_operator_profile", ["dc_cogent_classic_edge_and_network_data_center_portfolio", "company_cogent_communications", "cogent_official_data_center_registry.jsonl"], "Ten OSM objects crosswalk to French facility or city candidates and Phoenix; 62 North American market labels, 19 European facilities, hidden building multiplicity, 86 edge sites, dated statutory counts, power, GPU and companywide financial scopes remain separate."),
    entity("GasLINE_Dernbach_amplifier_sites", ["GasLINE"], "reviewed_non_data_center_network_site", ["gasline_osm_classification_registry.jsonl", "gasline_osm_classification_summary.json"], "Eight tiny OSM building footprints sit inside two named telecommunications amplifier-site enclosures. Official GasLINE evidence describes a dark-fibre network that reaches third-party data centers, not an owned data-center portfolio; zero physical facilities or MW are inferred."),
    entity("IBM_Cloud_and_legacy_IBM_facility_labels", ["IBM"], "reviewed_physical_operator_and_legacy_identity_boundary", ["dc_ibm_cloud_global_physical_code_and_accelerator_portfolio", "dc_kyndryl_global_managed_infrastructure_and_legacy_ibm_facility_boundary", "company_ibm", "company_kyndryl", "ibm_cloud_kyndryl_boundary_registry.jsonl"], "Eight IBM-operator OSM objects are retained across legacy France and Horsham labels; seven France objects align at site-group level with current Kyndryl certificates after the 2021 separation, while IBM Cloud's 47 physical codes have no official code-to-building bridge."),
    entity("Kyndryl", ["Kyndryl Deutschland GmbH"], "reviewed_physical_operator_profile", ["dc_kyndryl_global_managed_infrastructure_and_legacy_ibm_facility_boundary", "company_kyndryl", "ibm_cloud_kyndryl_boundary_registry.jsonl"], "Two German OSM objects align with certified Schwalbach/Eschborn and Oberursel data-center rows; the eleven selected France and Germany certificate groups are not a complete global fleet, property or capacity roster."),
    entity("Compass_Datacenters_and_Thunderball_legacy_misattribution", ["Compass", "True North Data Solutions"], "reviewed_physical_operator_and_legacy_misattribution_boundary", ["dc_compass_datacenters_current_hyperscale_and_transition_market_portfolio", "company_compass_datacenters", "compass_datacenters_market_registry.jsonl"], "Twenty-one related OSM objects include six Thunderball objects with a raw True North operator label. Virginia DEQ and Loudoun permits identify Compass at four exact addresses; the raw label is preserved but not used as current operator proof, while the TikTok-named footprint remains an unverified tenant label."),
    entity("ETIX", ["ETIX"], "reviewed_physical_operator_profile", ["dc_etix_france_belgium_thailand_edge_and_ai_ready_portfolio", "company_etix", "etix_official_facility_registry.jsonl"], "Five ETIX-tagged OSM objects map to base or newly acquired candidates; four name-only objects cover two legacy Vendee #2 geometries, Lille #1 and an unverified Labege transaction-site candidate. The 15-site directory, four-site legal-control transition and Bangkok #2 expansion remain separate scopes."),
    entity("TelemaxX", ["TelemaxX Telekommunikation GmbH"], "reviewed_physical_operator_profile_with_former_data_center_POP_boundary", ["dc_telemaxx_karlsruhe_regional_colocation_and_cloud_portfolio", "company_telemaxx", "telemaxx_official_facility_registry.jsonl"], "Five TelemaxX-tagged OSM objects map to the complete provider directory, but only IPC1, IPC3, IPC4 and IPC5 remain in the current four-data-center housing scope. IPC2 is now POP Technologiepark Karlsruhe, so its legacy data-center tag adds no fifth current facility."),
    entity("CANTV", ["CANTV"], "reviewed_physical_operator_profile_with_central_office_false_positive_boundary", ["dc_cantv_venezuela_data_center_and_telecommunications_central_office_boundary", "company_cantv", "cantv_data_center_and_central_office_registry.jsonl"], "Current service evidence names Data Center El Hatillo, but none of the seven CANTV-tagged OSM central-office or telecom-building objects matches it or is provider-confirmed as a current commercial data center. OSM objects add no verified facility, area, MW, equipment, GPU or financial count."),
    entity("REFSA_Telecomunicaciones", ["REFSA", "REFSA TELECOMUNICACIONES"], "reviewed_physical_operator_profile_with_fiber_node_false_positive_boundary", ["dc_refsatel_formosa_parque_industrial_data_center_and_fiber_node_boundary", "company_refsa_telecomunicaciones", "refsatel_data_center_and_fiber_node_registry.jsonl"], "Eight operator-tagged OSM rows plus two name-only rows reconcile to one Parque Industrial data-center shelter and nine official-map fiber nodes. Only the shelter is counted; network nodes add no facility, MW, rack, equipment, GPU or financial count."),
    entity("EDF", ["EDF"], "reviewed_internal_enterprise_data_center_profile_with_building_group_and_uncorroborated_point_boundary", ["dc_edf_france_internal_data_center_and_hpc_boundary", "company_edf_group", "edf_internal_data_center_registry.jsonl"], "Five EDF-labelled OSM objects reconcile to two current AFNOR-certified internal data-center sites: four Pacy building geometries and one NOE works or campus polygon. A Saint-Ouen point beside RTE's national control centre is absent from the current certificate and excluded from facility counts."),
    entity("BNP_Paribas", ["BNP Paribas"], "reviewed_internal_enterprise_data_center_profile_with_campus_building_legacy_sale_and_hosted_compute_boundary", ["dc_bnp_paribas_internal_data_center_and_hosted_hpc_boundary", "company_bnp_paribas", "bnp_paribas_internal_and_hosted_data_center_registry.jsonl"], "Five operator-tagged OSM objects plus one name-only relation reconcile to three current French site groups, one additional MAE2 campus building and one legacy Val-de-Reuil label. Two current Belgian sites are off the OSM operator sample, while atNorth and IBM Cloud scopes remain hosted or service boundaries."),
    entity("Vodafone_Group_and_legacy_Cable_Wireless_Worldwide", ["Vodafone", "Cable & Wireless", "Vodafone Türkiye"], "reviewed_diversified_telecom_data_center_subsea_legacy_and_brand_boundary", ["dc_vodafone_group_and_legacy_cww_data_center_subsea_and_brand_boundary", "company_vodafone_group", "vodafone_legacy_cww_data_center_evidence_registry.jsonl"], "Eleven operator-tagged OSM objects are reconciled with five additional name-only related rows. Only Esenyurt is in the exact current OSM site floor; seven landing stations are excluded from compute counts, Dublin geometries are grouped, dated UK and historical fleet disclosures are not treated as current, and CWW, CWC, One NZ, Panama and PNG corporate or brand lineages are separated."),
    entity("SRCE_University_Computing_Centre", ["Sveučilišni računski centar"], "reviewed_current_academic_data_center_power_and_HPC_accelerator_profile", ["dc_srce_hr_zoo_croatia_academic_data_center_and_hpc_portfolio", "company_srce_university_computing_centre", "srce_hr_zoo_data_center_hpc_registry.jsonl"], "Five operator-tagged OSM points exactly match SRCE's five HR-ZOO project sites. The current provider roster adds off-sample Srce ZG3 for six sites total, and current power, rack, generator, UPS, cooling and 97-A100 ZG2 evidence is retained without converting design nameplates into live IT load."),
    entity("UCBL_INSA_CCDD", ["Université Claude Bernard - Lyon 1"], "reviewed_joint_academic_data_center_building_group_and_migration_boundary", ["dc_ucbl_insa_ccdd_lyontech_la_doua_academic_data_center_boundary", "company_universite_claude_bernard_lyon_1", "ucbl_ccdd_data_center_hpc_registry.jsonl"], "Five adjacent identically named OSM ways are grouped into one CCDD facility: one main building geometry and four small support or technical structures of unverified exact role. First-phase and ultimate racks, planned efficiency, migration-window HPC evidence, current GPUs, IT load and public-university accounts retain separate scopes."),
    entity("Aruba_SpA", ["Aruba s.p.a.", "Aruba S.p.A."], "reviewed_current_owned_data_center_power_cooling_AI_and_private_financial_boundary", ["dc_aruba_europe_owned_and_partner_data_center_portfolio", "company_aruba_spa", "aruba_owned_data_center_registry.jsonl"], "Four operator-tagged OSM objects represent three of Aruba's seven reconstructed current owned physical facilities: IT1, IT2 and one IT4 DC-A group across two component geometries. IT3 DC-A/B/C and CZ2 are off-sample; future IT4 buildings, partners, power labels, live load, GPUs and private-company financials remain separate."),
    entity("BCX_Business_Connexion_Group", ["BCX"], "reviewed_current_data_center_cloud_dated_roster_power_and_audited_parent_financial_boundary", ["dc_bcx_south_africa_data_center_cloud_and_legacy_roster_boundary", "company_bcx_telkom_segment", "bcx_data_center_registry.jsonl"], "Four BCX-tagged OSM objects reconcile to two Midrand physical facility groups, NDC1 and NDC2, each represented by an overlapping building and enclosing site geometry. Current 9, 12, 21 and 5 counts, the dated ten-site table, power and area checksum conflicts, historical engineering, catalog GPUs and Telkom financial scopes remain separate."),
    entity("Cirion_Technologies", ["Cirion Technologies"], "reviewed_current_integrated_data_center_fiber_high_density_and_private_credit_boundary", ["dc_cirion_latin_america_data_center_fiber_and_high_density_boundary", "company_cirion_technologies", "cirion_data_center_registry.jsonl"], "Four operator-tagged OSM objects plus two name-only related rows reconcile to ROS1, BUE1, SAN1, LIM2 and LIM1, while the Las Toninas submarine landing station is excluded from compute counts. The eighteen-facility audit roster, two recent activations, RIO2 development, main and edge scopes, equipment, GPUs and rating financials remain separate."),
    entity("nLighten_France_legacy_Euclyde", ["Euclyde", "Euclyde Datacenters"], "reviewed_current_France_edge_portfolio_with_legacy_brand_end_state_capacity_and_audited_group_boundary", ["dc_euclyde_nlighten_france_edge_data_center_legacy_and_current_boundary", "company_nlighten_france_and_legacy_euclyde", "euclyde_nlighten_france_data_center_registry.jsonl"], "Five legacy Euclyde-labelled OSM objects route to NCE1, NCE2, LYS1, PAR1 and SXB1. The current nLighten France directory has eight sites including off-sample MLH1, PAR2 and PAR3; legacy codes, end-state capacity, buildings, live load, GPUs, European-group financials and French legal entities remain separate."),
    entity("DATA4", ["Data4", "data4", "Data4 Italia", "DATA4"], "reviewed_physical_operator_profile", ["dc_data4_european_portfolio", "company_data4"], "Published power terms vary between IT, reserve, total and available energy."),
    entity("AirTrunk", ["AirTrunk"], "reviewed_physical_operator_profile", ["dc_airtrunk_apac_portfolio", "company_airtrunk"], "Campus design capacity is not current live load."),
    entity("Aligned_Data_Centers", ["Aligned", "Aligned Data Centers", "Aligned Data Centres", "Aligned Data Centers, LLC", "ODATA"], "reviewed_physical_operator_profile", ["dc_aligned_north_america_public_directory", "dc_odata_aligned_latam_portfolio", "company_aligned_data_centers"], "ODATA and Aligned labels are joined at current platform level, not treated as identical facility brands historically."),
    entity("Africa_Data_Centres", ["Africa Data Centres", "Africa Data Centers"], "reviewed_physical_operator_profile", ["dc_africa_data_centres_current_core_portfolio", "company_africa_data_centres"], "Official cards mix critical IT, available and completion measures."),
    entity("Khazna_Data_Centers", ["Khazna", "Khazna Data Centers", "Khazna Data Centres"], "reviewed_physical_operator_profile", ["dc_khazna_global_portfolio", "company_khazna_data_centers"], "Visible markers do not allocate the entire company portfolio headline."),
    entity("Gulf_Data_Hub", ["Gulf Data Hub"], "reviewed_physical_operator_profile", ["dc_gulf_data_hub_gcc_portfolio", "company_gulf_data_hub"], "Website visibility, ownership and lifecycle are different scopes."),
    entity("Ascenty", ["Ascenty"], "reviewed_physical_operator_profile", ["dc_ascenty_latam_portfolio", "company_ascenty"], "Per-building active load and economics remain undisclosed."),
    entity("Scala_Data_Centers", ["Scala Data Centers", "Scala Data Centres"], "reviewed_physical_operator_profile", ["dc_scala_latam_portfolio", "company_scala_data_centers"], "Future land and power announcements are not current capacity."),
    entity("DayOne_Firmus", ["DayOne", "DayOne Data Centers", "DayOne Data Centres", "Firmus"], "reviewed_physical_operator_profile", ["dc_firmus_dayone_batam_dsx", "company_dayone"], "Announced accelerator and capacity ceilings are not installed inventory."),
    entity("GDS_Holdings", ["GDS", "GDS Holdings"], "reviewed_physical_operator_profile", ["dc_gds_china_portfolio", "company_gds_holdings"], "Area utilization and powered-land capacity use different denominators."),
    entity("VNET_Group", ["VNET", "VNET Group", "21Vianet"], "reviewed_physical_operator_profile", ["dc_vnet_china_portfolio", "company_vnet_group"], "Wholesale MW and retail cabinets are not additive."),
    entity("Chindata", ["Chindata"], "reviewed_physical_operator_profile", ["dc_chindata_china_portfolio", "company_chindata_china"], "The reviewed company snapshot is dated and predates ownership changes."),
    entity("STT_GDC_India", ["STT GDC", "STT GDC India"], "reviewed_physical_operator_profile", ["dc_stt_gdc_india_portfolio", "company_stt_gdc_india"], "Operating, development and investment-plan scopes remain separate."),
    entity("CtrlS", ["CtrlS", "CtrlS Datacenters", "CtrlS Datacentres"], "reviewed_physical_operator_profile", ["dc_ctrls_india_portfolio", "company_ctrls_datacenters"], "Company and credit-analysis facility and MW scopes conflict."),
    entity("Yotta", ["Yotta", "Yotta Data Services"], "reviewed_physical_operator_profile", ["dc_yotta_india_portfolio", "company_nidar_yotta"], "Owned, operated and future facilities remain separate."),
    entity("Sify", ["Sify", "Sify Technologies"], "reviewed_physical_operator_profile", ["dc_sify_india_portfolio", "company_sify_technologies"], "Installed, sold and revenue-generating MW remain separate."),
    entity("xAI", ["xAI"], "reviewed_neocloud_profile", ["neocloud_disclosure_registry.jsonl"], "OSM facility objects and GPU-service disclosures require an object-level join."),
]


PRIORITY_GAPS = {
    canonical_label(name): (entity_name, priority)
    for entity_name, priority, names in [
        ("atNorth", "P1", ["atNorth"]),
        ("Switch", "P1", ["Switch"]),
        ("Pulsant", "P2", ["Pulsant"]),
        ("Colt", "P2", ["Colt"]),
        ("Redcentric", "P2", ["Redcentric"]),
        ("DataPro", "P2", ["DataPro"]),
        ("Rostelecom", "P2", ["Rostelecom"]),
        ("IXcellerate", "P2", ["IXcellerate"]),
    ]
    for name in names
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_alias_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for item in PROFILED:
        for alias in item["aliases"]:
            key = canonical_label(alias)
            assert key not in index or index[key]["canonical_entity"] == item["canonical_entity"], (alias, index[key]["canonical_entity"])
            index[key] = item
    return index


def country_codes(row: dict) -> list[str]:
    return sorted({candidate.get("iso2") for candidate in row.get("country_candidates", []) if candidate.get("iso2")})


def build_operator_records(rows: list[dict], accessed_on: str) -> list[dict]:
    alias_index = build_alias_index()
    counts = Counter()
    countries: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        label = (row.get("operator") or "").strip()
        if not label:
            continue
        counts[label] += 1
        countries[label].update(country_codes(row))
    output = []
    for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())):
        key = canonical_label(label)
        match = alias_index.get(key)
        gap = PRIORITY_GAPS.get(key)
        if match:
            status = match["research_status"]
            canonical_entity = match["canonical_entity"]
            priority = "covered_current_profile"
            profile_refs = match["profile_refs"]
            boundary = match["coverage_boundary"]
        elif gap:
            canonical_entity, priority = gap
            status = "priority_operator_profile_gap"
            profile_refs = []
            boundary = "OSM count establishes mapped objects only; official roster, lifecycle, MW, GPU, equipment and financial evidence still require review."
        else:
            canonical_entity = None
            priority = "untriaged"
            status = "raw_operator_label_not_yet_entity_resolved"
            profile_refs = []
            boundary = "The raw OSM operator label may be an owner, tenant, telecom, enterprise, public institution, legacy brand or spelling variant."
        output.append({
            "id": f"osm_operator_label_{hashlib.sha256(label.encode()).hexdigest()[:16]}",
            "object_type": "OSMOperatorLabelCoverageAudit",
            "raw_operator_label": label,
            "normalized_label": key,
            "canonical_entity": canonical_entity,
            "mapped_object_count": count,
            "country_codes": sorted(countries[label]),
            "country_count": len(countries[label]),
            "research_status": status,
            "research_priority": priority,
            "profile_refs": profile_refs,
            "coverage_boundary": boundary,
            "accessed_on": accessed_on,
        })
    return output


def build_country_records(rows: list[dict], accessed_on: str) -> list[dict]:
    totals = Counter()
    operator_tagged = Counter()
    construction = Counter()
    for row in rows:
        codes = country_codes(row)
        for code in codes:
            totals[code] += 1
            if row.get("operator"):
                operator_tagged[code] += 1
            if row.get("tags", {}).get("construction"):
                construction[code] += 1
    return [{
        "id": f"osm_country_{code.lower()}",
        "object_type": "OSMCountryCoverageAudit",
        "iso2": code,
        "mapped_object_count": totals[code],
        "operator_tagged_object_count": operator_tagged[code],
        "operator_untagged_object_count": totals[code] - operator_tagged[code],
        "operator_tag_coverage_percent": round(operator_tagged[code] / totals[code] * 100, 2),
        "construction_tagged_object_count": construction[code],
        "research_priority_signal": "high_object_count_or_low_operator_tag_coverage" if totals[code] >= 50 or operator_tagged[code] / totals[code] < 0.5 else "standard",
        "coverage_boundary": "Country assignment and object count are OSM-derived; neither proves a complete national facility roster or operating status.",
        "accessed_on": accessed_on,
    } for code in sorted(totals, key=lambda code: (-totals[code], code))]


def build_summary(rows: list[dict], operator_records: list[dict], country_records: list[dict], accessed_on: str) -> dict:
    with_operator = sum(1 for row in rows if row.get("operator"))
    reviewed_objects = sum(row["mapped_object_count"] for row in operator_records if row["research_status"].startswith("reviewed_"))
    priority_rows = [row for row in operator_records if row["research_status"] == "priority_operator_profile_gap"]
    priority_entities: dict[str, dict] = {}
    for row in priority_rows:
        item = priority_entities.setdefault(row["canonical_entity"], {"canonical_entity": row["canonical_entity"], "priority": row["research_priority"], "mapped_object_count": 0, "raw_labels": [], "country_codes": set()})
        item["mapped_object_count"] += row["mapped_object_count"]
        item["raw_labels"].append(row["raw_operator_label"])
        item["country_codes"].update(row["country_codes"])
    ranked = sorted(priority_entities.values(), key=lambda item: (item["priority"], -item["mapped_object_count"], item["canonical_entity"]))
    for rank, item in enumerate(ranked, 1):
        item["rank"] = rank
        item["raw_labels"] = sorted(item["raw_labels"])
        item["country_codes"] = sorted(item["country_codes"])
    objects_without_iso2 = sum(1 for row in rows if not country_codes(row))
    summary = {
        "schema_version": 1,
        "registry": "Global data-center research coverage and gap audit",
        "accessed_on": accessed_on,
        "baseline": {
            "osm_mapped_objects": len(rows),
            "iso2_country_records": len(country_records),
            "objects_with_operator_label": with_operator,
            "objects_without_operator_label": len(rows) - with_operator,
            "distinct_nonempty_raw_operator_labels": len(operator_records),
            "objects_without_resolved_iso2": objects_without_iso2,
        },
        "review_join": {
            "mapped_objects_whose_raw_operator_label_routes_to_a_reviewed_profile": reviewed_objects,
            "percent_of_all_mapped_objects": round(reviewed_objects / len(rows) * 100, 2),
            "percent_of_operator_tagged_mapped_objects": round(reviewed_objects / with_operator * 100, 2),
            "boundary": "Routing a raw label to a reviewed company, portfolio or explicit exclusion-classification profile does not prove every OSM object is a physical facility or was individually reconciled to an official facility record.",
        },
        "priority_unreviewed_operator_entities": ranked,
        "priority_method": "P1 core physical operators first, then P2 operators and telecom platforms; mapped-object count breaks ties but is not market share.",
        "next_sequence": [
            "The ranked P1/P2 official facility, lifecycle and scale profile baseline is complete; continue through the highest-impact unresolved long-tail operators and aliases.",
            "Join site-level power, cooling and accelerator evidence without converting readiness into installed inventory.",
            "Join audited company or parent financials and preserve segment boundaries.",
            "Resolve high-count raw labels and legacy subsidiaries before expanding low-count country tails.",
            "Refresh the OSM baseline separately; never describe it as every physical data center worldwide.",
        ],
        "non_completion_statement": "Public sources do not expose every physical building, GPU, utility feed, equipment BOM, customer contract or site profit. Unknown fields remain explicit research results.",
    }
    summary["operator_records_sha256"] = canonical_hash(operator_records)
    summary["country_records_sha256"] = canonical_hash(country_records)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--input", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    rows = load_rows(args.input)
    operator_records = build_operator_records(rows, args.accessed_on)
    country_records = build_country_records(rows, args.accessed_on)
    summary = build_summary(rows, operator_records, country_records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    operator_path = args.output_dir / "global_data_center_operator_coverage_audit.jsonl"
    country_path = args.output_dir / "global_data_center_country_coverage_audit.jsonl"
    summary_path = args.output_dir / "global_data_center_coverage_audit_summary.json"
    operator_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in operator_records), encoding="utf-8")
    country_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in country_records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"operator_labels": len(operator_records), "countries": len(country_records), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
