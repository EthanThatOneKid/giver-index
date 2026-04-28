# GIVER Displacement Simulation — MiroFish Context

## Simulation Goal

Model the **GIVER Displacement Theory**: the hypothesis that linear (extraction-oriented) societies dominate in absolute scale but circular (giver-oriented) societies are growing faster in velocity and will displace them over time across key indicators.

## Agent Types

### League A — Countries (239 agents)
Each country-agent is defined by five GIVER dimensions:
- **Generative**: Delayed gratification culture (Hofstede LTO, 0–100)
- **Impact**: Structural capacity (GDP per capita PPP, log-scaled)
- **Verifiable**: Open collaboration (GitHub repos per capita — TODO)
- **Evidence-based**: Secular-rational worldview (WVS Inglehart x-axis)
- **Rooted**: Long-term ownership culture (Hofstede IVR, 0–100)

Country composite score: GIVER Index (0–100), higher = more circular.

### League B — People (100 rich agents, 100 influencer agents)
200 notable individuals scored by personal GIVER Index:
- **Generative**: Home country LTO culture
- **Impact**: Log(net worth in $B) as personal capacity
- **Verifiable**: Social media reach (follower count)
- **Evidence-based**: Home country WVS secular score
- **Rooted**: Home country IVR + career longevity

People compete in their own league, not against countries.

## Current World State (2025 Snapshot)

- **239 countries scored** | avg GIVER: 13.6/100
- **10 circular** | **229 linear**
- Top 5 (most circular): Luxembourg(LUX, 72.2), Macao S.A.R(MAC, 65.5), Sweden(SWE, 62.1), Japan(JPN, 61.9), South Korea(KOR, 61.5)
- Bottom 5 (most linear): South Georgia and the Islands(SGS, 0.0), American Samoa(ASM, 0.0), Niue(NIU, 0.0), Northern Mariana Islands(MNP, 0.0), Guam(GUM, 0.0)

## Displacement Mechanics

### What to Simulate
1. **Resource flows** — capital, talent, attention — from linear to circular agents
2. **Threshold effects** — circular agents below 50% score face systemic headwinds (linear inertia)
3. **Velocity tracking** — measure GIVER score delta per simulation cycle
4. **Emergent clustering** — circular agents in same region reinforce each other

### Interaction Rules
- Circular × Circular: mutual amplification (+)
- Circular × Linear: competition; linear often wins on raw mass, circular wins on velocity
- Linear × Linear: consolidation, extraction dynamics
- People × Countries: people can defect to high-GIVER countries as "escape velocity" events

### Convergence Criteria
Simulation ends when:
- Global average GIVER score crosses 55 (majority circular), OR
- 10 simulation cycles complete without GIVER delta > 0.5

## Data Sources

| Feed | Coverage | Used For |
|------|----------|----------|
| Hofstede 6-D | 83 countries | Generative, Rooted |
| World Bank GDP | 239 countries | Impact |
| WVS Inglehart | ~90 countries | Evidence-based |
| Top 200 people | 200 individuals | People league |

## Seed Files

- `seed_countries.csv` — 239 country agents
- `seed_people.csv` — 200 people agents (richest + influencers)
- `regional_clusters.json` — region groupings with intra-region rankings
- `agent_archetypes.json` — label + interaction hint per ISO3 code
