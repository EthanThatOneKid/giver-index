## Data Visualizations — What's Live Now

*Posted by @EthanThatOneKid · Pilot phase (Apr 2026)*

---

### Live artifact

**https://etok.zo.space/giver-map** — coverage-aware GIVER world map (2025 pilot)

---

### What the map shows

The map is built from the `giver-index` CLI output (`giver_index_2025.csv`), enriched with signal-count metadata per country and wired into four tabs:

| Tab | What it shows |
|-----|---------------|
| **Score** | Countries colored by GIVER score (green = circular, gray = linear/zero). Hover any country to inspect its dimension profile. |
| **Coverage** | Countries colored by evidence strength: green (4+ raw signals), amber (1-3), gray (0). Switches the color mode independently of the score tab. |
| **Regions** | Six UN region summaries — Europe, Asia, Americas, Africa, Oceania, Unknown — with average score, strong/partial/missing breakdowns, and top country per region. |
| **Method** | Signal inventory: what's wired now vs what's still pending. The honest current frontier of the model. |

---

### Signal inventory (what each country is scored on vs what it isn't)

**Wired now:**
- `ltv` — Hofstede Long Term Orientation
- `ivr` — Hofstede Indulgence vs Restraint
- `gdp_ppp` — World Bank GDP per capita PPP
- `generative` — derived from LTV (generative = min-max LTO)
- `impact` — derived from GDP per capita
- `evidence_based` — derived from WVS join (partial coverage)
- `rooted` — derived from IVR

**Still pending:**
- `self_expression` / `secular_rational` — WVS Inglehart axes (missing for most countries)
- `reincarnation_pct` — Pew afterlife belief data
- `b_corp_per_million` — B Lab certified B Corps per capita
- `repos_per_capita` — GitHub Archive events per capita
- `patents_per_million` — WIPO patent filings per capita
- `giving_rate` — charitable giving rate

---

### Current numbers

```
239 countries total
199 scored (83% coverage)
 54 strong (4+ raw signals) ← take most seriously
 91 partial (1-3 signals)  ← directional but imprecise
 94 missing (0 signals)    ← blank spots on the map
```

**Top leaders (strong coverage):**
1. Luxembourg — 72.2
2. Macao S.A.R — 65.5
3. Sweden — 62.1
4. Japan — 61.9
5. South Korea — 61.5

**By region average (strong only):**
1. Europe — 34.9 avg (38 countries, 38 strong)
2. Asia — 18.0 avg (47 countries, 11 strong)
3. Americas — 15.6 avg (27 countries, 5 strong)
4. Oceania — 9.8 avg (8 countries, 0 strong)
5. Africa — 4.8 avg (43 countries, 0 strong)

---

### What this visualization exposes honestly

The map is not a finished product. It is a coverage-aware first draft. Three things it correctly surfaces:

1. **Europe leads** not because the model is eurocentric, but because Hofstede's data covers European countries more densely — this is a data coverage story, not a civilization ranking.
2. **Most of Africa and Oceania are gray** because the feeds haven't reached them yet — these are the priority fill-in targets for the next iteration.
3. **"Score" and "Coverage" are two different maps** — a high-scoring gray country should be read as "potentially high, not yet verified" rather than "confirmed circular."

---

### Repository

All compute code: https://github.com/EthanThatOneKid/giver-index

### See also

- [GitHub Discussion #10 — Pilot Report: 2025](https://github.com/EthanThatOneKid/giver-index/discussions/10) — full methodology and data feed status
