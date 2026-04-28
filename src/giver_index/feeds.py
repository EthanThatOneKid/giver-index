"""Data feed fetcher and cache manager."""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Verified feed registry
# ---------------------------------------------------------------------------


@dataclass
class FeedSpec:
    name: str
    sources: list[str]
    source_type: str  # csv | api | http-post | scraper | report | web | archive | geojson
    description: str
    last_fetched: str | None = None
    etag: str | None = None

    def cache_key(self, source: str) -> str:
        return hashlib.sha1(source.encode()).hexdigest()[:12]


FEEDS: dict[str, FeedSpec] = {
    "hofstede": FeedSpec(
        name="Hofstede 6-D Dimension Matrix",
        sources=[
            "https://geerthofstede.com/wp-content/uploads/2016/08/6-dimensions-for-website-2015-08-16.csv",
            "https://geerthofstede.com/wp-content/uploads/2016/08/6-dimensions-for-website-2015-12-08-0-100.csv",
        ],
        source_type="csv",
        description="Country scores on Power Distance, Individualism, Masculinity, Uncertainty Avoidance, Long Term Orientation, Indulgence",
    ),
    "wvs": FeedSpec(
        name="World Values Survey",
        sources=[
            "https://www.worldvaluessurvey.org/AJDownload.jsp",
        ],
        source_type="http-post",
        description="Inglehart-Welzel cultural map: Traditional vs Secular-Rational; Survival vs Self-Expression",
    ),
    "world_bank_gdp": FeedSpec(
        name="World Bank GDP per capita",
        sources=[
            "https://api.worldbank.org/v2/country/{country}/indicator/NY.GDP.PCAP.PP.KD?format=json&per_page=20000",
        ],
        source_type="api",
        description="GDP per capita PPP (constant 2017 international $)",
    ),
    "b_corp": FeedSpec(
        name="B Lab Global — B Corp Count",
        sources=[
            "https://www.bcorporation.net/en-us/find-a-b-corp/",
        ],
        source_type="scraper",
        description="Certified B Corps per country",
    ),
    "circularity_gap": FeedSpec(
        name="Circularity Gap Report",
        sources=[
            "https://www.circleconomy.com/resources/circularity-gap-report-2025",
        ],
        source_type="report",
        description="Global circularity rate: 6.9% (2025), down from ~9.1% in 2018",
    ),
    "pew_afterlife": FeedSpec(
        name="Pew Research — Afterlife Beliefs",
        sources=[
            "https://www.pewresearch.org/religion/2025/05/06/beliefs-about-the-afterlife/",
        ],
        source_type="web",
        description="Karmic reincarnation belief rates by country",
    ),
    "giving_usa": FeedSpec(
        name="Giving USA Foundation",
        sources=[
            "https://store.givingusa.org/products/2025-data-tables",
        ],
        source_type="report",
        description="US household charitable giving rate: 66% (2000) → ~50% (2020)",
    ),
    "github_archive": FeedSpec(
        name="GitHub Archive",
        sources=[
            "https://data.gharchive.org/YYYY-MM-DD-HH.json.gz",
        ],
        source_type="archive",
        description="Hourly JSON.GZ archives of GitHub events since 2011",
    ),
    "geo_countries": FeedSpec(
        name="DataHub — Geo Countries",
        sources=[
            "https://datahub.io/core/geo-countries/_r/-/data/countries.geojson",
        ],
        source_type="geojson",
        description="Country polygons for world map overlay",
    ),
}


class FeedCache:
    """Manages local cache of fetched data feeds."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or (Path(__file__).parent.parent.parent / "data" / "feeds")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._registry_path = self.cache_dir / "feed_registry.json"
        self._registry: dict[str, dict] = self._load_registry()

    def _load_registry(self) -> dict[str, dict]:
        if self._registry_path.exists():
            return json.loads(self._registry_path.read_text())
        return {}

    def _save_registry(self) -> None:
        self._registry_path.write_text(json.dumps(self._registry, indent=2))

    def get(self, feed_id: str) -> Path | None:
        """Return path to cached feed if it exists."""
        entry = self._registry.get(feed_id)
        if not entry:
            return None
        p = self.cache_dir / entry["filename"]
        return p if p.exists() else None

    def set(self, feed_id: str, filename: str, metadata: dict[str, Any]) -> Path:
        entry = {
            "feed_id": feed_id,
            "filename": filename,
            "cached_at": datetime.now(UTC).isoformat(),
            **metadata,
        }
        self._registry[feed_id] = entry
        self._save_registry()
        return self.cache_dir / filename

    def fetch_csv(self, feed_id: str, url: str, force: bool = False) -> Path | None:
        """Fetch and cache a CSV feed."""
        cached = self.get(feed_id)
        if cached and not force:
            log.info("Using cached %s: %s", feed_id, cached)
            return cached

        log.info("Fetching CSV: %s from %s", feed_id, url)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        suffix = Path(url.split("?")[0]).suffix or ".csv"
        filename = f"{feed_id}{suffix}"
        out_path = self.cache_dir / filename
        out_path.write_bytes(resp.content)

        metadata = {"url": url, "size_bytes": len(resp.content), "etag": resp.headers.get("etag")}
        self.set(feed_id, filename, metadata)
        return out_path

    def fetch_geojson(self, feed_id: str, url: str, force: bool = False) -> Path | None:
        """Fetch and cache a GeoJSON feed."""
        cached = self.get(feed_id)
        if cached and not force:
            return cached

        log.info("Fetching GeoJSON: %s from %s", feed_id, url)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        out_path = self.cache_dir / f"{feed_id}.geojson"
        out_path.write_bytes(resp.content)

        metadata = {"url": url, "size_bytes": len(resp.content)}
        self.set(feed_id, f"{feed_id}.geojson", metadata)
        return out_path
