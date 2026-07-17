# Global data-center public location baseline

This import is the reproducible location layer for Brian's global AI data-center
research. It queries every current OpenStreetMap object matching any of these tags:

- `telecom=data_center`
- `building=data_center`
- `industrial=data_centre`
- `industrial=data_center`

Run from the repository root:

```sh
python3 scripts/build_global_data_center_registry.py
```

The registry deliberately leaves GPU count, IT/utility power capacity, and power
equipment empty. Those fields are populated only in the separate deep-research
layer when a company filing, operator page, utility filing, permit, or other
traceable source supports the claim.

## Coverage boundary

"Every" in this file means every object returned by the documented OSM query at
the retrieval time. It does **not** mean every physical data center worldwide.
Private enterprise rooms, undisclosed hyperscale facilities, military sites, and
poorly mapped regions are systematically undercounted. A campus can also appear as
several building objects.

PeeringDB is used only as a non-republished cross-check because its acceptable-use
policy restricts bulk redistribution. On 2026-07-17 its public site reported 5,858
facilities, versus the independently queryable OSM tag baseline in this directory.

## Data license and attribution

The location registry is derived from OpenStreetMap through the QLever OSM Planet
endpoint.

> © OpenStreetMap contributors. Data available under ODbL 1.0.

- OSM copyright and attribution: <https://www.openstreetmap.org/copyright>
- ODbL 1.0: <https://opendatacommons.org/licenses/odbl/1-0/>
- QLever OSM Planet: <https://qlever.dev/osm-planet>
- PeeringDB AUP: <https://www.peeringdb.com/aup>

Any redistributed modified database based on this registry must preserve the ODbL
share-alike requirements and attribution.
