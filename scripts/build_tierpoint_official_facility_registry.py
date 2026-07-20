#!/usr/bin/env python3
"""Build a scope-safe TierPoint facility, engineering and finance registry.

TierPoint's current directory has 37 page groups, while grouped Hawthorne,
Oklahoma City and Spokane pages resolve to 40 current specification-sheet
records.  The builder keeps those marketing records separate from KBRA's
33-facility securitized collateral, TierPoint's 40-data-center headline, the
TekPark 100-MW expansion, customer compute and standalone company financials.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY = "https://www.tierpoint.com/data-centers/"
ABOUT = "https://www.tierpoint.com/about-us/"
AI_HIGH_DENSITY = "https://www.tierpoint.com/services/data-center-services/ai-high-density-colocation/"
COREWEAVE = "https://www.tierpoint.com/news/tierpoint-to-provide-ultra-high-density-colocation-services-to-coreweave-to-serve-industries-in-emerging-technology/"
GROQ = "https://www.tierpoint.com/success-stories/groq/"
TERM_LOAN = "https://www.tierpoint.com/news/tierpoint-parent-closes-upsized-250-million-term-loan/"
ABS_2025 = "https://www.tierpoint.com/news/tierpoint-completes-240-million-securitization-financing-and-acquisition-of-pennsylvania-data-center-and-campus/"
KBRA_2025 = "https://www.kbra.com/publications/NWSCDPYs/kbra-assigns-ratings-to-tierpoint-issuer-llc-series-2025-3-and-series-2025-4-and-takes-other-rating-actions"
KBRA_2024 = "https://www.kbra.com/publications/fqWGvgRD/kbra-assigns-ratings-to-tierpoint-issuer-llc-series-2025-1-and-series-2025-2-and-takes-other-rating-actions"
EQUITY_2020 = "https://www.tierpoint.com/news/tierpoint-closes-320-million-in-equity-from-consortium-of-investors/"
OK2_2016 = "https://www.tierpoint.com/news/tierpoint-completes-oklahomas-largest-commercial-data-center/"


def page(state: str, slug: str) -> str:
    return f"https://www.tierpoint.com/data-centers/{state}/{slug}/"


def pdf(path: str) -> str:
    return f"https://web.tierpoint.com/hubfs/{path}"


def site(
    code: str,
    market: str,
    locality: str,
    region: str,
    address: str,
    page_url: str,
    spec_url: str,
    facility_k_sqft: float,
    data_center_k_sqft: float,
    utility: str,
    generators: str,
    ups: str,
    cooling: str,
    bms: str,
    *,
    high_density: str = "not_stated_on_reviewed_spec_sheet",
    conflicts: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict:
    return {
        "id": f"tierpoint_{code.lower()}",
        "object_type": "DataCenterFacilityEvidence",
        "provider_code": code,
        "market": market,
        "locality": locality,
        "region": region,
        "country_code": "US",
        "address_as_published": address,
        "lifecycle_as_of_2026_07_19": "current_provider_page_operational_colocation_facility",
        "published_space": {
            "spec_sheet_facility_or_gross_space_thousand_sqft": facility_k_sqft,
            "spec_sheet_production_or_data_center_space_thousand_sqft": data_center_k_sqft,
            "definition_boundary": "Published labels vary by sheet and may include gross building, production, raised-floor, expansion or available area; values are not a standardized sellable-area or operating-load measure.",
        },
        "power_and_cooling_evidence": {
            "utility_or_transformer": utility,
            "backup_generation": generators,
            "UPS_and_distribution": ups,
            "mechanical_cooling": cooling,
            "BMS_monitoring_and_life_safety": bms,
            "as_built_OEM_model_battery_runtime_acceptance_test_remaining_life_and_actual_loading": "undisclosed_except_where_named_in_text",
        },
        "high_density_and_liquid_cooling_evidence": high_density,
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "publication_conflicts": conflicts or [],
        "notes": notes or [],
        "boundary": "The current page and specification sheet establish a marketed facility and design equipment statements, not energized critical load, occupancy, utilization, actual rack density, TierPoint-owned compute or standalone site economics.",
        "source_urls": [page_url, spec_url],
    }


SITES = [
    site("LIT", "Little Rock", "Little Rock", "Arkansas", "15707 Chenal Pkwy, Little Rock, AR 72211", page("arkansas", "little-rock"), pdf("data-center/ar-little-rock-data-center-spec-sheet.pdf"), 30, 9, "2N A/B utilities; dual pad-mounted 3,000kVA transformers", "2 x 2,250kW Kohler generators; 4,000-gallon tank each", "true 2N UPS", "N+1 CRAHs and N+3 water pumps", "BMS temperature sensing; VESDA; temperature and humidity monitoring", high_density="up to 85kW per cabinet and liquid cooling on the reviewed sheet"),
    site("WAT", "Waterbury", "Waterbury", "Connecticut", "108 Bank Street, 5th Floor, Waterbury, CT 06702", page("connecticut", "waterbury"), pdf("data-center/ct-waterbury-data-center-spec-sheet.pdf"), 3, 1.6, "A/B utility paths; 3000A 3P/4W 208V service", "125kW natural-gas generator plus 400kW diesel generator", "true 2N UPS", "N+1 HVAC", "Ignition BMS monitoring HVAC and electrical systems"),
    site("JAX", "Jacksonville", "Jacksonville", "Florida", "8324 Baymeadows Way, Jacksonville, FL 32256", page("florida", "jacksonville"), pdf("data-center/fl-jacksonville-data-center-spec-sheet.pdf"), 120, 17, "2N A/B; 2,000kVA Utility 1 and 2,500kVA Utility 2 transformers", "sheet: 1 x 2,000kW plus 1 x 1,500kW generators with 5,000 gallons", "true 2N UPS", "N+1 HVAC", "Ignition BMS", high_density="up to 85kW per cabinet and liquid cooling on the reviewed sheet", conflicts=["Current page says two 2MW generators; specification sheet says one 2,000kW and one 1,500kW generator.", "Sheet states 17,000 square feet of data-center space plus 22,000 square feet of expansion; the registry checksum uses the 17,000 published production value only."]),
    site("POL", "Chicago", "Chicago", "Illinois", "601 W. Polk, Chicago, IL 60607", page("illinois", "chicago"), pdf("data-center/il-chicago-polk-data-center-spec-sheet.pdf"), 107, 16, "one 2,500kVA primary utility transformer; 3000A 3P/4W 208V service", "2 x 2.25MW diesel generators; 2,300-gallon tanks plus one external 14,000-gallon tank", "true 2N UPS", "N+1 HVAC", "EcoStruxure temperature, humidity, HVAC and electrical monitoring"),
    site("CHI", "Chicago West", "Franklin Park", "Illinois", "9333 West Grand Avenue, Chicago, IL 60131", page("illinois", "chicago-west"), pdf("data-center/il-chicago-west-data-center-spec-sheet.pdf"), 117.5, 15, "one 2,500kVA primary utility transformer; 3000A 3P/4W 208V service", "2 x 2MW diesel generators; 4,000-gallon tanks", "redundant UPS systems", "N+2 HVAC", "HVAC and electrical BMS monitoring"),
    site("LEN", "Kansas City Lenexa", "Lenexa", "Kansas", "14500 West 105th Street, Lenexa, KS 66215", page("kansas", "kansas-city-lenexa"), pdf("data-center/ks-kansas-city-lenexa-data-center-spec-sheet.pdf"), 58, 11, "2N A/B; dual 3,000kVA pad-mounted transformers", "2 x 2,500kW Caterpillar generators; 4,000-gallon tank each", "true 2N UPS", "N+1 CRAHs and chillers", "Vertiv Environet and Automated Control Systems BMS"),
    site("BAL", "Baltimore", "Baltimore", "Maryland", "1401 Russell Street, Baltimore, MD 21230", page("maryland", "baltimore"), pdf("data-center/md-baltimore-data-center-spec-sheet.pdf"), 28, 14, "2N A/B; 1,500kVA Utility 1 and 2,500kVA Utility 2 transformers", "redundant 1,500kW generators; 10,000 gallons on site", "true N+1 redundant UPS", "N+1 HVAC", "Ignition BMS"),
    site("BWI", "Baltimore BWI", "Linthicum Heights", "Maryland", "813 Pinnacle Drive, Linthicum Heights, MD 21090", page("maryland", "baltimore-bwi"), pdf("data-center/md-baltimore-bwi-data-center-spec-sheet.pdf"), 34, 13, "2N A/B; 1,560kVA transformer for each utility", "redundant 1,250kW generators; sheet prints 9,000K gallons", "true 2N UPS", "N+2 HVAC", "Ignition BMS", conflicts=["The specification sheet's '9,000K gallons' fuel text is retained as an obvious publisher-unit typo and is not normalized; the current page instead states minimum 48-hour runtime."]),
    site("AND", "Boston Andover", "Andover", "Massachusetts", "15 Shattuck Road, Andover, MA 01810", page("massachusetts", "boston-andover"), pdf("data-center/ma-boston-andover-data-center-spec-sheet.pdf"), 92.7, 21, "2N A/B; 3,360kVA Utility 1 and 3,750kVA Utility 2 transformers", "sheet: 5 x 1MW generators and 2 x 15,000-gallon underground tanks", "true 2N UPS", "N+2 HVAC", "Ignition BMS", conflicts=["Current page says two 2.5MW generators; specification sheet says five 1MW generators."]),
    site("MRL", "Boston Marlborough", "Marlborough", "Massachusetts", "34 St. Martin Drive, Marlborough, MA 01752", page("massachusetts", "boston-marlborough"), pdf("data-center/ma-boston-marlborough-data-center-spec-sheet.pdf"), 115, 50, "2N A/B utility paths", "7 x 1,000kW, 1 x 2.25MW and 2 x 2.5MW generators; 33,500 gallons", "true 2N UPS", "N+2 HVAC", "Metasys BMS", high_density="up to 85kW per cabinet on the reviewed sheet", conflicts=["Current page states 140,000 total square feet; specification sheet states 115,000 square feet. Registry checksum uses the sheet value."]),
    site("SLM", "St Louis Millpark", "Maryland Heights", "Missouri", "2315 Millpark Drive, Suite 104, Maryland Heights, MO 63043", page("missouri", "st-louis-millpark"), pdf("135870/TP-Facility_Fact_Sheet-SLM-WEB.pdf"), 23, 14.4, "2N A/B; dual 2,500kVA transformers", "2 x 2,000kW generators; 14,400 gallons", "true 2N UPS", "N+1 HVAC with free-cooling economizers", "BMS monitoring"),
    site("SLO", "St Louis Olive", "St Louis", "Missouri", "1111 Olive Street, St. Louis, MO 63101", page("missouri", "st-louis-olive"), pdf("data-center/mo-st-louis-olive-data-center-spec-sheet.pdf"), 124, 11, "N+1 utility; dual 2,000kVA transformers", "N+1 2,000kW Caterpillar generators; 2,000-gallon tank each", "N+1 UPS", "N+1 AHUs, chillers, pumps and cooling towers", "VESDA and BMS"),
    site("SLL", "St Louis Locust", "St Louis", "Missouri", "2300 Locust Street, St. Louis, MO 63103", page("missouri", "st-louis-locust"), pdf("St.%20Louis%20Locust%20St%20(SLL)%20Data%20Center%20Spec%20Sheet.pdf"), 135.84, 22.64, "N+1 5MW utility with 3MW critical N+1", "4 x 2MW generators", "N+1 UPS", "N+1 HVAC with air-side economizers", "real-time monitoring and VESDA", conflicts=["Sheet also identifies 45,000 square feet of expansion beyond the 22,640-square-foot Phase 1 value used in the checksum."]),
    site("BEL", "Omaha Bellevue", "Bellevue", "Nebraska", "1001 North Fort Crook Road, Bellevue, NE 68005", page("nebraska", "omaha-bellevue"), pdf("data-center/ne-omaha-bellevue-data-center-spec-sheet.pdf"), 100, 21, "A/B; 9,000kW redundant utility from diverse substations", "sheet: four generators totaling 5.5MW", "N+1 UPS", "N+1 HVAC", "Ignition BMS", conflicts=["Current page says five generators totaling 5.5MW; specification sheet says four generators totaling 5.5MW."]),
    site("MID", "Omaha Midlands", "Papillion", "Nebraska", "11425 South 84th Street, Papillion, NE 68046", page("nebraska", "omaha-midlands"), pdf("data-center/Data%20Center%20Spec%20Sheet%20-%20Midlands%20MID.pdf"), 63, 15, "A/B; 6,500kW redundant utility from diverse substations", "sheet: two generators totaling 4.75MW", "N+1 UPS", "N+1 HVAC", "Ignition BMS", conflicts=["Current page says two 2.25MW generators, or 4.5MW total; specification sheet says 4.75MW total."]),
    site("HWT", "New York Hawthorne", "Hawthorne", "New York", "11 Skyline Drive, Hawthorne, NY 10532", page("new-york", "new-york-hawthorne"), pdf("data-center/Data%20Center%20Spec%20Sheet%20-%20Hawthorne%20HWT.pdf"), 46, 28, "2N A/B; 3 x 2,000kVA transformers", "3 x 1,000kW plus 2 x 2,000kW generators", "true 2N UPS", "N+2 HVAC", "Ignition BMS"),
    site("HW2", "New York Hawthorne", "Hawthorne", "New York", "17 Skyline Drive, Hawthorne, NY 10532", page("new-york", "new-york-hawthorne"), pdf("data-center/Data%20Center%20Spec%20Sheet%20-%20Hawthorne%20HWT2.pdf"), 172, 28, "2N A/B; 2 x 2,000kVA transformers", "2 x 2,000kW generators; 9,000 gallons", "true 2N UPS", "N+2 HVAC", "Ignition BMS", conflicts=["Sheet header says 13,500+ square feet of data-center space while a later production-space row and current page state 28,000 square feet; checksum uses 28,000."]),
    site("CL2", "Charlotte North Myers", "Charlotte", "North Carolina", "125 North Myers Street, Charlotte, NC 28202", page("north-carolina", "charlotte-north-myers"), pdf("data-center/nc-charlotte-north-myers-data-center-spec-sheet.pdf"), 30.6, 7.5, "2N; 2 x 2,500kVA transformers", "2 x 1,750kW generators; 6,000 gallons", "true 2N UPS", "N+1 HVAC", "BMS monitoring"),
    site("CL4", "Charlotte Center Park", "Charlotte", "North Carolina", "1805 Center Park Drive, Charlotte, NC 28217", page("north-carolina", "charlotte-center-park"), pdf("data-center/Data%20Center%20Spec%20Sheet%20-%20Charlotte%20CLT4.pdf"), 60, 20, "2N; 2 x 3,000kVA transformers", "sheet: 2 x 2,250kW generators; 8,000 gallons", "true 2N UPS", "N+1 HVAC", "BMS monitoring", high_density="up to 85kW per cabinet on the reviewed sheet", conflicts=["Current page says four 2.25MW generators; specification sheet says two."]),
    site("RAL", "Raleigh", "Raleigh", "North Carolina", "5301 Departure Drive, Raleigh, NC 27616", page("north-carolina", "raleigh"), pdf("data-center/nc-raleigh-data-center-spec-sheet.pdf"), 65, 33, "2N; 5 x 2,500kVA transformers", "5 x 2,000kW generators; 20,000 gallons", "true 2N UPS", "N+2 chiller plant with at least N+1 CRAC/CRAH", "monitoring and control systems"),
    site("RTP", "Raleigh RTP", "Durham", "North Carolina", "99 TW Alexander Drive, Durham, NC 27709", page("north-carolina", "raleigh-rtp"), pdf("data-center/nc-raleigh-rtp-data-center-spec-sheet-tierpoint.pdf"), 70, 34, "2N; 2 x 2,500kVA transformers for DC100/DC200", "4 x 2MW generators; 4,000-gallon belly tank each", "true 2N UPS", "2N HVAC", "Schneider EcoStruxure BMS"),
    site("OKC", "Oklahoma City", "Oklahoma City", "Oklahoma", "4121 Perimeter Center Place, Oklahoma City, OK 73112", page("oklahoma", "oklahoma-city"), pdf("data-center/ok-oklahoma-city-data-center1-spec-sheet.pdf"), 22, 14, "A/B; 3000A 3P/4W 208V service", "3 x 1MW standby diesel generators", "redundant UPS systems", "N+1 HVAC", "Ignition BMS"),
    site("OK2", "Oklahoma City", "Oklahoma City", "Oklahoma", "4114 Perimeter Center Place, Oklahoma City, OK 73112", page("oklahoma", "oklahoma-city"), pdf("data-center/ok-oklahoma-city-data-center2-spec-sheet.pdf"), 69, 34, "A/B; historical release says two substations totaling 5,000kVA", "sheet prints 2 x 2MW generators totaling 8,000kW", "redundant UPS systems", "N+1 HVAC", "Ignition BMS", high_density="up to 85kW per cabinet on the reviewed sheet", conflicts=["Specification sheet's two 2MW generators totaling 8,000kW is an internal arithmetic error; current page states two 2MW generators, while the 2016 release stated four diesel generators."], notes=["Historical source: " + OK2_2016]),
    site("TUL", "Tulsa Archer", "Tulsa", "Oklahoma", "322 E. Archer Street, Tulsa, OK 74120", page("oklahoma", "tulsa-archer"), pdf("data-center/ok-tulsa-archer-data-center-spec-sheet.pdf"), 36, 4, "A/B; 1600A 3P/4W 480V service", "2 x 1MW diesel generators; shared 4,000-gallon tank plus 300 gallons each", "redundant UPS systems", "not_extracted_from_reviewed_sheet", "BMS monitoring HVAC and electrical systems"),
    site("TL2", "Tulsa State Farm", "Tulsa", "Oklahoma", "12151 E. State Farm Boulevard, Tulsa, OK 74146", page("oklahoma", "tulsa-state-farm"), pdf("data-center/Data%20Center%20Spec%20Sheet%20-%20Tulsa%20TUL2.pdf"), 32, 16, "dual substation feeds; 3000A 3P/4W 480V service", "2 x 2.5MW diesel generators; 3,500 gallons each", "true 2N; page states 2 x 1.2MW UPS and 8 x 300kVA PDUs", "N+1 HVAC", "BMS monitoring", conflicts=["Specification code is TL2 while a source filename uses TUL2; address also appears as 12151 E 48th Street in provider material."]),
    site("TEK", "Allentown TekPark", "Breinigsville", "Pennsylvania", "9999 Hamilton Boulevard, Building 4, Breinigsville, PA 18031", page("pennsylvania", "allentown-tekpark"), pdf("data-center/pa-allentown-data-center-spec-sheet.pdf"), 122, 58, "two redundant A/B 69kV transmission lines", "sheet: 8 x 2MW N+1 generators and 39,000 gallons", "true 2N UPS", "N+1 HVAC", "Ignition BMS", high_density="up to 85kW per cabinet on the reviewed sheet", conflicts=["Current page states 96,000 square feet of raised-floor space; sheet states 58,000 square feet of data-center space.", "Current page states 15 x 2.5MW and 8 x 2MW generators; sheet states 8 x 2MW."], notes=["TierPoint acquired the formerly leased building and 137-acre campus in 2025; a separate 100MW power expansion was targeted for the second half of 2026 and is not current critical load."]),
    site("BET", "Bethlehem", "Bethlehem", "Pennsylvania", "3864 Courtney Street, Suite 130, Bethlehem, PA 18017", page("pennsylvania", "bethlehem"), pdf("data-center/pa-bethleham-data-center-spec-sheet.pdf"), 25, 12, "N A/B; sheet prints 1,000kVA Utility 1 and 1500VA Utility 2", "2 x 600kW plus 1 x 1,000kW generators", "true N+1 UPS", "N+1 HVAC", "Ignition BMS", conflicts=["The sheet's 1500VA Utility 2 transformer text is retained as a likely kVA publisher typo and not normalized."]),
    site("LVQ", "Lehigh Valley", "Bethlehem", "Pennsylvania", "3949 Schelden Circle, Bethlehem, PA 18017", page("pennsylvania", "lehigh-valley"), pdf("data-center/pa-lehigh-valley-data-center-spec-sheet.pdf"), 27, 8.7, "N, A/B; 2,000kVA transformer", "3 x 1.5MW generators; 10,000 gallons", "true 2N UPS", "N+1 HVAC", "Ignition BMS"),
    site("PHI", "Philadelphia", "Philadelphia", "Pennsylvania", "4775 League Island Boulevard, Philadelphia, PA 19112", page("pennsylvania", "philadelphia"), pdf("data-center/pa-philadelphia-data-center-spec-sheet.pdf"), 25, 11, "2N; 2 x 2,250kVA transformers", "3 x 1.5MW generators; 13,000 gallons", "true 2N UPS", "N+2 HVAC", "Ignition BMS"),
    site("VFO", "Valley Forge", "Norristown", "Pennsylvania", "1000 Adams Avenue, Norristown, PA 19403", page("pennsylvania", "valley-forge"), pdf("data-center/pa-valley-forge-data-center-spec-sheet.pdf"), 137, 61, "2N; detailed utility transformer field not published on reviewed sheet", "9 x 2.5MW generators; 30,000 gallons", "true 2N UPS", "N+1 HVAC", "Ignition BMS"),
    site("SFE", "Sioux Falls East", "Sioux Falls", "South Dakota", "700 East 54th Street North, Sioux Falls, SD 57104", page("south-dakota", "sioux-falls-east"), pdf("data-center/sd-sioux-falls-east-data-center-spec-sheet.pdf"), 16, 4.2, "A/B; 2000A 3P/4W 208V service", "800kW generator with 1,400 gallons plus 1,000kW generator with 1,841 gallons", "N+1 UPS", "N+1 HVAC", "Vertiv Environet monitoring"),
    site("NSH", "Nashville", "Franklin", "Tennessee", "311 Eddy Lane, Franklin, TN 37064", page("tennessee", "nashville"), pdf("data-center/Data%20Center%20Spec%20Sheet%20-%20Nashville%20NSH.pdf"), 52, 26, "2N; reviewed sheet utility-service row is misaligned and does not disclose a rating", "sheet: 2 x 2,250kW Kohler generators; 4,000-gallon tank each", "true 2N UPS", "N+1 mechanical at full capacity", "VESDA and monitoring", conflicts=["Current page says four 2MW generators; specification sheet says two 2,250kW generators.", "Sheet's utility-service field prints '24x7 Remote Hands', an obvious layout/content error; no electrical rating is inferred."]),
    site("DAL", "Dallas", "Dallas", "Texas", "3004 Irving Boulevard, Dallas, TX 75247", page("texas", "dallas"), pdf("data-center/tx-dallas-data-center-spec-sheet.pdf"), 68, 51, "2N; 3 x 3,750kVA plus 1 x 2,000kVA transformers", "current page: 6 x 2.0MW generators; sheet prints 2.0kW, with 3,600 gallons each plus 15,000- and 25,000-gallon USTs", "true 2N UPS", "N+1 CRAHs", "BMS monitoring", conflicts=["Specification sheet prints 2.0kW per generator; current page's 2.0MW is treated as the intended rating, while the typo remains recorded."]),
    site("DAL2", "Dallas Allen", "Allen", "Texas", "820 Allen Commerce Parkway, Allen, TX 75013", page("texas", "dallas-allen"), pdf("data-center/tx-dallas-allen-data-center-spec-sheet.pdf"), 29, 16, "2N; dual 3,000kVA transformers", "sheet: 2 x 2MW Cummins generators; 4,000 gallons each", "true 2N UPS", "N+1 HVAC with air-side economizers", "VESDA and BMS", high_density="up to 85kW per cabinet on the reviewed sheet", conflicts=["Current page additionally states one 1MW generator; specification sheet lists only two 2MW units."]),
    site("DFW", "Dallas Fort Worth", "Fort Worth", "Texas", "13701 Independence Parkway, Fort Worth, TX 76177", page("texas", "fort-worth"), pdf("TP-Facility_Fact_Sheet-DFW-WEB.pdf"), 208, 45, "12MW 2N A/B distribution; two 25kV feeds and 8 x 2,500kVA transformers", "8 x 2.25MW generators in 2N; 40,000 gallons total", "true 2N UPS", "N+1 HVAC with air-side economizers", "VESDA and BMS"),
    site("SEA", "Seattle", "Seattle", "Washington", "100 4th Avenue N., Seattle, WA 98109", page("washington", "seattle"), pdf("data-center/wa-seattle-data-center-spec-sheet.pdf"), 33, 25, "A/B; 12,000A 3P/4W 480/277V service", "5 x 2MW generators in N+2; 72,000 gallons", "redundant UPS systems", "N+1 HVAC", "Schneider StruxureWare monitoring"),
    site("SPO01_02", "Spokane", "Liberty Lake", "Washington", "23403 E. Mission Avenue, Liberty Lake, WA 99019", page("washington", "spokane"), pdf("data-center/wa-spokane-data-center-spec-sheet.pdf"), 32, 21, "A/B; 4000A 3P/4W 480/277V service", "sheet: 6 x 800kW N+1 generators; 15,000 gallons", "redundant UPS systems", "N+1 HVAC", "Schneider StruxureWare monitoring", conflicts=["Current page says four 1.25MW plus six 800kW generators; specification sheet says six 800kW units."], notes=["One current address and one combined specification sheet are labeled SPO01/02. This record is not proof of two separate buildings and is counted once in the 40-record reconciliation."]),
    site("SPO03", "Spokane", "Liberty Lake", "Washington", "23017 E. Mission Avenue, Liberty Lake, WA 99019", page("washington", "spokane"), pdf("data-center/wa-spokane-data-center2-spec-sheet.pdf"), 16.5, 9.9, "A/B; 4000A 3P/4W 480/277V service", "2,500kW 2N generation; 15,000 gallons", "redundant UPS systems", "N+1 HVAC", "Schneider StruxureWare monitoring", notes=["Groq customer evidence is associated with Spokane and describes customer LPU inference hardware, not TierPoint-owned GPUs."]),
    site("MKE", "Milwaukee", "Milwaukee", "Wisconsin", "3701 W. Burnham Street, Milwaukee, WI 53215", page("wisconsin", "milwaukee"), pdf("FactSheets/data-center/wi-milwaukee-data-center-spec-sheet.pdf"), 26, 3.6, "A/B; 3000A 3P/4W 208V service", "500kW DC1 plus 2 x 1MW DC2 diesel generators", "true 2N UPS", "N+1 HVAC", "Ignition BMS", conflicts=["Current page says 28,000 total square feet; specification sheet says 26,000. Registry checksum uses the sheet value.", "Sheet also states 3,400 square feet available beyond 3,600 square feet of production space."]),
    site("SFW", "Sioux Falls West", "Sioux Falls", "South Dakota", "5300 North La Mesa Drive, Sioux Falls, SD 57107", page("south-dakota", "sioux-falls-west"), pdf("data-center/sd-sioux-falls-west-data-center-spec-sheet.pdf"), 25, 4.3, "A/B; 3000A 3P/4W 208V service", "1MW generator; 3,500 gallons", "single UPS system", "N+1 HVAC", "Vertiv Environet monitoring"),
]


OSM_CROSSWALK = {
    "osm_way_777196805": ("tierpoint_tek", "exact_current_facility_candidate_owner_label"),
    "osm_way_159959672": ("tierpoint_tul", "exact_current_facility_website"),
    "osm_way_253682978": ("tierpoint_sll", "exact_current_facility_candidate_name_and_coordinates"),
    "osm_way_335468616": ("tierpoint_spo01_02", "current_facility_candidate_name_and_coordinates_combined_sheet_boundary"),
    "osm_way_819981908": ("tierpoint_nsh", "exact_current_facility_website"),
    "osm_way_610845529": ("tierpoint_bwi", "exact_current_facility_name_and_locality"),
    "osm_way_388148510": ("tierpoint_lit", "exact_current_facility_website"),
    "osm_node_9721703993": ("tierpoint_mke", "exact_current_facility_name_and_coordinates"),
    "osm_way_239032142": ("tierpoint_sfw", "exact_current_facility_name_and_locality"),
    "osm_way_483307714": ("tierpoint_dal2", "exact_current_facility_name_and_coordinates"),
    "osm_way_211832626": ("tierpoint_and", "exact_current_facility_operator_and_locality"),
    "osm_way_880052062": ("tierpoint_len", "exact_current_facility_operator_and_coordinates"),
    "osm_way_838817907": ("tierpoint_cl4", "exact_current_facility_operator_and_website"),
    "osm_way_465042594": ("tierpoint_dal", "exact_current_facility_operator_and_website"),
    "osm_way_1109881281": ("tierpoint_vfo", "exact_current_facility_name_and_coordinates"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [{"source_order": order, "accessed_on": accessed_on, **row} for order, row in enumerate(SITES, 1)]
    assert len(rows) == 40
    assert len({row["id"] for row in rows}) == 40
    assert len({row["source_urls"][0] for row in rows}) == 37
    assert len({row["source_urls"][1] for row in rows}) == 40
    assert round(sum(row["published_space"]["spec_sheet_facility_or_gross_space_thousand_sqft"] for row in rows), 2) == 2595.14
    assert round(sum(row["published_space"]["spec_sheet_production_or_data_center_space_thousand_sqft"] for row in rows), 2) == 826.84
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "facility_ref": facility_ref,
            "classification": classification,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_owner": source.get("owner"),
            "website": source.get("website"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "capacity_counting_rule": "OSM geometry is a crosswalk only and does not create a second facility, capacity or operating-load value.",
        })
    assert len(rows) == 15
    assert Counter(row["raw_operator"] for row in rows)["TierPoint"] == 5
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    source_urls = list(dict.fromkeys([
        DIRECTORY, ABOUT, AI_HIGH_DENSITY, COREWEAVE, GROQ, TERM_LOAN,
        ABS_2025, KBRA_2025, KBRA_2024, EQUITY_2020, OK2_2016,
        *(url for row in records for url in row["source_urls"]),
    ]))
    return {
        "id": "tierpoint_official_facility_summary_2026_07_19",
        "operator": "TierPoint",
        "legal_entity_boundary": "TierPoint LLC and financing parents or issuers; exact current legal asset ownership by facility is not publicly reconciled",
        "accessed_on": accessed_on,
        "current_directory_reconciliation": {
            "provider_headline_data_centers": 40,
            "US_markets": 20,
            "current_page_groups": 37,
            "current_spec_sheet_records": 40,
            "grouped_pages": {
                "New_York_Hawthorne": ["HWT", "HW2"],
                "Oklahoma_City": ["OKC", "OK2"],
                "Spokane": ["SPO01_02_combined_spec", "SPO03"],
            },
            "code_boundary": "The Spokane first sheet and address are combined as SPO01/02 and counted once. Splitting the label into two assumed buildings would produce 41 codes and is not supported by the reviewed public evidence.",
            "spec_sheet_facility_or_gross_space_checksum_sqft": 2_595_140,
            "spec_sheet_production_or_data_center_space_checksum_sqft": 826_840,
            "space_boundary": "The two checksums reproduce heterogeneous sheet fields; they are not standardized sellable area, live floor area, ownership area or critical load.",
        },
        "securitized_collateral_boundary": {
            "measurement_date": "2025-05-31",
            "facilities": 33,
            "sellable_sqft": 647_314,
            "critical_load_MW": 96.0,
            "unique_customers": 2_562,
            "weighted_average_remaining_contract_term_years": 1.9,
            "annualized_monthly_recurring_revenue_USD_million": 471.5,
            "annualized_adjusted_net_operating_income_USD_million": 240.3,
            "AANOI_divided_by_AMRR_percent": 50.965,
            "tenure": {"fee_simple_facilities": 10, "leasehold_facilities": 23, "one_lease_term_years": 99},
            "boundary": "KBRA metrics apply to the 33-facility securitized collateral pool, not all 40 provider facilities or audited standalone TierPoint revenue, EBITDA, operating profit or cash flow. AANOI/AMRR is a collateral NOI-style ratio, not a company operating margin.",
            "prior_snapshot_2024_11_30": {"facilities": 33, "sellable_sqft": 638_788, "critical_load_MW": 95.7, "customers": 2_652, "AMRR_USD_million": 471.5, "AANOI_USD_million": 237.4},
        },
        "power_and_cooling_reconciliation": {
            "site_level_records_with_utility_generator_UPS_cooling_and_BMS_fields": 40,
            "high_density_service_page": {"provider_wording_facilities": "a_dozen", "rack_density_kW_in_excess_of": 130, "cooling": ["direct_to_chip_liquid", "liquid_to_air"], "monitoring": "cabinet_level_power_and_thermal", "resilience": "upgraded_redundant_UPS_and_generators"},
            "explicit_85kW_sheet_records": ["LIT", "JAX", "MRL", "CL4", "OK2", "TEK", "DAL2"],
            "boundary": "130+kW and 85kW are supported design ceilings for selected configurations, not a count of deployed racks, current density or live liquid-cooled MW. Sheet rows do not disclose full as-built one-line diagrams, OEM model inventories, battery runtime, maintenance state or actual loading.",
        },
        "AI_and_accelerator_boundary": {
            "CoreWeave_2023": {"relationship": "long_term_ultra_high_density_colocation", "TierPoint_site": "undisclosed", "site_MW_GPU_model_count_and_financial_terms": "undisclosed"},
            "Groq_Spokane": {"customer_hardware": "Groq_LPU_inference_systems", "TierPoint_role": "facility_power_cooling_connectivity_and_colocation", "liquid_cooling": "capability_as_customer_evolves"},
            "TierPoint_owned_physical_GPU_inventory": "not_established",
            "physical_GPU_model_count_owner_delivery_state_site_rack_fabric_power_utilization_revenue_and_margin": "undisclosed",
            "boundary": "CoreWeave and Groq evidence establishes customer workloads. Groq LPUs are not GPUs, and neither customer's hardware is a TierPoint-owned accelerator ledger entry.",
        },
        "ownership_financing_and_financial_boundary": {
            "company_status": "private",
            "majority_shareholder_as_of_2025_07_14": "Argo Infrastructure Partners",
            "2020_preferred_equity_USD_million": 320,
            "2020_named_investors": ["Argo Infrastructure Partners", "Wafra", "Macquarie Capital", "Cequel III", "Ontario Teachers' Pension Plan", "RedBird Capital Partners", "Stephens Capital Partners", "Thompson Street Capital Partners"],
            "2025_parent_term_loan_USD_million": 250,
            "term_loan_uses": ["expansion_and_capex", "selected_lease_buyouts", "variable_funding_note_refresh", "Series_B_preferred_redemption"],
            "2025_ABS_USD_million": 240,
            "four_transaction_ABS_issuance_total_USD_billion": 1.99,
            "ABS_boundary": "The $1.99bn is cumulative issuance across four transactions, not disclosed current net debt. Interest, maturity, drawn term-loan amount, total company debt and covenant headroom are not fully disclosed in the reviewed provider releases.",
            "TekPark_transaction_and_expansion": {"formerly_leased_building_and_137_acre_campus_acquired": True, "power_expansion_MW": 100, "target": "second_half_2026", "boundary": "100MW is an expansion program target and is not added to the 96MW collateral critical-load snapshot."},
            "standalone_TierPoint_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_net_debt_customer_concentration_ROIC_and_valuation": "undisclosed",
            "current_cap_table_percentages_preferences_voting_rights_and_ultimate_economic_ownership": "undisclosed",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "distinct_current_facility_candidates": 15,
            "operator_tagged_objects": 5,
            "name_owner_or_website_only_objects": 10,
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Only five objects carry operator=TierPoint and affect operator-tag coverage. Ten additional objects are reconciled through names, owner, website, locality or coordinates; all remain map crosswalks rather than a complete facility census.",
        },
        "outlook": {
            "positive_signals": ["forty_current_US_facility_records", "96MW_securitized_collateral_base", "a_dozen_high_density_facilities", "130kW_plus_rack_design_ceiling", "CoreWeave_and_Groq_customer_validation", "TekPark_100MW_expansion_program", "institutional_infrastructure_sponsor_and_capital_market_access"],
            "risk_signals": ["private_standalone_financials_undisclosed", "short_1_9_year_collateral_contract_term", "collateral_pool_smaller_than_provider_roster", "leasehold_majority_23_of_33", "no_site_level_live_load_or_utilization", "no_owned_GPU_inventory", "publication_conflicts_and_spec_sheet_typos", "expansion_grid_construction_and_customer_execution_risk"],
            "analytical_view": "TierPoint has unusually useful site-level electrical and mechanical marketing evidence and a credible enterprise-to-AI colocation upgrade path. The securitized pool offers a partial earnings and capacity window, but it cannot support a standalone equity valuation or operating-margin conclusion because company-wide revenue, profit, debt, cap table, live load, utilization and site economics remain undisclosed.",
        },
        "remaining_material_gaps": [
            "forty_provider_records_to_thirty_three_ABS_assets_and_exact_legal_title_lease_issuer_and_lifecycle_bridge",
            "per_site_operating_energized_customer_accepted_leased_utilized_billed_and_actual_IT_load",
            "per_site_as_built_one_line_grid_voltage_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_acceptance_test_loading_and_remaining_life",
            "per_site_live_liquid_cooled_MW_actual_rack_density_measured_PUE_WUE_energy_water_and_emissions",
            "physical_GPU_or_LPU_model_count_owner_delivery_state_site_rack_fabric_power_utilization_customer_revenue_and_margin",
            "standalone_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_net_debt_maturity_covenants_customer_concentration_site_economics_ROIC_and_valuation",
            "current_cap_table_percentages_preferences_voting_rights_governance_and_ultimate_economic_ownership",
            "TekPark_100MW_permits_grid_energization_construction_customer_contract_acceptance_and_live_load",
        ],
        "sources": source_urls,
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_rows = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_rows, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "tierpoint_official_facility_registry.jsonl"
    summary_path = args.output_dir / "tierpoint_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "page_groups": len({row['source_urls'][0] for row in records}), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
