from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issue_type: Mapped[str] = mapped_column(String(64), index=True)
    conditions_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    actions_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    legal_ref_ids: Mapped[List[int]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class PathwayTemplate(Base):
    __tablename__ = "pathway_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issue_type: Mapped[str] = mapped_column(String(64), index=True)
    lang: Mapped[str] = mapped_column(String(8), index=True)
    steps_json: Mapped[list[Any]] = mapped_column(JSON, default=list)
    evidence_json: Mapped[list[Any]] = mapped_column(JSON, default=list)
    escalation_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class CityAuthority(Base):
    __tablename__ = "city_authorities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    state: Mapped[str] = mapped_column(String(64))
    cyber_portal_url: Mapped[str] = mapped_column(String(512))
    police_portal_url: Mapped[str] = mapped_column(String(512))
    helpline_numbers: Mapped[List[str]] = mapped_column(JSON, default=list)
    notes_en: Mapped[str] = mapped_column(Text, default="")
    notes_hi: Mapped[str] = mapped_column(Text, default="")


class LegalReference(Base):
    __tablename__ = "legal_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    act_name: Mapped[str] = mapped_column(String(256))
    section_code: Mapped[str] = mapped_column(String(64))
    short_text_en: Mapped[str] = mapped_column(Text, default="")
    short_text_hi: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class AppSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anon_user_id: Mapped[str] = mapped_column(String(128), index=True)
    language: Mapped[str] = mapped_column(String(8), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    queries: Mapped[List["QueryLog"]] = relationship(back_populates="session")


class QueryLog(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    raw_input: Mapped[str] = mapped_column(Text)
    raw_input_redacted: Mapped[str] = mapped_column(Text, default="")
    parsed_output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    session: Mapped[Optional[AppSession]] = relationship(back_populates="queries")
    recommendations: Mapped[List["Recommendation"]] = relationship(back_populates="query")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("queries.id"), nullable=True, index=True)
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    pathway_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    explanation_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    model_version: Mapped[str] = mapped_column(String(64), default="v1")

    query: Mapped[Optional[QueryLog]] = relationship(back_populates="recommendations")
    feedback_entries: Mapped[List["FeedbackEntry"]] = relationship(back_populates="recommendation")


class FeedbackEntry(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(Integer, ForeignKey("recommendations.id"), index=True)
    vote: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    helpfulness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recommendation: Mapped[Recommendation] = relationship(back_populates="feedback_entries")