# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""TamisTool configuration loading and management."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

import tomli_w

CONFIG_DIR = Path.home() / ".tamis"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "database": {
        "mode": "single",
        "single_db_path": str(Path.home() / ".tamis" / "tamis.db"),
        "per_client_dir": str(Path.home() / ".tamis" / "clients"),
    },
    "scan": {
        "stale_days": 30,
    },
}

DEFAULT_CONFIG_TOML = """\
# TamisTool configuration
# https://hexbinedit.io

[database]
# Storage mode: "single" (all clients in one DB) or "per_client" (one DB per client)
mode = "single"
single_db_path = "~/.tamis/tamis.db"
per_client_dir = "~/.tamis/clients"

[scan]
# Number of days without data before a table is considered stale
stale_days = 30
"""


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load configuration from TOML file, falling back to defaults."""
    path = config_path or CONFIG_PATH
    if not path.exists():
        return _deep_copy(DEFAULT_CONFIG)

    with open(path, "rb") as f:
        user_config = tomllib.load(f)

    config = _deep_copy(DEFAULT_CONFIG)
    for section, values in user_config.items():
        if section in config and isinstance(config[section], dict) and isinstance(values, dict):
            config[section].update(values)
        else:
            config[section] = values
    return config


def save_config(config: dict[str, Any], config_path: Path | None = None) -> None:
    """Persist configuration to TOML file."""
    path = config_path or CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(config, f)


def init_config(config_path: Path | None = None, force: bool = False) -> Path:
    """Create default config file. Returns the path written to."""
    path = config_path or CONFIG_PATH
    if path.exists() and not force:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_CONFIG_TOML, encoding="utf-8")
    return path


def _deep_copy(d: dict[str, Any]) -> dict[str, Any]:
    """Shallow-safe deep copy for simple nested dicts."""
    return {k: dict(v) if isinstance(v, dict) else v for k, v in d.items()}
