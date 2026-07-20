#!/usr/bin/env python3
"""Build a scope-preserving neocloud and linked-capacity-host registry.

The registry is a reviewed snapshot of official company pages and public-company
filings.  It intentionally does not add unlike quantities: active, contracted,
under-construction and pipeline MW are different lifecycle measures; installed,
ordered, managed and customer-dedicated GPUs are different inventory scopes.
Provider Regions and availability zones are service labels, not buildings.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


RECORDS = [
    {
        "id": "neocloud_coreweave",
        "company": "CoreWeave",
        "roster": "primary_operator",
        "ownership_status": "public_NASDAQ_CRWV",
        "business_model": ["GPU_cloud", "AI_infrastructure_software", "long_term_capacity_tenant"],
        "physical_and_service_footprint": {
            "data_centers_2025_12_31": 43,
            "service_AZ_identifiers_2026_04_17": 56,
            "boundary": "AZ identifiers are service failure domains and do not reconcile one-for-one to physical data centers.",
        },
        "power_disclosure": [
            {"value": ">850", "unit": "MW", "as_of": "2025-12-31", "lifecycle": "active"},
            {"value": 3.1, "unit": "GW", "as_of": "2025-12-31", "lifecycle": "contracted"},
            {"value": ">1", "unit": "GW", "as_of": "2026-Q1", "lifecycle": "active"},
            {"value": ">3.5", "unit": "GW", "as_of": "2026-Q1", "lifecycle": "contracted"},
            {"value": ">8", "unit": "GW", "as_of": "2030", "lifecycle": "target"},
        ],
        "gpu_disclosure": {
            "current_exact_physical_count": "undisclosed",
            "historical_count": {"value": ">250000", "as_of": "2024-12-31", "scope": "company_fleet"},
            "vendor": "NVIDIA",
            "platforms": ["GB200_NVL72", "GB300_NVL72", "RTX_PRO_6000"],
            "boundary": "The historical 2024 count is not a current fleet count and cannot be assigned to a site.",
        },
        "commercial_disclosure": {
            "FY2025_revenue_usd_million": 5131,
            "FY2025_operating_loss_usd_million": 46,
            "FY2025_net_loss_usd_million": 1167,
            "Q1_2026_revenue_usd_million": 2078,
            "Q1_2026_revenue_backlog_usd_million": 99400,
            "boundary": "Backlog is broader than GAAP RPO and is not current revenue or cash.",
        },
        "landscape_refs": ["dc_coreweave_global_fleet", "dc_coreweave_europe_service_footprint", "dc_galaxy_helios_dickens_county", "dc_applied_digital_polaris_forge_1_coreweave", "dc_core_scientific_coreweave_us_portfolio"],
        "financial_profile_ref": "company_coreweave",
        "sources": [
            "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm",
            "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000222/crwv-20260331.htm",
            "https://docs.coreweave.com/platform/regions/all-availability-zones",
        ],
    },
    {
        "id": "neocloud_nscale",
        "company": "Nscale",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["AI_infrastructure_operator", "GPU_cloud", "campus_developer"],
        "physical_and_service_footprint": {
            "reviewed_named_programs": ["Narvik_Norway", "Monarch_West_Virginia", "Verne_Iceland", "Loughton_UK", "Sines_Portugal", "Ward_County_Texas"],
            "boundary": "The list mixes individual campuses, partner facilities and future programs; it is not a current operating-facility count.",
        },
        "power_disclosure": [
            {"value": 230, "unit": "MW", "site": "Narvik", "lifecycle": "initial_design"},
            {"value": 290, "unit": "MW", "site": "Narvik", "lifecycle": "potential_addition"},
            {"value": 1.35, "unit": "GW", "site": "Monarch", "lifecycle": "phase_one_LOI"},
            {"value": 15, "unit": "MW", "site": "Verne_Iceland", "lifecycle": "2026_deployment_target"},
            {"value": 234, "unit": "MW", "site": "Ward_County", "lifecycle": "contracted_critical_IT"},
        ],
        "gpu_disclosure": {
            "deployments": [
                {"value": 100000, "model": "NVIDIA_undisclosed", "site": "Narvik", "lifecycle": "end_2026_target"},
                {"value": ">30000", "model": "NVIDIA_Rubin", "site": "Narvik", "lifecycle": "2027_Microsoft_target"},
                {"value": "~4600", "model": "NVIDIA_Blackwell_Ultra", "site": "Verne_Iceland", "lifecycle": "2026_target"},
                {"value": 23040, "model": "NVIDIA_GB300", "site": "Loughton", "lifecycle": "Q1_2027_target"},
                {"value": "~12600", "model": "NVIDIA_GB300", "site": "Sines_first_building", "lifecycle": "Q1_2026_service_target"},
                {"value": ">66000", "model": "NVIDIA_Vera_Rubin", "site": "Sines_second_building", "lifecycle": "late_2027_start_target"},
                {"value": "~104000", "model": "NVIDIA_GB300", "site": "Ward_County", "lifecycle": "Q3_2026_phased_delivery_target"},
            ],
            "boundary": "Deployment announcements overlap in customers, timing and program scope; no company-wide installed total is derived.",
        },
        "commercial_disclosure": {"audited_consolidated_financials": "not_publicly_disclosed"},
        "landscape_refs": ["dc_stargate_norway_narvik", "dc_nscale_monarch_west_virginia", "dc_nscale_verne_iceland", "dc_nscale_loughton_uk", "dc_start_campus_sines_portugal", "dc_nscale_ward_county_texas"],
        "financial_profile_ref": None,
        "sources": [
            "https://www.nscale.com/press-releases/stargate-norway-nscale-aker-openai",
            "https://www.nscale.com/press-releases/nscale-west-virginia-ai-factory",
            "https://www.nscale.com/press-releases/nscale-and-verne",
            "https://www.nscale.com/press-releases/nscale-microsoft-2025",
            "https://www.nscale.com/press-releases/nscale-start-campus",
        ],
    },
    {
        "id": "neocloud_crusoe",
        "company": "Crusoe",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["AI_data_center_developer", "AI_cloud_operator", "onsite_power_developer"],
        "physical_and_service_footprint": {"confirmed_campus": "Stargate_Abilene", "buildings": 8, "floor_area_sqft": 4000000},
        "power_disclosure": [
            {"value": 1.2, "unit": "GW", "site": "Abilene", "lifecycle": "design"},
            {"value": 42, "unit": "percent_of_total_capacity", "site": "Abilene", "as_of": "2026-06", "lifecycle": "delivered_share"},
        ],
        "gpu_disclosure": {"site_count": "undisclosed", "model": "NVIDIA_GB200", "portfolio_chip_claim": ">2000000", "boundary": "The chip claim covers Abilene plus a wider OpenAI/Oracle portfolio and is neither a GPU-only nor site-installed count."},
        "commercial_disclosure": {"audited_consolidated_financials": "not_publicly_disclosed", "Series_E_financing_usd_billion": ">1", "boundary": "Private funding is financing, not revenue."},
        "landscape_refs": ["dc_openai_stargate_abilene"],
        "financial_profile_ref": "company_crusoe",
        "sources": ["https://www.crusoe.ai/about/company", "https://www.oracle.com/data-centers/abilene/", "https://openai.com/index/stargate-advances-with-partnership-with-oracle/"],
    },
    {
        "id": "neocloud_lambda",
        "company": "Lambda",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["GPU_cloud", "dedicated_GPU_clusters", "AI_superclusters"],
        "physical_and_service_footprint": {"published_product_scales": ["instances_1_to_8_GPUs", "clusters_16_to_2000_plus_GPUs", "superclusters_4000_to_165000_plus_GPUs"], "boundary": "Product configuration ranges are not physical fleet inventory."},
        "power_disclosure": [],
        "gpu_disclosure": {"Microsoft_agreement": "tens_of_thousands_of_NVIDIA_GPUs_including_GB300_NVL72", "lifecycle": "multi_year_deployment_agreement_announced_2025_11_03", "boundary": "No exact delivered, active, owned or site-allocated count is disclosed."},
        "commercial_disclosure": {"audited_consolidated_financials": "not_publicly_disclosed", "Microsoft_agreement_value": "multibillion_USD", "boundary": "Agreement value is not recognized revenue."},
        "landscape_refs": ["dc_aligned_dfw04_plano_lambda"],
        "financial_profile_ref": None,
        "sources": ["https://lambda.ai/welcome/ai-cloud", "https://lambda.ai/blog/lambda-announces-multibillion-dollar-agreement-with-microsoft-to-deploy-ai-infrastructure-powered-by-tens-of-thousands-of-nvidia-gpus"],
    },
    {
        "id": "neocloud_nebius",
        "company": "Nebius",
        "roster": "primary_operator",
        "ownership_status": "public_NASDAQ_NBIS",
        "business_model": ["AI_cloud", "owned_AI_factory_developer", "dedicated_AI_clusters"],
        "physical_and_service_footprint": {"named_US_and_Europe_context": ["Kansas_City", "New_Jersey", "Iceland", "Pennsylvania"], "boundary": "Named locations mix operating deployments and owned/build-to-suit expansion."},
        "power_disclosure": [
            {"value": "up_to_300", "unit": "MW", "site": "New_Jersey", "lifecycle": "build_to_suit"},
            {"value": "800_to_1000", "unit": "MW", "as_of": "end_2026", "lifecycle": "connected_power_target"},
            {"value": ">5", "unit": "GW", "as_of": "end_2030", "lifecycle": "NVIDIA_system_enablement_target"},
            {"value": "up_to_1.2", "unit": "GW", "site": "Pennsylvania", "lifecycle": "secured_power_and_land"},
        ],
        "gpu_disclosure": {"current_exact_count": "undisclosed", "systems_target": "more_than_5GW_of_NVIDIA_systems_by_end_2030", "boundary": "A GW enablement target is not a physical GPU count or current active fleet."},
        "commercial_disclosure": {"Q1_2026_revenue_usd_million": 399.0, "Q1_2026_GAAP_operating_loss_usd_million": 128.0, "Q1_2026_adjusted_EBITDA_usd_million": 129.5, "Q1_2026_net_income_continuing_operations_usd_million": 621.2, "Q1_2026_investment_revaluation_gain_usd_million": 780.6, "Q1_2026_adjusted_net_loss_usd_million": 100.3, "Meta_order_framework_usd_billion_up_to": 27, "boundary": "Net income was dominated by an investment revaluation gain; Meta's up-to-$15B backstop is not the same as guaranteed backlog."},
        "landscape_refs": [],
        "financial_profile_ref": "company_nebius",
        "sources": ["https://www.sec.gov/Archives/edgar/data/1513845/000110465926059872/tm2614392d1_ex99-1.htm", "https://www.sec.gov/Archives/edgar/data/1513845/000110465926027886/tm268879d1_6k.htm", "https://nebius.com/newsroom/nvidia-and-nebius-partner-to-scale-full-stack-ai-cloud", "https://nebius.com/newsroom/nebius-accelerates-us-expansion-adding-up-to-300-mw-capacity-at-new-data-center-in-new-jersey"],
    },
    {
        "id": "neocloud_fluidstack",
        "company": "Fluidstack",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["AI_cloud", "custom_data_center_and_cluster_delivery", "GPU_infrastructure_manager"],
        "physical_and_service_footprint": {"named_programs": ["Iceland_and_Europe_exascale", "New_York_and_Texas_for_Anthropic", "France_1GW_supercomputer", "Barber_Lake_via_Cipher"]},
        "power_disclosure": [{"value": 1, "unit": "GW", "site": "France", "lifecycle": "commitment"}, {"value": 168, "unit": "MW_critical_IT", "site": "Cipher_Barber_Lake_phase_I", "lifecycle": "lease_delivery_expected_2026_09"}, {"value": 39, "unit": "MW_critical_IT", "site": "Cipher_Barber_Lake_phase_II", "lifecycle": "lease_delivery_expected_2027_01"}],
        "gpu_disclosure": {"company_claim": ">100000_GPUs_under_management", "customer_cluster_example": "2560_A100_or_H100_for_poolside", "boundary": "Under management is not owned inventory; the poolside cluster is a customer-specific historical deployment."},
        "commercial_disclosure": {"Anthropic_infrastructure_program_usd_billion": 50, "Barber_Lake_initial_contract_value_usd_billion": 3, "audited_consolidated_financials": "not_publicly_disclosed", "boundary": "Customer infrastructure commitments and lease contract value are not Fluidstack recognized revenue."},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://fluidstack.io/blog/fluidstack-to-deploy-energy-efficient-exascale-gpu-clusters-in-europe-in-collaboration-with-nvidia-borealis-data-center-and-dell-technologies", "https://fluidstack.io/blog/fluidstack-selected-by-anthropic-to-deliver-custom-data-centers-in-the-us", "https://fluidstack.io/blog/fluidstack-helped-poolside-deploy-2-500-gpus-within-48-hours", "https://investors.cipherdigital.com/news-releases/news-release-details/cipher-mining-signs-168-mw-10-year-ai-hosting-agreement/"],
    },
    {
        "id": "neocloud_voltage_park",
        "company": "Voltage_Park",
        "roster": "primary_operator",
        "ownership_status": "brand_merged_with_Lightning_AI_2026_01",
        "business_model": ["GPU_cloud", "dedicated_clusters"],
        "physical_and_service_footprint": {"company_claimed_data_centers": 6, "states": 4, "published_location_labels": ["Quincy_WA", "Puyallup_WA", "Salt_Lake_City_UT_site_1", "Salt_Lake_City_UT_site_2", "Fort_Worth_TX", "Allen_TX", "Sterling_VA"], "boundary": "The page says six data centers while its location labels resolve to seven entries; the inconsistency is preserved."},
        "power_disclosure": [],
        "gpu_disclosure": {"physical_GPU_count": 24000, "model": "NVIDIA_HGX_H100", "ownership_claim": "owns_hardware_and_software", "cluster_ranges": "64_to_4088_reservable_up_to_8000_plus"},
        "commercial_disclosure": {"long_term_capital_foundation_usd_billion": 1, "audited_consolidated_financials": "not_publicly_disclosed"},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://www.voltagepark.com/infrastructure", "https://www.voltagepark.com/blog/scaling-ai-in-2025-flexibility-speed", "https://www.voltagepark.com/about"],
    },
    {
        "id": "neocloud_tensorwave",
        "company": "TensorWave",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["AMD_GPU_cloud", "dedicated_GPU_clusters"],
        "physical_and_service_footprint": {"TECfusions_partnership": "1GW_secured_capacity", "boundary": "Secured partnership capacity is not current energized or utilized IT load."},
        "power_disclosure": [{"value": 1, "unit": "GW", "lifecycle": "secured_via_TECfusions_partnership"}],
        "gpu_disclosure": {"cluster_count": 8192, "model": "AMD_MI325X", "cooling": "direct_liquid", "latest_company_wording": "more_than_8000_built", "boundary": "The cluster is not assigned to the whole 1GW capacity scope."},
        "commercial_disclosure": {"Series_A_usd_million": 100, "total_funding_usd_million": ">500", "Series_B_2026_usd_million": 350, "Series_B_valuation_usd_billion": 1.55, "audited_consolidated_financials": "not_publicly_disclosed"},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://tensorwave.com/blog/tensorwave-secures-a-massive-1-gw-capacity-for-ai-powered-infrastructure", "https://tensorwave.com/blog/series-a", "https://tensorwave.com/blog/gtc-2026-the-ai-revolution-delivers-the-multi-gpu-multi-cloud-imperative", "https://tensorwave.com/about"],
    },
    {
        "id": "neocloud_together_ai",
        "company": "Together_AI",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["AI_native_cloud", "inference_platform", "dedicated_GPU_clusters"],
        "physical_and_service_footprint": {"capacity_partners": ["Hypertec", "independently_capitalized_new_investor_capacity"], "boundary": "Physical locations, ownership and current acceptance status are not reconciled publicly."},
        "power_disclosure": [{"value": 200, "unit": "MW", "as_of": "2025-02", "lifecycle": "secured"}, {"value": ">500", "unit": "MW", "as_of": "2026-07", "lifecycle": "future_compute_commitments_capitalized_independently"}],
        "gpu_disclosure": {"Hypertec_cluster": {"value": 36000, "model": "NVIDIA_GB200_NVL72", "lifecycle": "deployment_statement"}, "boundary": "The 36,000-GPU statement does not disclose current live count, owner, utilization or physical site roster."},
        "commercial_disclosure": {"Series_B_2025_usd_million": 305, "Series_C_2026_usd_million": 800, "audited_consolidated_financials": "not_publicly_disclosed", "boundary": "Equity funding and capacity commitments are not revenue."},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://www.together.ai/blog/together-ai-announcing-305m-series-b", "https://www.together.ai/blog/announcing-our-series-c", "https://www.together.ai/blog/together-instant-clusters-ga"],
    },
    {
        "id": "neocloud_vultr",
        "company": "Vultr",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["general_cloud", "GPU_cloud", "AI_superclusters"],
        "physical_and_service_footprint": {"cloud_regions_as_of_2026_05": 33, "Europe_regions": 9, "boundary": "A provider Region can contain multiple physical data centers and is not a building count."},
        "power_disclosure": [{"value": 50, "unit": "MW", "site": "5C_Springfield_Ohio", "lifecycle": "new_deployment_announced_2025_12"}],
        "gpu_disclosure": {"Ohio_expansion": {"value": ">24000", "model": "AMD_MI355X", "lifecycle": "additional_deployment"}, "other_platforms": ["NVIDIA_HGX_B200"], "boundary": "The Ohio announcement is not a company-wide live fleet count."},
        "commercial_disclosure": {"audited_consolidated_financials": "not_publicly_disclosed"},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://blogs.vultr.com/milan-cloud-data-center-region", "https://blogs.vultr.com/vultr-amd-ai-supercluster", "https://docs.vultr.com/platform/glossary"],
    },
    {
        "id": "neocloud_gmi_cloud",
        "company": "GMI_Cloud",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["GPU_cloud", "bare_metal_GPU_clusters", "inference_platform"],
        "physical_and_service_footprint": {"geographies": ["North_America", "Europe", "APAC"], "exact_site_roster": "undisclosed"},
        "power_disclosure": [],
        "gpu_disclosure": {"company_claim": "30000_plus_GPUs_deployed", "data_center_wording": "owned_data_centers", "models": ["H100", "H200", "B200", "GB200_NVL72", "GB300_NVL72"], "boundary": "Exact current count by model, address, power and utilization is undisclosed."},
        "commercial_disclosure": {"customers": "300_plus", "audited_consolidated_financials": "not_publicly_disclosed"},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://www.gmicloud.ai/en/company/about", "https://www.gmicloud.ai/en/gpus"],
    },
    {
        "id": "neocloud_runpod",
        "company": "RunPod",
        "roster": "primary_operator",
        "ownership_status": "private",
        "business_model": ["GPU_cloud_marketplace", "serverless_GPU", "dedicated_pods"],
        "physical_and_service_footprint": {"provider_regions": 31, "partner_data_center_model": True, "boundary": "RunPod orchestrates resources while physical storage is managed by global partner data centers; Region IDs are not owned-building counts."},
        "power_disclosure": [{"value": ">1", "unit": "MW", "site": "AP_IN_1", "lifecycle": "live_2026_04_20"}],
        "gpu_disclosure": {"models_offered": "30_plus", "examples": ["B300", "H200", "B200", "RTX_PRO_6000", "H100", "A100"], "AP_IN_1_focus": "H100_80GB", "current_owned_physical_count": "undisclosed"},
        "commercial_disclosure": {"audited_consolidated_financials": "not_publicly_disclosed"},
        "landscape_refs": [],
        "financial_profile_ref": None,
        "sources": ["https://www.runpod.io/product/cloud-gpus", "https://www.runpod.io/legal", "https://www.runpod.io/blog/new-runpod-datacenter-now-live-ap-in-1"],
    },
    {
        "id": "host_applied_digital",
        "company": "Applied_Digital",
        "roster": "linked_capacity_host",
        "ownership_status": "public_NASDAQ_APLD",
        "business_model": ["AI_HPC_data_center_developer", "powered_shell_and_cooling_owner", "colocation_lessor"],
        "physical_and_service_footprint": {"anchor_program": "Polaris_Forge_1", "anchor_tenant": "CoreWeave"},
        "power_disclosure": [{"value": 400, "unit": "MW_critical_IT", "site": "Polaris_Forge_1", "lifecycle": "CoreWeave_leased"}, {"value": 175, "unit": "MW", "site": "Polaris_Forge_1", "as_of": "2026-07-01", "lifecycle": "campus_live_company_claim"}, {"value": 50, "unit": "MW", "site": "Polaris_Forge_1", "as_of": "2025-11", "lifecycle": "CoreWeave_specific_RFS"}],
        "gpu_disclosure": {"tenant_inventory": "undisclosed", "boundary": "CoreWeave fleet counts cannot be assigned to the landlord campus."},
        "commercial_disclosure": {"Q3_FY2026_revenue_usd_million": 126.637, "Q3_FY2026_operating_loss_usd_million": 85.667, "Q3_FY2026_adjusted_EBITDA_usd_million": 44.1, "anticipated_CoreWeave_contract_revenue_usd_billion": "~11", "boundary": "Contract revenue is multi-year and not current revenue or profit."},
        "landscape_refs": ["dc_applied_digital_polaris_forge_1_coreweave"],
        "financial_profile_ref": "company_applied_digital",
        "sources": ["https://ir.applieddigital.com/news-events/press-releases/detail/148/applied-digital-reports-fiscal-third-quarter-2026-results", "https://ir.applieddigital.com/news-events/press-releases/detail/157/applied-digital-delivers-second-building-at-polaris-forge-1"],
    },
    {
        "id": "host_core_scientific",
        "company": "Core_Scientific",
        "roster": "linked_capacity_host",
        "ownership_status": "public_NASDAQ_CORZ",
        "business_model": ["high_density_colocation", "crypto_site_converter", "power_interconnection_owner"],
        "physical_and_service_footprint": {"CoreWeave_facilities": 6, "named_sites": 5},
        "power_disclosure": [{"value": "~590", "unit": "MW_net_critical_IT", "lifecycle": "CoreWeave_contracted"}, {"value": "~900", "unit": "MW_grid", "lifecycle": "secured"}, {"value": 243, "unit": "MW", "as_of": "2026-Q1", "lifecycle": "billed"}],
        "gpu_disclosure": {"tenant_inventory": "undisclosed", "boundary": "No CoreWeave site-level GPU allocation is public."},
        "commercial_disclosure": {"Q1_2026_revenue_usd_million": 115.244, "Q1_2026_colocation_revenue_usd_million": 77.539, "Q1_2026_operating_loss_usd_million": 310.422, "Q1_2026_adjusted_EBITDA_usd_million": 4.352, "contract_revenue_estimate_usd_billion": "~10", "boundary": "The quarter includes a $266.5M non-cash impairment; contract revenue is a multi-year estimate."},
        "landscape_refs": ["dc_core_scientific_coreweave_us_portfolio"],
        "financial_profile_ref": "company_core_scientific",
        "sources": ["https://investors.corescientific.com/news-events/press-releases/detail/136/core-scientific-announces-first-quarter-fiscal-year-2026-results", "https://investors.corescientific.com/sec-filings/all-sec-filings/content/0001193125-26-165121/d149019dex992.htm"],
    },
    {
        "id": "host_iren",
        "company": "IREN",
        "roster": "linked_capacity_host",
        "ownership_status": "public_NASDAQ_IREN",
        "business_model": ["vertically_integrated_AI_cloud", "data_center_developer", "legacy_Bitcoin_miner_transition"],
        "physical_and_service_footprint": {"sites_with_grid_or_equivalent_agreements": 7, "portfolio_power_capacity_mw": 4510, "geographies": ["Texas", "Oklahoma", "British_Columbia"], "boundary": "Portfolio power includes development rights and is not active AI IT load."},
        "power_disclosure": [{"value": 480, "unit": "MW", "as_of": "end_2026", "lifecycle": "AI_cloud_capacity_target"}, {"value": 1210, "unit": "MW", "as_of": "2027", "lifecycle": "AI_cloud_capacity_in_build_target"}, {"value": 5, "unit": "GW", "lifecycle": "secured_global_power_pipeline"}, {"value": 60, "unit": "MW", "site": "Childress", "lifecycle": "NVIDIA_contract_deployment_target_early_2027"}],
        "gpu_disclosure": {"as_of_2026_03_31": "approximately_150000_installed_or_on_order", "new_B300_purchase": "over_50000", "delivery": "phased_H2_2026", "NVIDIA_investment_right_delivery_condition": "up_to_600000_GPUs", "boundary": "Installed-or-on-order is not installed active inventory; 600,000 is a vesting ceiling, not an order or fleet count."},
        "commercial_disclosure": {"Q3_FY2026_revenue_usd_million": 144.8, "Q3_FY2026_net_loss_usd_million": 247.8, "Q3_FY2026_adjusted_EBITDA_usd_million": 59.5, "cash_usd_million": 2213.3, "NVIDIA_contract_value_usd_billion": 3.4, "AI_cloud_ARR_under_contract_usd_billion": 3.1, "boundary": "ARR and contract value are not quarterly GAAP revenue; the 150,000-GPU capacity is not all delivered."},
        "landscape_refs": [],
        "financial_profile_ref": "company_iren",
        "sources": ["https://www.sec.gov/Archives/edgar/data/1878848/000187884826000026/iren-20260331.htm", "https://www.sec.gov/Archives/edgar/data/1878848/000114036126007905/ny20064909x3_ex99-1.htm", "https://www.sec.gov/Archives/edgar/data/1878848/000187884826000025/irenreportsq3fy26results.htm"],
    },
    {
        "id": "host_galaxy_digital",
        "company": "Galaxy_Digital",
        "roster": "linked_capacity_host",
        "ownership_status": "public_NASDAQ_GLXY",
        "business_model": ["powered_land_and_interconnection_developer", "data_center_lessor", "digital_assets_platform"],
        "physical_and_service_footprint": {"anchor_campus": "Helios", "anchor_tenant": "CoreWeave"},
        "power_disclosure": [{"value": 133, "unit": "MW_critical_IT", "site": "Helios_phase_I", "as_of": "2026-07-06", "lifecycle": "delivered"}, {"value": 526, "unit": "MW_critical_IT", "site": "Helios", "lifecycle": "CoreWeave_contracted"}, {"value": 800, "unit": "MW_gross", "site": "Helios", "lifecycle": "CoreWeave_contracted"}, {"value": ">1.6", "unit": "GW_gross", "site": "Helios", "lifecycle": "approved_campus_power"}],
        "gpu_disclosure": {"tenant_inventory": "undisclosed", "vendor_context": "NVIDIA", "boundary": "CoreWeave fleet disclosures cannot be assigned to Helios."},
        "commercial_disclosure": {"Q1_2026_revenue_usd_million": 10041.4, "Q1_2026_operating_loss_usd_million_derived": 235.3, "Q1_2026_net_loss_usd_million": 216.3, "anticipated_average_annual_Helios_revenue_usd_billion": ">1", "boundary": "Galaxy's gross digital-asset presentation is not comparable with cloud revenue; Helios economics are projections."},
        "landscape_refs": ["dc_galaxy_helios_dickens_county"],
        "financial_profile_ref": "company_galaxy_digital",
        "sources": ["https://www.sec.gov/Archives/edgar/data/1859392/000185939226000016/glxy-20251231.htm", "https://www.galaxy.com/newsroom/galaxy-completes-phase-i-of-its-helios-data-center-campus"],
    },
    {
        "id": "host_cipher_digital",
        "company": "Cipher_Digital",
        "roster": "linked_capacity_host",
        "ownership_status": "public_NASDAQ_CIFR",
        "business_model": ["data_center_developer", "HPC_host", "legacy_Bitcoin_miner_transition"],
        "physical_and_service_footprint": {"Fluidstack_site": "Barber_Lake", "other_transition_sites": ["Black_Pearl", "hyperscaler_site_undisclosed"], "name_change": "Cipher_Mining_to_Cipher_Digital_2026_Q1"},
        "power_disclosure": [{"value": 168, "unit": "MW_critical_IT", "site": "Barber_Lake_phase_I", "lifecycle": "Fluidstack_leased_delivery_expected_2026_09"}, {"value": 39, "unit": "MW_critical_IT", "site": "Barber_Lake_phase_II", "lifecycle": "additional_Fluidstack_leased_delivery_expected_2027_01"}, {"value": 244, "unit": "MW_gross", "site": "Barber_Lake_phase_I", "lifecycle": "maximum_supporting_capacity"}, {"value": "~2.4", "unit": "GW", "as_of": "2025-09", "lifecycle": "HPC_pipeline_excluding_contracted_Fluidstack_MW"}],
        "gpu_disclosure": {"count_and_models": "undisclosed", "ownership_boundary": "The agreement allows Google-owned property in the tenant space; landlord, tenant and end-customer equipment ownership must remain separate."},
        "commercial_disclosure": {"Q1_2026_revenue_usd_million": 34.838, "revenue_scope": "Bitcoin_mining", "Q1_2026_operating_loss_usd_million": 114.569, "Q1_2026_net_loss_usd_million": 114.316, "Q1_2026_adjusted_EBITDA_loss_usd_million": 48.222, "cash_usd_million": 715.203, "purchases_of_property_and_equipment_usd_million": 553.990, "initial_Fluidstack_contract_value_usd_billion": "~3", "Google_backstop_usd_billion": 1.4, "boundary": "Q1 revenue was still Bitcoin mining; future contracted lease value is not current HPC revenue."},
        "landscape_refs": [],
        "financial_profile_ref": "company_cipher_digital",
        "sources": ["https://www.sec.gov/Archives/edgar/data/1819989/000181998926000028/cifr-20260331.htm", "https://investors.cipherdigital.com/news-releases/news-release-details/cipher-mining-signs-168-mw-10-year-ai-hosting-agreement/", "https://investors.cipherdigital.com/static-files/75bc38da-4315-46c6-85cc-f001ae925659"],
    },
]


COMMON_GAPS = [
    "current site-level active, accepted, utilized and billed IT load",
    "complete physical building and ownership or lease crosswalk",
    "current GPU inventory by model, owner, delivery state and site",
    "rack count, density, fabric, optics and storage bill of materials",
    "grid feeds, substations, transformers, switchgear, UPS and backup generation",
    "cooling topology, equipment OEMs, measured PUE, WUE and absolute water",
    "site revenue, utilization, operating profit and return on invested capital",
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_records(accessed_on: str) -> list[dict]:
    assert len(RECORDS) == 17
    assert Counter(row["roster"] for row in RECORDS) == {"primary_operator": 12, "linked_capacity_host": 5}
    assert len({row["id"] for row in RECORDS}) == len(RECORDS)
    assert len({row["company"] for row in RECORDS}) == len(RECORDS)
    output = []
    for position, source in enumerate(RECORDS, start=1):
        row = dict(source)
        row["source_order"] = position
        row["accessed_on"] = accessed_on
        row["object_type"] = "NeocloudDisclosureProfile"
        row["scope_boundaries"] = {
            "power": "Do not sum active, contracted, secured, under-construction, target and pipeline power.",
            "accelerators": "Do not sum installed, ordered, managed, customer-dedicated, performance-equivalent and target counts.",
            "locations": "Do not convert provider Regions, AZs, partner sites or program labels into one-building records.",
            "economics": "Do not convert funding, contract value, ARR, backlog or projected revenue into recognized revenue or profit.",
        }
        row["common_undisclosed_or_unreconciled"] = COMMON_GAPS
        row["source_snapshot_sha256"] = canonical_hash(source)
        output.append(row)
    return output


def build_summary(records: list[dict], accessed_on: str) -> dict:
    ownership = Counter("public" if row["ownership_status"].startswith("public_") else "private_or_brand" for row in records)
    return {
        "registry": "Neocloud and linked-capacity-host disclosure registry",
        "accessed_on": accessed_on,
        "records": len(records),
        "primary_operator_records": sum(row["roster"] == "primary_operator" for row in records),
        "linked_capacity_host_records": sum(row["roster"] == "linked_capacity_host" for row in records),
        "public_company_records": ownership["public"],
        "private_or_brand_records": ownership["private_or_brand"],
        "public_financial_profile_refs": sorted(row["financial_profile_ref"] for row in records if row["financial_profile_ref"]),
        "no_companywide_power_sum": True,
        "no_companywide_or_cross_company_GPU_sum": True,
        "critical_reconciliation_examples": [
            "IREN 150,000 is installed or on order, not 150,000 active GPUs.",
            "Fluidstack over 100,000 is under management, not owned inventory.",
            "Together AI over 500 MW is future independently capitalized compute commitment, not active load.",
            "Cipher Barber Lake separates 168 MW phase I, 39 MW phase II and 244 MW phase-I gross support capacity.",
            "Vultr and RunPod Region counts are provider service scopes, not owned physical building counts.",
        ],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    summary = build_summary(records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "neocloud_disclosure_registry.jsonl"
    summary_path = args.output_dir / "neocloud_disclosure_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
