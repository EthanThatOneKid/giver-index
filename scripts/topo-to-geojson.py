#!/usr/bin/env python3
"""Convert world-atlas TopoJSON to GeoJSON with ISO3 country codes."""

import json

WORLD_ALTAS_ALIAS = {
    "W. Sahara": "western sahara",
    "Dem. Rep. Congo": "democratic republic of the congo",
    "Fr. S. Antarctic Lands": "french southern and antarctic lands",
    "Timor-Leste": "east timor",
    "eSwatini": "eswatini",
    "Côte d'Ivoire": "ivory coast",
    "Eq. Guinea": "equatorial guinea",
    "Solomon Is.": "solomon islands",
    "S. Sudan": "south sudan",
    "Korea": "south korea",
    "N. Cyprus": "northern cyprus",
    "Bosnia and Herz.": "bosnia and herzegovina",
    "Czech Rep.": "czechia",
    "Macedonia": "north macedonia",
}

with open("/home/workspace/code/github.com/EthanThatOneKid/giver-index/data/outputs/giver_index_2025.csv") as f:
    iso_map = {}
    for line in f.read().splitlines()[1:]:
        p = line.split(",")
        if len(p) >= 2:
            iso = p[0].strip()
            name = p[1].strip().lower()
            iso_map[name] = iso

with open("/home/workspace/code/github.com/EthanThatOneKid/giver-index/data/feeds/world_atlas_110m.json") as f:
    topo = json.load(f)

arcs = topo["arcs"]
geoms = topo["objects"]["countries"]["geometries"]


def resolve_arcs(arcs_list):
    mx, my = 0.0, 0.0
    result = []
    for a in arcs_list:
        ai = abs(a)
        for dx, dy in arcs[ai]:
            mx += dx
            my += dy
        result.append([round(mx * 1000) / 1000, round(my * 1000) / 1000])
    return result


out = {"type": "FeatureCollection", "features": []}
matched = unmatched = 0

for g in geoms:
    name_raw = g.get("properties", {}).get("name", "")
    name = name_raw.lower().strip()

    canon = WORLD_ALTAS_ALIAS.get(name_raw, name)
    iso3 = iso_map.get(canon, iso_map.get(name, f"UNK-{g.get('id', g['properties'].get('name', 'anon'))}"))

    if iso3.startswith("UNK"):
        unmatched += 1
    else:
        matched += 1

    arcs_data = g["arcs"]
    if g["type"] == "MultiPolygon":
        coords = [[[resolve_arcs(r) for r in poly] for poly in arcs_data]]
    else:
        coords = [[resolve_arcs(r) for r in arcs_data]]

    out["features"].append({
        "type": "Feature",
        "properties": {"ISO3166-1-Alpha-3": iso3, "name": name_raw},
        "geometry": {"type": g["type"], "coordinates": coords},
    })

p = "/home/workspace/code/github.com/EthanThatOneKid/giver-index/data/feeds/world_atlas_110m_geojson.json"
with open(p, "w") as f:
    json.dump(out, f)

sz = len(open(p).read())
print(f"Matched: {matched}/{matched + unmatched}, Features: {len(out['features'])}, Size: {sz / 1024:.0f} KB")
