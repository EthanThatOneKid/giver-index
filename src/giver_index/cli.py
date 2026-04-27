"""CLI entry point for the GIVER Index."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
from rich.console import Console

from .giver import GiverComputer
from . import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@main.command()
@click.option("--year", "-y", type=int, default=2025, help="Year to compute GIVER index for")
@click.option("--weights", "-w", type=str, default=None, help="JSON string of dimension weights")
@click.option("--data-dir", "-d", type=click.Path(exists=True, file_okay=False), default=None)
def compute(year: int, weights: str | None, data_dir: Path | None) -> None:
    """Fetch data feeds, compute GIVER scores, and save outputs."""
    try:
        import json
        w = json.loads(weights) if weights else None
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid weights JSON: {e}[/red]")
        sys.exit(1)

    data_path = Path(data_dir) if data_dir else None
    computer = GiverComputer(data_path)

    console.print(f"[cyan]Computing GIVER index for {year}...[/cyan]")
    df = computer.compute(year=year, weights=w)

    console.print(f"[green]✓[/green] Computed {len(df)} countries.")
    console.print(f"  Output: {computer.output_dir / f'giver_index_{year}.csv'}")
    top5 = df.head(5)[["iso3", "country_name", "giver_score"]]
    console.print("\nTop 5 (most circular):")
    for _, row in top5.iterrows():
        console.print(f"  {row['iso3']:4s} {row['country_name']:<30s} {row['giver_score']:.1f}")


@main.command()
@click.option("--year", "-y", type=int, default=2025, help="Year to inspect")
@click.option("--top-n", "-n", type=int, default=20, help="Number of top/bottom countries to show")
@click.option("--data-dir", "-d", type=click.Path(exists=True, file_okay=False), default=None)
def inspect(year: int, top_n: int, data_dir: Path | None) -> None:
    """Print GIVER index rankings for a given year."""
    data_path = Path(data_dir) if data_dir else None
    computer = GiverComputer(data_path)
    computer.inspect(year=year, top_n=top_n)


@main.command()
@click.option("--year", "-y", type=int, default=2025, help="Year to export")
@click.option("--format", "-f", type=click.Choice(["json", "geojson"]), default="json")
@click.option("--data-dir", "-d", type=click.Path(exists=True, file_okay=False), default=None)
def export(year: int, format: str, data_dir: Path | None) -> None:
    """Export GIVER scores as JSON or GeoJSON."""
    data_path = Path(data_dir) if data_dir else None
    computer = GiverComputer(data_path)
    out_path = computer.export(year=year, format=format)
    console.print(f"[green]✓[/green] Exported: {out_path}")


if __name__ == "__main__":
    main()