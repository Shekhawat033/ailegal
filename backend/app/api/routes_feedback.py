from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.pydantic_schemas import FeedbackRequest, FeedbackResponse
from app.repositories import logs_repo
from app.db.models import Recommendation

router = APIRouter(prefix="/v1", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
def post_feedback(body: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    rec = db.get(Recommendation, body.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="recommendation not found")
    logs_repo.save_feedback(db, body.recommendation_id, body.vote, body.comment, body.helpfulness_score)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return FeedbackResponse()
