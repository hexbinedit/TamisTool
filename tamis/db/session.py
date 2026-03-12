# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""Database session management with single / per-client mode switching.

All modules that need database access must import get_session() from here.
The DB path is NEVER hardcoded elsewhere — this module is the single source of truth.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tamis.config import load_config
from tamis.db.models import Base

if TYPE_CHECKING:
    pass

_DB_MODE_SINGLE = "single"
_DB_MODE_PER_CLIENT = "per_client"


def resolve_db_path(client_name: str | None = None, config: dict | None = None) -> Path:
    """Determine the SQLite DB path based on current configuration.

    Args:
        client_name: Required when database.mode is "per_client".
        config: Pre-loaded config dict; loaded from disk if not provided.

    Returns:
        Resolved Path to the SQLite database file.

    Raises:
        ValueError: If mode is "per_client" and client_name is not supplied.
        ValueError: If an unknown database mode is configured.
    """
    cfg = config or load_config()
    db_cfg = cfg.get("database", {})
    mode = db_cfg.get("mode", _DB_MODE_SINGLE)

    if mode == _DB_MODE_SINGLE:
        raw = db_cfg.get("single_db_path", "~/.tamis/tamis.db")
        return Path(raw).expanduser().resolve()

    if mode == _DB_MODE_PER_CLIENT:
        if not client_name:
            raise ValueError(
                "database.mode is 'per_client' but no client_name was provided. "
                "Pass --client when running tamis commands."
            )
        raw_dir = db_cfg.get("per_client_dir", "~/.tamis/clients")
        client_dir = Path(raw_dir).expanduser().resolve()
        return client_dir / f"{client_name}.db"

    raise ValueError(
        f"Unknown database.mode {mode!r} in config. "
        f"Valid values are: '{_DB_MODE_SINGLE}', '{_DB_MODE_PER_CLIENT}'."
    )


def _make_engine(db_path: Path):
    """Create a SQLite engine, ensuring parent directories exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(engine)
    return engine


@contextmanager
def get_session(
    client_name: str | None = None,
    config: dict | None = None,
) -> Generator[Session, None, None]:
    """Context manager yielding a SQLAlchemy Session.

    Usage::

        with get_session(client_name="acme") as session:
            clients = session.query(Client).all()

    The session is committed on successful exit and rolled back on exception.

    Args:
        client_name: Client name used in per_client mode to select the DB file.
        config: Pre-loaded config dict; loaded from disk if not provided.
    """
    cfg = config or load_config()
    db_path = resolve_db_path(client_name=client_name, config=cfg)
    engine = _make_engine(db_path)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
