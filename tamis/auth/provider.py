# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Auth abstraction layer for TamisTool.

Supports two modes:
  client-credentials  — OAuth2 app secret flow (fully automated, default)
  device-code         — Interactive browser-based OAuth2 flow (human-in-the-loop, once)

Usage::

    provider = build_provider(
        auth_mode="client-credentials",
        tenant_id="...",
        app_id="...",
        app_secret="...",
    )
    credential = provider.get_credential()
    # Pass credential to Kusto client (Phase 1)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from azure.identity import ClientSecretCredential, DeviceCodeCredential


class AuthProvider(ABC):
    """Base class for TamisTool authentication providers."""

    @abstractmethod
    def get_credential(self):
        """Return an Azure credential object suitable for Kusto / ADX authentication."""
        ...


class ClientCredentialsProvider(AuthProvider):
    """OAuth2 Client Credentials flow — fully automated, no human interaction required."""

    def __init__(self, tenant_id: str, app_id: str, app_secret: str) -> None:
        self.tenant_id = tenant_id
        self.app_id = app_id
        self._app_secret = app_secret  # underscore — never expose in logs

    def __repr__(self) -> str:
        return (
            f"ClientCredentialsProvider("
            f"tenant_id={self.tenant_id!r}, app_id={self.app_id!r}, app_secret='***MASKED***')"
        )

    def get_credential(self) -> ClientSecretCredential:
        return ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.app_id,
            client_secret=self._app_secret,
        )


class DeviceCodeProvider(AuthProvider):
    """OAuth2 Device Code flow — interactive, requires the user to complete a browser challenge once.

    Token caching (via tamis.auth.token_cache) avoids re-authentication on subsequent runs.
    Cache integration is wired during Phase 1 Kusto implementation.
    """

    def __init__(self, tenant_id: str, app_id: str) -> None:
        self.tenant_id = tenant_id
        self.app_id = app_id

    def __repr__(self) -> str:
        return (
            f"DeviceCodeProvider("
            f"tenant_id={self.tenant_id!r}, app_id={self.app_id!r})"
        )

    def get_credential(self) -> DeviceCodeCredential:
        # DeviceCodeCredential handles the URL/code prompt natively.
        # On first call it will print a URL and code; the user completes auth in a browser.
        # Token cache persistence is integrated in Phase 1.
        return DeviceCodeCredential(
            tenant_id=self.tenant_id,
            client_id=self.app_id,
        )


def build_provider(
    auth_mode: str,
    tenant_id: str,
    app_id: str,
    app_secret: str | None = None,
) -> AuthProvider:
    """Factory: construct the correct AuthProvider for the given mode.

    Args:
        auth_mode:  "client-credentials" or "device-code".
        tenant_id:  Azure tenant ID (required for both modes).
        app_id:     App registration client ID (required for both modes).
        app_secret: Client secret (required for client-credentials, unused for device-code).

    Returns:
        An AuthProvider instance.

    Raises:
        ValueError: If auth_mode is not recognised.
    """
    if auth_mode == "client-credentials":
        return ClientCredentialsProvider(
            tenant_id=tenant_id,
            app_id=app_id,
            app_secret=app_secret,  # type: ignore[arg-type]  # validated by caller
        )
    if auth_mode == "device-code":
        return DeviceCodeProvider(tenant_id=tenant_id, app_id=app_id)

    raise ValueError(
        f"Unknown auth mode: {auth_mode!r}. "
        "Valid values are: 'client-credentials', 'device-code'."
    )
