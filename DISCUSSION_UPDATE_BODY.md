## Live Dashboard

**→ https://etok.zo.space/giver-map**

A cinematic, source-cited infographic experience built on the GIVER Index data pipeline.

---

## What's New (2026-04-28)

### Cinematic Redesign

The dashboard has been rebuilt as a narrative artifact, not just a dashboard:

- **Animated aurora background** — subtle pulsing gradient that sets a reflective, contemplative tone
- **Staged story cards** — the page opens with a scrollable narrative sequence that introduces each dimension before revealing the data
- **Live choropleth atlas** — countries rendered as colored SVG paths on a natural-earth projection, colored by GIVER score
- **Coverage-aware country panel** — shows signal strength (records available per country) alongside the score
- **Regional summary strip** — a horizontal bar chart showing mean GIVER score by region (Africa, Americas, Asia, Europe, Oceania)
- **On-page source ledger** — every dimension explicitly cites its upstream source with a link
- **Responsive dark theme** — full-bleed dark surface with accent colors keyed to circular/linear archetype

### Data Pipeline Fixes

- Pew reincarnation data now normalized **within the Pew sample only** (not against all countries) — prevents scores from being artificially deflated by countries with zero Buddhist/universalist afterlife belief
- Region assignment now covers all **239 countries** — only uninhabited Antarctic territories remain "Unknown"
- GeoJSON SVG paths now derived from world-atlas 110m (44 KB TopoJSON → 258 features) — enables choropleth rendering
- API returns: `updatedAt`, `sources`, regional summaries, and `coverage_tier` per country

### API Improvements

`/api/giver-map-data` now returns:
- `updatedAt` — ISO timestamp of last data refresh
- `sources` — array of `{name, url, license, description}` for all upstream feeds
- `regions` — per-region `{name, count, avgScore}` summary
- `records` — full country array with `signal_count`, `coverage_tier`, `giver_dimension`
- `top` / `bottom` — filtered by `giver_dimension === "circular"` / `"linear"`

---

## Generated Figures (Updated)

| Figure | Description |
|--------|-------------|
| Fig 1 | Distribution of GIVER scores across 239 countries — all fall below 50 (linear archetype dominant in all countries on current data) |
| Fig 2 | Top 10 / Bottom 10 countries ranked by GIVER score |
| Fig 3 | Mean GIVER score by region — Africa lowest, Europe highest |
| Fig 4 | Box plot of score spread by region |
| Fig 5 | Spider/radar chart — Belgium (top country) dimension profile |
| Fig 6 | Choropleth world map — live at etok.zo.space/giver-map |

---

## Current Coverage

| Feed | Countries | Coverage |
|------|-----------|----------|
| Hofstede LTO + IVR | 101 | 42% |
| World Bank GDP PPP | 197 | 82% |
| Pew Reincarnation | 43 | 18% |
| WVS Secular values | 77 | 32% |

---

## Open Issues / Next Steps

1. **WVS replication** — ZA7503 EVS/WVS trend file requires manual registration; investigate bulk access
2. **GitHub Archive** — aggregate public GitHub event data per country for the Verifiable dimension
3. **B Corp scraper** — unverified scraper endpoint; need a reliable per-country B Corp count source
4. **People League** — two-league framework designed (countries + individuals) but not yet surfaced in the UI
5. **Slopometry integration** — the GIVER output feeds into MiroFish agent-simulation context; needs a live MiroFish deployment to consume it

---

*Last updated: 2026-04-28 · Data: Hofstede (101 countries), World Bank (197), Pew (43), WVS (77) · Pipeline: Python CLI + Zo Space API*