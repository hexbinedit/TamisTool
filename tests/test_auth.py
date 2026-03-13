# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Unit tests for tamis.auth.provider — auth abstraction layer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tamis.auth.provider import (
    AuthProvider,
    ClientCredentialsProvider,
    DeviceCodeProvider,
    build_provider,
)


class TestBuildProvider:
    def test_client_credentials_returns_correct_type(self):
        provider = build_provider(
            auth_mode="client-credentials",
            tenant_id="tenant-123",
            app_id="app-456",
            app_secret="secret-789",
        )
        assert isinstance(provider, ClientCredentialsProvider)

    def test_device_code_returns_correct_type(self):
        provider = build_provider(
            auth_mode="device-code",
            tenant_id="tenant-123",
            app_id="app-456",
        )
        assert isinstance(provider, DeviceCodeProvider)

    def test_device_code_ignores_app_secret(self):
        # app_secret should be accepted without error but not stored
        provider = build_provider(
            auth_mode="device-code",
            tenant_id="tenant-123",
            app_id="app-456",
            app_secret="should-be-ignored",
        )
        assert isinstance(provider, DeviceCodeProvider)
        assert not hasattr(provider, "_app_secret")

    def test_unknown_mode_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown auth mode"):
            build_provider(
                auth_mode="magic-auth",
                tenant_id="tenant-123",
                app_id="app-456",
            )

    def test_all_providers_implement_abstract_base(self):
        cc = build_provider("client-credentials", "t", "a", "s")
        dc = build_provider("device-code", "t", "a")
        assert isinstance(cc, AuthProvider)
        assert isinstance(dc, AuthProvider)


class TestClientCredentialsProvider:
    def test_stores_credentials(self):
        p = ClientCredentialsProvider("tenant", "app", "secret")
        assert p.tenant_id == "tenant"
        assert p.app_id == "app"
        assert p._app_secret == "secret"

    def test_repr_masks_secret(self):
        p = ClientCredentialsProvider("tenant-id", "app-id", "super-secret")
        r = repr(p)
        assert "super-secret" not in r
        assert "MASKED" in r

    def test_repr_shows_non_secret_fields(self):
        p = ClientCredentialsProvider("tenant-id", "app-id", "secret")
        r = repr(p)
        assert "tenant-id" in r
        assert "app-id" in r

    @patch("tamis.auth.provider.ClientSecretCredential")
    def test_get_credential_calls_azure_sdk(self, mock_csc):
        p = ClientCredentialsProvider("tenant", "app", "secret")
        p.get_credential()
        mock_csc.assert_called_once_with(
            tenant_id="tenant",
            client_id="app",
            client_secret="secret",
        )

    @patch("tamis.auth.provider.ClientSecretCredential")
    def test_get_credential_returns_credential_object(self, mock_csc):
        mock_cred = MagicMock()
        mock_csc.return_value = mock_cred
        p = ClientCredentialsProvider("tenant", "app", "secret")
        result = p.get_credential()
        assert result is mock_cred


class TestDeviceCodeProvider:
    def test_stores_non_secret_fields(self):
        p = DeviceCodeProvider("tenant", "app")
        assert p.tenant_id == "tenant"
        assert p.app_id == "app"

    def test_repr_shows_fields(self):
        p = DeviceCodeProvider("tenant-id", "app-id")
        r = repr(p)
        assert "tenant-id" in r
        assert "app-id" in r

    @patch("tamis.auth.provider.DeviceCodeCredential")
    def test_get_credential_calls_azure_sdk(self, mock_dcc):
        p = DeviceCodeProvider("tenant", "app")
        p.get_credential()
        mock_dcc.assert_called_once_with(
            tenant_id="tenant",
            client_id="app",
        )

    @patch("tamis.auth.provider.DeviceCodeCredential")
    def test_get_credential_returns_credential_object(self, mock_dcc):
        mock_cred = MagicMock()
        mock_dcc.return_value = mock_cred
        p = DeviceCodeProvider("tenant", "app")
        result = p.get_credential()
        assert result is mock_cred


class TestTokenCache:
    def test_load_returns_none_when_no_cache(self, tmp_path, monkeypatch):
        import tamis.auth.token_cache as tc
        monkeypatch.setattr(tc, "CACHE_DIR", tmp_path / "token_cache")
        result = tc.load_cache("tenant-123", "app-456")
        assert result is None

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        import tamis.auth.token_cache as tc
        monkeypatch.setattr(tc, "CACHE_DIR", tmp_path / "token_cache")
        data = {"access_token": "test-token", "expires_in": 3600}
        tc.save_cache("tenant-123", "app-456", data)
        loaded = tc.load_cache("tenant-123", "app-456")
        assert loaded == data

    def test_different_tenants_get_separate_cache_files(self, tmp_path, monkeypatch):
        import tamis.auth.token_cache as tc
        monkeypatch.setattr(tc, "CACHE_DIR", tmp_path / "token_cache")
        tc.save_cache("tenant-A", "app-1", {"token": "A"})
        tc.save_cache("tenant-B", "app-1", {"token": "B"})
        assert tc.load_cache("tenant-A", "app-1") == {"token": "A"}
        assert tc.load_cache("tenant-B", "app-1") == {"token": "B"}

    def test_clear_cache_removes_file(self, tmp_path, monkeypatch):
        import tamis.auth.token_cache as tc
        monkeypatch.setattr(tc, "CACHE_DIR", tmp_path / "token_cache")
        tc.save_cache("tenant-123", "app-456", {"token": "data"})
        assert tc.clear_cache("tenant-123", "app-456") is True
        assert tc.load_cache("tenant-123", "app-456") is None

    def test_clear_cache_returns_false_if_no_file(self, tmp_path, monkeypatch):
        import tamis.auth.token_cache as tc
        monkeypatch.setattr(tc, "CACHE_DIR", tmp_path / "token_cache")
        assert tc.clear_cache("no-tenant", "no-app") is False
