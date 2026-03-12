# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Tests for the baseline table catalog loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tamis.catalog import load_catalog

CATALOG_JSON_PATH = Path(__file__).parent.parent / "tamis" / "catalog" / "tables.json"

# Tables explicitly named in the specification
SPEC_REQUIRED_TABLES = {
    "SecurityAlert",
    "SecurityEvent",
    "SignInLogs",
    "AuditLogs",
    "CommonSecurityLog",
    "DeviceEvents",
    "DeviceNetworkEvents",
    "DeviceProcessEvents",
    "OfficeActivity",
    "AzureActivity",
}


class TestCatalogLoading:
    def test_load_catalog_returns_list(self):
        catalog = load_catalog()
        assert isinstance(catalog, list), "Catalog must be a list of table dicts"

    def test_catalog_is_not_empty(self):
        catalog = load_catalog()
        assert len(catalog) > 0, "Catalog must contain at least one entry"

    def test_each_entry_has_required_keys(self):
        catalog = load_catalog()
        required_keys = {"name", "description", "source", "required_fields", "use_cases"}
        for entry in catalog:
            missing = required_keys - set(entry.keys())
            assert not missing, f"Entry {entry.get('name')!r} is missing keys: {missing}"

    def test_table_names_are_strings(self):
        catalog = load_catalog()
        for entry in catalog:
            assert isinstance(entry["name"], str), f"Table name must be a string: {entry!r}"
            assert entry["name"].strip(), "Table name must not be blank"

    def test_required_fields_are_lists(self):
        catalog = load_catalog()
        for entry in catalog:
            assert isinstance(entry["required_fields"], list), (
                f"{entry['name']}: 'required_fields' must be a list"
            )

    def test_use_cases_are_lists(self):
        catalog = load_catalog()
        for entry in catalog:
            assert isinstance(entry["use_cases"], list), (
                f"{entry['name']}: 'use_cases' must be a list"
            )

    def test_spec_required_tables_present(self):
        catalog = load_catalog()
        names = {entry["name"] for entry in catalog}
        missing = SPEC_REQUIRED_TABLES - names
        assert not missing, (
            f"Catalog is missing tables required by specification: {missing}"
        )

    def test_no_duplicate_table_names(self):
        catalog = load_catalog()
        names = [entry["name"] for entry in catalog]
        assert len(names) == len(set(names)), "Catalog contains duplicate table names"

    def test_catalog_json_is_valid(self):
        """Ensure the raw JSON file parses cleanly."""
        raw = CATALOG_JSON_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert "tables" in data, "tables.json must have a 'tables' key"
        assert isinstance(data["tables"], list)

    def test_catalog_json_has_meta(self):
        raw = CATALOG_JSON_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert "_meta" in data, "tables.json should contain a '_meta' block"
        assert "version" in data["_meta"]

    def test_new_entry_loadable_without_code_changes(self, tmp_path, monkeypatch):
        """Adding a new table to tables.json should not require code changes."""
        import tamis.catalog as cat_module

        new_catalog = {
            "_meta": {"version": "test", "description": "test", "maintainer": "test", "note": ""},
            "tables": [
                {
                    "name": "CustomTestTable",
                    "description": "A custom table added for testing.",
                    "source": "Custom",
                    "required_fields": ["TimeGenerated", "TestField"],
                    "use_cases": ["test_use_case"],
                }
            ],
        }
        test_json = tmp_path / "tables.json"
        test_json.write_text(json.dumps(new_catalog), encoding="utf-8")

        # Monkeypatch the catalog path and reload
        monkeypatch.setattr(cat_module, "_CATALOG_PATH", test_json)
        catalog = cat_module.load_catalog()
        assert len(catalog) == 1
        assert catalog[0]["name"] == "CustomTestTable"
