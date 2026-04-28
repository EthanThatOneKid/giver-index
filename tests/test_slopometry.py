import json

import pandas as pd

from giver_index.slopometry import build_seed_df, generate_narrative


def test_build_seed_df_creates_expected_mirofish_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "iso3": "USA",
                "country_name": "United States",
                "region": "Americas",
                "giver_score": 45.5,
                "giver_dimension": "linear",
                "ltv": 26,
                "ivr": 68,
                "generative": 12.0,
                "impact": 0.0,
                "verifiable": 0.0,
                "evidence_based": 0.0,
                "rooted": 88.0,
            }
        ]
    )

    seed = build_seed_df(df)

    assert list(seed.columns) == [
        "id",
        "name",
        "type",
        "giver_score",
        "giver_dimension",
        "generative",
        "impact",
        "verifiable",
        "evidence_based",
        "rooted",
        "ltv",
        "ivr",
        "region",
        "archetype_traits",
    ]
    assert seed.loc[0, "id"] == "USA"
    assert seed.loc[0, "type"] == "country"
    assert json.loads(seed.loc[0, "archetype_traits"])["top_dimension"] == "rooted"


def test_generate_narrative_mentions_velocity_question() -> None:
    narrative = generate_narrative(2025, top_n=10)

    assert "GIVER velocity" in narrative
    assert "Top 10 countries by GIVER velocity" in narrative
