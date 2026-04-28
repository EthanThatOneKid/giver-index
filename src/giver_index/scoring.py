"""Component scoring functions for each GIVER dimension."""

from __future__ import annotations

import math

import pandas as pd


def z_score(series: pd.Series, eps: float = 1e-8) -> pd.Series:
    """Standard z-score normalization."""
    return (series - series.mean()) / (series.std() + eps)


def min_max(series: pd.Series) -> pd.Series:
    """Min-max normalization to [0, 100]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(50.0, index=series.index)
    return (series - mn) / (mx - mn) * 100


def safe_log(series: pd.Series, base: float = math.e) -> pd.Series:
    """Log transform with +1 safety offset."""
    return series.apply(lambda x: math.log(x + 1) if pd.notna(x) and x >= 0 else math.nan)


def _has_data(series: pd.Series) -> bool:
    """Return True if the series has at least one non-NaN value."""
    return series.notna().any()


def compute_generative(df: pd.DataFrame) -> pd.Series:
    """Generative = Hofstede Long Term Orientation (LTO) score.

    High LTO → delayed gratification, systemic investment = circular.
    """
    if "ltv" not in df.columns:
        return pd.Series(dtype=float)
    scores = pd.to_numeric(df["ltv"], errors="coerce")
    if scores.isna().all():
        return pd.Series(dtype=float)
    return min_max(scores)


def compute_impact(df: pd.DataFrame, b_corp_df: pd.DataFrame | None = None) -> pd.Series:
    """Impact = composite of structural capacity (GDP) + certified impact (B Corps)."""
    gdp_norm = pd.Series(dtype=float)
    b_corp_norm = pd.Series(dtype=float)

    if "gdp_ppp" in df.columns:
        vals = pd.to_numeric(df["gdp_ppp"], errors="coerce")
        if vals.notna().any():
            gdp_norm = min_max(vals)

    if b_corp_df is not None and "b_corp_per_million" in b_corp_df.columns:
        vals = pd.to_numeric(b_corp_df["b_corp_per_million"], errors="coerce")
        if vals.notna().any():
            b_corp_norm = min_max(vals)

    if not _has_data(gdp_norm) and not _has_data(b_corp_norm):
        return pd.Series(dtype=float)

    if _has_data(b_corp_norm):
        return gdp_norm * 0.6 + b_corp_norm * 0.4
    return gdp_norm


def compute_verifiable(df: pd.DataFrame, github_df: pd.DataFrame | None = None) -> pd.Series:
    """Verifiable = log(GitHub repos per capita) + patent density."""
    github_norm = pd.Series(dtype=float)
    patent_norm = pd.Series(dtype=float)

    if github_df is not None and "repos_per_capita" in github_df.columns:
        vals = pd.to_numeric(github_df["repos_per_capita"], errors="coerce").dropna()
        if vals.any():
            github_norm = min_max(vals)

    if "patents_per_million" in df.columns:
        vals = pd.to_numeric(df["patents_per_million"], errors="coerce")
        if vals.notna().any():
            patent_norm = min_max(vals)

    if not _has_data(github_norm) and not _has_data(patent_norm):
        return pd.Series(dtype=float)

    if _has_data(patent_norm):
        return github_norm * 0.5 + patent_norm * 0.5
    return github_norm


def compute_evidence_based(df: pd.DataFrame, pew_df: pd.DataFrame | None = None) -> pd.Series:
    """Evidence-based = WVS self-expression score + Pew reincarnation belief.

    Both dimensions are normalized across ALL 239 countries (not just the
    subset with data), so a country with no WVS score still gets a fair
    evidence_based score from its reincarnation belief, and vice versa.
    """
    wvs_norm = pd.Series(dtype=float)
    pew_norm = pd.Series(dtype=float)

    if "self_expression" in df.columns:
        vals = pd.to_numeric(df["self_expression"], errors="coerce")
        if vals.notna().any():
            wvs_norm = min_max(vals)

    if pew_df is not None and "reincarnation_pct_normalized" in pew_df.columns:
        vals = pd.to_numeric(pew_df["reincarnation_pct_normalized"], errors="coerce")
        if vals.notna().any():
            pew_norm = vals.dropna()
    elif "reincarnation_pct" in df.columns:
        vals = pd.to_numeric(df["reincarnation_pct"], errors="coerce")
        if vals.notna().any():
            pew_norm = min_max(vals)

    if not _has_data(wvs_norm) and not _has_data(pew_norm):
        return pd.Series(dtype=float)

    if _has_data(pew_norm):
        return wvs_norm * 0.6 + pew_norm * 0.4 if _has_data(wvs_norm) else pew_norm
    return wvs_norm


def compute_rooted(df: pd.DataFrame, giving_df: pd.DataFrame | None = None) -> pd.Series:
    """Rooted = Hofstede Indulgence vs Restraint (IVR) + charitable giving rate."""
    ivr_norm = pd.Series(dtype=float)
    giving_norm = pd.Series(dtype=float)

    if "ivr" in df.columns:
        vals = pd.to_numeric(df["ivr"], errors="coerce")
        if vals.notna().any():
            ivr_norm = min_max(vals)

    if giving_df is not None and "giving_rate_pct" in giving_df.columns:
        vals = pd.to_numeric(giving_df["giving_rate_pct"], errors="coerce")
        if vals.notna().any():
            giving_norm = min_max(vals)

    if not _has_data(ivr_norm) and not _has_data(giving_norm):
        return pd.Series(dtype=float)

    if _has_data(giving_norm):
        return ivr_norm * 0.5 + giving_norm * 0.5
    return ivr_norm


DEFAULT_WEIGHTS = {
    "generative": 0.20,
    "impact": 0.25,
    "verifiable": 0.20,
    "evidence_based": 0.15,
    "rooted": 0.20,
}


def compute_giver_index(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.Series:
    """Compute composite GIVER index (0–100) per country."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    components = {}

    components["generative"] = compute_generative(df)
    components["evidence_based"] = compute_evidence_based(df)
    components["rooted"] = compute_rooted(df)
    components["impact"] = compute_impact(df)
    components["verifiable"] = compute_verifiable(df)

    score = pd.Series(0.0, index=df.index)
    total_weight = 0.0

    for dim, weight in w.items():
        s = components.get(dim)
        if s is not None and _has_data(s):
            score = score.add(s.fillna(0) * weight, fill_value=0)
            total_weight += weight

    if total_weight > 0 and total_weight < 1.0:
        score = score / total_weight

    return score.clip(0, 100).round(2)
