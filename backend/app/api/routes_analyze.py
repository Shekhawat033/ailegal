from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.privacy import hash_session_token
from app.db.models import AppSession
from app.db.session import get_db
from app.models.pydantic_schemas import AnalyzeRequest, AnalyzeResponse, ClarifyRequest, ClarifyResponse
from app.repositories import logs_repo
from app.services.clarifier import best_clarify_question
from app.services.nlp_analyze import analyze_message

router = APIRouter(prefix="/v1", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)) -> AnalyzeResponse:
    t0 = time.perf_counter()
    session: Optional[AppSession] = None
    if req.session_token:
        session = logs_repo.get_or_create_session(
            db, hash_session_token(req.session_token), req.lang
        )
    try:
        out = await analyze_message(req.message, req.lang, req.city)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    if out.missing_fields:
        out.clarify_question = await best_clarify_question(req.lang, out.missing_fields, out.issue_type)
    ms = int((time.perf_counter() - t0) * 1000)
    if session:
        logs_repo.log_query(
            db,
            session,
            req.message,
            out.model_dump(),
            out.confidence,
            response_time_ms=ms,
        )
    try:
        db.commit()
    except Exception:
        db.rollback()
    return out


@router.post("/clarify", response_model=ClarifyResponse)
async def clarify(req: ClarifyRequest) -> ClarifyResponse:
    try:
        q = await best_clarify_question(req.lang, req.missing_fields, req.issue_type)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return ClarifyResponse(question=q)
