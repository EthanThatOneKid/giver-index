# GIVER Index

> **G**enerative · **I**mpact · **V**erifiable · **E**vidence-based · **R**ooted

An open standard for measuring the circular vs. linear tilt of cultures, organizations, and individuals — and tracking displacement toward rooted, high-impact co-creation between humans and AI.

## Status

**109 countries currently score above zero** in the Hofstede + WVS pilot. **100 countries now carry a WVS evidence-based signal**, while the remaining gaps still need World Bank, Pew, GitHub, and other feeds. Work in progress.

## Quick Start

```bash
pip install -e .
giver-index compute --year 2025
```

## Current Findings (2025 Pilot)

**Coverage:** 109 of 239 countries currently score above zero in the Hofstede + WVS pipeline. WVS now fills 100 countries for the `evidence_based` dimension, including many countries that previously scored 0 across the board.

**Top scorers (most circular):**
| Rank | Country | LTV | WVS Self-Expression | IVR | GIVER |
|---|---|---|---|---|---|
| 1 | Japan | 88 | 1.695 | 42 | 74.2 |
| 2 | South Korea | 100 | 1.283 | 29 | 70.8 |
| 3 | Sweden | 53 | 1.086 | 78 | 68.6 |
| 4 | Belgium | 82 | 0.317 | 57 | 66.0 |
| 5 | Luxembourg | 64 | 0.438 | 56 | 59.6 |

**Newly lifted by WVS (no Hofstede, but no longer zero):**
| Country | WVS Self-Expression | GIVER |
|---|---|---|
| Germany | 1.211 | 23.3 |
| Denmark | 0.697 | 19.1 |
| Netherlands | 0.567 | 18.0 |
| Switzerland | 0.221 | 15.2 |
| Spain | 0.195 | 15.0 |

**Still missing:** 130 countries still score 0 due to missing Hofstede and WVS coverage, or because only still-unwired feeds would contribute meaningful signal there.

**Output:** `giver-index export-slopometry --year 2025` produces MiroFish-compatible seed data.

## Public Artifacts

- Map page: https://etok.zo.space/giver-map
- Map data API: https://etok.zo.space/api/giver-map-data
- GeoJSON API: https://etok.zo.space/api/geo-countries
- GitHub repo: https://github.com/EthanThatOneKid/giver-index

## Project Structure

```
giver-index/
├── README.md
├── METHODOLOGY.md
├── pyproject.toml
├── src/
│   └── giver_index/
│       ├── __init__.py
│       ├── cli.py          # Entry point: compute, inspect, export
│       ├── feeds.py        # Fetch & cache raw data feeds
│       ├── scoring.py      # Component scoring functions
│       └── giver.py        # Composite index computation
├── data/
│   ├── feeds/              # Cached raw data (gitignored)
│   ├── outputs/            # Computed GIVER scores
│   └── top200/             # Seed data (richest + social wealth)
├── notebooks/              # Exploratory analysis
└── tests/
```

## Data Feeds (verified endpoints)

| Feed | Source | Status |
|---|---|---|
| Hofstede 6-D | `geerthofstede.com` (CSV) | ✅ Verified |
| World Values Survey | `worldvaluessurvey.org` | ✅ Verified |
| World Bank Indicators | `api.worldbank.org` | ✅ Verified |
| Circularity Gap Report | Circle Economy | ✅ Verified |
| Pew Afterlife Beliefs | Pew Research | ✅ Verified |
| B Corp Growth | B Lab Global | ✅ Verified |
| GitHub Archive | `data.gharchive.org` | ✅ Verified |
| Giving USA | `store.givingusa.org` | ✅ Verified |
| Geo Countries (GeoJSON) | `datahub.io/core/geo-countries` | ✅ Verified |

## Key Concepts

- **Mass** — Absolute scale of a system (linear GDP vs circular impact investing AUM)
- **Velocity** — Growth rate of a system (creator economy CAGR vs B Corp growth)
- **Effect** — Outcome quality per unit (patents vs open source repos)
- **GIVER Displacement Theory** — Linear systems dominate in mass; circular systems are healing in velocity

## Ecosystem

| Project | Role |
|---|---|
| [Agenticracy](https://github.com/agenticracy/agenticracy-skill) | Constitutional standard for human-AI co-working |
| [MiroFish](https://github.com/666ghj/MiroFish) | Agent-based simulation engine |
| [Slopometry](https://psylligent.com) | Measurement device for AI output waste |
| [Workability.ai](https://workability.ai) | Implementation & change management |

## License

AGPL-3.0 — copyleft, share modifications.
