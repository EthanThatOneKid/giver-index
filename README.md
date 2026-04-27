# GIVER Index

> **G**enerative · **I**mpact · **V**erifiable · **E**vidence-based · **R**ooted

An open standard for measuring the circular vs. linear tilt of cultures, organizations, and individuals — and tracking displacement toward rooted, high-impact co-creation between humans and AI.

## Quick Start

```bash
pip install -e .
giver-index compute --year 2025
```

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