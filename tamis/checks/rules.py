# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Health check rule definitions for TamisTool.

Phase 3 — Health check execution is not yet implemented.
This module defines the rule structure and interface contract.

Rules are evaluated per-table during a health_check scan and produce
FieldResult records indicating field presence and quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class FieldRule:
    """A validation rule for a single field within a table."""

    field_name: str
    description: str
    required: bool = True
    max_null_percentage: float = 10.0  # Flag if > this % of sampled rows are null
    validator: Callable[[Any], bool] | None = None  # Optional value-level check

    def __repr__(self) -> str:
        return f"<FieldRule field={self.field_name!r} required={self.required}>"


@dataclass
class TableRule:
    """Collection of field rules for a specific table."""

    table_name: str
    field_rules: list[FieldRule] = field(default_factory=list)

    def validate(self, sample_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Evaluate all field rules against sampled data rows.

        Phase 3 — Not yet implemented.
        """
        raise NotImplementedError("Phase 3: Health check validation not yet implemented.")


# ---------------------------------------------------------------------------
# Built-in rules for well-known tables
# ---------------------------------------------------------------------------

SECURITY_EVENT_RULES = TableRule(
    table_name="SecurityEvent",
    field_rules=[
        FieldRule("EventID", "Windows Event ID — must be present and non-null.", required=True, max_null_percentage=0.0),
        FieldRule("Computer", "Source computer hostname.", required=True, max_null_percentage=5.0),
        FieldRule("Account", "User account involved in the event.", required=True, max_null_percentage=20.0),
        FieldRule("TimeGenerated", "Event timestamp.", required=True, max_null_percentage=0.0),
    ],
)

SIGN_IN_LOGS_RULES = TableRule(
    table_name="SignInLogs",
    field_rules=[
        FieldRule("UserPrincipalName", "UPN of the signing-in user.", required=True, max_null_percentage=5.0),
        FieldRule("IPAddress", "Client IP address.", required=True, max_null_percentage=10.0),
        FieldRule("ResultType", "Sign-in result code (0 = success).", required=True, max_null_percentage=0.0),
        FieldRule("TimeGenerated", "Event timestamp.", required=True, max_null_percentage=0.0),
    ],
)

DEVICE_PROCESS_RULES = TableRule(
    table_name="DeviceProcessEvents",
    field_rules=[
        FieldRule("FileName", "Process image name.", required=True, max_null_percentage=5.0),
        FieldRule("ProcessCommandLine", "Full command line — critical for analysis.", required=True, max_null_percentage=15.0),
        FieldRule("DeviceName", "Endpoint hostname.", required=True, max_null_percentage=0.0),
        FieldRule("TimeGenerated", "Event timestamp.", required=True, max_null_percentage=0.0),
    ],
)

#: Registry of all built-in table rules, keyed by table name.
BUILTIN_RULES: dict[str, TableRule] = {
    r.table_name: r
    for r in [
        SECURITY_EVENT_RULES,
        SIGN_IN_LOGS_RULES,
        DEVICE_PROCESS_RULES,
    ]
}
