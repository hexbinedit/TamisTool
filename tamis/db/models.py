# Copyright (c) 2024 hexbinedit.io
# SPDX-License-Identifier: MIT

"""SQLAlchemy ORM models for TamisTool."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Client(Base):
    """Top-level client record."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Reference only — no secrets stored
    sentinel_workspace_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    projects: Mapped[list[Project]] = relationship(
        "Project", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.name!r}>"


class Project(Base):
    """Project scoping under a client."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    client: Mapped[Client] = relationship("Client", back_populates="projects")
    scans: Mapped[list[Scan]] = relationship(
        "Scan", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} client_id={self.client_id}>"


class Scan(Base):
    """Individual scan run record."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    scan_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # discovery | baseline | health_check
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending | running | complete | failed

    project: Mapped[Project] = relationship("Project", back_populates="scans")
    table_results: Mapped[list[TableResult]] = relationship(
        "TableResult", back_populates="scan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Scan id={self.id} type={self.scan_type!r} status={self.status!r}>"


class TableResult(Base):
    """Per-table findings from a scan."""

    __tablename__ = "table_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(Integer, ForeignKey("scans.id"), nullable=False)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_event_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unknown"
    )  # healthy | empty | missing | warning

    scan: Mapped[Scan] = relationship("Scan", back_populates="table_results")
    field_results: Mapped[list[FieldResult]] = relationship(
        "FieldResult", back_populates="table_result", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TableResult id={self.id} table={self.table_name!r} status={self.status!r}>"


class FieldResult(Base):
    """Per-field findings within a table result (Phase 3 — health checks)."""

    __tablename__ = "field_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_result_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("table_results.id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_present: Mapped[Optional[bool]] = mapped_column(nullable=True)
    null_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array

    table_result: Mapped[TableResult] = relationship(
        "TableResult", back_populates="field_results"
    )

    def __repr__(self) -> str:
        return f"<FieldResult id={self.id} field={self.field_name!r} present={self.is_present}>"
