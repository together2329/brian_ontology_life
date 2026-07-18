#!/usr/bin/env python3
"""Build an atomic, non-additive accelerator disclosure ledger.

Every row points to one reviewed local evidence path.  Physical inventory,
historical milestones, delivery flow, managed hardware, compute equivalents,
future targets, design accommodation and architecture maxima remain distinct.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


def claim(
    claim_id: str,
    source_kind: str,
    source_ref: str,
    evidence_path: str,
    evidence_value: object,
    normalized_value: int,
    qualifier: str,
    unit: str,
    model: str,
    scope: str,
    lifecycle: str,
    physicality: str,
    ownership: str,
    overlap_group: str,
    boundary: str,
    multiplicity: int | None = None,
) -> dict:
    row = {
        "claim_id": claim_id,
        "source_kind": source_kind,
        "source_ref": source_ref,
        "evidence_path": evidence_path,
        "evidence_value": evidence_value,
        "normalized_quantity": {
            "value": normalized_value,
            "qualifier": qualifier,
            "unit": unit,
        },
        "model": model,
        "scope": scope,
        "lifecycle": lifecycle,
        "physicality": physicality,
        "ownership": ownership,
        "overlap_group": overlap_group,
        "boundary": boundary,
    }
    if multiplicity is not None:
        row["multiplicity"] = multiplicity
    return row


CLAIMS = [
    claim("data4_par03_design_200k", "landscape", "dc_data4_paris_saclay_cluster", "capacity_and_accelerators.PAR03_design.GPU_accommodation_nearly", 200000, 200000, "nearly", "GPU_accommodation", "undisclosed_GPU", "PAR03_design", "design_accommodation", "design_capacity_not_inventory", "undisclosed", "data4_par03", "A design ceiling is not an order, installed fleet, live inventory or utilized capacity."),
    claim("coresite_ch2_stn_1536_b200", "landscape", "dc_coresite_ch2_chicago", "racks_and_accelerators.STN_GPU_One_as_published_2025_10_09.accelerator_count", 1536, 1536, "exact", "physical_GPU", "NVIDIA_B200", "STN_GPU_One_at_CH2", "named_customer_deployment", "physical_accelerator_count", "STN_or_customer_not_CoreSite", "coresite_ch2_stn", "The named customer deployment is not CoreSite-owned inventory or the site's total GPU count."),
    claim("aws_accelerated_chips_landed_2_1m", "landscape", "dc_aws_global_infrastructure_portfolio", "accelerators.current_companywide_delivery_signal.accelerated_chips_landed_last_12_months_more_than", 2100000, 2100000, "more_than", "accelerated_chip", "mixed_custom_and_third_party", "AWS_companywide_last_12_months", "delivery_flow", "mixed_chip_flow_not_current_inventory", "mixed_or_undisclosed", "aws_accelerator_flow", "A twelve-month delivery flow mixes custom and third-party chips and is not current installed inventory."),
    claim("aws_nvidia_commitment_1m", "landscape", "dc_aws_global_infrastructure_portfolio", "accelerators.future_commitments_not_current_inventory.NVIDIA_GPUs_starting_2026_more_than", 1000000, 1000000, "more_than", "physical_GPU_commitment", "NVIDIA_model_undisclosed", "AWS_starting_2026", "future_commitment", "future_physical_quantity", "undisclosed", "aws_nvidia_commitment", "A future commitment is not delivered, installed, active or site-allocated inventory."),
    claim("google_virgo_tpu8t_134k", "landscape", "dc_google_global_data_center_portfolio", "accelerators.Virgo_single_fabric_TPU_8t_chips_supported", 134000, 134000, "up_to_supported", "TPU_chip", "Google_TPU_8t", "Virgo_single_fabric", "architecture_capacity", "logical_architecture_capacity", "Google", "google_architecture", "Supported fabric scale may span data centers and is not proof of installed chips at one site."),
    claim("google_logical_tpu_cluster_1m", "landscape", "dc_google_global_data_center_portfolio", "accelerators.logical_training_cluster_TPU_chips_supported_more_than", 1000000, 1000000, "more_than_supported", "TPU_chip", "Google_TPU_generation_mixed_or_undisclosed", "logical_training_cluster", "architecture_capacity", "logical_architecture_capacity", "Google", "google_architecture", "Logical cluster capacity is not a physical campus or live global inventory."),
    claim("google_vera_rubin_supported_960k", "landscape", "dc_google_global_data_center_portfolio", "accelerators.NVIDIA_Vera_Rubin_GPUs_supported_up_to", 960000, 960000, "up_to_supported", "GPU", "NVIDIA_Vera_Rubin", "Google_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "google_architecture", "Supported maximum is not installed, active or site-allocated inventory."),
    claim("meta_late_2023_h100_clusters_24k_each", "landscape", "dc_meta_global_data_center_portfolio", "accelerators.disclosed_cluster_milestones.late_2023_H100_clusters.H100_GPUs_each", 24000, 24000, "exact_each", "physical_GPU", "NVIDIA_H100", "two_late_2023_clusters", "historical_build_milestone", "physical_accelerator_count", "Meta", "meta_cluster_milestones", "Two historical cluster milestones cannot be multiplied and added to a current fleet without overlap, retirement and site evidence.", 2),
    claim("meta_later_h100_cluster_129k", "landscape", "dc_meta_global_data_center_portfolio", "accelerators.disclosed_cluster_milestones.later_H100_cluster.H100_GPUs", 129000, 129000, "exact", "physical_GPU", "NVIDIA_H100", "five_emptied_production_data_centers", "historical_build_milestone", "physical_accelerator_count", "Meta", "meta_cluster_milestones", "The milestone is not a current global count and its relation to earlier clusters is unresolved."),
    claim("meta_catalina_pod_72_blackwell", "landscape", "dc_meta_global_data_center_portfolio", "accelerators.Blackwell_Catalina_pod_example.NVIDIA_Blackwell_GPUs", 72, 72, "exact_example", "physical_GPU", "NVIDIA_Blackwell", "Catalina_pod_example", "reference_deployment_example", "physical_accelerator_count", "Meta", "meta_catalina_example", "One pod example is not the fleet quantity or a site-wide inventory."),
    claim("aws_rainier_trainium2_500k", "landscape", "dc_aws_project_rainier", "accelerators.count_as_of_2026_Q4_release_more_than", 500000, 500000, "more_than", "physical_accelerator_chip", "AWS_Trainium2", "Project_Rainier", "reported_deployment", "physical_accelerator_count", "AWS_or_Anthropic_service_boundary", "aws_rainier", "The source count is retained at Project Rainier scope and is not a GPU count."),
    claim("aws_trainium2_landed_1_4m", "landscape", "dc_aws_project_rainier", "accelerators.broader_AWS_trainium2_landed", 1400000, 1400000, "exact_reported_flow", "accelerator_chip", "AWS_Trainium2", "broader_AWS", "delivery_flow", "chip_flow_not_site_inventory", "AWS", "aws_trainium2_broader", "The broader landed count must not be assigned entirely to Rainier or treated as same-date active inventory."),
    claim("anthropic_trainium2_use_1m", "landscape", "dc_aws_project_rainier", "accelerators.broader_anthropic_trainium2_use", "more_than_1000000", 1000000, "more_than", "accelerator_chip", "AWS_Trainium2", "broader_Anthropic_use", "reported_use", "physical_accelerator_count_scope_uncertain", "AWS_or_Anthropic_service_boundary", "aws_trainium2_broader", "The broader Anthropic-use count overlaps AWS deployment scopes and is not fully assignable to Rainier."),
    claim("nscale_narvik_100k_target", "landscape", "dc_stargate_norway_narvik", "accelerators.initial_target.NVIDIA_GPU_count", 100000, 100000, "exact_target", "physical_GPU", "NVIDIA_model_undisclosed", "Narvik", "end_2026_target", "future_physical_quantity", "Nscale_or_customer_boundary", "nscale_microsoft_deployments", "A target is not delivered, installed, active or utilized inventory."),
    claim("humain_nvidia_first_phase_18k", "landscape", "dc_humain_saudi_ai_factory_portfolio", "portfolio_scale.NVIDIA_collaboration.first_phase_physical_GPU_count", 18000, 18000, "exact_plan", "physical_GPU", "NVIDIA_GB300_Grace_Blackwell", "HUMAIN_NVIDIA_first_phase", "future_first_phase", "future_physical_quantity", "HUMAIN_or_partner_boundary", "humain_nvidia_program", "The first-phase plan is not current delivered, energized or utilized inventory and lacks site allocation."),
    claim("xai_colossus_h100_equivalent_1m", "landscape", "dc_xai_colossus_2_southaven", "accelerators.Colossus_I_and_II_aggregate_H100_GPU_equivalents_end_2025_more_than", 1000000, 1000000, "more_than", "H100_equivalent", "mixed_accelerators", "Colossus_I_and_II_aggregate", "end_2025_compute_equivalence", "compute_equivalent_not_physical_count", "SpaceXAI", "xai_memphis_program", "Compute equivalence is not a count of physical H100s or a Colossus 2 site inventory."),
    claim("xai_memphis_physical_target_1m", "landscape", "dc_xai_colossus_2_southaven", "accelerators.Memphis_program_physical_GPU_target_by_2026", 1000000, 1000000, "exact_target", "physical_GPU", "model_mix_undisclosed", "Memphis_program", "2026_target", "future_physical_quantity", "SpaceXAI", "xai_memphis_program", "A program target is not a verified Colossus 2 physical inventory."),
    claim("nscale_loughton_23040", "landscape", "dc_nscale_loughton_uk", "accelerators.initial_physical_GPU_count", 23040, 23040, "exact_target", "physical_GPU", "NVIDIA_GB300", "Loughton_initial", "Q1_2027_target", "future_physical_quantity", "Nscale_or_Microsoft_boundary", "nscale_microsoft_deployments", "Target delivery is not current installed, active or utilized inventory."),
    claim("nscale_sines_first_12600", "landscape", "dc_start_campus_sines_portugal", "accelerators.first_building.physical_GPU_count_approximate", 12600, 12600, "approximate_target", "physical_GPU", "NVIDIA_GB300_Blackwell_Ultra", "Sines_first_building", "Q1_2026_service_target", "future_or_unverified_physical_quantity", "Nscale_or_Microsoft_boundary", "nscale_microsoft_deployments", "The service target does not prove the current live count at the review date."),
    claim("nscale_sines_second_66k", "landscape", "dc_start_campus_sines_portugal", "accelerators.second_building.physical_GPU_count_more_than", 66000, 66000, "more_than_target", "physical_GPU", "NVIDIA_Vera_Rubin", "Sines_second_building", "late_2027_start_target", "future_physical_quantity", "Nscale_or_Microsoft_boundary", "nscale_microsoft_deployments", "A separate future building deployment is not current campus inventory."),
    claim("nscale_ward_county_104k", "landscape", "dc_nscale_ward_county_texas", "accelerators.initial_physical_GPU_count_approximate", 104000, 104000, "approximate_target", "physical_GPU", "NVIDIA_GB300", "Ward_County_initial", "Q3_2026_phased_delivery_target", "future_physical_quantity", "Nscale_or_Microsoft_boundary", "nscale_microsoft_deployments", "Phased delivery is not same-date installed, active or utilized inventory."),
    claim("coreweave_2024_fleet_250k", "landscape", "dc_coreweave_global_fleet", "accelerators.historical_disclosed_inventory.2024_12_31.physical_GPU_count_more_than", 250000, 250000, "more_than", "physical_GPU", "majority_NVIDIA_Hopper", "CoreWeave_global_fleet", "historical_2024_12_31", "physical_accelerator_count", "CoreWeave", "coreweave_fleet", "The historical count is not a current fleet count or a per-campus allocation."),
    claim("coreweave_dallas_8192_h100", "landscape", "dc_coreweave_dallas_graph500_cluster", "accelerators.benchmark_cluster_physical_GPU_count", 8192, 8192, "exact", "physical_GPU", "NVIDIA_H100", "Dallas_Graph500_cluster", "benchmark_deployment", "physical_accelerator_count", "CoreWeave", "coreweave_dallas", "The benchmark cluster is a confirmed subset, not the facility's total inventory."),
    claim("firmus_dayone_batam_170k", "landscape", "dc_firmus_dayone_batam_dsx", "accelerators_and_compute.NVIDIA_accelerators_up_to", 170000, 170000, "up_to", "physical_accelerator", "Grace_Blackwell_Vera_Rubin_or_Vera", "Batam_DSX_program", "2027_2028_future_ceiling", "future_physical_quantity", "Firmus_customer_or_NVIDIA_financing_boundary", "firmus_dayone_batam", "The ceiling is not an order, delivery, installed fleet or live service count."),
    claim("oracle_b200_max_131072", "landscape", "dc_oracle_oci_global_region_portfolio", "accelerators.published_OCI_Supercluster_architecture_maxima_not_installed_fleet.NVIDIA_B200_GPUs", 131072, 131072, "up_to_supported", "GPU", "NVIDIA_B200", "OCI_Supercluster_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "oracle_supercluster_maxima", "Published maximum configuration is not installed inventory or a named-site count."),
    claim("oracle_gb200_b200_max_131072", "landscape", "dc_oracle_oci_global_region_portfolio", "accelerators.published_OCI_Supercluster_architecture_maxima_not_installed_fleet.NVIDIA_B200_GPUs_in_GB200_superchips", 131072, 131072, "up_to_supported", "GPU", "NVIDIA_B200_in_GB200_superchips", "OCI_Supercluster_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "oracle_supercluster_maxima", "This alternative maximum configuration overlaps other Oracle architecture maxima and is not inventory."),
    claim("oracle_h200_max_65536", "landscape", "dc_oracle_oci_global_region_portfolio", "accelerators.published_OCI_Supercluster_architecture_maxima_not_installed_fleet.NVIDIA_H200_GPUs", 65536, 65536, "up_to_supported", "GPU", "NVIDIA_H200", "OCI_Supercluster_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "oracle_supercluster_maxima", "Published maximum configuration is not installed inventory or a named-site count."),
    claim("oracle_h100_max_16384", "landscape", "dc_oracle_oci_global_region_portfolio", "accelerators.published_OCI_Supercluster_architecture_maxima_not_installed_fleet.NVIDIA_H100_GPUs", 16384, 16384, "up_to_supported", "GPU", "NVIDIA_H100", "OCI_Supercluster_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "oracle_supercluster_maxima", "Published maximum configuration is not installed inventory or a named-site count."),
    claim("oracle_a100_max_32768", "landscape", "dc_oracle_oci_global_region_portfolio", "accelerators.published_OCI_Supercluster_architecture_maxima_not_installed_fleet.NVIDIA_A100_GPUs", 32768, 32768, "up_to_supported", "GPU", "NVIDIA_A100", "OCI_Supercluster_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "oracle_supercluster_maxima", "Published maximum configuration is not installed inventory or a named-site count."),
    claim("oracle_mi300x_max_16384", "landscape", "dc_oracle_oci_global_region_portfolio", "accelerators.published_OCI_Supercluster_architecture_maxima_not_installed_fleet.AMD_MI300X_GPUs", 16384, 16384, "up_to_supported", "GPU", "AMD_MI300X", "OCI_Supercluster_architecture", "architecture_capacity", "logical_architecture_capacity", "undisclosed", "oracle_supercluster_maxima", "Published maximum configuration is not installed inventory or a named-site count."),
    claim("china_telecom_lingang_10k", "landscape", "dc_china_telecom_shanghai_lingang_intelligent_computing_center", "accelerators.operating_cluster.accelerator_cards_approximate", 10000, 10000, "approximate", "accelerator_card", "domestic_model_mix_undisclosed", "Shanghai_Lingang_operating_cluster", "operating_cluster", "physical_accelerator_count", "China_Telecom_or_service_boundary", "china_telecom_lingang", "Approximate card count lacks exact model mix, ownership, utilization and rack allocation."),
    claim("china_mobile_hohhot_20k", "landscape", "dc_china_mobile_hohhot_intelligent_computing_center", "accelerators.AI_accelerator_cards_approximate", 20000, 20000, "approximate", "accelerator_card", "model_mix_undisclosed", "China_Mobile_Hohhot", "operating_cluster", "physical_accelerator_count", "China_Mobile_or_service_boundary", "china_mobile_hohhot", "Approximate card count lacks exact model mix, ownership, utilization and rack allocation."),
    claim("china_mobile_harbin_18k", "landscape", "dc_china_mobile_harbin_intelligent_computing_center", "accelerators.AI_accelerator_cards", 18000, 18000, "exact_reported", "accelerator_card", "domestic_model_mix_undisclosed", "China_Mobile_Harbin", "operating_cluster", "physical_accelerator_count", "China_Mobile_or_service_boundary", "china_mobile_harbin", "Reported card count lacks exact model mix, ownership, utilization and rack allocation."),
    claim("yotta_nm1_live_9216", "landscape", "dc_yotta_india_portfolio", "accelerator_lifecycle_ledger.latest_site_specific_live_inventory_2026_06_23.total_derived", 9216, 9216, "derived_from_exact_models", "physical_GPU", "8192_H100_plus_1024_L40S", "Yotta_NM1", "explicitly_live_2026_06_23", "physical_accelerator_count", "Yotta_or_contract_boundary", "yotta_inventory", "This newest site-specific live count is not necessarily the full portfolio inventory."),
    claim("yotta_portfolio_live_over_10k", "landscape", "dc_yotta_india_portfolio", "accelerator_lifecycle_ledger.portfolio_disclosures_that_do_not_fully_reconcile.3.NVIDIA_GPUs_live_in_production_more_than", 10000, 10000, "more_than", "physical_GPU", "model_mix_undisclosed", "Yotta_portfolio", "live_in_production_2026_02_18", "physical_accelerator_count", "Yotta_or_contract_boundary", "yotta_inventory", "The portfolio headline and later site-specific count do not fully reconcile and must not be added."),
    claim("yotta_b300_plan_20736", "landscape", "dc_yotta_india_portfolio", "accelerator_lifecycle_ledger.portfolio_disclosures_that_do_not_fully_reconcile.5.planned_B300_GPUs", 20736, 20736, "exact_plan", "physical_GPU", "NVIDIA_B300", "Yotta_Gorilla_framework", "delivery_by_2026_09_30", "future_physical_quantity", "Yotta_or_Gorilla_boundary", "yotta_future_plans", "This appears to be the February tranche and is not additive to the later expanded plan."),
    claim("yotta_d2_b300_plan_30k", "landscape", "dc_yotta_india_portfolio", "accelerator_lifecycle_ledger.portfolio_disclosures_that_do_not_fully_reconcile.6.D2_planned_B300_Ultra_GPUs", 30000, 30000, "exact_plan", "physical_GPU", "NVIDIA_B300_Ultra", "Yotta_D2", "FY2027_FY2028_target", "future_physical_quantity", "Yotta_or_partner_boundary", "yotta_future_plans", "The later plan supersedes or expands earlier disclosures and is not current live inventory."),
    claim("yotta_nm2_36k_plan", "landscape", "dc_yotta_india_portfolio", "accelerator_lifecycle_ledger.portfolio_disclosures_that_do_not_fully_reconcile.6.NM2_planned_GB300_or_Vera_Rubin_GPUs", 36000, 36000, "exact_plan", "physical_GPU", "NVIDIA_GB300_or_Vera_Rubin", "Yotta_NM2", "FY2027_FY2028_target", "future_physical_quantity", "Yotta_or_partner_boundary", "yotta_future_plans", "The model mix and delivery state remain unresolved; this is not current live inventory."),
    claim("du_dso_supported_4k", "landscape", "dc_du_dubai_silicon_oasis_dxb2", "accelerator_ledger.annual_report_2025.supported_GPU_count", 4000, 4000, "exact_supported", "GPU", "NVIDIA_model_undisclosed", "du_DSO_5_1MW_facility_scope", "2025_supported_deployment", "supported_count_scope_not_current_inventory", "du_AIHostingHub_or_customer_boundary", "du_dso", "Supported GPU count is not assumed to be the later B300 cluster or current total inventory."),
    claim("voltage_park_24k_h100", "neocloud", "neocloud_voltage_park", "gpu_disclosure.physical_GPU_count", 24000, 24000, "exact_reported", "physical_GPU", "NVIDIA_HGX_H100", "Voltage_Park_company_fleet", "current_company_claim", "physical_accelerator_count", "Voltage_Park", "voltage_park", "The company owns the hardware, but exact site allocation and utilization remain incomplete."),
    claim("tensorwave_8192_mi325x", "neocloud", "neocloud_tensorwave", "gpu_disclosure.cluster_count", 8192, 8192, "exact_cluster", "physical_GPU", "AMD_MI325X", "TensorWave_cluster", "built_cluster", "physical_accelerator_count", "TensorWave_or_financing_boundary", "tensorwave", "The cluster is not the inventory of the wider 1 GW capacity scope."),
    claim("together_hypertec_36k_gb200", "neocloud", "neocloud_together_ai", "gpu_disclosure.Hypertec_cluster.value", 36000, 36000, "exact_deployment_statement", "physical_GPU", "NVIDIA_GB200_NVL72", "Together_Hypertec_cluster", "deployment_statement", "physical_accelerator_count_scope_uncertain", "owner_undisclosed", "together_hypertec", "The statement does not prove current live count, owner, utilization or physical site roster."),
    claim("vultr_ohio_mi355x_24k", "neocloud", "neocloud_vultr", "gpu_disclosure.Ohio_expansion.value", ">24000", 24000, "more_than", "physical_GPU", "AMD_MI355X", "Vultr_Ohio_expansion", "additional_deployment", "physical_accelerator_count_scope_uncertain", "Vultr_or_financing_boundary", "vultr_ohio", "The announcement is not a company-wide live fleet count."),
    claim("gmi_cloud_deployed_30k", "neocloud", "neocloud_gmi_cloud", "gpu_disclosure.company_claim", "30000_plus_GPUs_deployed", 30000, "more_than_or_equal", "physical_GPU", "mixed_NVIDIA_models", "GMI_Cloud_company_claim", "deployed_company_claim", "physical_accelerator_count_scope_uncertain", "GMI_Cloud", "gmi_cloud", "Exact current model count, address, power and utilization are undisclosed."),
    claim("fluidstack_managed_100k", "neocloud", "neocloud_fluidstack", "gpu_disclosure.company_claim", ">100000_GPUs_under_management", 100000, "more_than", "GPU_under_management", "mixed_or_undisclosed", "Fluidstack_company_claim", "current_management_scope", "managed_hardware_not_owned_inventory", "customer_or_host_owned", "fluidstack_managed", "Under management is not owned inventory and may span customers and hosts."),
    claim("iren_installed_or_ordered_150k", "neocloud", "host_iren", "gpu_disclosure.as_of_2026_03_31", "approximately_150000_installed_or_on_order", 150000, "approximately", "physical_GPU", "mixed_NVIDIA_models", "IREN_company_scope", "installed_or_on_order_2026_03_31", "mixed_installed_and_future_quantity", "IREN_or_financing_boundary", "iren_gpu_program", "Installed-or-on-order cannot be read as installed, active or site-allocated inventory."),
    claim("iren_nvidia_right_600k", "neocloud", "host_iren", "gpu_disclosure.NVIDIA_investment_right_delivery_condition", "up_to_600000_GPUs", 600000, "up_to", "physical_GPU_delivery_condition", "NVIDIA_model_mix_undisclosed", "IREN_NVIDIA_investment_right", "future_vesting_ceiling", "future_option_ceiling_not_order", "IREN_or_NVIDIA_boundary", "iren_gpu_program", "The vesting ceiling is not an order, delivered fleet or current inventory."),
    claim("ark_longcross_nebius_4k_blackwell_ultra", "landscape", "dc_ark_data_centres_uk_europe_portfolio", "accelerators.Longcross_Nebius.initial_announced_GPU_count", 4000, 4000, "exact_initial_announced_deployment", "physical_GPU", "NVIDIA_Blackwell_Ultra", "Nebius_at_Ark_Longcross", "launched_2025_11_after_initial_announcement", "physical_accelerator_count", "Nebius_customer_not_Ark", "ark_longcross_nebius", "The later launch confirms the Blackwell Ultra cluster, but the 4,000 figure remains the initial deployment scope and is not Ark-owned or a current portfolio total."),
]


GLOBAL_CONTRACT = {
    "unit": "GPU, TPU, accelerator card, accelerated chip, H100-equivalent and supported architecture are different units.",
    "lifecycle": "Committed, ordered, landed, installed, active, utilized and retired are separate states.",
    "physicality": "Architecture maxima, design accommodation and compute equivalents are not physical inventory.",
    "ownership": "Operator, tenant, customer, financier, host and service-manager ownership remain separate.",
    "additivity": "Every row is non-additive by default; overlap must be disproved before any total is calculated.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


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


def value_at_path(row: object, path: str) -> object:
    value = row
    for component in path.split("."):
        if isinstance(value, list):
            value = value[int(component)]
        else:
            value = value[component]
    return value


def load_landscape(path: Path) -> dict[str, dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {row["id"]: row for row in document["campus_profiles"]}


def load_jsonl(path: Path) -> dict[str, dict]:
    return {row["id"]: row for row in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())}


def build_records(landscape_path: Path, neocloud_path: Path, accessed_on: str) -> list[dict]:
    indexes = {
        "landscape": load_landscape(landscape_path),
        "neocloud": load_jsonl(neocloud_path),
    }
    assert len(CLAIMS) == 48
    assert len({row["claim_id"] for row in CLAIMS}) == len(CLAIMS)
    records = []
    for position, source in enumerate(CLAIMS, start=1):
        evidence = indexes[source["source_kind"]][source["source_ref"]]
        actual = value_at_path(evidence, source["evidence_path"])
        assert actual == source["evidence_value"], (source["claim_id"], actual, source["evidence_value"])
        urls = collect_urls(evidence.get("sources", []))
        assert urls, source["claim_id"]
        records.append({
            "id": f"accelerator_claim_{source['claim_id']}",
            "object_type": "AcceleratorDisclosureClaim",
            "source_order": position,
            **source,
            "official_evidence_urls": urls,
            "official_evidence_url_count": len(urls),
            "source_snapshot_sha256": canonical_hash(evidence),
            "comparison_contract": GLOBAL_CONTRACT,
            "included_in_cross_company_total": False,
            "accessed_on": accessed_on,
        })
    return records


def build_summary(records: list[dict], accessed_on: str) -> dict:
    return {
        "ledger": "Atomic accelerator disclosure claims",
        "accessed_on": accessed_on,
        "claim_records": len(records),
        "source_record_count": len({(row["source_kind"], row["source_ref"]) for row in records}),
        "source_kind_counts": dict(sorted(Counter(row["source_kind"] for row in records).items())),
        "lifecycle_counts": dict(sorted(Counter(row["lifecycle"] for row in records).items())),
        "physicality_counts": dict(sorted(Counter(row["physicality"] for row in records).items())),
        "overlap_group_count": len({row["overlap_group"] for row in records}),
        "official_evidence_url_count": len({url for row in records for url in row["official_evidence_urls"]}),
        "cross_company_accelerator_total": None,
        "reason_no_total": "The rows mix units, dates, physicality, ownership, lifecycle, sites and overlapping program scopes.",
        "high_signal_reconciliation_groups": [
            "aws_trainium2_broader versus aws_rainier",
            "google architecture capacity versus physical inventory",
            "meta historical milestones versus current fleet",
            "nscale Microsoft future deployments",
            "oracle alternative Supercluster maxima",
            "xAI compute equivalent versus physical target",
            "Yotta exact live, portfolio headline and future plans",
            "IREN installed-or-on-order versus NVIDIA vesting ceiling",
            "Ark-hosted Nebius initial deployment versus Ark-owned inventory",
        ],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--landscape", type=Path, default=Path("life/knowledge/global_ai_data_center_landscape_202607.yaml"))
    parser.add_argument("--neocloud", type=Path, default=Path("life/imports/global_data_centers_20260717/neocloud_disclosure_registry.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.landscape, args.neocloud, args.accessed_on)
    summary = build_summary(records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ledger = args.output_dir / "accelerator_disclosure_ledger.jsonl"
    summary_path = args.output_dir / "accelerator_disclosure_summary.json"
    ledger.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "ledger": str(ledger), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
