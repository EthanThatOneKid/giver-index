#!/usr/bin/env python3
"""Generate all GIVER Index visualizations for the GitHub Discussion."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

OUT_DIR = Path(__file__).parent


def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        "/home/workspace/code/github.com/EthanThatOneKid/giver-index/data/outputs/giver_index_2025.csv"
    )
    df.columns = [c.strip() for c in df.columns]
    # Add source counts
    df["signal_count"] = (
        df[["ltv", "ivr", "gdp_ppp", "self_expression", "secular_rational"]]
        .notna()
        .sum(axis=1)
    )
    # Coverage tier
    def tier(row):
        if row.get("giver_score") and row["giver_score"] > 0:
            return "Strong (≥2 signals)" if row["signal_count"] >= 2 else "Partial (1 signal)"
        return "No Signal"
    df["coverage_tier"] = df.apply(tier, axis=1)
    return df


def fmt_region(r: str) -> str:
    """Human-readable region labels."""
    return {
        "Africa": "Africa",
        "Americas": "Americas",
        "Asia": "Asia",
        "Europe": "Europe",
        "Oceania": "Oceania",
        "No Signal": "No Signal",
    }.get(r, r)


def plot_01_distribution(df: pd.DataFrame) -> None:
    """Score distribution + coverage tier breakdown."""
    scored = df[df["giver_score"] > 0]
    tiers = scored["coverage_tier"].value_counts()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("GIVER Index 2025 — Score Distribution & Data Coverage", fontsize=14, fontweight="bold", y=1.02)

    # --- Left: histogram ---
    ax = axes[0]
    bins = np.arange(0, 105, 5)
    n, bins_out, patches = ax.hist(scored["giver_score"], bins=bins, color="#4C6EF5", edgecolor="white", linewidth=0.5)
    ax.axvline(scored["giver_score"].mean(), color="#FA5252", linestyle="--", linewidth=1.8, label=f"Mean = {scored['giver_score'].mean():.1f}")
    ax.axvline(50, color="#20C997", linestyle=":", linewidth=1.8, label="Circular/Linear Threshold = 50")
    ax.set_xlabel("GIVER Score", fontsize=11)
    ax.set_ylabel("Number of Countries", fontsize=11)
    ax.set_title("Distribution of Scores Across All 199 Scored Countries", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, max(n) * 1.15)
    ax.text(0.97, 0.95, f"n = {len(scored)} countries", transform=ax.transAxes,
            ha="right", va="top", fontsize=9, color="gray")

    # --- Right: coverage pie ---
    ax2 = axes[1]
    tier_labels = ["Strong\n(≥2 data signals)", "Partial\n(1 signal)", "No Signal\n(score = 0)"]
    tier_colors = ["#51CF66", "#FFE066", "#C92A2A"]
    tier_order = ["Strong (≥2 signals)", "Partial (1 signal)", "No Signal"]
    vals = [tiers.get(t, 0) for t in tier_order]
    wedges, texts, autotexts = ax2.pie(
        vals,
        labels=tier_labels,
        colors=tier_colors,
        autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
        startangle=90,
        textprops={"fontsize": 10},
    )
    ax2.set_title("Data Signal Coverage", fontsize=11)
    ax2.text(0, -1.35,
             f"Strong: {tiers.get('Strong (≥2 signals)', 0)} countries | "
             f"Partial: {tiers.get('Partial (1 signal)', 0)} countries | "
             f"No Signal: {tiers.get('No Signal', 0)} countries",
             ha="center", fontsize=9, color="gray")

    plt.tight_layout()
    out = OUT_DIR / "01_distribution.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"✓ {out.name}")
    plt.close()
    return out


def plot_02_regional_comparison(df: pd.DataFrame) -> None:
    """Mean score by region + box spread — all 6 regions shown explicitly."""
    scored = df[df["giver_score"] > 0].copy()
    # Map empty region → "No Signal"
    scored["region"] = scored["region"].fillna("").replace("", "No Signal")

    ALL_REGIONS = ["Europe", "Asia", "Americas", "Africa", "Oceania", "No Signal"]
    REGION_COLORS = {
        "Europe": "#4C6EF5",
        "Asia": "#20C997",
        "Americas": "#FFE066",
        "Africa": "#FA5252",
        "Oceania": "#9775FA",
        "No Signal": "#868E96",
    }
    # Sort regions by mean (descending)
    means = scored.groupby("region")["giver_score"].mean().reindex(ALL_REGIONS).sort_values(ascending=False)
    order = means.index.tolist()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("GIVER Index 2025 — Regional Comparison", fontsize=14, fontweight="bold", y=1.02)

    # Left: mean bar chart
    ax = axes[0]
    colors = [REGION_COLORS[r] for r in order]
    bars = ax.bar([fmt_region(r) for r in order], means[order], color=colors, edgecolor="white", linewidth=0.7)
    ax.axhline(50, color="#20C997", linestyle=":", linewidth=1.8, label="Circular threshold (50)")
    ax.axhline(scored["giver_score"].mean(), color="gray", linestyle="--", linewidth=1.2, label=f"Global mean ({scored['giver_score'].mean():.1f})")
    for bar, val in zip(bars, means[order]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.1f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Mean GIVER Score", fontsize=11)
    ax.set_title("Mean Score by Region (all 6 regions shown)", fontsize=11)
    ax.set_ylim(0, 80)
    ax.legend(fontsize=9)
    ax.tick_params(axis="x", labelsize=9)

    # Right: box plot
    ax2 = axes[1]
    box_data = [scored[scored["region"] == r]["giver_score"].values for r in order]
    bp = ax2.boxplot(box_data, patch_artist=True, tick_labels=[fmt_region(r) for r in order])
    for patch, region in zip(bp["boxes"], order):
        patch.set_facecolor(REGION_COLORS[region])
        patch.set_alpha(0.7)
    ax2.axhline(50, color="#20C997", linestyle=":", linewidth=1.8, label="Circular threshold (50)")
    ax2.set_ylabel("GIVER Score", fontsize=11)
    ax2.set_title("Score Distribution by Region (box plot)", fontsize=11)
    ax2.tick_params(axis="x", labelsize=9)
    ax2.legend(fontsize=9)

    plt.tight_layout()
    out = OUT_DIR / "02_regional.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"✓ {out.name}")
    plt.close()
    return out


def plot_03_radar(df: pd.DataFrame) -> None:
    """Radar chart for top 5 + bottom 5 countries across 5 dimensions."""
    scored = df[df["giver_score"] > 0].sort_values("giver_score", ascending=False)
    top5 = scored.head(5)
    bottom5 = scored.tail(5)

    DIMENSIONS = ["generative", "impact", "verifiable", "evidence_based", "rooted"]
    DIM_LABELS = ["G\nGenerative", "I\nImpact", "V\nVerifiable", "E\nEvidence-based", "R\nRooted"]
    N_DIMS = len(DIMENSIONS)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), subplot_kw=dict(polar=True))
    fig.suptitle("GIVER Index 2025 — Dimension Breakdown: Top 5 vs Bottom 5 Countries", fontsize=14, fontweight="bold", y=1.05)

    angles = np.linspace(0, 2 * np.pi, N_DIMS, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    PALETTE = ["#4C6EF5", "#20C997", "#9775FA", "#FA5252", "#FFE066"]
    BOTTOM_PALETTE = ["#868E96", "#ADB5BD", "#CED4DA", "#DEE2E6", "#E9ECEF"]

    def plot_radar(ax, countries, palette, title):
        for i, (_, row) in enumerate(countries.iterrows()):
            vals = [float(row.get(d, 0) or 0) for d in DIMENSIONS]
            vals += vals[:1]
            label = f"{row['iso3']} ({row['giver_score']:.0f})"
            ax.plot(angles, vals, color=palette[i], linewidth=1.5, label=label)
            ax.fill(angles, vals, color=palette[i], alpha=0.07)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(DIM_LABELS, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color="gray")
        ax.set_title(title, fontsize=11, fontweight="bold", pad=15)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)

    plot_radar(axes[0], top5, PALETTE, "Top 5 Most Circular Countries")
    plot_radar(axes[1], bottom5, BOTTOM_PALETTE, "Bottom 5 Most Linear Countries")

    plt.tight_layout()
    out = OUT_DIR / "03_radar.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"✓ {out.name}")
    plt.close()
    return out


def plot_04_signal_heatmap(df: pd.DataFrame) -> None:
    """Heatmap: mean number of data signals per dimension per region."""
    scored = df[df["giver_score"] > 0].copy()
    scored["region"] = scored["region"].fillna("").replace("", "No Signal")

    DIMENSIONS = ["generative", "impact", "verifiable", "evidence_based", "rooted"]
    DIM_HUMAN = {
        "generative": "G – Generative\n(Hofstede LTO)",
        "impact": "I – Impact\n(GDP per capita)",
        "verifiable": "V – Verifiable\n(GitHub + patents)",
        "evidence_based": "E – Evidence-based\n(WVS secular/survival)",
        "rooted": "R – Rooted\n(Hofstede IVR)",
    }

    SIGNAL_COLS = ["ltv", "gdp_ppp", "github_repos_per_million", "self_expression", "secular_rational", "ivr"]
    DIM_SIGNAL_MAP = {
        "generative": "ltv",
        "impact": "gdp_ppp",
        "verifiable": "github_repos_per_million",
        "evidence_based": "self_expression",
        "rooted": "ivr",
    }

    ALL_REGIONS = sorted(scored["region"].unique())
    mat = np.zeros((len(DIMENSIONS), len(ALL_REGIONS)))
    dim_labels_h = [DIM_HUMAN[d] for d in DIMENSIONS]

    for j, region in enumerate(ALL_REGIONS):
        for i, dim in enumerate(DIMENSIONS):
            col = DIM_SIGNAL_MAP[dim]
            if col in df.columns:
                vals = scored[scored["region"] == region][col].dropna()
                mat[i, j] = len(vals) / max(len(scored[scored["region"] == region]), 1)

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(mat, cmap="YlGn", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(ALL_REGIONS)))
    ax.set_xticklabels([fmt_region(r) for r in ALL_REGIONS], fontsize=10, rotation=30, ha="right")
    ax.set_yticks(range(len(DIMENSIONS)))
    ax.set_yticklabels(dim_labels_h, fontsize=10)
    ax.set_title("Data Signal Coverage Heatmap: Signals Available per Dimension by Region\n(Darker green = more countries have this signal | Max 100%)", fontsize=12, fontweight="bold", pad=12)

    cbar = plt.colorbar(im, ax=ax, shrink=0.6)
    cbar.set_label("% of countries in region with this signal", fontsize=9)
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

    # Annotate cells
    for i in range(len(DIMENSIONS)):
        for j in range(len(ALL_REGIONS)):
            val = mat[i, j]
            color = "white" if val > 0.6 else "black"
            ax.text(j, i, f"{val:.0%}", ha="center", va="center", fontsize=9, color=color, fontweight="bold")

    plt.tight_layout()
    out = OUT_DIR / "04_heatmap.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"✓ {out.name}")
    plt.close()
    return out


def plot_05_top_bottom(df: pd.DataFrame) -> None:
    """Horizontal bar chart — top 20 vs bottom 20 countries."""
    scored = df[df["giver_score"] > 0].sort_values("giver_score", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(15, 10))
    fig.suptitle("GIVER Index 2025 — Top 20 vs Bottom 20 Countries", fontsize=14, fontweight="bold", y=0.92)

    # Color by tier
    def bar_color(score):
        if score >= 60: return "#4C6EF5"   # deep blue — strong circular
        if score >= 50: return "#20C997"   # teal — circular borderline
        if score >= 35: return "#FFE066"   # yellow — moderate linear
        if score >= 20: return "#FF922B"   # orange — linear
        return "#FA5252"                    # red — extreme linear

    def plot_side(ax, countries, title):
        n = len(countries)
        y_pos = np.arange(n)
        scores = countries["giver_score"].values
        colors = [bar_color(s) for s in scores]
        bars = ax.barh(y_pos, scores, color=colors, edgecolor="white", linewidth=0.5, height=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['iso3']}  " for _, row in countries.iterrows()], fontsize=7)
        ax.set_xlabel("GIVER Score", fontsize=11)
        ax.set_xlim(0, 105)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.axvline(50, color="#20C997", linestyle=":", linewidth=1.5, label="Threshold 50")
        ax.invert_yaxis()
        for bar, score in zip(bars, scores):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{score:.1f}", va="center", fontsize=7, color="gray")
        ax.legend(fontsize=8)

    top20 = scored.head(20).iloc[::-1]  # flip so #1 is on top
    bottom20 = scored.tail(20)

    plot_side(axes[0], top20, "Top 20 Most Circular")
    plot_side(axes[1], bottom20, "Bottom 20 Most Linear")

    # Legend
    legend_elements = [
        mpatches.Patch(color="#4C6EF5", label="≥60 Strong Circular"),
        mpatches.Patch(color="#20C997", label="50–59 Circular"),
        mpatches.Patch(color="#FFE066", label="35–49 Moderate Linear"),
        mpatches.Patch(color="#FF922B", label="20–34 Linear"),
        mpatches.Patch(color="#FA5252", label="<20 Extreme Linear"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=5, fontsize=9,
               bbox_to_anchor=(0.5, 0.01), frameon=False)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.05, hspace=0.25)
    out = OUT_DIR / "05_top_bottom.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"✓ {out.name}")
    plt.close()
    return out


if __name__ == "__main__":
    df = load_data()
    outs = []
    for plot_fn in [plot_01_distribution, plot_02_regional_comparison, plot_03_radar, plot_04_signal_heatmap, plot_05_top_bottom]:
        outs.append(plot_fn(df))
    print("\nAll done.")
