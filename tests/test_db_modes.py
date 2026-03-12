# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Tests for database mode switching (single vs per_client)."""

from __future__ import annotations

import pytest

from tamis.db.session import resolve_db_path


class TestSingleMode:
    def test_returns_configured_single_path(self, tmp_path):
        db_file = tmp_path / "tamis.db"
        config = {
            "database": {
                "mode": "single",
                "single_db_path": str(db_file),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        resolved = resolve_db_path(config=config)
        assert resolved == db_file.resolve()

    def test_single_mode_ignores_client_name(self, tmp_path):
        db_file = tmp_path / "tamis.db"
        config = {
            "database": {
                "mode": "single",
                "single_db_path": str(db_file),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        # client_name should have no effect in single mode
        resolved_with = resolve_db_path(client_name="acme", config=config)
        resolved_without = resolve_db_path(client_name=None, config=config)
        assert resolved_with == resolved_without

    def test_default_mode_is_single(self, tmp_path):
        # When mode key is absent, defaults to single
        db_file = tmp_path / "tamis.db"
        config = {
            "database": {
                "single_db_path": str(db_file),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        resolved = resolve_db_path(config=config)
        assert resolved == db_file.resolve()


class TestPerClientMode:
    def test_returns_client_specific_path(self, tmp_path):
        clients_dir = tmp_path / "clients"
        config = {
            "database": {
                "mode": "per_client",
                "single_db_path": str(tmp_path / "tamis.db"),
                "per_client_dir": str(clients_dir),
            }
        }
        resolved = resolve_db_path(client_name="acme", config=config)
        assert resolved == (clients_dir / "acme.db").resolve()

    def test_different_clients_get_different_paths(self, tmp_path):
        clients_dir = tmp_path / "clients"
        config = {
            "database": {
                "mode": "per_client",
                "single_db_path": str(tmp_path / "tamis.db"),
                "per_client_dir": str(clients_dir),
            }
        }
        path_acme = resolve_db_path(client_name="acme", config=config)
        path_beta = resolve_db_path(client_name="beta-corp", config=config)
        assert path_acme != path_beta
        assert path_acme.name == "acme.db"
        assert path_beta.name == "beta-corp.db"

    def test_raises_without_client_name(self, tmp_path):
        config = {
            "database": {
                "mode": "per_client",
                "single_db_path": str(tmp_path / "tamis.db"),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        with pytest.raises(ValueError, match="client_name"):
            resolve_db_path(client_name=None, config=config)

    def test_raises_on_unknown_mode(self, tmp_path):
        config = {
            "database": {
                "mode": "invalid_mode",
                "single_db_path": str(tmp_path / "tamis.db"),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        with pytest.raises(ValueError, match="Unknown database.mode"):
            resolve_db_path(config=config)


class TestGetSession:
    def test_single_mode_creates_db_and_tables(self, tmp_path):
        from tamis.db.models import Client
        from tamis.db.session import get_session

        db_file = tmp_path / "test.db"
        config = {
            "database": {
                "mode": "single",
                "single_db_path": str(db_file),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        with get_session(config=config) as session:
            # Should be able to query without error (tables created)
            count = session.query(Client).count()
            assert count == 0
        assert db_file.exists()

    def test_per_client_mode_creates_scoped_db(self, tmp_path):
        from tamis.db.models import Client
        from tamis.db.session import get_session

        clients_dir = tmp_path / "clients"
        config = {
            "database": {
                "mode": "per_client",
                "single_db_path": str(tmp_path / "tamis.db"),
                "per_client_dir": str(clients_dir),
            }
        }
        with get_session(client_name="testclient", config=config) as session:
            count = session.query(Client).count()
            assert count == 0
        assert (clients_dir / "testclient.db").exists()

    def test_session_rollback_on_exception(self, tmp_path):
        from tamis.db.models import Client
        from tamis.db.session import get_session

        db_file = tmp_path / "rollback_test.db"
        config = {
            "database": {
                "mode": "single",
                "single_db_path": str(db_file),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }

        with pytest.raises(RuntimeError):
            with get_session(config=config) as session:
                session.add(Client(name="will-be-rolled-back"))
                session.flush()
                raise RuntimeError("Simulated failure")

        # Client should not be persisted after rollback
        with get_session(config=config) as session:
            count = session.query(Client).count()
            assert count == 0

    def test_client_and_default_project_created(self, tmp_path):
        from tamis.db.models import Client, Project
        from tamis.db.session import get_session

        db_file = tmp_path / "client_test.db"
        config = {
            "database": {
                "mode": "single",
                "single_db_path": str(db_file),
                "per_client_dir": str(tmp_path / "clients"),
            }
        }
        with get_session(config=config) as session:
            client = Client(name="test-client")
            session.add(client)
            session.flush()
            project = Project(client_id=client.id, name="default")
            session.add(project)

        with get_session(config=config) as session:
            c = session.query(Client).filter(Client.name == "test-client").first()
            assert c is not None
            assert len(c.projects) == 1
            assert c.projects[0].name == "default"
