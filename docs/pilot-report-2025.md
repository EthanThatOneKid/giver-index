## GIVER Index Pilot Report — 2025

*Posted by @EthanThatOneKid | April 2026*

---

## tl;dr

We built a live GIVER Index pipeline (83 countries scored, 238 total in scope) and found that the circular/linear divide is real and measurable — but our current data coverage is thin enough that the rankings are more illustrative than definitive. The gaps are the story.

---

## What is the GIVER Index?

The GIVER Index (Generative · Impact · Verifiable · Evidence-based · Rooted) is an open standard for measuring how much a society or individual operates in a **circular** (legacy-building, high-impact, verifiable) paradigm versus a **linear** (extractive, performative, short-term) one.

It is part of the broader Agenticracy ecosystem — a set of open standards for responsible human-AI co-creation.

### Dimensions

| Dimension | Signal | Data Source |
|---|---|---|
| **Generative** | Long-term orientation, quiet excellence | Hofstede LTO |
| **Impact** | Path-clearing, structural capacity | World Bank GDP (pending) |
| **Verifiable** | Open collaboration, real-world results | GitHub Archive (pending) |
| **Evidence-based** | Empirical worldview, self-expression | WVS self-expression index |
| **Rooted** | Legacy-building, charitable orientation | Hofstede IVR + Giving USA (pending) |

---

## Current Status

**83 countries** have at least one scored dimension. The composite GIVER score is currently computed from Hofstede LTV + IVR (generative, rooted) and WVS self-expression (evidence-based). The remaining dimensions (impact, verifiable) are stubs pending data.

**~155 countries** have no scored data and score 0 by default.

---

## Top Scorers (as of 2025 pilot)

| Rank | Country | GIVER Score | Archetype |
|---|---|---|---|
| 1 | Belgium | 69.1 | Circular |
| 2 | Japan | 65.5 | Circular |
| 3 | Sweden | 64.5 | Circular |
| 4 | Austria | 60.7 | Circular |
| 5 | South Korea | ~58.0 | Circular |

These align with intuition — East Asian and Northern European societies that invest structurally, score high on self-expression, and build for the long term.

---

## Key Findings

### 1. Hofstede has real coverage holes

Of 111 Hofstede countries, only **83 map cleanly to ISO3 codes**. Missing high-value countries include Switzerland, Netherlands, Ireland, Denmark, Greece, Portugal, and Bulgaria.

These are precisely the kind of wealthy, structurally-oriented societies that should score highly on the circular archetype. Without them, the rankings are systematically incomplete.

### 2. WVS fills many gaps — but is not a perfect substitute

The Inglehart/WVS self-expression index covers **151 countries** including 55+ that Hofstede misses. Countries like Chile, Turkey, and Cyprus went from 0 to meaningful scores once WVS was wired into evidence_based. However, WVS measures something slightly different from Hofstede LTO (values orientation vs. long-term institutional investment), so mixing sources introduces methodological noise.

### 3. The circular/linear split is coarse and data-dependent

At a threshold of 50:
- ~28 countries score as circular
- ~10 countries score as linear
- ~205 countries score 0 (no data)

The countries scoring 0 are not necessarily "most linear" — they are data-invisible. The current distribution mostly separates "data-rich" countries from the rest, not genuinely measuring civilizational tilt.

### 4. The gaps are where the story lives

A country like Nigeria or Vietnam scoring 0 does not reflect reality — it reflects that we have no WVS or Hofstede signal for them in our current pipeline. Filling in World Bank, Pew, and GitHub data would bring 150+ additional countries into scope and dramatically change the picture.

---

## What We Have Built

The CLI and pipeline are live at github.com/EthanThatOneKid/giver-index:

- `giver-index compute --year 2025` — compute all scores
- `giver-index inspect --year 2025` — view rankings
- `giver-index export --year 2025` — JSON / GeoJSON export
- `giver-index export-slopometry` — MiroFish seed format

---

## What's Missing (and Why It Matters)

**Impact dimension (World Bank GDP per capita) — ~200 countries missing.** GDP per capita is a strong proxy for a society's structural capacity to do path-clearing work. Without it, countries like Singapore or UAE — which have enormous impact capacity but mixed GIVER signals — are invisible.

**Verifiable dimension (GitHub Archive per-capita) — not yet wired.** Open-source activity is a concrete signal of verifiable, generative output. The challenge is that GH Archive is large (hourly JSON.GZ files) and needs a per-capita normalization strategy.

**Evidence-based: Pew reincarnation/belief data — ~40 countries covered.** Pew Research data on afterlife beliefs (reincarnation, karmic cycles) is a direct circular-archetype marker. Needs wiring.

**Rooted: Giving USA / charitable giving rates — pending.** Charitable giving rate is a direct signal of rooted, legacy-building orientation.

---

## Roadmap

1. **World Bank GDP per capita** — fills impact for 200+ countries
2. **World map visualization** — public-facing dashboard at etok.zo.space/giver-map
3. **Pew reincarnation data** — adds ~40 countries to evidence_based
4. **GitHub Archive per-capita** — concrete verifiable signal for open-society countries
5. **MiroFish seed export** — plug scores directly into agent-based simulation

---

## Methodology Notes

- **Normalization:** Each dimension is min-max scaled to [0, 100] within the available dataset. Countries with no data receive a score of 0.
- **Composite:** Weighted average (G:20%, I:25%, V:20%, E:15%, R:20%). Missing dimensions are excluded and the score is renormalized.
- **Threshold:** Countries scoring 50 or above are labeled "circular"; below 50 are "linear." This threshold is illustrative — it will be recalibrated as more dimensions are populated.
- **Sources:** Hofstede 6-D (2015), World Values Survey Wave 6 (Inglehart self-expression index). Both are publicly available but require parsing from non-standard formats.

---

## Contributing

This is an open project. If you have access to clean World Bank, Pew, or GitHub aggregate data, knowledge of Hofstede code mappings we missed, or thoughts on the scoring methodology — open an issue or PR.

The Agenticracy skill (github.com/agenticracy/agenticracy-skill) defines the broader context; this repo focuses on measurement.

---

*This report reflects work as of April 2026. The GIVER Index is experimental and subject to revision as methodology improves.*