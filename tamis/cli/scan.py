# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""CLI commands for scan management: run, list, show.

NOTE: Scan execution (Kusto connectivity) is implemented in Phase 1.
      Phase 0 provides the CLI interface and DB scaffolding only.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tamis.auth.provider import build_provider
from tamis.db.models import Scan, TableResult
from tamis.db.session import get_session

app = typer.Typer(help="Run and review workspace scans.")
console = Console()
err_console = Console(stderr=True)


class ScanType(str, Enum):
    discovery = "discovery"
    baseline = "baseline"
    health = "health_check"


class AuthMode(str, Enum):
    client_credentials = "client-credentials"
    device_code = "device-code"


@app.command("run")
def scan_run(
    client: str = typer.Option(..., "--client", "-c", help="Target client name."),
    scan_type: ScanType = typer.Option(
        ScanType.discovery, "--type", "-t", help="Scan type to run."
    ),
    auth_mode: AuthMode = typer.Option(
        AuthMode.client_credentials,
        "--auth",
        help=(
            "Authentication mode. "
            "'client-credentials' (default) uses app ID + secret. "
            "'device-code' uses an interactive browser challenge."
        ),
    ),
    # Credentials — never stored, passed at runtime only
    app_id: Optional[str] = typer.Option(
        None, "--app-id", envvar="TAMIS_APP_ID", help="Azure AD app registration client ID."
    ),
    app_secret: Optional[str] = typer.Option(
        None,
        "--app-secret",
        envvar="TAMIS_APP_SECRET",
        help="Client secret (client-credentials mode only).",
        hide_input=True,
    ),
    tenant_id: Optional[str] = typer.Option(
        None, "--tenant-id", envvar="TAMIS_TENANT_ID", help="Azure tenant ID."
    ),
    workspace_id: Optional[str] = typer.Option(
        None, "--workspace-id", envvar="TAMIS_WORKSPACE_ID", help="Sentinel workspace ID."
    ),
    cluster_uri: Optional[str] = typer.Option(
        None, "--cluster-uri", envvar="TAMIS_CLUSTER_URI", help="Kusto cluster URI."
    ),
) -> None:
    """Run a scan against a client workspace.

    Phase 1 — Kusto connectivity not yet implemented.
    """
    # ── Auth flag validation ──────────────────────────────────────────────
    if not app_id:
        err_console.print("[red]Error:[/red] --app-id (or TAMIS_APP_ID) is required.")
        raise typer.Exit(code=1)

    if not tenant_id:
        err_console.print("[red]Error:[/red] --tenant-id (or TAMIS_TENANT_ID) is required.")
        raise typer.Exit(code=1)

    if auth_mode == AuthMode.client_credentials and not app_secret:
        err_console.print(
            "[red]Error:[/red] --app-secret (or TAMIS_APP_SECRET) is required "
            "for --auth client-credentials."
        )
        raise typer.Exit(code=1)

    if auth_mode == AuthMode.device_code and app_secret:
        console.print(
            "[yellow]WARN:[/yellow] --app-secret is ignored in device-code mode."
        )

    # ── Build auth provider ───────────────────────────────────────────────
    provider = build_provider(
        auth_mode=auth_mode.value,
        tenant_id=tenant_id,
        app_id=app_id,
        app_secret=app_secret,
    )
    # credential = provider.get_credential()
    # Passed to Kusto client in Phase 1 — provider is ready.

    console.print(
        f"[yellow]Phase 0:[/yellow] Scan execution is not yet implemented. "
        f"Scan type '{scan_type.value}' for client '{client}' | auth={auth_mode.value}."
    )
    console.print(
        "Kusto connectivity and scan logic will be added in Phase 1. "
        "See docs/SCAN_TYPES.md for planned scan behaviour."
    )


@app.command("list")
def scan_list(
    client: str = typer.Option(..., "--client", "-c", help="Client name."),
) -> None:
    """List past scans for a client."""
    with get_session(client_name=client) as session:
        from tamis.db.models import Client, Project

        db_client = session.query(Client).filter(Client.name == client).first()
        if not db_client:
            err_console.print(f"[red]Error:[/red] Client '{client}' not found.")
            raise typer.Exit(code=1)

        project_ids = [p.id for p in db_client.projects]
        if not project_ids:
            console.print("[yellow]No projects found for this client.[/yellow]")
            return

        scans = (
            session.query(Scan)
            .filter(Scan.project_id.in_(project_ids))
            .order_by(Scan.run_at.desc())
            .all()
        )

    if not scans:
        console.print(f"[yellow]No scans found for client '{client}'.[/yellow]")
        return

    tbl = Table(title=f"Scans — {client}", show_lines=False)
    tbl.add_column("ID", justify="right", style="dim")
    tbl.add_column("Project ID", justify="right")
    tbl.add_column("Type")
    tbl.add_column("Status")
    tbl.add_column("Run At")

    for s in scans:
        status_style = "green" if s.status == "complete" else "yellow"
        tbl.add_row(
            str(s.id),
            str(s.project_id),
            s.scan_type,
            f"[{status_style}]{s.status}[/{status_style}]",
            s.run_at.strftime("%Y-%m-%d %H:%M UTC"),
        )

    console.print(tbl)


@app.command("show")
def scan_show(
    scan_id: int = typer.Argument(..., help="Scan ID to inspect."),
    client: Optional[str] = typer.Option(
        None, "--client", "-c", help="Client name (required for per_client DB mode)."
    ),
) -> None:
    """Show results of a specific scan."""
    with get_session(client_name=client) as session:
        scan = session.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            err_console.print(f"[red]Error:[/red] Scan id={scan_id} not found.")
            raise typer.Exit(code=1)

        console.print(f"\n[bold]Scan {scan.id}[/bold]  type={scan.scan_type}  status={scan.status}")
        console.print(f"Run at: {scan.run_at.strftime('%Y-%m-%d %H:%M UTC')}")

        results = (
            session.query(TableResult)
            .filter(TableResult.scan_id == scan_id)
            .order_by(TableResult.table_name)
            .all()
        )

    if not results:
        console.print("[yellow]No table results recorded for this scan.[/yellow]")
        return

    tbl = Table(title="Table Results", show_lines=False)
    tbl.add_column("Table", style="bold")
    tbl.add_column("Status")
    tbl.add_column("Row Count", justify="right")
    tbl.add_column("Last Event")

    for r in results:
        status_colors = {
            "healthy": "green",
            "empty": "yellow",
            "missing": "red",
            "warning": "orange3",
        }
        sc = status_colors.get(r.status, "white")
        tbl.add_row(
            r.table_name,
            f"[{sc}]{r.status}[/{sc}]",
            f"{r.row_count:,}" if r.row_count is not None else "—",
            r.last_event_time.strftime("%Y-%m-%d") if r.last_event_time else "—",
        )

    console.print(tbl)
