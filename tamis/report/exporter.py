# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Report generation and export logic.

Phase 1+ — Report rendering is not yet implemented.
This module provides the interface contract for Phase 1 implementation.

Supported output formats (planned):
  html     — Jinja2 template rendered to .html file (default)
  csv      — Flat table inventory via pandas
  json     — Structured JSON for downstream tooling
  parquet  — Columnar format for data pipeline ingestion
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

ReportFormat = Literal["html", "csv", "json", "parquet"]


class ReportExporter:
    """Generates and exports TamisTool scan reports.

    Phase 1+ — Not yet implemented.
    """

    TEMPLATES_DIR = Path(__file__).parent / "templates"

    def __init__(self, scan_data: dict[str, Any]) -> None:
        """
        Args:
            scan_data: Structured dict produced by scan execution containing
                       client info, table results, and baseline gap analysis.
        """
        self._data = scan_data

    def export(self, fmt: ReportFormat, output_path: Path) -> Path:
        """Render and write a report in the requested format.

        Args:
            fmt: Output format — html | csv | json | parquet.
            output_path: Destination file path.

        Returns:
            The path the report was written to.
        """
        raise NotImplementedError(f"Phase 1+: Report export format '{fmt}' not yet implemented.")

    def _render_html(self, output_path: Path) -> Path:
        """Render Jinja2 HTML report template."""
        raise NotImplementedError("Phase 1: HTML rendering not yet implemented.")

    def _render_csv(self, output_path: Path) -> Path:
        """Export flat table inventory as CSV."""
        raise NotImplementedError("Phase 2: CSV export not yet implemented.")

    def _render_json(self, output_path: Path) -> Path:
        """Export structured JSON."""
        raise NotImplementedError("Phase 2: JSON export not yet implemented.")

    def _render_parquet(self, output_path: Path) -> Path:
        """Export columnar Parquet file via pandas/pyarrow."""
        raise NotImplementedError("Phase 3: Parquet export not yet implemented.")
