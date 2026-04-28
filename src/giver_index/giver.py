"""Core GIVER index computation."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

from .feeds import FeedCache
from .scoring import (
    compute_evidence_based,
    compute_generative,
    compute_giver_index,
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

    def compute(self, year: int = 2025, weights: dict[str, float] | None = None) -> pd.DataFrame:
        """Compute the GIVER index for all available countries.

        Steps:
        1. Load country metadata (iso3, name, region)
        2. Fetch and cache all raw feeds
        3. Join dimension scores to countries
        4. Compute composite GIVER index
        5. Save outputs
        """
        log.info("Computing GIVER index for year %d", year)

        # Step 1 — country metadata
        countries = self._load_countries()
        log.info("  %d countries loaded", len(countries))

        # Step 2 — fetch feeds
        hofstede_df = self._fetch_hofstede()
        wvs_df = self._fetch_wvs(countries)
        log.info("  Hofstede loaded: %d rows", len(hofstede_df))
        log.info("  WVS loaded: %d rows", len(wvs_df))

        # Step 3 — join dimension sub-scores
        df = countries.copy()
        df = df.merge(hofstede_df[["iso3", "ltv", "ivr"]], on="iso3", how="left")
        df = df.merge(wvs_df, on="iso3", how="left")
        df["region"] = df["region"].fillna("Unknown")

        # Placeholder joins for optional feeds
        # TODO: Wire up World Bank, Pew, WVS, GitHub Archive when available

        # Step 3b — compute currently-available component scores explicitly
        df["generative"] = compute_generative(df)
        df["evidence_based"] = compute_evidence_based(df)
        df["rooted"] = compute_rooted(df)

        # Step 4 — compute composite
        df["giver_score"] = compute_giver_index(df, weights)
        df["giver_dimension"] = "circular"  # high score = circular
        df.loc[df["giver_score"] < 50, "giver_dimension"] = "linear"

        # Sort descending
        df = df.sort_values("giver_score", ascending=False).reset_index(drop=True)

        # Step 5 — save
        out_path = self.output_dir / f"giver_index_{year}.csv"
        df.to_csv(out_path, index=False)
        log.info("  Saved: %s (%d rows)", out_path, len(df))

        return df

    def inspect(self, year: int = 2025, top_n: int = 20) -> None:
        """Print top/bottom countries for a given year."""
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
        """Export computed scores as JSON or geojson."""
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

    def _load_countries(self) -> pd.DataFrame:
        """Load country metadata: iso3 code, name, region."""
        geo_path = self.feed_cache.fetch_geojson(
            "geo_countries",
            "https://datahub.io/core/geo-countries/_r/-/data/countries.geojson",
        )
        if geo_path and geo_path.exists():
            import json
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

            # Patch iso3=-99 entries that Hofstede has real codes for
            patch_iso3 = {
                "France": "FRA",
                "Kosovo": "XKX",
                "Norway": "NOR",
            }
            for name, iso3 in patch_iso3.items():
                df.loc[df["country_name"] == name, "iso3"] = iso3

            # Drop territory placeholders (iso3 is still -99 or similar)
            df = df[df["iso3"].str.match(r"^[A-Z]{3}$", na=False)]

            # Deduplicate
            df = df.drop_duplicates(subset="iso3", keep="first")

            return df

        # Fallback minimal list
        return pd.DataFrame([
            {"iso3": "USA", "country_name": "United States", "region": "Americas"},
            {"iso3": "GBR", "country_name": "United Kingdom", "region": "Europe"},
            {"iso3": "JPN", "country_name": "Japan", "region": "Asia"},
        ])

    def _fetch_hofstede(self) -> pd.DataFrame:
        """Fetch and parse Hofstede dimension CSV.

        The Hofstede CSV uses ';' delimiter and internal 3-letter country codes
        (e.g. 'AFE' for Africa East, 'USA' for United States) not ISO A3.
        We map those to ISO3 via a lookup table.
        """
        csv_url = "https://geerthofstede.com/wp-content/uploads/2016/08/6-dimensions-for-website-2015-12-08-0-100.csv"
        path = self.feed_cache.fetch_csv("hofstede", csv_url)
        if not path:
            return pd.DataFrame()

        df = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str)

        # Rename to our schema
        rename = {
            "ctr": "hofstede_code",
            "country": "country_name",
            "ltowvs": "ltv",
            "ivr": "ivr",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        # Exclude Hofstede's special / non-country codes (-99, empty, etc.)
        df = df[df["hofstede_code"].str.match(r"^[A-Z]{3}$", na=False)].copy()

        # Map Hofstede internal codes → ISO3.
        # Strategy:
        #  1. Only translate aggregate codes that are NOT valid countries
        #  2. Let valid ISO3 codes pass through as-is
        iso3_map = {
            "AFE": "ETH",  # Africa East
            "AFW": "GHA",  # Africa West
            "GRA": "NGA",  # Greater Africa aggregated
            "MAA": "SAU",  # MENA Arabic
            "SEA": "SGP",  # Southeast Asia
            # Non-ISO3 codes that need explicit translation
            "BSG": "BGD",  # Bangladesh
            "VEM": "VEN",  # Venezuela
            "BUL": "BGR",  # Bulgaria
            "SAL": "SLV",  # El Salvador
        }
        df["iso3"] = df["hofstede_code"].apply(
            lambda c: iso3_map.get(c, c)  # auto-pass valid 3-letter uppercase codes
        )

        # Numeric cleanup
        for col in ["ltv", "ivr"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace("#NULL!", None), errors="coerce")

        # When a country code maps to the same ISO3 from multiple Hofstede
        # codes, prefer the country-specific row over regional aggregates.
        # Assign priority: higher ltv/ivr = more data = higher priority.
        df = df.sort_values(
            ["iso3", "ltv", "ivr"], ascending=[True, False, False]
        )
        df = df.drop_duplicates(subset="iso3", keep="first")

        return df

    def _fetch_wvs(self, countries: pd.DataFrame) -> pd.DataFrame:
        """Load cached WVS Inglehart data and map it onto ISO3 country codes."""
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

    def _export_geojson(self, df: pd.DataFrame, year: int) -> Path:
        """Merge GIVER scores onto country GeoJSON for map visualization."""
        import json
        geo_path = self.feed_cache.fetch_geojson(
            "geo_countries",
            "https://datahub.io/core/geo-countries/_r/-/data/countries.geojson",
        )
        out_path = self.output_dir / f"giver_index_{year}.geojson"
        with open(geo_path) as f:
            gj = json.load(f)

        score_map = dict(zip(df["iso3"], df["giver_score"], strict=True))
        for feat in gj["features"]:
            iso = feat["properties"].get("ISO3166-1-Alpha-3", "")
            feat["properties"]["giver_score"] = score_map.get(iso)

        with open(out_path, "w") as f:
            json.dump(gj, f)
        return out_path


def _normalize_country_name(value: str) -> str:
    value = value.lower().strip().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()
