# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""CLI commands for client management: new, list, show, delete."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tamis.db.models import Client, Project, Scan
from tamis.db.session import get_session

app = typer.Typer(help="Manage client records.")
console = Console()
err_console = Console(stderr=True, style="bold red")


def _resolve_client_name(name: str, session) -> Client | None:
    """Look up a client by name. Returns None if not found."""
    return session.query(Client).filter(Client.name == name).first()


@app.command("new")
def client_new(
    name: str = typer.Argument(..., help="Unique client name (slug-style, e.g. 'acme-corp')."),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Optional notes."),
    workspace_id: Optional[str] = typer.Option(
        None, "--workspace-id", "-w", help="Sentinel workspace ID (reference only, not a secret)."
    ),
) -> None:
    """Create a new client record and a default project."""
    with get_session(client_name=name) as session:
        existing = _resolve_client_name(name, session)
        if existing:
            err_console.print(f"[red]Error:[/red] Client '{name}' already exists (id={existing.id}).")
            raise typer.Exit(code=1)

        client = Client(name=name, notes=notes, sentinel_workspace_id=workspace_id)
        session.add(client)
        session.flush()  # assign client.id before creating project

        default_project = Project(client_id=client.id, name="default")
        session.add(default_project)

    console.print(f"[green]Created client[/green] '{name}' with a default project.")


@app.command("list")
def client_list() -> None:
    """List all clients."""
    with get_session() as session:
        clients = session.query(Client).order_by(Client.name).all()

    if not clients:
        console.print("[yellow]No clients found.[/yellow] Use 'tamis client new <name>' to add one.")
        return

    tbl = Table(title="Clients", show_lines=False)
    tbl.add_column("ID", style="dim", justify="right")
    tbl.add_column("Name", style="bold")
    tbl.add_column("Workspace ID", style="dim")
    tbl.add_column("Created")
    tbl.add_column("Notes")

    for c in clients:
        tbl.add_row(
            str(c.id),
            c.name,
            c.sentinel_workspace_id or "—",
            c.created_at.strftime("%Y-%m-%d"),
            c.notes or "—",
        )

    console.print(tbl)


@app.command("show")
def client_show(
    name: str = typer.Argument(..., help="Client name."),
) -> None:
    """Show client details and scan history."""
    with get_session(client_name=name) as session:
        client = _resolve_client_name(name, session)
        if not client:
            err_console.print(f"[red]Error:[/red] Client '{name}' not found.")
            raise typer.Exit(code=1)

        console.print(f"\n[bold]Client:[/bold] {client.name} (id={client.id})")
        if client.notes:
            console.print(f"[dim]Notes:[/dim] {client.notes}")
        if client.sentinel_workspace_id:
            console.print(f"[dim]Workspace ID:[/dim] {client.sentinel_workspace_id}")
        console.print(f"[dim]Created:[/dim] {client.created_at.strftime('%Y-%m-%d %H:%M UTC')}")

        for project in client.projects:
            console.print(f"\n  [bold]Project:[/bold] {project.name} (id={project.id})")

            scans = (
                session.query(Scan)
                .filter(Scan.project_id == project.id)
                .order_by(Scan.run_at.desc())
                .limit(10)
                .all()
            )

            if not scans:
                console.print("    [dim]No scans yet.[/dim]")
                continue

            scan_tbl = Table(show_header=True, show_lines=False, padding=(0, 1))
            scan_tbl.add_column("Scan ID", style="dim", justify="right")
            scan_tbl.add_column("Type")
            scan_tbl.add_column("Status")
            scan_tbl.add_column("Run At")

            for s in scans:
                status_style = "green" if s.status == "complete" else "yellow"
                scan_tbl.add_row(
                    str(s.id),
                    s.scan_type,
                    f"[{status_style}]{s.status}[/{status_style}]",
                    s.run_at.strftime("%Y-%m-%d %H:%M UTC"),
                )

            console.print(scan_tbl)


@app.command("delete")
def client_delete(
    name: str = typer.Argument(..., help="Client name to remove."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Remove a client and all associated data."""
    if not yes:
        confirm = typer.confirm(
            f"This will permanently delete client '{name}' and all its scans. Continue?"
        )
        if not confirm:
            console.print("Aborted.")
            raise typer.Exit(code=0)

    with get_session(client_name=name) as session:
        client = _resolve_client_name(name, session)
        if not client:
            err_console.print(f"[red]Error:[/red] Client '{name}' not found.")
            raise typer.Exit(code=1)

        session.delete(client)

    console.print(f"[green]Deleted[/green] client '{name}'.")
