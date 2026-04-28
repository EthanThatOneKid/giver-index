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


def compute_generative(df: pd.DataFrame) -> pd.Series:
    """Generative = Hofstede Long Term Orientation (LTO) score.

    High LTO → delayed gratification, systemic investment = circular.
    """
    col = "ltv"  # Long Term Orientation column name in Hofstede CSV
    if col not in df.columns:
        raise ValueError(f"Hofstede CSV missing column '{col}'. Available: {list(df.columns)}")
    scores = pd.to_numeric(df[col], errors="coerce")
    return min_max(scores)


def compute_impact(df: pd.DataFrame, b_corp_df: pd.DataFrame | None = None) -> pd.Series:
    """Impact = composite of structural capacity (GDP) + certified impact (B Corps)."""
    gdp_col = "gdp_ppp"  # placeholder — will come from World Bank join
    if gdp_col in df.columns:
        gdp_norm = min_max(pd.to_numeric(df[gdp_col], errors="coerce"))
    else:
        gdp_norm = pd.Series(dtype=float)

    if b_corp_df is not None and "b_corp_per_million" in b_corp_df.columns:
        b_corp_norm = min_max(pd.to_numeric(b_corp_df["b_corp_per_million"], errors="coerce"))
    else:
        b_corp_norm = pd.Series(dtype=float)

    if gdp_norm.empty and b_corp_norm.empty:
        return pd.Series(dtype=float)

    # Weighted composite: 60% GDP capacity, 40% certified impact
    combined = gdp_norm * 0.6 + b_corp_norm * 0.4 if not b_corp_norm.empty else gdp_norm
    return combined


def compute_verifiable(df: pd.DataFrame, github_df: pd.DataFrame | None = None) -> pd.Series:
    """Verifiable = log(GitHub repos per capita) + patent density.

    Signals open collaboration + verifiable invention.
    """
    github_norm = pd.Series(dtype=float)
    patent_norm = pd.Series(dtype=float)

    if github_df is not None and "repos_per_capita" in github_df.columns:
        repos_log = safe_log(pd.to_numeric(github_df["repos_per_capita"], errors="coerce"))
        github_norm = min_max(repos_log)

    patent_col = "patents_per_million"  # from WIPO / World Bank
    if df is not None and patent_col in df.columns:
        patent_norm = min_max(pd.to_numeric(df[patent_col], errors="coerce"))

    if github_norm.empty and patent_norm.empty:
        return pd.Series(dtype=float)

    return github_norm * 0.5 + patent_norm * 0.5 if not patent_norm.empty else github_norm


def compute_evidence_based(df: pd.DataFrame, pew_df: pd.DataFrame | None = None) -> pd.Series:
    """Evidence-based = WVS self-expression score + Pew reincarnation belief.

    Self-expression → empirical worldview; reincarnation belief → circular karmic lens.
    """
    wvs_col = "self_expression"  # from WVS Inglehart scale
    wvs_norm = pd.Series(dtype=float)
    pew_norm = pd.Series(dtype=float)

    if df is not None and wvs_col in df.columns:
        wvs_norm = min_max(pd.to_numeric(df[wvs_col], errors="coerce"))

    if pew_df is not None and "reincarnation_pct" in pew_df.columns:
        pew_norm = min_max(pd.to_numeric(pew_df["reincarnation_pct"], errors="coerce"))

    if wvs_norm.empty and pew_norm.empty:
        return pd.Series(dtype=float)

    return wvs_norm * 0.6 + pew_norm * 0.4 if not pew_norm.empty else wvs_norm


def compute_rooted(df: pd.DataFrame, giving_df: pd.DataFrame | None = None) -> pd.Series:
    """Rooted = Hofstede Indulgence vs Restraint (IVR) + charitable giving rate.

    High IVR + high giving = legacy-building, not extractive.
    """
    ivr_col = "ivr"  # Indulgence vs Restraint from Hofstede
    ivr_norm = pd.Series(dtype=float)
    giving_norm = pd.Series(dtype=float)

    if df is not None and ivr_col in df.columns:
        ivr_norm = min_max(pd.to_numeric(df[ivr_col], errors="coerce"))

    if giving_df is not None and "giving_rate_pct" in giving_df.columns:
        giving_norm = min_max(pd.to_numeric(giving_df["giving_rate_pct"], errors="coerce"))

    if ivr_norm.empty and giving_norm.empty:
        return pd.Series(dtype=float)

    return ivr_norm * 0.5 + giving_norm * 0.5 if not giving_norm.empty else ivr_norm


# ---------------------------------------------------------------------------
# Composite GIVER score
# ---------------------------------------------------------------------------

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
    """Compute composite GIVER index for a country DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: iso3 (country code), country_name,
        and dimension sub-scores or source data for each dimension.
    weights : dict, optional
        Override default dimension weights.

    Returns
    -------
    pd.Series
        GIVER index (0–100) per country, indexed by iso3.
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    components = {}

    # Generative — requires Hofstede LTO
    if "ltv" in df.columns:
        components["generative"] = min_max(pd.to_numeric(df["ltv"], errors="coerce"))

    # Impact — GDP + B Corps
    components["impact"] = compute_impact(df)

    # Verifiable — GitHub + patents
    components["verifiable"] = compute_verifiable(df)

    # Evidence-based — WVS + Pew
    components["evidence_based"] = compute_evidence_based(df)

    # Rooted — IVR + giving
    components["rooted"] = compute_rooted(df)

    # Build composite, skipping missing dimensions
    score = pd.Series(0.0, index=df.index)
    total_weight = 0.0

    for dim, weight in w.items():
        if dim in components and not components[dim].empty:
            score = score.add(components[dim].fillna(0) * weight, fill_value=0)
            total_weight += weight

    if total_weight > 0 and total_weight < 1.0:
        score = score / total_weight  # renormalize if some dims missing

    return score.clip(0, 100).round(2)
