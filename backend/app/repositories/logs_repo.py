from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.privacy import redact_pii
from app.db.models import AppSession, FeedbackEntry, QueryLog, Recommendation


def get_or_create_session(db: Session, anon_hash: str, language: str) -> AppSession:
    row = db.scalars(select(AppSession).where(AppSession.anon_user_id == anon_hash)).first()
    if row:
        return row
    row = AppSession(anon_user_id=anon_hash, language=language)
    db.add(row)
    db.flush()
    return row


def log_query(
    db: Session,
    session: Optional[AppSession],
    raw_input: str,
    parsed: dict[str, Any],
    confidence: Optional[float],
    response_time_ms: Optional[int] = None,
) -> QueryLog:
    q = QueryLog(
        session_id=session.id if session else None,
        raw_input=raw_input,
        raw_input_redacted=redact_pii(raw_input),
        parsed_output_json=parsed,
        confidence=confidence,
        response_time_ms=response_time_ms,
    )
    db.add(q)
    db.flush()
    return q


def save_recommendation(
    db: Session,
    session: Optional[AppSession],
    query: Optional[QueryLog],
    pathway: dict[str, Any],
    explanation: dict[str, Any],
    model_version: str,
) -> Recommendation:
    rec = Recommendation(
        query_id=query.id if query else None,
        session_id=session.id if session else None,
        pathway_json=pathway,
        explanation_json=explanation,
        model_version=model_version,
    )
    db.add(rec)
    db.flush()
    return rec


def save_feedback(
    db: Session,
    recommendation_id: int,
    vote: int,
    comment: Optional[str],
    helpfulness_score: Optional[float],
) -> FeedbackEntry:
    fb = FeedbackEntry(
        recommendation_id=recommendation_id,
        vote=vote,
        comment=comment,
        helpfulness_score=helpfulness_score,
    )
    db.add(fb)
    db.flush()
    return fb
