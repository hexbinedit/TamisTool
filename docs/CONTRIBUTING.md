# Contributing to TamisTool

> hexbinedit.io internal development guide.

---

## Dev Environment Setup

**Requirements:** Python 3.11+, [pyenv](https://github.com/pyenv/pyenv) (optional), [pipx](https://pipx.pypa.io/)

```bash
# Clone the repo
git clone https://github.com/hexbinedit/tamistool
cd tamistool

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
.venv\Scripts\activate        # Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify the CLI is available
tamis --version
```

## Project Structure

```
tamis/
├── tamis/
│   ├── __init__.py          Package version and metadata
│   ├── __main__.py          Root Typer app — mounts all sub-apps
│   ├── config.py            Config loading/saving (TOML, defaults)
│   ├── cli/
│   │   ├── client.py        client new/list/show/delete commands
│   │   ├── scan.py          scan run/list/show commands
│   │   ├── report.py        report generate command
│   │   └── config.py        config init/show/set commands
│   ├── db/
│   │   ├── models.py        SQLAlchemy ORM models
│   │   └── session.py       DB mode switching — get_session()
│   ├── kusto/
│   │   ├── client.py        KustoCredentials + TamisKustoClient
│   │   └── queries.py       KQL query templates
│   ├── catalog/
│   │   └── tables.json      Baseline table definitions (JSON — no code needed for new entries)
│   ├── checks/
│   │   └── rules.py         Health check rule definitions
│   └── report/
│       ├── exporter.py      Report generation interface
│       └── templates/
│           └── report.html  Jinja2 HTML report template
├── tests/
├── docs/
├── README.md
└── pyproject.toml
```

## Running Tests

```bash
pytest
# With coverage
pytest --cov=tamis --cov-report=html
```

## How to Add a New Table to the Baseline Catalog

Edit `tamis/catalog/tables.json` and add a new entry to the `"tables"` array:

```json
{
  "name": "YourTableName",
  "description": "What this table contains.",
  "source": "Which connector or product populates it.",
  "required_fields": ["TimeGenerated", "Field1", "Field2"],
  "use_cases": ["use_case_slug_1", "use_case_slug_2"]
}
```

**No code changes are required.** The catalog is loaded dynamically at runtime.

## How to Write a New Health Check Rule

Add a `TableRule` to `tamis/checks/rules.py` and register it in `BUILTIN_RULES`:

```python
MY_TABLE_RULES = TableRule(
    table_name="MyTableName",
    field_rules=[
        FieldRule("FieldName", "Description of the field.", required=True, max_null_percentage=5.0),
    ],
)

BUILTIN_RULES["MyTableName"] = MY_TABLE_RULES
```

Health check execution (Phase 3) will pick up the rule automatically.

## Branch and PR Conventions

- Branch names: `feature/<short-description>`, `fix/<short-description>`, `phase/<N>-<name>`
- PRs require a description and passing CI before merge
- All files must include the hexbinedit.io copyright header

## Copyright Header

All source files must start with:

```python
# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT
```
