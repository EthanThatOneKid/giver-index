"""CLI entry point for the GIVER Index."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
import pandas as pd
from rich.console import Console

from . import __version__
from .giver import GiverComputer
from .slopometry import build_seed_df, generate_narrative
from .mirofish import export_mirofish_context

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


@main.command("export-slopometry")
@click.option("--year", "-y", type=int, default=2025, help="Year to export seed data for")
@click.option("--top-n", "-n", type=int, default=10, help="Number of top countries to highlight in narrative")
@click.option("--output-dir", "-o", type=click.Path(file_okay=False), default=None)
@click.option("--data-dir", "-d", type=click.Path(exists=True, file_okay=False), default=None)
def export_slopometry(year: int, top_n: int, output_dir: Path | None, data_dir: Path | None) -> None:
    """Generate MiroFish-compatible seed data and simulation narrative."""
    data_path = Path(data_dir) if data_dir else None
    computer = GiverComputer(data_path)
    out_dir = Path(output_dir) if output_dir else computer.output_dir

    # Load computed GIVER data
    csv_path = computer.output_dir / f"giver_index_{year}.csv"
    if not csv_path.exists():
        console.print(f"[red]No data for {year}. Run `giver-index compute --year {year}` first.[/red]")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Build seed CSV
    seed_df = build_seed_df(df)
    seed_path = out_dir / f"slopometry_seed_{year}.csv"
    seed_df.to_csv(seed_path, index=False)

    # Write narrative
    narrative = generate_narrative(year, top_n=top_n)
    narrative_path = out_dir / f"slopometry_narrative_{year}.txt"
    narrative_path.write_text(narrative)

    console.print(f"[green]✓[/green] Seed CSV: {seed_path} ({len(seed_df)} agents)")
    console.print(f"[green]✓[/green] Narrative: {narrative_path}")
    console.print("\nSeed preview:")
    console.print(seed_df.head(5).to_string(index=False))
    console.print("\nNarrative excerpt:")
    console.print(narrative[:500] + "...")


@main.command("export-mirofish")
@click.option("--year", "-y", type=int, default=2025, help="Year to export")
@click.option("--output-dir", "-o", type=click.Path(file_okay=False), default=None)
@click.option("--data-dir", "-d", type=click.Path(exists=True, file_okay=False), default=None)
def export_mirofish(year: int, output_dir: Path | None, data_dir: Path | None) -> None:
    """Export MiroFish-compatible data."""
    data_path = Path(data_dir) if data_dir else None
    computer = GiverComputer(data_path)
    out_dir = Path(output_dir) if output_dir else computer.output_dir

    # Load computed GIVER data
    csv_path = computer.output_dir / f"giver_index_{year}.csv"
    if not csv_path.exists():
        console.print(f"[red]No data for {year}. Run `giver-index compute --year {year}` first.[/red]")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Load Top 200 people data
    people_path = computer.data_dir / "top200" / "consolidated_top_200.csv"
    if not people_path.exists():
        console.print(f"[red]Top 200 data not found: {people_path}[/red]")
        sys.exit(1)

    people_df = pd.read_csv(people_path)

    # Export MiroFish context
    export_mirofish_context(df, people_df, out_dir)

    console.print(f"[green]✓[/green] Exported MiroFish context to {out_dir}")


if __name__ == "__main__":
    main()
