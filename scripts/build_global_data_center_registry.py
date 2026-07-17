#!/usr/bin/env python3
"""Build a public, reproducible global data-center location registry from OSM.

The output is a derivative database of OpenStreetMap and is therefore distributed
under ODbL 1.0. It is a location baseline, not a claim that every operating data
center is present. GPU counts, utility capacity, and equipment are enriched in a
separate evidence-backed layer because those attributes are rarely mapped in OSM.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path


ENDPOINT = "https://qlever.dev/api/osm-planet"
OSM_COPYRIGHT = "https://www.openstreetmap.org/copyright"
ODBL = "https://opendatacommons.org/licenses/odbl/1-0/"

DETAIL_QUERY = """
PREFIX osm: <https://www.openstreetmap.org/>
PREFIX osm2rdf: <https://osm2rdf.cs.uni-freiburg.de/rdf#>
PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?x ?type ?name ?operator ?owner ?area ?building ?telecom
       ?industrial ?website ?start_date
       ?opening_date ?construction ?addr_city ?addr_state ?addr_postcode
       ?wikidata ?levels
WHERE {
  {
    ?x osmkey:telecom "data_center" .
  } UNION {
    ?x osmkey:building "data_center" .
  } UNION {
    ?x osmkey:industrial "data_centre" .
  } UNION {
    ?x osmkey:industrial "data_center" .
  }
  OPTIONAL { ?x rdf:type ?type . }
  OPTIONAL { ?x osmkey:name ?name . }
  OPTIONAL { ?x osmkey:operator ?operator . }
  OPTIONAL { ?x osmkey:owner ?owner . }
  OPTIONAL { ?x osm2rdf:area ?area . }
  OPTIONAL { ?x osmkey:building ?building . }
  OPTIONAL { ?x osmkey:telecom ?telecom . }
  OPTIONAL { ?x osmkey:industrial ?industrial . }
  OPTIONAL { ?x osmkey:website ?website . }
  OPTIONAL { ?x osmkey:start_date ?start_date . }
  OPTIONAL { ?x osmkey:opening_date ?opening_date . }
  OPTIONAL { ?x osmkey:construction ?construction . }
  OPTIONAL { ?x osmkey:addr:city ?addr_city . }
  OPTIONAL { ?x osmkey:addr:state ?addr_state . }
  OPTIONAL { ?x osmkey:addr:postcode ?addr_postcode . }
  OPTIONAL { ?x osmkey:wikidata ?wikidata . }
  OPTIONAL { ?x osmkey:building:levels ?levels . }
}
""".strip()

GEOMETRY_QUERY = """
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>
SELECT DISTINCT ?x ?wkt
WHERE {
  {
    ?x osmkey:telecom "data_center" .
  } UNION {
    ?x osmkey:building "data_center" .
  } UNION {
    ?x osmkey:industrial "data_centre" .
  } UNION {
    ?x osmkey:industrial "data_center" .
  }
  ?x geo:hasGeometry/geo:asWKT ?wkt .
}
""".strip()

COUNTRY_QUERY_TEMPLATE = """
PREFIX ogc: <http://www.opengis.net/rdf#>
PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>
SELECT DISTINCT ?x ?country ?country_name ?iso
WHERE {
  VALUES ?x { %s }
  ?x ogc:sfIntersects ?country .
  ?country osmkey:boundary "administrative" ; osmkey:admin_level 2 .
  OPTIONAL { ?country osmkey:name ?country_name . }
  OPTIONAL { ?country osmkey:ISO3166-1 ?iso . }
}
""".strip()


NUMBER_PAIR = re.compile(
    r"(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+"
    r"(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
)


def fetch_query(endpoint: str, query: str) -> dict:
    body = urllib.parse.urlencode({"query": query}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": "BrianOntologyDataCenterResearch/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def fetch_all(endpoint: str):
    details = fetch_query(endpoint, DETAIL_QUERY)
    geometries = fetch_query(endpoint, GEOMETRY_QUERY)
    detail_bindings = details.get("results", {}).get("bindings", [])
    sources = sorted({value(item, "x") for item in detail_bindings if value(item, "x")})
    country_bindings = []
    country_query_meta = []
    for offset in range(0, len(sources), 250):
        chunk = sources[offset : offset + 250]
        values_clause = " ".join(f"<{source}>" for source in chunk)
        response = fetch_query(endpoint, COUNTRY_QUERY_TEMPLATE % values_clause)
        country_bindings.extend(response.get("results", {}).get("bindings", []))
        country_query_meta.append(response.get("meta", {}))
    return detail_bindings, geometries, country_bindings, {
        "detail_query": details.get("meta", {}),
        "geometry_query": geometries.get("meta", {}),
        "country_query_chunks": len(country_query_meta),
        "country_query_meta": country_query_meta,
    }


def value(binding: dict, key: str):
    item = binding.get(key)
    return item.get("value") if item else None


def representative_coordinate(wkt: str | None):
    if not wkt:
        return None, None, "missing"
    pairs = [(float(x), float(y)) for x, y in NUMBER_PAIR.findall(wkt)]
    if not pairs:
        return None, None, "missing"
    if wkt.lstrip().upper().startswith("POINT"):
        lon, lat = pairs[0]
        return lat, lon, "osm_point"
    # Data-center polygons are usually compact buildings/campuses. A bounding-box
    # midpoint is stable and sufficient for a world map; the OSM polygon remains
    # authoritative for footprint area.
    lons = [item[0] for item in pairs]
    lats = [item[1] for item in pairs]
    return (
        (min(lats) + max(lats)) / 2,
        (min(lons) + max(lons)) / 2,
        "geometry_bbox_midpoint",
    )


def as_number(raw: str | None):
    if raw is None:
        return None
    try:
        number = float(raw)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return round(number, 3)


def compact(record: dict) -> dict:
    return {key: val for key, val in record.items() if val not in (None, "", [], {})}


def merge_rows(
    bindings: list[dict], geometry_response: dict, country_bindings: list[dict]
) -> list[dict]:
    geometry_by_source = {
        value(binding, "x"): value(binding, "wkt")
        for binding in geometry_response.get("results", {}).get("bindings", [])
        if value(binding, "x")
    }
    countries_by_source: dict[str, list[dict]] = collections.defaultdict(list)
    for binding in country_bindings:
        source_url = value(binding, "x")
        candidate = compact(
            {
                "iso2": value(binding, "iso"),
                "name": value(binding, "country_name"),
                "osm_relation_url": value(binding, "country"),
            }
        )
        if source_url and candidate and candidate not in countries_by_source[source_url]:
            countries_by_source[source_url].append(candidate)
    by_source: dict[str, dict] = {}
    for binding in bindings:
        source_url = value(binding, "x")
        if not source_url:
            continue
        lat, lon, coordinate_method = representative_coordinate(
            geometry_by_source.get(source_url)
        )
        osm_type, osm_id = source_url.rstrip("/").rsplit("/", 2)[-2:]
        record = by_source.setdefault(
            source_url,
            {
                "id": f"osm_{osm_type}_{osm_id}",
                "object_type": "DataCenterLocation",
                "source_url": source_url,
                "source_dataset": "OpenStreetMap via QLever OSM Planet",
                "osm_type": osm_type,
                "osm_id": int(osm_id),
                "name": value(binding, "name"),
                "operator": value(binding, "operator"),
                "owner": value(binding, "owner"),
                "latitude": round(lat, 7) if lat is not None else None,
                "longitude": round(lon, 7) if lon is not None else None,
                "coordinate_method": coordinate_method,
                "footprint_area_m2": as_number(value(binding, "area")),
                "building_levels": value(binding, "levels"),
                "country_candidates": countries_by_source.get(source_url, []),
                "address": compact(
                    {
                        "city": value(binding, "addr_city"),
                        "state": value(binding, "addr_state"),
                        "postcode": value(binding, "addr_postcode"),
                    }
                ),
                "tags": compact(
                    {
                        "telecom": value(binding, "telecom"),
                        "building": value(binding, "building"),
                        "industrial": value(binding, "industrial"),
                        "construction": value(binding, "construction"),
                        "start_date": value(binding, "start_date"),
                        "opening_date": value(binding, "opening_date"),
                    }
                ),
                "website": value(binding, "website"),
                "wikidata": value(binding, "wikidata"),
                "evidence_status": "mapped_public_location",
                "gpu_count": None,
                "it_capacity_mw": None,
                "utility_capacity_mw": None,
                "power_equipment": None,
            },
        )
    return [compact(record) for record in by_source.values()]


def build_summary(records: list[dict], retrieved_at: str, endpoint: str, query_meta: dict):
    countries = collections.Counter()
    operators = collections.Counter()
    mapped_status = collections.Counter()
    with_area = 0
    with_name = 0
    with_operator = 0
    with_country = 0
    with_coordinate = 0
    for record in records:
        candidates = record.get("country_candidates", [])
        iso_codes = sorted({item.get("iso2") for item in candidates if item.get("iso2")})
        if iso_codes:
            with_country += 1
            countries.update(iso_codes)
        if record.get("operator"):
            with_operator += 1
            operators[record["operator"]] += 1
        if record.get("name"):
            with_name += 1
        if record.get("footprint_area_m2") is not None:
            with_area += 1
        if record.get("latitude") is not None:
            with_coordinate += 1
        tags = record.get("tags", {})
        if tags.get("construction") or tags.get("building") == "construction":
            mapped_status["construction_or_planned_tag"] += 1
        else:
            mapped_status["no_construction_tag"] += 1
    return {
        "schema_version": 1,
        "generated_at": retrieved_at,
        "source": {
            "name": "OpenStreetMap via QLever OSM Planet",
            "endpoint": endpoint,
            "osm_copyright_url": OSM_COPYRIGHT,
            "license": "ODbL 1.0",
            "license_url": ODBL,
            "attribution": "© OpenStreetMap contributors",
            "query_result_meta": query_meta,
        },
        "coverage": {
            "records": len(records),
            "with_coordinates": with_coordinate,
            "with_country": with_country,
            "with_name": with_name,
            "with_operator": with_operator,
            "with_footprint_area": with_area,
            "mapped_status_counts": dict(mapped_status),
            "country_counts": dict(countries.most_common()),
            "top_operators_by_mapped_object_count": dict(operators.most_common(100)),
        },
        "limits": [
            "This is the complete result of the stated OSM tag query, not every data center in the physical world.",
            "OSM coverage and tagging quality vary materially by country and operator.",
            "A mapped object may be a building, campus, node, or industrial site; multiple objects can belong to one campus.",
            "Absence of a construction tag does not prove that a facility is operational.",
            "GPU counts, power capacity, cooling, and electrical equipment require separate source-backed enrichment.",
            "Coordinates for non-point geometries are bounding-box midpoints; OSM geometry and area remain authoritative.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for JSONL registry and summary JSON",
    )
    parser.add_argument("--endpoint", default=ENDPOINT)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bindings, geometry_response, country_bindings, query_meta = fetch_all(args.endpoint)
    records = merge_rows(bindings, geometry_response, country_bindings)
    records.sort(
        key=lambda item: (
            (item.get("country_candidates") or [{}])[0].get("iso2", ""),
            item.get("operator") or "",
            item.get("name") or "",
            item["source_url"],
        )
    )
    retrieved_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    registry_path = output_dir / "osm_data_center_locations.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = build_summary(
        records,
        retrieved_at=retrieved_at,
        endpoint=args.endpoint,
        query_meta=query_meta,
    )
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"registry": str(registry_path), **summary["coverage"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
