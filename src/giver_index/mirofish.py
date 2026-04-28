"""Enhanced MiroFish context export — two-league simulation seed package."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .giver import GiverComputer
from .slopometry import build_seed_df, generate_narrative

log = logging.getLogger(__name__)

UN_REGIONS: dict[str, str] = {
    "ATG": "Americas", "ARG": "Americas", "BHS": "Americas", "BRB": "Americas",
    "BLZ": "Americas", "BOL": "Americas", "BRA": "Americas", "CAN": "Americas",
    "CHL": "Americas", "COL": "Americas", "CRI": "Americas", "CUB": "Americas",
    "DOM": "Americas", "ECU": "Americas", "SLV": "Americas", "GRD": "Americas",
    "GTM": "Americas", "GUY": "Americas", "HTI": "Americas", "HND": "Americas",
    "JAM": "Americas", "MEX": "Americas", "NIC": "Americas", "PAN": "Americas",
    "PRY": "Americas", "PER": "Americas", "KNA": "Americas", "LCA": "Americas",
    "VCT": "Americas", "SUR": "Americas", "TTO": "Americas", "USA": "Americas",
    "URY": "Americas", "VEN": "Americas", "TCA": "Americas",
    "DNR": "Americas",  # disputed
}

ISO3_TO_REGION: dict[str, str] = {
    # Americas (NAFTA + Caribbean)
    "USA": "Americas", "CAN": "Americas", "MEX": "Americas",
    "BLZ": "Americas", "GTM": "Americas", "SLV": "Americas", "HND": "Americas",
    "NIC": "Americas", "CRI": "Americas", "PAN": "Americas",
    "COL": "Americas", "VEN": "Americas", "ECU": "Americas", "PER": "Americas",
    "BOL": "Americas", "BRA": "Americas", "CHL": "Americas", "ARG": "Americas",
    "URY": "Americas", "PRY": "Americas", "GUY": "Americas", "SUR": "Americas",
    "JAM": "Americas", "TTO": "Americas", "BRB": "Americas", "BHS": "Americas",
    "HTI": "Americas", "DOM": "Americas", "CUB": "Americas", "PUR": "Americas",
    "PRI": "Americas",
    # Europe
    "GBR": "Europe", "FRA": "Europe", "DEU": "Europe", "ITA": "Europe",
    "ESP": "Europe", "PRT": "Europe", "NLD": "Europe", "BEL": "Europe",
    "CHE": "Europe", "AUT": "Europe", "SWE": "Europe", "NOR": "Europe",
    "DNK": "Europe", "FIN": "Europe", "ISL": "Europe", "IRL": "Europe",
    "GRC": "Europe", "POL": "Europe", "CZE": "Europe", "HUN": "Europe",
    "ROU": "Europe", "BGR": "Europe", "HRV": "Europe", "SRB": "Europe",
    "SVN": "Europe", "SVK": "Europe", "LTU": "Europe", "LVA": "Europe",
    "EST": "Europe", "UKR": "Europe", "BLR": "Europe", "MDA": "Europe",
    "BIH": "Europe", "MNE": "Europe", "MKD": "Europe", "ALB": "Europe",
    "GEO": "Europe", "ARM": "Europe", "AZE": "Europe", "KAZ": "Europe",
    "RUS": "Europe", "TUR": "Europe", "CYP": "Europe", "MLT": "Europe",
    "LUX": "Europe", "MCO": "Europe", "SMR": "Europe", "AND": "Europe",
    "LIE": "Europe",
    # Asia
    "CHN": "Asia", "JPN": "Asia", "KOR": "Asia", "IND": "Asia",
    "IDN": "Asia", "MYS": "Asia", "PHL": "Asia", "THA": "Asia",
    "VNM": "Asia", "SGP": "Asia", "BRN": "Asia", "KHM": "Asia",
    "LAO": "Asia", "MMR": "Asia", "NPL": "Asia", "BGD": "Asia",
    "PAK": "Asia", "AFG": "Asia", "IRN": "Asia", "IRQ": "Asia",
    "SAU": "Asia", "ARE": "Asia", "QAT": "Asia", "KWT": "Asia",
    "BHR": "Asia", "OMN": "Asia", "YEM": "Asia", "JOR": "Asia",
    "LBN": "Asia", "SYR": "Asia", "ISR": "Asia", "PSE": "Asia",
    "JPN": "Asia", "TWN": "Asia", "HKG": "Asia", "MNG": "Asia",
    "TJK": "Asia", "TKM": "Asia", "UZB": "Asia", "KGZ": "Asia",
    "PNG": "Oceania",
    # Africa
    "ZAF": "Africa", "EGY": "Africa", "NGA": "Africa", "KEN": "Africa",
    "GHA": "Africa", "ETH": "Africa", "TZA": "Africa", "UGA": "Africa",
    "MAR": "Africa", "DZA": "Africa", "TUN": "Africa", "LBY": "Africa",
    "SDN": "Africa", "ZMB": "Africa", "ZWE": "Africa", "Botswana": "Africa",
    "NAM": "Africa", "MOZ": "Africa", "AGO": "Africa", "COD": "Africa",
    "COG": "Africa", "CMR": "Africa", "CIV": "Africa", "SEN": "Africa",
    "MLI": "Africa", "BFA": "Africa", "NER": "Africa", "TCD": "Africa",
    "SOM": "Africa", "MDG": "Africa", "RWA": "Africa", "BDI": "Africa",
    "SSD": "Africa", "CAF": "Africa", "TGO": "Africa", "BEN": "Africa",
    "LBR": "Africa", "SLE": "Africa", "GNQ": "Africa", "GAB": "Africa",
    "CPV": "Africa", "MUS": "Africa", "SYC": "Africa", "COM": "Africa",
    "DJI": "Africa",
    # Oceania
    "AUS": "Oceania", "NZL": "Oceania", "FJI": "Oceania", "VUT": "Oceania",
    "SLB": "Oceania", "WSM": "Oceania", "TON": "Oceania", "FSM": "Oceania",
    "KIR": "Oceania", "PLW": "Oceania", "MHL": "Oceania", "NRU": "Oceania",
    "TUV": "Oceania",
}

# Manual geography name → ISO3 mapping for Top 200
GEO_TO_ISO3: dict[str, str] = {
    "United States": "USA", "United Kingdom": "GBR", "United Arab Emirates": "ARE",
    "South Korea": "KOR", "China": "CHN", "Hong Kong": "HKG", "India": "IND",
    "Russia": "RUS", "France": "FRA", "Germany": "DEU", "Italy": "ITA",
    "Spain": "ESP", "Netherlands": "NLD", "Switzerland": "CHE", "Canada": "CAN",
    "Australia": "AUS", "Japan": "JPN", "Singapore": "SGP", "Brazil": "BRA",
    "Mexico": "MEX", "Indonesia": "IDN", "Thailand": "THA", "Vietnam": "VNM",
    "Malaysia": "MYS", "Philippines": "PHL", "Israel": "ISR", "Saudi Arabia": "SAU",
    "Turkey": "TUR", "Poland": "POL", "Sweden": "SWE", "Nigeria": "NGA",
    "South Africa": "ZAF", "Egypt": "EGY", "Argentina": "ARG", "Colombia": "COL",
    "Chile": "CHL", "Pakistan": "PAK", "Bangladesh": "BGD", "Kenya": "KEN",
    "Ireland": "IRL", "Norway": "NOR", "Denmark": "DNK", "Belgium": "BEL",
    "Austria": "AUT", "Luxembourg": "LUX", "Finland": "FIN", "Czech Republic": "CZE",
    "Romania": "ROU", "Portugal": "PRT", "Greece": "GRC", "Hungary": "HUN",
    "Ukraine": "UKR", "Iraq": "IRQ", "Iran": "IRN", "Qatar": "QAT",
    "Kuwait": "KWT", "Bahrain": "BHR", "Oman": "OMN", "New Zealand": "NZL",
    "Puerto Rico": "PRI", "Taiwan": "TWN", "Hong Kong": "HKG",
    "Cayman Islands": "CYM", "British Virgin Islands": "VGB",
    "Bermuda": "BMU", "Isle of Man": "IMN", "Jersey": "JEY",
    "Guernsey": "GGY", "Panama": "PAN", "Uruguay": "URY",
    "Costa Rica": "CRI", "Dominican Republic": "DOM", "Peru": "PER",
    "Ecuador": "ECU", "Guatemala": "GTM", "Honduras": "HND",
}


def _extract_net_worth(notes: str) -> float | None:
    """Extract net worth in billions from notes string."""
    if not notes or not isinstance(notes, str):
        return None
    import re
    m = re.search(r"\$([0-9,]+)B", notes)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r"([0-9,]+)\s*B", notes)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def _extract_followers(notes: str) -> float | None:
    """Extract follower count in millions from notes string."""
    if not notes or not isinstance(notes, str):
        return None
    import re
    m = re.search(r"([0-9.]+)\s*M", notes)
    if m:
        return float(m.group(1))
    m = re.search(r"([0-9,]+)\s*million", notes)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def _safe_log(x: float, base: float = 10) -> float:
    import math
    return math.log(x + 1) if x >= 0 else 0.0


def compute_persona_scores(
    people_df: pd.DataFrame,
    country_scores: pd.DataFrame,
) -> pd.DataFrame:
    """Score individuals on the GIVER index using their country as a proxy.

    People compete in their own league (vs other people), not vs countries.
    Their score is relative to others in the people dataset.
    """
    df = people_df.copy()

    # Map geography → ISO3
    df["iso3"] = df["geography"].map(GEO_TO_ISO3)

    # Merge country-level GIVER sub-dimensions
    cscore = country_scores[[
        "iso3", "ltv", "ivr", "giver_score",
    ]].copy()
    df = df.merge(cscore, on="iso3", how="left")

    # Generative: country's LTO culture
    df["generative"] = df["ltv"].fillna(50)

    # Impact: log(net worth) — wealth as structural capacity
    df["net_worth_b"] = df["notes"].apply(_extract_net_worth)
    df["impact_raw"] = df["net_worth_b"].apply(_safe_log)
    # Min-max within people dataset for comparability
    if df["impact_raw"].notna().any():
        mn, mx = df["impact_raw"].min(), df["impact_raw"].max()
        if mx > mn:
            df["impact"] = (df["impact_raw"] - mn) / (mx - mn) * 100
        else:
            df["impact"] = 50.0
    else:
        df["impact"] = 0.0

    # Verifiable: social reach (follower count as public accountability)
    df["followers_m"] = df["notes"].apply(_extract_followers)
    df["verifiable_raw"] = df["followers_m"].fillna(0) * 1e6
    df["verifiable"] = df["verifiable_raw"]
    if df["verifiable"].notna().any():
        mn, mx = df["verifiable"].min(), df["verifiable"].max()
        if mx > mn:
            df["verifiable"] = (df["verifiable"] - mn) / (mx - mn) * 100
        else:
            df["verifiable"] = 50.0
    else:
        df["verifiable"] = 0.0

    # Evidence-based: country's WVS secular-rational score
    df["evidence_based"] = df["ltv"].fillna(50)  # proxy via LTO

    # Rooted: country's IVR + tenure proxy
    df["rooted"] = df["ivr"].fillna(50)

    # Composite (same weights as countries but recalibrated)
    df["giver_score"] = (
        df["generative"].fillna(50) * 0.20 +
        df["impact"] * 0.25 +
        df["verifiable"].fillna(0) * 0.20 +
        df["evidence_based"].fillna(50) * 0.15 +
        df["rooted"].fillna(50) * 0.20
    ).round(2)

    df["giver_dimension"] = "circular"
    df.loc[df["giver_score"] < 50, "giver_dimension"] = "linear"

    return df


def build_regional_clusters(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Group countries into UN regions ranked by GIVER score."""
    clusters = {}
    for _, row in df.iterrows():
        region = ISO3_TO_REGION.get(row["iso3"], "Other")
        if region not in clusters:
            clusters[region] = {
                "region": region,
                "countries": [],
                "avg_score": 0.0,
                "circular_count": 0,
                "linear_count": 0,
            }
        clusters[region]["countries"].append({
            "iso3": row["iso3"],
            "name": row["country_name"],
            "giver_score": row["giver_score"],
            "giver_dimension": row["giver_dimension"],
        })
        if row["giver_dimension"] == "circular":
            clusters[region]["circular_count"] += 1
        else:
            clusters[region]["linear_count"] += 1

    result = []
    for region, data in sorted(clusters.items()):
        scores = [c["giver_score"] for c in data["countries"]]
        data["avg_score"] = round(sum(scores) / len(scores), 2) if scores else 0.0
        data["countries"] = sorted(data["countries"], key=lambda x: x["giver_score"], reverse=True)
        result.append(data)

    return result


def build_archetype_labels(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Generate archetype labels + interaction hints per country."""
    archetypes = {}
    for _, row in df.iterrows():
        iso = row["iso3"]
        score = row.get("giver_score", 0) or 0.0
        dim = row.get("giver_dimension", "linear")

        # Top dimension
        dims = {
            "generative": row.get("ltv", 50) or 50,
            "impact": row.get("gdp_ppp", 0) or 0,
            "evidence_based": row.get("wvs_secular", 50) or 50,
            "rooted": row.get("ivr", 50) or 50,
        }
        top_dim = max(dims, key=dims.get) if any(dims.values()) else "impact"

        if score >= 70:
            label = "Giver Elite"
        elif score >= 55:
            label = "Giver Emerging"
        elif score >= 40:
            label = "Hybrid"
        elif score >= 25:
            label = "Linear Stagnant"
        else:
            label = "Linear Extractive"

        archetypes[iso] = {
            "label": label,
            "dimension": dim,
            "top_dimension": top_dim,
            "giver_score": round(score, 2),
            "interaction_bias": 0.1 if dim == "circular" else -0.1,
        }
    return archetypes


def generate_simulation_narrative(df: pd.DataFrame, people_df: pd.DataFrame) -> str:
    """Generate the enhanced MiroFish simulation requirement text."""
    n_countries = len(df)
    n_circular = (df["giver_dimension"] == "circular").sum()
    n_linear = n_countries - n_circular
    avg = df["giver_score"].mean()
    top5 = df.head(5)[["iso3", "country_name", "giver_score"]].values.tolist()
    bot5 = df.tail(5)[["iso3", "country_name", "giver_score"]].values.tolist()

    n_people = len(people_df)
    n_richest = (people_df["list_type"] == "richest").sum()
    n_social = (people_df["list_type"] == "social_media").sum()

    return f"""# GIVER Displacement Simulation — MiroFish Context

## Simulation Goal

Model the **GIVER Displacement Theory**: the hypothesis that linear (extraction-oriented) societies dominate in absolute scale but circular (giver-oriented) societies are growing faster in velocity and will displace them over time across key indicators.

## Agent Types

### League A — Countries ({n_countries} agents)
Each country-agent is defined by five GIVER dimensions:
- **Generative**: Delayed gratification culture (Hofstede LTO, 0–100)
- **Impact**: Structural capacity (GDP per capita PPP, log-scaled)
- **Verifiable**: Open collaboration (GitHub repos per capita — TODO)
- **Evidence-based**: Secular-rational worldview (WVS Inglehart x-axis)
- **Rooted**: Long-term ownership culture (Hofstede IVR, 0–100)

Country composite score: GIVER Index (0–100), higher = more circular.

### League B — People ({n_richest} rich agents, {n_social} influencer agents)
200 notable individuals scored by personal GIVER Index:
- **Generative**: Home country LTO culture
- **Impact**: Log(net worth in $B) as personal capacity
- **Verifiable**: Social media reach (follower count)
- **Evidence-based**: Home country WVS secular score
- **Rooted**: Home country IVR + career longevity

People compete in their own league, not against countries.

## Current World State (2025 Snapshot)

- **{n_countries} countries scored** | avg GIVER: {avg:.1f}/100
- **{n_circular} circular** | **{n_linear} linear**
- Top 5 (most circular): {", ".join(f"{c[1]}({c[0]}, {c[2]:.1f})" for c in top5)}
- Bottom 5 (most linear): {", ".join(f"{c[1]}({c[0]}, {c[2]:.1f})" for c in bot5)}

## Displacement Mechanics

### What to Simulate
1. **Resource flows** — capital, talent, attention — from linear to circular agents
2. **Threshold effects** — circular agents below 50% score face systemic headwinds (linear inertia)
3. **Velocity tracking** — measure GIVER score delta per simulation cycle
4. **Emergent clustering** — circular agents in same region reinforce each other

### Interaction Rules
- Circular × Circular: mutual amplification (+)
- Circular × Linear: competition; linear often wins on raw mass, circular wins on velocity
- Linear × Linear: consolidation, extraction dynamics
- People × Countries: people can defect to high-GIVER countries as "escape velocity" events

### Convergence Criteria
Simulation ends when:
- Global average GIVER score crosses 55 (majority circular), OR
- 10 simulation cycles complete without GIVER delta > 0.5

## Data Sources

| Feed | Coverage | Used For |
|------|----------|----------|
| Hofstede 6-D | 83 countries | Generative, Rooted |
| World Bank GDP | 239 countries | Impact |
| WVS Inglehart | ~90 countries | Evidence-based |
| Top 200 people | 200 individuals | People league |

## Seed Files

- `seed_countries.csv` — {n_countries} country agents
- `seed_people.csv` — {n_people} people agents (richest + influencers)
- `regional_clusters.json` — region groupings with intra-region rankings
- `agent_archetypes.json` — label + interaction hint per ISO3 code
"""


def export_mirofish_context(
    giver_df: pd.DataFrame,
    people_df: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    """Export the full MiroFish simulation context package."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Enhanced seed countries
    seed_df = build_seed_df(giver_df)
    countries_path = output_dir / "seed_countries.csv"
    seed_df.to_csv(countries_path, index=False)
    log.info("Wrote: %s (%d rows)", countries_path, len(seed_df))

    # 2. Seed people
    people_scored = compute_persona_scores(people_df, giver_df)
    people_cols = [
        "name", "iso3", "geography", "list_type", "giver_score", "giver_dimension",
        "generative", "impact", "verifiable", "evidence_based", "rooted",
        "net_worth_b", "followers_m",
    ]
    people_out = output_dir / "seed_people.csv"
    people_scored[[c for c in people_cols if c in people_scored.columns]].to_csv(
        people_out, index=False
    )
    log.info("Wrote: %s (%d rows)", people_out, len(people_scored))

    # 3. Regional clusters
    clusters = build_regional_clusters(giver_df)
    clusters_path = output_dir / "regional_clusters.json"
    clusters_path.write_text(json.dumps({"regions": clusters}, indent=2))
    log.info("Wrote: %s (%d regions)", clusters_path, len(clusters))

    # 4. Archetype labels
    archetypes = build_archetype_labels(giver_df)
    archetypes_path = output_dir / "agent_archetypes.json"
    archetypes_path.write_text(json.dumps({"archetypes": archetypes}, indent=2))
    log.info("Wrote: %s (%d archetypes)", archetypes_path, len(archetypes))

    # 5. Simulation narrative
    narrative = generate_simulation_narrative(giver_df, people_scored)
    narrative_path = output_dir / "simulation_narrative.md"
    narrative_path.write_text(narrative)
    log.info("Wrote: %s", narrative_path)

    # 6. Simulation config
    config = {
        "simulation": {
            "name": "GIVER Displacement Theory",
            "description": "Model the transition from linear to circular worldviews",
            "leagues": [
                {"name": "countries", "agent_file": "seed_countries.csv", "n_agents": len(seed_df)},
                {"name": "people", "agent_file": "seed_people.csv", "n_agents": len(people_scored)},
            ],
            "convergence": {
                "global_score_threshold": 55,
                "max_cycles_without_delta": 10,
                "delta_threshold": 0.5,
            },
            "weights": {
                "generative": 0.20,
                "impact": 0.25,
                "verifiable": 0.20,
                "evidence_based": 0.15,
                "rooted": 0.20,
            },
        }
    }
    config_path = output_dir / "simulation_config.yaml"
    config_path.write_text(yaml.dump(config, default_flow_style=False))
    log.info("Wrote: %s", config_path)

    return {
        "countries": countries_path,
        "people": people_out,
        "clusters": clusters_path,
        "archetypes": archetypes_path,
        "narrative": narrative_path,
        "config": config_path,
    }
