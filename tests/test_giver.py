import pandas as pd

from giver_index.giver import GiverComputer, _normalize_country_name


def test_normalize_country_name_collapses_punctuation() -> None:
    assert _normalize_country_name("Hong Kong S.A.R.") == "hong kong s a r"
    assert _normalize_country_name("Bosnia & Herzegovina") == "bosnia and herzegovina"


def test_fetch_wvs_maps_aliases_and_deduplicates(tmp_path) -> None:
    data_dir = tmp_path / "data"
    feeds_dir = data_dir / "feeds"
    feeds_dir.mkdir(parents=True)
    (feeds_dir / "feed_registry.json").write_text("{}")
    (feeds_dir / "wvs_inglehart.csv").write_text(
        "\n".join(
            [
                "idx,country,region,x,y,remark",
                "826,Great Britain,English-Speaking,1.0,2.0,",
                "909,North Ireland,English-Speaking,3.0,4.0,",
                "158,Taiwan ROC,Confucian,5.0,6.0,",
                "0,Claude Sonnet 4,AI system,9.0,9.0,",
            ]
        )
    )

    countries = pd.DataFrame(
        [
            {"iso3": "GBR", "country_name": "United Kingdom"},
            {"iso3": "TWN", "country_name": "Taiwan"},
        ]
    )

    result = GiverComputer(data_dir=data_dir)._fetch_wvs(countries)
    result = result.sort_values("iso3").reset_index(drop=True)

    assert list(result["iso3"]) == ["GBR", "TWN"]
    assert result.loc[0, "self_expression"] == 3.0
    assert result.loc[0, "secular_rational"] == 2.0
    assert result.loc[1, "self_expression"] == 6.0
    assert result.loc[1, "secular_rational"] == 5.0
