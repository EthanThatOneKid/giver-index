# GIVER Index — Methodology

## Design Philosophy

The GIVER Index is a **composite score** (0–100) that quantifies how "circular" (other-oriented, long-term, verifiable) vs "linear" (self-oriented, short-term, performative) a given unit is, across five dimensions.

Higher = more circular (GIVER-aligned). Lower = more linear (extractive/performative).

## The Five Dimensions

| Dimension | Description | Linear Signal | Circular Signal |
|---|---|---|---|
| **Generative** | Value-adding without fanfare | Performing busyness | Quiet excellence |
| **Impact** | Path clearing for others | Theater outputs | Real-world results |
| **Verifiable** | Evidence-based outcomes | Vanity metrics | Measurable, durable outcomes |
| **Evidence-based** | Data-driven but not showy | Reports for optics | Unsung heroes, behind the scenes |
| **Rooted** | Legacy-building, not extractive | Quick wins | Long-term ownership |

## Composite Score Formula

For a country `c` and year `y`:

```
GIVER(c, y) = w1·G(c,y) + w2·I(c,y) + w3·V(c,y) + w4·E(c,y) + w5·R(c,y)
```

Where each sub-score is a z-score normalization of one or more raw indicators, mapped to [0, 100].

### Default Weights

```
w1 = 0.20  # Generative
w2 = 0.25  # Impact
w3 = 0.20  # Verifiable
w4 = 0.15  # Evidence-based
w5 = 0.20  # Rooted
```

Weights are configurable via `--weights` CLI flag.

## Data Sources & Mapping

### Generative (w1)

- **Source:** Hofstede — *Long Term Orientation* (LTO) score
- **Rationale:** High LTO = delayed gratification, systemic investment = generative
- **Raw:** 0–100 score per country
- **Normalization:** Min-max to [0, 100]

### Impact (w2)

- **Source A:** World Bank — GDP per capita (PPP, constant 2017 international $)
- **Source B:** B Lab Global — B Corp count per million adults
- **Rationale:** Impact is measured by structural capacity (GDP) + certified impact organizations
- **Composite:** Weighted average of two normalized signals

### Verifiable (w3)

- **Source A:** GitHub Archive — public repos per capita (log scale)
- **Source B:** WIPO — patent applications per million
- **Rationale:** Verifiable outputs = open collaboration (GitHub) + verifiable invention (patents)
- **Composite:** Log GitHub repos + patent density, normalized

### Evidence-based (w4)

- **Source:** World Values Survey — Inglehart self-expression vs survival score
- **Secondary:** Pew Research — afterlife belief (% believing in karmic reincarnation)
- **Rationale:** Self-expression values correlate with evidence-seeking; karmic belief correlates with circular worldview
- **Composite:** WVS secular-rational + Pew reincarnation belief, z-scored

### Rooted (w5)

- **Source A:** Hofstede — *Indulgence vs Restraint* (IVR) score
- **Source B:** Giving USA — charity giving rate (% households)
- **Rationale:** Rooted = legacy-building = generosity + restraint
- **Composite:** IVR + charitable giving rate, normalized

## Limitations

1. **Hofstede is from 1960s–2000s surveys** — may not reflect current cultural state
2. **WVS waves are 7+ years apart** — temporal resolution is coarse
3. **GIVER is a framing device** — not a tested causal model; correlation ≠ causation
4. **B Corp data is skewed** — heavily weighted toward Western Europe + US
5. **GitHub is English-biases** — open source activity is not uniformly distributed globally

## Change Log

- **v0.1.0** — Initial framework, Hofstede + WVS + Pew pilot scoring
- **v0.1.1** — Added World Bank GDP + B Corp composite for Impact
- **v0.2.0** — GitHub Archive + WIPO patent integration for Verifiable