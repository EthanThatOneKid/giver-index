## Data Visualizations — GIVER Index 2025

*Posted by @EthanThatOneKid — April 2026*

Five charts generated from the verified GIVER Index dataset (239 countries, 4 feeds).

---

### Fig 1. GIVER Score Distribution (239 countries)

![GIVER Score Distribution](docs/visualizations/01_distribution.png)

A bimodal distribution with a heavy right skew. The majority of countries cluster between 0–20 (linear archetype), while a long tail extends toward 60 (circular archetype). Luxembourg (60.6) is the most circular; most countries score below the global median of 4.2. The shape validates GIVER Displacement Theory: linear systems dominate numerically; circular systems dominate in their growth velocity.

---

### Fig 2. Mean GIVER Score by Region

![Mean GIVER Score by Region](docs/visualizations/02_regional.png)

Europe leads with a mean score of 29.4 (n=43 countries), driven by Luxembourg, Belgium, Sweden, Austria, and France. The Americas average 8.6 (n=27), Asia 6.6 (n=46), Africa 3.5 (n=47), and Oceania 3.0 (n=8). The score spread is tightest in Europe (higher LTO/IVR signal) and widest in Africa (high GDP variance, low Hofstede coverage). No regions have all countries above 50 — even Europe has a long tail of small/territorial countries scoring near zero.

---

### Fig 3. Top-10 Countries: Five-Dimension Radar

![Radar — Top 10 Countries](docs/visualizations/03_radar.png)

Shows the five GIVER dimension sub-scores (Generative, Impact, Verifiable, Evidence-based, Rooted) for the top 10 countries. Key observations: South Korea scores 100 on Generative (LTO=100 in Hofstede) but has a weak Rooted score (IVR=29). Japan and Belgium are the most balanced across all five dimensions. Sweden and Czechia have strong Evidence-based signals (WVS data available). Luxembourg, despite having no WVS/Pew data, scores highly via Generative+Impact+Rooted.

---

### Fig 4. Generative vs Evidence-Based Scatter (with GDP bubble)

![Generative vs Evidence-Based Scatter](docs/visualizations/04_heatmap.png)

Each country is plotted by its Generative (LTO) score vs Evidence-based (WVS self-expression + Pew reincarnation) score, with bubble size proportional to GDP per capita (PPP). Countries in the upper-right are strong on both dimensions — they invest long-term AND have empirical worldviews. Countries in the lower-left are linear/extractive. Notable: Japan and South Korea cluster upper-right (high LTO + high reincarnation belief). Most African and South Asian countries cluster in the lower-left (low LTO, low WVS coverage). The size of the Japan/South Korea bubbles reflects their high GDP per capita.

---

### Fig 5. Top-10 vs Bottom-10 Countries

![Top-10 vs Bottom-10](docs/visualizations/05_top_bottom.png)

Side-by-side bar charts of the top 10 most circular and bottom 10 most linear countries. The top 10 (Luxembourg → France) form a clear cluster of wealthy, high-LTO European nations plus South Korea and Japan. The bottom 10 (Sudan → Central African Republic) are all conflict-affected, low-GDP African nations — validating that the GIVER index is detecting real structural disadvantage. The gap is stark: Luxembourg scores 60.6 vs CAF at 0.02 — a 3,000× difference.

---

### How These Were Generated

```bash
# Regenerate all charts at any time
python3 docs/visualizations/generate.py

# Charts are auto-described and saved to docs/visualizations/
```

Charts use a consistent color palette: `#1a4f5c` (teal) for primary, `#c94f4f` (muted red) for contrast, `#f5d76e` (gold) for accent. All axes are labeled clearly; legends are inside the chart where possible. No emoji or regional glyphs — all regions spelled out. Zero "Unknown" labels on any chart.

---

### What's Next

- **Fig 6** — World choropleth map (GeoJSON overlay) → deploy to `etok.zo.space/giver-map`
- **Fig 7** — Dimension contribution breakdown (stacked bar) showing how each feed contributes to each country's score
- **Fig 8** — Timeline: mock historical GIVER trend using cached WVS wave data (1981–2020)