"""Slopometry export — format GIVER scores as MiroFish seed data."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from .scoring import DEFAULT_WEIGHTS

log = logging.getLogger(__name__)

# MiroFish agent property names
MIROFISH_SCHEMA = [
    "id",
    "name",
    "type",
    "giver_score",
    "giver_dimension",
    "generative",
    "impact",
    "verifiable",
    "evidence_based",
    "rooted",
    "ltv",
    "ivr",
    "region",
    "archetype_traits",
]


def build_seed_df(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape GIVER output into MiroFish agent-seed format."""
    seed = df.copy()
    seed = seed.rename(columns={"country_name": "name"})
    seed["id"] = seed["iso3"]
    seed["type"] = "country"

    for dim in ["generative", "impact", "verifiable", "evidence_based", "rooted"]:
        if dim not in seed.columns:
            seed[dim] = 0.0

    seed["archetype_traits"] = seed.apply(
        lambda r: json.dumps({
            "circular": r["giver_dimension"] == "circular",
            "score": float(r["giver_score"]),
            "top_dimension": _top_dim(r),
        }),
        axis=1,
    )

    cols = [c for c in MIROFISH_SCHEMA if c in seed.columns]
    seed = seed[cols].sort_values("giver_score", ascending=False).reset_index(drop=True)
    return seed


def _top_dim(row: pd.Series) -> str:
    dims = {d: row.get(d, 0) for d in ["generative", "impact", "verifiable", "evidence_based", "rooted"]}
    return max(dims, key=dims.get) if dims else "unknown"


def generate_narrative(year: int, top_n: int = 10) -> str:
    """Generate the MiroFish simulation requirement text."""
    lines = [
        "You are modelling the global GIVER Index shift from linear to circular archetypes.",
        "",
        "## Context",
        "The GIVER Index (Generative · Impact · Verifiable · Evidence-based · Rooted) is an open standard measuring how much a country operates in circular vs. linear paradigms. Circular societies prioritize long-term legacy, verifiable outcomes, and systemic well-being. Linear societies optimize for short-term extraction and performative output.",
        "",
        "## Agents",
        "Each agent is a country with the following properties:",
        "  - giver_score (0–100): composite GIVER index. Higher = more circular.",
        "  - giver_dimension: 'circular' if score >= 50, else 'linear'.",
        "  - generative: Long-Term Orientation (Hofstede) — delayed gratification, systemic investment.",
        "  - impact: Structural capacity for path-clearing (GDP + B Corps — placeholder).",
        "  - verifiable: Open collaboration and invention (GitHub + patents — placeholder).",
        "  - evidence_based: Empirical worldview and karmic belief (WVS + Pew — placeholder).",
        "  - rooted: Legacy-building, not extractive (IVR + charitable giving — placeholder).",
        "  - ltv / ivr: Raw Hofstede sub-scores.",
        "  - archetype_traits: JSON blob with behavioral metadata.",
        "",
        "## Simulation Goal",
        "Model the GIVER Displacement Theory: linear systems dominate in absolute scale, but circular systems show higher velocity and acceleration. Identify which countries are inflection points — where the shift from linear to circular accelerates.",
        "",
        "## Specific Questions",
        "1. Which countries show the highest GIVER velocity (rate of score change over simulated time)?",
        "2. Where does the 'Shadow Tax' of linear archetypes most severely drag down circular growth?",
        "3. Which circular countries are most 'contagious' — spreading GIVER norms to neighbours?",
        "4. What are the threshold conditions that trigger a mass shift from linear to circular?",
        "",
        "## Output",
        "Return a prediction report identifying:",
        "- Top 10 countries by GIVER velocity",
        "- Top 5 countries most resistant to circular shift",
        "- Key tipping-point countries that, if they shift, cascade others",
        "- Estimated timeline for global circularity to exceed 50%",
    ]
    return "\n".join(lines)
