# TamisTool Scan Types Reference

> Reference documentation for each scan type with example output, KQL queries, and interpretation guidance.

---

## Overview

TamisTool supports three scan types, implemented across development phases:

| Scan Type | Phase | Command | Purpose |
|---|---|---|---|
| `discovery` | Phase 1 | `tamis scan run --type discovery` | Enumerate all tables in the workspace |
| `baseline` | Phase 2 | `tamis scan run --type baseline` | Compare against the curated table catalog |
| `health_check` | Phase 3 | `tamis scan run --type health` | Validate field-level ingestion quality |

---

## Discovery Scan

### Purpose

Enumerate every table present in the target Sentinel workspace. For each table, record:

- Whether the table is accessible
- Approximate row count
- Last ingestion timestamp
- Status: `active`, `empty`, or `stale`

**Use for:** initial onboarding assessment before committing to deeper analysis.

### Status Definitions

| Status | Meaning |
|---|---|
| `active` | Table has data ingested within the past `scan.stale_days` days |
| `empty` | Table exists but contains zero rows |
| `stale` | Table has rows but last event is older than `scan.stale_days` days |

### KQL Queries Used

**List all tables with row counts and last ingestion:**

```kql
search *
| summarize Count=count(), LastIngestion=max(TimeGenerated) by Type
| order by Type asc
```

**Row count for a specific table:**

```kql
SecurityEvent
| count
```

**Last event timestamp:**

```kql
SecurityEvent
| summarize LastEvent=max(TimeGenerated)
```

### Example Output

```
Table Inventory — acme-corp  (discovery scan, 2024-03-01 09:15 UTC)

Table                    Status    Row Count   Last Event
────────────────────────────────────────────────────────
AuditLogs                active    1,204,532   2024-03-01
AzureActivity            active      342,110   2024-03-01
CommonSecurityLog        stale          8,901   2024-01-15
DeviceEvents             active    4,102,003   2024-03-01
SecurityAlert            active       12,455   2024-03-01
SecurityEvent            empty             0   —
SignInLogs               active      899,201   2024-03-01
```

---

## Baseline Scan

### Purpose

Compare the discovered tables against TamisTool's bundled catalog of well-known Sentinel and
Defender tables. For each catalog entry, report:

- `present` — table exists and has recent data
- `empty` — table exists but has no rows
- `missing` — table is not present in the workspace
- `warning` — present but low volume or stale

**Use for:** gap analysis and client reporting to identify missing data sources.

### Catalog Tables

The bundled catalog covers (see `tamis/catalog/tables.json` for full list):

- SecurityAlert, SecurityEvent, SignInLogs, AuditLogs
- CommonSecurityLog (CEF)
- DeviceEvents, DeviceNetworkEvents, DeviceProcessEvents, DeviceFileEvents, DeviceLogonEvents
- OfficeActivity, AzureActivity, AzureDiagnostics
- Syslog, DnsEvents, WindowsFirewall

### KQL Queries Used

**Check table health within stale window:**

```kql
SignInLogs
| where TimeGenerated > ago(30d)
| summarize Count=count(), LastEvent=max(TimeGenerated)
```

### Example Output

```
Baseline Gap Analysis — acme-corp

Table                    Status     Use Cases
─────────────────────────────────────────────────────────────────────
SecurityAlert            present    incident_response, threat_detection
SecurityEvent            missing    identity_investigation, lateral_movement
SignInLogs               present    identity_investigation, account_compromise
AuditLogs                present    identity_investigation, persistence
CommonSecurityLog        warning    network_investigation, firewall_analysis
DeviceEvents             present    endpoint_investigation, threat_detection
DeviceNetworkEvents      present    c2_detection, lateral_movement
DeviceProcessEvents      present    execution_analysis, malware_detection
OfficeActivity           missing    phishing_follow_up, data_exfiltration

Coverage: 7 / 9 baseline tables present (77%)
```

---

## Health Check Scan

> **Phase 3** — Not yet implemented.

### Purpose

Validate ingestion *quality* on known tables. For each table in scope:

- Check that required fields are present and non-null above a configured threshold
- Sample field values and flag anomalies (e.g. all-null `EventID` in `SecurityEvent`)
- Compare field schema against expected structure

**Use for:** the "is this table being parsed correctly?" assertion before relying on it for investigations.

### Field Rules

Health check rules are defined in `tamis/checks/rules.py`. Each rule specifies:

- `field_name` — the field to check
- `required` — whether absence is a hard failure
- `max_null_percentage` — acceptable null rate in sampled rows

### Example Output (Planned)

```
Health Check — SecurityEvent

Field                    Present    Null %    Status
──────────────────────────────────────────────────────
TimeGenerated            ✓          0.0%      healthy
EventID                  ✓          78.2%     WARNING — high null rate
Computer                 ✓          2.1%      healthy
Account                  ✗          —         MISSING — field not present
Activity                 ✓          0.5%      healthy
```

---

*hexbinedit.io — https://hexbinedit.io*
