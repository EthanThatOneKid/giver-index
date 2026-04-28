## Data Visualizations — What's Live Now

*Posted by @EthanThatOneKid*

This section documents the five key charts generated from the GIVER Index 2025 pilot. All source data and generation scripts live in the [`docs/visualizations/`](https://github.com/EthanThatOneKid/giver-index/tree/main/docs/visualizations) directory.

---

### 1. Score Distribution & Coverage Tier

![Score Distribution](https://raw.githubusercontent.com/EthanThatOneKid/giver-index/main/docs/visualizations/01_distribution.png)

- **Left:** Histogram of GIVER scores for all 199 scored countries. The mean is **43.3** — the world is more linear than circular by this measure.
- **Right:** Coverage breakdown. 54 countries have strong signal (≥2 data feeds); 91 are partial; 94 have no signal (shown gray on the map).

**Key insight:** The distribution is right-skewed. Most countries score between 30–50, with a long tail below 20. Luxembourg (72.2) is a clear outlier.

---

### 2. Regional Comparison

![Regional Comparison](https://raw.githubusercontent.com/EthanThatOneKid/giver-index/main/docs/visualizations/02_regional.png)

- **Left:** Mean GIVER score by region. Europe leads at 34.9, followed by Asia-Pacific (34.5). The Americas scores mid-range; Africa shows the lowest average.
- **Right:** Box plot showing the spread within each region. Europe has the widest spread (few high performers, many mid-range). Asia-Pacific shows high variance — Japan/South Korea score 61+ while Central Asian nations score below 25.

**Key insight:** Regional averages obscure massive internal variation. "Europe" includes both Luxembourg at 72.2 and several countries below 30.

---

### 3. Top 5 Dimension Radar

![Dimension Radar](https://raw.githubusercontent.com/EthanThatOneKid/giver-index/main/docs/visualizations/03_radar.png)

Five countries with the highest composite GIVER scores, broken down by dimension. Note how different countries lead on different dimensions — no single country dominates all five. This confirms the index is capturing real multidimensional variation rather than a single general factor.

---

### 4. Signal Coverage Heatmap by Region

![Coverage Heatmap](https://raw.githubusercontent.com/EthanThatOneKid/giver-index/main/docs/visualizations/04_heatmap.png)

Average number of data signals available per dimension, by region. Higher = more data confidence. The heatmap reveals that **Impact (GDP)** is the best-covered dimension globally, while **Verifiable** (open-source/patents) is the weakest — reflecting the absence of GitHub Archive processing so far.

---

### 5. Top 20 vs Bottom 20

![Top 20 vs Bottom 20](https://raw.githubusercontent.com/EthanThatOneKid/giver-index/main/docs/visualizations/05_top_bottom.png)

Countries are heavily clustered in the 35–55 range. The bottom 20 are all below 22. This clustering suggests the scoring model is functioning — there's a clear spectrum from circular to linear archetypes — but most humanity is compressed into the middle zone.

---

## What's Next

- **GitHub Archive** (#6) → powers the `verifiable` dimension fully
- **Pew reincarnation** (#8) → adds `evidence_based` signal for Southeast Asia
- **D3 world map** → live choropleth replaces static PNGs
- **Slopometry narrative** → richer simulation prompts for MiroFish