# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Tests verifying credential masking — secrets must NEVER appear in output."""

from __future__ import annotations

import pytest

from tamis.kusto.client import KustoCredentials


class TestCredentialMasking:
    """Secrets must not be present in any string representation."""

    SECRET = "super-secret-value-that-must-not-leak"  # noqa: S105

    def _make_creds(self) -> KustoCredentials:
        return KustoCredentials(
            app_id="app-id-123",
            app_secret=self.SECRET,
            tenant_id="tenant-id-456",
            workspace_id="workspace-id-789",
            cluster_uri="https://cluster.kusto.windows.net",
        )

    def test_repr_does_not_contain_secret(self):
        creds = self._make_creds()
        assert self.SECRET not in repr(creds), "Secret leaked in __repr__"

    def test_str_does_not_contain_secret(self):
        creds = self._make_creds()
        assert self.SECRET not in str(creds), "Secret leaked in __str__"

    def test_repr_contains_masked_placeholder(self):
        creds = self._make_creds()
        assert "MASKED" in repr(creds), "__repr__ should contain 'MASKED' placeholder"

    def test_repr_contains_non_secret_fields(self):
        creds = self._make_creds()
        r = repr(creds)
        assert "app-id-123" in r, "app_id should be visible in repr"
        assert "tenant-id-456" in r, "tenant_id should be visible in repr"
        assert "workspace-id-789" in r, "workspace_id should be visible in repr"

    def test_fields_are_accessible(self):
        """Attributes must still be accessible programmatically for SDK use."""
        creds = self._make_creds()
        assert creds.app_secret == self.SECRET

    def test_format_string_does_not_expose_secret(self):
        creds = self._make_creds()
        formatted = f"Connecting with credentials: {creds}"
        assert self.SECRET not in formatted

    def test_fstring_repr_does_not_expose_secret(self):
        creds = self._make_creds()
        formatted = f"{creds!r}"
        assert self.SECRET not in formatted
