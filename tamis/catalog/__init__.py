# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Baseline table catalog for TamisTool.

Load the catalog with: from tamis.catalog import load_catalog
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).parent / "tables.json"


def load_catalog() -> list[dict[str, Any]]:
    """Load the bundled baseline table catalog from tables.json.

    Returns a list of table definition dicts. New tables can be added
    by editing tables.json — no code changes required.
    """
    with open(_CATALOG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["tables"]
