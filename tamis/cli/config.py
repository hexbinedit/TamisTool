# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""CLI commands for configuration management: init, show, set."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax

from tamis.config import CONFIG_PATH, init_config, load_config, save_config

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

app = typer.Typer(help="Manage TamisTool configuration.")
console = Console()
err_console = Console(stderr=True)


@app.command("init")
def config_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config."),
    config_path: Optional[Path] = typer.Option(
        None, "--config", help="Config file path (default: ~/.tamis/config.toml)."
    ),
) -> None:
    """Create the default config file at ~/.tamis/config.toml."""
    path = init_config(config_path=config_path, force=force)
    console.print(f"[green]Config initialised:[/green] {path}")


@app.command("show")
def config_show(
    config_path: Optional[Path] = typer.Option(
        None, "--config", help="Config file path (default: ~/.tamis/config.toml)."
    ),
) -> None:
    """Print current configuration."""
    path = config_path or CONFIG_PATH
    if not path.exists():
        console.print(
            f"[yellow]No config file found at {path}.[/yellow] "
            "Run 'tamis config init' to create one."
        )
        console.print("\n[dim]Using built-in defaults:[/dim]")

    content = path.read_text(encoding="utf-8") if path.exists() else _defaults_as_toml()
    console.print(Syntax(content, "toml", theme="monokai", line_numbers=False))


@app.command("set")
def config_set(
    key: str = typer.Argument(
        ..., help="Config key in dot notation, e.g. 'database.mode'."
    ),
    value: str = typer.Argument(..., help="New value to set."),
    config_path: Optional[Path] = typer.Option(
        None, "--config", help="Config file path (default: ~/.tamis/config.toml)."
    ),
) -> None:
    """Update a single configuration value.

    Examples:

        tamis config set database.mode per_client

        tamis config set scan.stale_days 14
    """
    path = config_path or CONFIG_PATH
    if not path.exists():
        console.print(
            f"[yellow]Config not found at {path}. Creating default config first.[/yellow]"
        )
        init_config(config_path=path)

    config = load_config(config_path=path)

    parts = key.split(".")
    if len(parts) != 2:
        err_console.print(
            "[red]Error:[/red] Key must be in 'section.key' format, e.g. 'database.mode'."
        )
        raise typer.Exit(code=1)

    section, field = parts
    if section not in config:
        err_console.print(
            f"[red]Error:[/red] Unknown section '{section}'. "
            f"Valid sections: {', '.join(config.keys())}"
        )
        raise typer.Exit(code=1)

    # Attempt type coercion based on existing value
    existing = config[section].get(field)
    coerced = _coerce_value(value, type(existing) if existing is not None else str)

    config[section][field] = coerced
    save_config(config, config_path=path)
    console.print(f"[green]Set[/green] {key} = {coerced!r}")


def _coerce_value(raw: str, target_type: type):
    """Coerce a string value to the target type."""
    if target_type is bool:
        return raw.lower() in ("true", "1", "yes")
    if target_type is int:
        try:
            return int(raw)
        except ValueError:
            return raw
    if target_type is float:
        try:
            return float(raw)
        except ValueError:
            return raw
    return raw


def _defaults_as_toml() -> str:
    from tamis.config import DEFAULT_CONFIG_TOML
    return DEFAULT_CONFIG_TOML
