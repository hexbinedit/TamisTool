# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""TamisTool — Kusto Table Analyzer entry point.

All Typer sub-apps are mounted here. Use 'tamis --help' to see available commands.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from tamis import __version__
from tamis.cli.client import app as client_app
from tamis.cli.config import app as config_app
from tamis.cli.report import app as report_app
from tamis.cli.scan import app as scan_app

app = typer.Typer(
    name="tamis",
    help=(
        "TamisTool — Kusto Table Analyzer\n\n"
        "SIEM visibility auditing for Microsoft Sentinel and Defender.\n"
        "Built by hexbinedit.io — https://hexbinedit.io"
    ),
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

app.add_typer(client_app, name="client")
app.add_typer(scan_app, name="scan")
app.add_typer(report_app, name="report")
app.add_typer(config_app, name="config")

console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"tamis [bold]{__version__}[/bold] — hexbinedit.io")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug output."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output except errors."),
    config: Optional[str] = typer.Option(
        None, "--config", help="Override config file path."
    ),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colour output."),
) -> None:
    """TamisTool global options."""
    # Options are declared here for --help visibility.
    # Per-command propagation is handled via context or environment as needed.


def main() -> None:
    app()


if __name__ == "__main__":
    main()
