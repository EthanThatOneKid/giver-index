"""Core GIVER index computation."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from .feeds import FeedCache
from .scoring import (
    compute_evidence_based,
    compute_generative,
    compute_giver_index,
    compute_impact,
    compute_rooted,
)

log = logging.getLogger(__name__)

WVS_COUNTRY_ALIASES = {
    "Bosnia Herzegovina": "Bosnia and Herzegovina",
    "Great Britain": "United Kingdom",
    "Hong Kong SAR": "Hong Kong S.A.R.",
    "Macau SAR": "Macao S.A.R",
    "North Ireland": "United Kingdom",
    "Serbia": "Republic of Serbia",
    "Taiwan ROC": "Taiwan",
    "United States": "United States of America",
}

# Country name → ISO3 lookup, used across feed fetchers
COUNTRY_NAME_TO_ISO3: dict[str, str] = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Angola": "AGO",
    "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT",
    "Azerbaijan": "AZE", "Bangladesh": "BGD", "Belarus": "BLR", "Belgium": "BEL",
    "Benin": "BEN", "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH",
    "Botswana": "BWA", "Brazil": "BRA", "Bulgaria": "BGR", "Burkina Faso": "BFA",
    "Burundi": "BDI", "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Chad": "TCD", "Chile": "CHL", "China": "CHN", "Colombia": "COL",
    "Costa Rica": "CRI", "Croatia": "HRV", "Cuba": "CUB", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Denmark": "DNK", "Dominican Republic": "DOM",
    "East Timor": "TLS", "Ecuador": "ECU", "Egypt": "EGY", "El Salvador": "SLV",
    "Estonia": "EST", "Ethiopia": "ETH", "Finland": "FIN", "France": "FRA",
    "Gabon": "GAB", "Gambia": "GMB", "Georgia": "GEO", "Germany": "DEU",
    "Ghana": "GHA", "Greece": "GRC", "Guatemala": "GTM", "Guinea": "GIN",
    "Haiti": "HTI", "Honduras": "HND", "Hungary": "HUN", "India": "IND",
    "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Ivory Coast": "CIV", "Jamaica": "JAM",
    "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN",
    "Kosovo": "XKX", "Kuwait": "KWT", "Latvia": "LVA", "Lebanon": "LBN",
    "Liberia": "LBR", "Libya": "LBY", "Lithuania": "LTU", "Luxembourg": "LUX",
    "Madagascar": "MDG", "Malawi": "MWI", "Malaysia": "MYS", "Mali": "MLI",
    "Mauritania": "MRT", "Mexico": "MEX", "Moldova": "MDA", "Mongolia": "MNG",
    "Montenegro": "MNE", "Morocco": "MAR", "Mozambique": "MOZ", "Myanmar": "MMR",
    "Namibia": "NAM", "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL",
    "Nicaragua": "NIC", "Niger": "NER", "Nigeria": "NGA", "North Korea": "PRK",
    "North Macedonia": "MKD", "Norway": "NOR", "Oman": "OMN", "Pakistan": "PAK",
    "Palestine": "PSE", "Panama": "PAN", "Papua New Guinea": "PNG",
    "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL", "Poland": "POL",
    "Portugal": "PRT", "Puerto Rico": "PRI", "Qatar": "QAT", "Romania": "ROU",
    "Russia": "RUS", "Rwanda": "RWA", "Saudi Arabia": "SAU", "Senegal": "SEN",
    "Serbia": "SRB", "Sierra Leone": "SLE", "Singapore": "SGP", "Slovakia": "SVK",
    "Slovenia": "SVN", "Somalia": "SOM", "South Africa": "ZAF", "South Korea": "KOR",
    "South Sudan": "SSD", "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN",
    "Sweden": "SWE", "Switzerland": "CHE", "Syria": "SYR", "Taiwan": "TWN",
    "Tajikistan": "TJK", "Tanzania": "TZA", "Thailand": "THA", "Togo": "TGO",
    "Trinidad and Tobago": "TTO", "Tunisia": "TUN", "Turkey": "TUR",
    "Turkmenistan": "TKM", "Uganda": "UGA", "Ukraine": "UKR",
    "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States of America": "USA", "Uruguay": "URY", "Uzbekistan": "UZB",
    "Venezuela": "VEN", "Vietnam": "VNM", "Yemen": "YEM", "Zambia": "ZMB",
    "Zimbabwe": "ZWE",
}


class GiverComputer:
    """Orchestrates feed fetching, scoring, and output for the GIVER index."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or (Path(__file__).parent.parent.parent / "data")
        self.feed_cache = FeedCache(self.data_dir / "feeds")
        self.output_dir = self.data_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._country_meta: pd.DataFrame | None = None

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def compute(self, year: int = 2025, weights: Optional[dict[str, float]] = None) -> pd.DataFrame:
        """Compute the GIVER index for all available countries."""
        log.info("Computing GIVER index for year %d", year)

        countries = self._load_countries()
        log.info("  %d countries loaded", len(countries))

        hofstede_df = self._fetch_hofstede()
        wvs_df = self._fetch_wvs(countries)
        gdp_df = self._fetch_world_bank()
        pew_df = self._fetch_pew_afterlife()
        log.info("  Hofstede loaded: %d rows", len(hofstede_df))
        log.info("  WVS loaded: %d rows", len(wvs_df))
        log.info("  World Bank GDP: %d rows", len(gdp_df))
        log.info("  Pew reincarnation: %d countries", len(pew_df))

        df = countries.copy()
        df = df.merge(hofstede_df[["iso3", "ltv", "ivr"]], on="iso3", how="left")
        df = df.merge(wvs_df, on="iso3", how="left")
        df = df.merge(gdp_df, on="iso3", how="left")
        df = df.merge(pew_df, on="iso3", how="left")
        df = self._assign_regions(df)
        df["region"] = df["region"].fillna("Unknown")

        df["generative"] = compute_generative(df)
        df["evidence_based"] = compute_evidence_based(df, pew_df)
        df["rooted"] = compute_rooted(df)
        df["impact"] = compute_impact(df)

        df["giver_score"] = compute_giver_index(df, weights)
        df["giver_dimension"] = "circular"
        df.loc[df["giver_score"] < 50, "giver_dimension"] = "linear"

        df = df.sort_values("giver_score", ascending=False).reset_index(drop=True)

        out_path = self.output_dir / f"giver_index_{year}.csv"
        df.to_csv(out_path, index=False)
        log.info("  Saved: %s (%d rows)", out_path, len(df))

        self._export_geojson(df, year)

        return df

    def inspect(self, year: int = 2025, top_n: int = 20) -> None:
        out_path = self.output_dir / f"giver_index_{year}.csv"
        if not out_path.exists():
            print(f"No data for {year}. Run `giver-index compute --year {year}` first.")
            return
        df = pd.read_csv(out_path)
        print(f"\n=== GIVER Index {year} ===")
        print(f"Total countries: {len(df)}")
        print(f"\nTop {top_n} (most circular):")
        print(df.head(top_n)[["iso3", "country_name", "giver_score", "giver_dimension"]].to_string(index=False))
        print(f"\nBottom {top_n} (most linear):")
        print(df.tail(top_n)[["iso3", "country_name", "giver_score", "giver_dimension"]].to_string(index=False))

    def export(self, year: int, format: str = "json") -> Path:
        out_path = self.output_dir / f"giver_index_{year}.csv"
        if not out_path.exists():
            raise FileNotFoundError(f"No data for {year}. Run compute first.")
        df = pd.read_csv(out_path)
        if format == "json":
            out = self.output_dir / f"giver_index_{year}.json"
            df.to_json(out, orient="records", indent=2)
        elif format == "geojson":
            out = self._export_geojson(df, year)
        else:
            raise ValueError(f"Unknown format: {format}. Use 'json' or 'geojson'.")
        log.info("Exported: %s", out)
        return out

    # -------------------------------------------------------------------------
    # Feed loading helpers
    # -------------------------------------------------------------------------

    def _assign_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign UN region to every row based on country name."""
        REGION_MAP = {
            "Luxembourg": "Europe", "Belgium": "Europe", "Sweden": "Europe",
            "Austria": "Europe", "France": "Europe", "United Kingdom": "Europe",
            "Netherlands": "Europe", "Germany": "Europe", "Switzerland": "Europe",
            "Norway": "Europe", "Denmark": "Europe", "Finland": "Europe",
            "Ireland": "Europe", "Czechia": "Europe", "Malta": "Europe",
            "Iceland": "Europe", "Portugal": "Europe", "Slovenia": "Europe",
            "Estonia": "Europe", "Spain": "Europe", "Italy": "Europe",
            "Greece": "Europe", "Hungary": "Europe", "Poland": "Europe",
            "Romania": "Europe", "Croatia": "Europe", "Lithuania": "Europe",
            "Slovakia": "Europe", "Latvia": "Europe", "Bulgaria": "Europe",
            "Serbia": "Europe", "Montenegro": "Europe", "North Macedonia": "Europe",
            "Moldova": "Europe", "Ukraine": "Europe", "Belarus": "Europe",
            "Russia": "Europe", "Bosnia and Herzegovina": "Europe",
            "Albania": "Europe", "Kosovo": "Europe", "Georgia": "Europe",
            "Armenia": "Europe", "Azerbaijan": "Europe", "Cyprus": "Europe",
            "Macao S.A.R": "Asia", "South Korea": "Asia", "Japan": "Asia",
            "Singapore": "Asia", "Taiwan": "Asia", "Hong Kong S.A.R.": "Asia",
            "China": "Asia", "India": "Asia", "Indonesia": "Asia",
            "Thailand": "Asia", "Vietnam": "Asia", "Philippines": "Asia",
            "Malaysia": "Asia", "Bangladesh": "Asia", "Pakistan": "Asia",
            "Sri Lanka": "Asia", "Nepal": "Asia", "Myanmar": "Asia",
            "Cambodia": "Asia", "Laos": "Asia", "Kazakhstan": "Asia",
            "Uzbekistan": "Asia", "Tajikistan": "Asia", "Kyrgyzstan": "Asia",
            "Afghanistan": "Asia", "Mongolia": "Asia", "North Korea": "Asia",
            "Iran": "Asia", "Iraq": "Asia", "Turkey": "Asia", "Israel": "Asia",
            "Jordan": "Asia", "Lebanon": "Asia", "Syria": "Asia",
            "Saudi Arabia": "Asia", "Kuwait": "Asia", "Qatar": "Asia",
            "United Arab Emirates": "Asia", "Oman": "Asia", "Yemen": "Asia",
            "Bahrain": "Asia", "Palestine": "Asia", "Brunei": "Asia",
            "East Timor": "Asia", "Maldives": "Asia", "Bhutan": "Asia",
            "Papua New Guinea": "Oceania", "New Zealand": "Oceania",
            "Australia": "Oceania", "Fiji": "Oceania", "Solomon Islands": "Oceania",
            "Vanuatu": "Oceania", "Samoa": "Oceania", "Tonga": "Oceania",
            "Canada": "Americas", "United States of America": "Americas",
            "Mexico": "Americas", "Chile": "Americas", "Brazil": "Americas",
            "Colombia": "Americas", "Argentina": "Americas", "Peru": "Americas",
            "Venezuela": "Americas", "Guatemala": "Americas", "Cuba": "Americas",
            "Dominican Republic": "Americas", "Honduras": "Americas",
            "Paraguay": "Americas", "Bolivia": "Americas", "Ecuador": "Americas",
            "El Salvador": "Americas", "Nicaragua": "Americas", "Costa Rica": "Americas",
            "Panama": "Americas", "Puerto Rico": "Americas", "Jamaica": "Americas",
            "Trinidad and Tobago": "Americas", "Guyana": "Americas", "Suriname": "Americas",
            "Uruguay": "Americas", "Haiti": "Americas",
            "South Africa": "Africa", "Nigeria": "Africa", "Kenya": "Africa",
            "Ghana": "Africa", "Tanzania": "Africa", "Ethiopia": "Africa",
            "Uganda": "Africa", "Mozambique": "Africa", "Zimbabwe": "Africa",
            "Cameroon": "Africa", "Ivory Coast": "Africa", "Senegal": "Africa",
            "Botswana": "Africa", "Namibia": "Africa", "Zambia": "Africa",
            "Angola": "Africa", "Rwanda": "Africa", "Sudan": "Africa",
            "South Sudan": "Africa", "Somalia": "Africa", "Madagascar": "Africa",
            "Malawi": "Africa", "Mali": "Africa", "Burkina Faso": "Africa",
            "Gabon": "Africa", "Benin": "Africa", "Niger": "Africa",
            "Togo": "Africa", "Mauritania": "Africa", "Liberia": "Africa",
            "Sierra Leone": "Africa", "Libya": "Africa", "Egypt": "Africa",
            "Morocco": "Africa", "Tunisia": "Africa", "Algeria": "Africa",
            "Chad": "Africa", "Burundi": "Africa", "Gambia": "Africa",
            "Djibouti": "Africa", "Eritrea": "Africa", "Guinea": "Africa",
            "Congo": "Africa", "Democratic Republic of the Congo": "Africa",
            "Lesotho": "Africa", "Eswatini": "Africa", "Equatorial Guinea": "Africa",
            "Mauritius": "Africa", "Seychelles": "Africa", "Cape Verde": "Africa",
            "Comoros": "Africa", "São Tomé and Príncipe": "Africa",
        }
        df = df.copy()
        df["region"] = df["country_name"].map(REGION_MAP).fillna("Unknown")
        return df

    def _load_countries(self) -> pd.DataFrame:
        geo_path = self.feed_cache.fetch_geojson(
            "geo_countries",
            "https://datahub.io/core/geo-countries/_r/-/data/countries.geojson",
        )
        if geo_path and geo_path.exists():
            with open(geo_path) as f:
                gj = json.load(f)
            records = []
            for feat in gj["features"]:
                props = feat["properties"]
                records.append({
                    "iso3": props.get("ISO3166-1-Alpha-3", ""),
                    "country_name": props.get("name", ""),
                    "region": props.get("REGION_UN", "Unknown"),
                })
            df = pd.DataFrame(records).dropna(subset=["iso3"])
            patch_iso3 = {
                "France": "FRA",
                "Kosovo": "XKX",
                "Norway": "NOR",
            }
            for name, iso3 in patch_iso3.items():
                df.loc[df["country_name"] == name, "iso3"] = iso3
            df = df[df["iso3"].str.match(r"^[A-Z]{3}$", na=False)]
            df = df.drop_duplicates(subset="iso3", keep="first")
            return df
        return pd.DataFrame([
            {"iso3": "USA", "country_name": "United States", "region": "Americas"},
            {"iso3": "GBR", "country_name": "United Kingdom", "region": "Europe"},
            {"iso3": "JPN", "country_name": "Japan", "region": "Asia"},
        ])

    def _fetch_hofstede(self) -> pd.DataFrame:
        csv_url = "https://geerthofstede.com/wp-content/uploads/2016/08/6-dimensions-for-website-2015-12-08-0-100.csv"
        path = self.feed_cache.fetch_csv("hofstede", csv_url)
        if not path:
            return pd.DataFrame()
        df = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str)
        rename = {
            "ctr": "hofstede_code",
            "country": "country_name",
            "ltowvs": "ltv",
            "ivr": "ivr",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        df = df[df["hofstede_code"].str.match(r"^[A-Z]{3}$", na=False)].copy()
        iso3_map = {
            "AFE": "ETH", "AFW": "GHA", "GRA": "NGA", "MAA": "SAU", "SEA": "SGP",
            "BSG": "BGD", "VEM": "VEN", "BUL": "BGR", "SAL": "SLV",
        }
        df["iso3"] = df["hofstede_code"].apply(lambda c: iso3_map.get(c, c))
        for col in ["ltv", "ivr"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace("#NULL!", None), errors="coerce")
        df = df.sort_values(["iso3", "ltv", "ivr"], ascending=[True, False, False])
        df = df.drop_duplicates(subset="iso3", keep="first")
        return df

    def _fetch_wvs(self, countries: pd.DataFrame) -> pd.DataFrame:
        path = self.feed_cache.get("wvs_inglehart")
        if path is None:
            fallback = self.feed_cache.cache_dir / "wvs_inglehart.csv"
            path = fallback if fallback.exists() else None
        if not path or not path.exists():
            return pd.DataFrame(columns=["iso3", "self_expression", "secular_rational"])
        wvs = pd.read_csv(path)
        if wvs.empty:
            return pd.DataFrame(columns=["iso3", "self_expression", "secular_rational"])
        required = {"country", "region", "x", "y"}
        if not required.issubset(wvs.columns):
            log.warning("WVS file missing expected columns: %s", sorted(required - set(wvs.columns)))
            return pd.DataFrame(columns=["iso3", "self_expression", "secular_rational"])
        wvs = wvs[wvs["region"] != "AI system"].copy()
        wvs["country_name"] = wvs["country"].replace(WVS_COUNTRY_ALIASES)
        wvs["country_key"] = wvs["country_name"].map(_normalize_country_name)
        country_lookup = countries[["iso3", "country_name"]].copy()
        country_lookup["country_key"] = country_lookup["country_name"].map(_normalize_country_name)
        country_lookup = country_lookup.drop_duplicates(subset="country_key", keep="first")
        matched = wvs.merge(country_lookup[["iso3", "country_key"]], on="country_key", how="left")
        matched = matched.dropna(subset=["iso3"]).copy()
        matched["self_expression"] = pd.to_numeric(matched["y"], errors="coerce")
        matched["secular_rational"] = pd.to_numeric(matched["x"], errors="coerce")
        matched = (
            matched.groupby("iso3", as_index=False)[["self_expression", "secular_rational"]]
            .mean()
        )
        return matched

    def _fetch_world_bank(self) -> pd.DataFrame:
        cache_path = self.feed_cache.get("world_bank_gdp")
        if cache_path and cache_path.exists():
            log.info("Using cached World Bank GDP data")
        else:
            log.info("Fetching World Bank GDP per capita from API...")
            url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.KD?format=json&per_page=300&date=2023"
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or len(data) < 2:
                log.warning("Unexpected World Bank API response structure")
                return pd.DataFrame(columns=["iso3", "gdp_ppp"])
            records = []
            for entry in data[1]:
                country_code = entry.get("countryiso3code", "")
                value = entry.get("value")
                if country_code and value is not None:
                    records.append({"iso3": country_code, "gdp_ppp": float(value)})
            if records:
                wb_df = pd.DataFrame(records).drop_duplicates(subset="iso3", keep="first")
                out_path = self.feed_cache.cache_dir / "world_bank_gdp.csv"
                wb_df.to_csv(out_path, index=False)
                self.feed_cache.set("world_bank_gdp", "world_bank_gdp.csv", {"url": url, "rows": len(wb_df)})
                log.info("  World Bank cached: %d countries", len(wb_df))
                return wb_df
            return pd.DataFrame(columns=["iso3", "gdp_ppp"])
        df = pd.read_csv(cache_path)
        if "iso3" not in df.columns or "gdp_ppp" not in df.columns:
            return pd.DataFrame(columns=["iso3", "gdp_ppp"])
        return df[["iso3", "gdp_ppp"]].drop_duplicates(subset="iso3", keep="first")

    def _fetch_pew_afterlife(self) -> pd.DataFrame:
        """Reincarnation belief rates from Pew Research (2025).

        Source: https://www.pewresearch.org/religion/2025/05/06/beliefs-about-the-afterlife/
        Table: "Belief in reincarnation" — adults who say definitely or probably
        "people will be reborn in this world again and again."

        Pew surveyed ~48 countries. Scores are min-max normalized within the Pew
        sample only (not against all 239 countries) so that a country with no Pew
        data gets evidence_based purely from WVS.
        """
        raw = [
            ("India", 48), ("Thailand", 48), ("Sri Lanka", 70), ("Indonesia", 18),
            ("Malaysia", 17), ("Philippines", 27), ("Japan", 34), ("South Korea", 33),
            ("Singapore", 29), ("Nigeria", 48), ("Kenya", 53), ("Ghana", 44),
            ("South Africa", 41), ("Tanzania", 36), ("Uganda", 32), ("Mozambique", 28),
            ("Angola", 31), ("Ethiopia", 24), ("Chile", 44), ("Brazil", 27),
            ("Mexico", 28), ("Colombia", 33), ("Peru", 38), ("Argentina", 26),
            ("Venezuela", 29), ("Poland", 12), ("Sweden", 12), ("France", 14),
            ("Germany", 15), ("Spain", 16), ("Italy", 18), ("Netherlands", 14),
            ("United Kingdom", 13), ("Belgium", 16), ("Austria", 17),
            ("Switzerland", 15), ("Czech Republic", 11), ("Hungary", 13),
            ("Greece", 19), ("Portugal", 17), ("Turkey", 11), ("Israel", 14),
            ("Jordan", 9), ("Lebanon", 15), ("Egypt", 12), ("Tunisia", 13),
            ("Morocco", 11), ("Bangladesh", 14), ("United States", 31),
            ("Canada", 29), ("Pakistan", 13), ("Afghanistan", 16), ("Nepal", 38),
        ]
        records = [{"country_name": n, "reincarnation_pct": p} for n, p in raw]
        df = pd.DataFrame(records)
        df["reincarnation_pct"] = pd.to_numeric(df["reincarnation_pct"], errors="coerce")
        df["iso3"] = df["country_name"].map(COUNTRY_NAME_TO_ISO3)
        df = df.dropna(subset=["iso3"])

        # Min-max normalize within the Pew sample; result is 0-100 on Pew survey countries
        vals = df["reincarnation_pct"].values.astype(float)
        mn, mx = vals.min(), vals.max()
        if mx > mn:
            df["reincarnation_pct"] = (vals - mn) / (mx - mn) * 100
        else:
            df["reincarnation_pct"] = 50.0

        return df[["iso3", "reincarnation_pct"]]

    def _export_geojson(self, df: pd.DataFrame, year: int) -> Path:
        geo_path = self.feed_cache.fetch_geojson(
            "geo_countries",
            "https://datahub.io/core/geo-countries/_r/-/data/countries.geojson",
        )
        out_path = self.output_dir / f"giver_index_{year}.geojson"
        if not geo_path or not geo_path.exists():
            log.warning("GeoJSON not available, skipping geo export")
            return out_path
        with open(geo_path) as f:
            gj = json.load(f)
        score_map = dict(zip(df["iso3"], df["giver_score"], strict=True))
        for feat in gj["features"]:
            iso = feat["properties"].get("ISO3166-1-Alpha-3", "")
            feat["properties"]["giver_score"] = score_map.get(iso)
        with open(out_path, "w") as f:
            json.dump(gj, f)
        log.info("  GeoJSON: %s", out_path)
        return out_path


def _normalize_country_name(value: str) -> str:
    value = value.lower().strip().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()