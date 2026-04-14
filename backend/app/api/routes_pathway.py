from __future__ import annotations

import time
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.privacy import hash_session_token
from app.db.models import AppSession
from app.db.session import get_db
from app.models.pydantic_schemas import (
    PathwayExplainRequest,
    PathwayExplainResponse,
    PathwayGenerateRequest,
    PathwayGenerateResponse,
)
from app.repositories import logs_repo
from app.services.explainability_service import explain_step
from app.services.pathway_generator import generate_pathway

router = APIRouter(prefix="/v1/pathway", tags=["pathway"])


@router.post("/generate", response_model=PathwayGenerateResponse)
async def pathway_generate(
    req: PathwayGenerateRequest, db: Session = Depends(get_db)
) -> PathwayGenerateResponse:
    t0 = time.perf_counter()
    session: Optional[AppSession] = None
    if req.session_token:
        session = logs_repo.get_or_create_session(
            db, hash_session_token(req.session_token), req.lang
        )
    try:
        out = await generate_pathway(
            db,
            req.extraction,
            req.lang,
            req.city or (req.extraction.entities or {}).get("city_slug"),
            req.user_notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    q = None
    if session:
        q = logs_repo.log_query(
            db,
            session,
            req.user_notes or "[pathway_generate]",
            req.extraction.model_dump(),
            req.extraction.confidence,
            response_time_ms=int((time.perf_counter() - t0) * 1000),
        )
    pathway_payload: dict[str, Any] = {
        "pathway": [p.model_dump() for p in out.pathway],
        "evidence_checklist": out.evidence_checklist,
        "city_contacts": out.city_contacts,
        "urgency": out.urgency,
        "confidence": out.confidence,
    }
    expl = {
        "explanation_map": out.explanation_map,
        "disclaimer": out.disclaimer,
        "rule_id": out.rule_id_matched,
        "template_id": out.template_id,
    }
    if session and q:
        rec = logs_repo.save_recommendation(
            db,
            session,
            q,
            pathway_payload,
            expl,
            get_settings().assistant_model_version,
        )
        out.recommendation_id = rec.id
    try:
        db.commit()
    except Exception:
        db.rollback()
    return out


@router.post("/explain", response_model=PathwayExplainResponse)
def pathway_explain(
    req: PathwayExplainRequest, db: Session = Depends(get_db)
) -> PathwayExplainResponse:
    return explain_step(
        db,
        req.step_no,
        req.issue_type,
        req.lang,
        req.rule_id,
        req.template_id,
        req.pathway_snapshot,
        req.missing_fields,
        req.pathway_confidence,
    )
