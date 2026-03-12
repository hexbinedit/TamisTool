# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Kusto / Azure Data Explorer client wrapper.

Phase 1 — Kusto connectivity is not yet implemented.
This module provides the interface contract for Phase 1 implementation.

IMPORTANT: Credentials must NEVER appear in log output, even in --verbose mode.
           All credential parameters must be masked when logging.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KustoCredentials:
    """Runtime credentials — never persisted to disk or logged."""

    app_id: str
    app_secret: str  # MASKED in all __repr__ / __str__ output
    tenant_id: str
    workspace_id: str
    cluster_uri: str

    def __repr__(self) -> str:
        # Mask secret — never expose in debug output
        return (
            f"KustoCredentials("
            f"app_id={self.app_id!r}, "
            f"app_secret='***MASKED***', "
            f"tenant_id={self.tenant_id!r}, "
            f"workspace_id={self.workspace_id!r}, "
            f"cluster_uri={self.cluster_uri!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class KustoQueryResult:
    """Result container for a Kusto query."""

    rows: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


class TamisKustoClient:
    """Thin wrapper around azure-kusto-data for TamisTool queries.

    Phase 1 — Not yet implemented.
    """

    def __init__(self, credentials: KustoCredentials) -> None:
        self._credentials = credentials
        # Intentionally not logging credentials here

    def test_connection(self) -> bool:
        """Verify connectivity to the Kusto cluster."""
        raise NotImplementedError("Phase 1: Kusto connection not yet implemented.")

    def run_query(self, kql: str) -> KustoQueryResult:
        """Execute a KQL query and return results."""
        raise NotImplementedError("Phase 1: Kusto query execution not yet implemented.")

    def close(self) -> None:
        """Release any held connections."""
        pass
