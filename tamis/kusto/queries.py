# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""KQL query templates for TamisTool scan operations.

Phase 1 — Query execution is not yet implemented.
This module defines the KQL strings used by each scan type.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Discovery scan queries
# ---------------------------------------------------------------------------

#: List all tables present in the workspace with approximate row counts.
DISCOVERY_LIST_TABLES = """
search *
| summarize Count=count(), LastIngestion=max(TimeGenerated) by Type
| order by Type asc
"""

#: Row count for a specific table (parameterised — substitute {table_name}).
DISCOVERY_TABLE_ROW_COUNT = """
{table_name}
| count
"""

#: Most recent event timestamp for a table.
DISCOVERY_TABLE_LAST_EVENT = """
{table_name}
| summarize LastEvent=max(TimeGenerated)
"""

# ---------------------------------------------------------------------------
# Baseline scan queries
# ---------------------------------------------------------------------------

#: Check if a table exists and has recent data (within stale_days).
BASELINE_TABLE_HEALTH = """
{table_name}
| where TimeGenerated > ago({stale_days}d)
| summarize Count=count(), LastEvent=max(TimeGenerated)
"""

# ---------------------------------------------------------------------------
# Health check queries (Phase 3)
# ---------------------------------------------------------------------------

#: Sample field presence for a table.
HEALTH_FIELD_PRESENCE = """
{table_name}
| limit 1000
| project {field_list}
| summarize {null_checks}
"""
