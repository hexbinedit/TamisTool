# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Device Code Flow token cache for TamisTool.

Caches MSAL token data locally so the user does not need to complete the
browser challenge on every run. Client Credentials tokens are NOT cached
(they are cheap to reissue and require no user interaction).

SECURITY
--------
- Cache files are written with mode 0o600 (owner read/write only).
- Never log or print token values.
- Cache directory (~/.tamis/token_cache/) must not be committed to source
  control — ensured by .gitignore.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CACHE_DIR = Path.home() / ".tamis" / "token_cache"


def get_cache_path(tenant_id: str, app_id: str) -> Path:
    """Return the cache file path for a given tenant/app combination."""
    return CACHE_DIR / f"{tenant_id}_{app_id}.json"


def load_cache(tenant_id: str, app_id: str) -> dict[str, Any] | None:
    """Load cached token data for the given tenant/app.

    Returns the parsed token dict, or None if no cache exists.
    Never raises on missing or unreadable cache — callers should handle None
    by initiating a fresh Device Code flow.
    """
    path = get_cache_path(tenant_id, app_id)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_cache(tenant_id: str, app_id: str, token_data: dict[str, Any]) -> None:
    """Persist token data to disk with restricted permissions.

    Args:
        tenant_id:   Azure tenant ID — used to scope the cache file name.
        app_id:      App registration client ID.
        token_data:  Token dict (e.g. serialised MSAL cache) to persist.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = get_cache_path(tenant_id, app_id)
    path.write_text(json.dumps(token_data), encoding="utf-8")
    # Restrict to owner read/write only — tokens are sensitive
    try:
        path.chmod(0o600)
    except NotImplementedError:
        # Windows does not support chmod; rely on NTFS ACLs and user profile isolation
        pass


def clear_cache(tenant_id: str, app_id: str) -> bool:
    """Remove a cached token file.

    Returns True if the file was deleted, False if it did not exist.
    """
    path = get_cache_path(tenant_id, app_id)
    if path.exists():
        path.unlink()
        return True
    return False
