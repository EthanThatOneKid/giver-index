import pandas as pd

from giver_index.scoring import compute_giver_index


def test_compute_giver_index_uses_available_dimensions_only() -> None:
    df = pd.DataFrame(
        {
            "iso3": ["AAA", "BBB"],
            "country_name": ["Alpha", "Beta"],
            "ltv": [10, 90],
            "ivr": [20, 80],
        }
    )

    scores = compute_giver_index(df)

    assert list(scores.round(1)) == [0.0, 100.0]


def test_compute_giver_index_respects_weight_override() -> None:
    df = pd.DataFrame(
        {
            "iso3": ["AAA", "BBB"],
            "country_name": ["Alpha", "Beta"],
            "ltv": [90, 10],
            "ivr": [10, 90],
        }
    )

    scores = compute_giver_index(
        df,
        weights={
            "generative": 1.0,
            "impact": 0.0,
            "verifiable": 0.0,
            "evidence_based": 0.0,
            "rooted": 0.0,
        },
    )

    assert list(scores.round(1)) == [100.0, 0.0]
