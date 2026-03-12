# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""CLI commands for report generation.

NOTE: Report rendering (Jinja2/CSV/JSON/Parquet) is implemented in Phase 1+.
      Phase 0 provides the CLI interface and stub only.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(help="Generate and export scan reports.")
console = Console()


class ReportFormat(str, Enum):
    html = "html"
    csv = "csv"
    json = "json"
    parquet = "parquet"


@app.command("generate")
def report_generate(
    client: str = typer.Option(..., "--client", "-c", help="Target client name."),
    scan_id: Optional[int] = typer.Option(
        None, "--scan-id", help="Specific scan ID (defaults to latest)."
    ),
    fmt: ReportFormat = typer.Option(
        ReportFormat.html, "--format", "-f", help="Output format."
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path. Defaults to ./<client>_report.<ext>."
    ),
) -> None:
    """Generate a report from scan results.

    Phase 1+ — Report rendering not yet implemented.
    """
    console.print(
        f"[yellow]Phase 0:[/yellow] Report generation is not yet implemented. "
        f"Requested: client='{client}', format='{fmt.value}', scan_id={scan_id or 'latest'}."
    )
    console.print(
        "Jinja2 HTML templates and CSV/JSON/Parquet export will be added in Phase 1+. "
        "See docs/REPORT_GUIDE.md for the planned report structure."
    )
