"""Core GIVER index computation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from .feeds import FeedCache
from .scoring import compute_giver_index, DEFAULT_WEIGHTS

log = logging.getLogger(__name__)


class GiverComputer:
    """Orchestrates feed fetching, scoring, and output for the GIVER index."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self.data_dir = data_dir or (Path(__file__).parent.parent.parent / "data")
        self.feed_cache = FeedCache(self.data_dir / "feeds")
        self.output_dir = self.data_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._country_meta: Optional[pd.DataFrame] = None

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def compute(self, year: int = 2025, weights: Optional[dict[str, float]] = None) -> pd.DataFrame:
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
        log.info("  Hofstede loaded: %d rows", len(hofstede_df))

        # Step 3 — join dimension sub-scores
        df = countries.copy()
        df = df.merge(hofstede_df[["iso3", "ltv", "ivr"]], on="iso3", how="left")

        # Placeholder joins for optional feeds
        # TODO: Wire up World Bank, Pew, WVS, GitHub Archive when available

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
                    "region": props.get("REGION_UN", ""),
                })
            df = pd.DataFrame(records).dropna(subset=["iso3"])
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

        # Map Hofstede internal codes → ISO3
        iso3_map = {
            "AFG": "AFG", "ALB": "ALB", "ALG": "DZA", "ANG": "AGO", "ARA": "ARE",
            "ARG": "ARG", "ARM": "ARM", "AUS": "AUS", "AUT": "AUT", "AZE": "AZE",
            "BDI": "BDI", "BEL": "BEL", "BEN": "BEN", "BFA": "BFA", "BGD": "BGD",
            "BGR": "BGR", "BHR": "BHR", "BHS": "BHS", "BIH": "BIH", "BLR": "BLR",
            "BOL": "BOL", "BRA": "BRA", "BRB": "BRB", "BSG": "BGD", "BTN": "BTN",
            "BWA": "BWA", "CAF": "CAF", "CAN": "CAN", "CHE": "CHE", "CHL": "CHL",
            "CHN": "CHN", "CIV": "CIV", "CMR": "CMR", "COD": "COD", "COG": "COG",
            "COL": "COL", "COM": "COM", "CPV": "CPV", "CRI": "CRI", "CZE": "CZE",
            "DEU": "DEU", "DNK": "DNK", "DOM": "DOM", "ECU": "ECU", "EGY": "EGY",
            "ESP": "ESP", "EST": "EST", "ETH": "ETH", "FIN": "FIN", "FRA": "FRA",
            "GAB": "GAB", "GAM": "GMB", "GBR": "GBR", "GEO": "GEO", "GHA": "GHA",
            "GRC": "GRC", "GTM": "GTM", "GUY": "GUY", "HKG": "HKG", "HND": "HND",
            "HRV": "HRV", "HTI": "HTI", "HUN": "HUN", "IDN": "IDN", "IND": "IND",
            "IRL": "IRL", "IRN": "IRN", "IRQ": "IRQ", "ISL": "ISL", "ISR": "ISR",
            "ITA": "ITA", "JAM": "JAM", "JOR": "JOR", "JPN": "JPN", "KAZ": "KAZ",
            "KEN": "KEN", "KGZ": "KGZ", "KHM": "KHM", "KOR": "KOR", "KSA": "SAU",
            "KWT": "KWT", "LAO": "LAO", "LBN": "LBN", "LBR": "LBR", "LBY": "LBY",
            "LTU": "LTU", "LUX": "LUX", "LVA": "LVA", "MAR": "MAR", "MCO": "MCO",
            "MDA": "MDA", "MDG": "MDG", "MEX": "MEX", "MKD": "MKD", "MLI": "MLI",
            "MLT": "MLT", "MMR": "MMR", "MNE": "MNE", "MNG": "MNG", "MOZ": "MOZ",
            "MRT": "MRT", "MUS": "MUS", "MYS": "MYS", "NAM": "NAM", "NER": "NER",
            "NGA": "NGA", "NIC": "NIC", "NLD": "NLD", "NOR": "NOR", "NPL": "NPL",
            "NZL": "NZL", "OMN": "OMN", "PAK": "PAK", "PAN": "PAN", "PER": "PER",
            "PHL": "PHL", "PNG": "PNG", "POL": "POL", "PRY": "PRY", "PRT": "PRT",
            "PRY": "PRY", "QAT": "QAT", "ROU": "ROU", "RUS": "RUS", "RWA": "RWA",
            "SAU": "SAU", "SDN": "SDN", "SEN": "SEN", "SGP": "SGP", "SLE": "SLE",
            "SLV": "SLV", "SRB": "SRB", "SSD": "SSD", "STP": "STP", "SUR": "SUR",
            "SVK": "SVK", "SVN": "SVN", "SWE": "SWE", "SYR": "SYR", "TCD": "TCD",
            "TGO": "TGO", "THA": "THA", "TJK": "TJK", "TKM": "TKM", "TTO": "TTO",
            "TUN": "TUN", "TUR": "TUR", "TWN": "TWN", "TZA": "TZA", "UGA": "UGA",
            "UKR": "UKR", "URY": "URY", "USA": "USA", "UZB": "UZB", "VEM": "VEN",
            "VNM": "VNM", "YEM": "YEM", "ZAF": "ZAF", "ZMB": "ZMB", "ZWE": "ZWE",
            # Hofstede custom regional aggregates (approximate to a representative ISO3)
            "AFE": "ETH",  # Africa East → Ethiopia (representative)
            "AFW": "GHA",  # Africa West → Ghana
            "GRA": "NGA",  # East/West Africa aggregated → Nigeria
            "MAA": "SAU",  # MENA Arabic → Saudi Arabia
            "SEA": "SGP",  # Southeast Asia → Singapore
        }
        df["iso3"] = df["hofstede_code"].map(iso3_map).fillna(df["hofstede_code"])

        # Auto-map: Hofstede codes that happen to be valid ISO3
        missing_iso3 = df[df["iso3"].isna()]["hofstede_code"].unique()
        for code in missing_iso3:
            if code == code.upper() and len(code) == 3:
                df.loc[df["hofstede_code"] == code, "iso3"] = code

        df["iso3"] = df["iso3"].fillna(df["hofstede_code"])

        # Numeric cleanup
        for col in ["ltv", "ivr"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace("#NULL!", None), errors="coerce")
        return df

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

        score_map = dict(zip(df["iso3"], df["giver_score"]))
        for feat in gj["features"]:
            iso = feat["properties"].get("ISO3166-1-Alpha-3", "")
            feat["properties"]["giver_score"] = score_map.get(iso, None)

        with open(out_path, "w") as f:
            json.dump(gj, f)
        return out_path