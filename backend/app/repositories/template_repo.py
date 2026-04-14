from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PathwayTemplate


def get_template(db: Session, issue_type: str, lang: str) -> PathwayTemplate | None:
    r = db.execute(
        select(PathwayTemplate)
        .where(
            PathwayTemplate.issue_type == issue_type,
            PathwayTemplate.lang == lang,
        )
        .limit(1)
    ).scalar_one_or_none()
    if r is not None:
        return r
    return db.execute(
        select(PathwayTemplate)
        .where(
            PathwayTemplate.issue_type == issue_type,
            PathwayTemplate.lang == "en",
        )
        .limit(1)
    ).scalar_one_or_none()


def get_template_by_id(db: Session, tid: int) -> PathwayTemplate | None:
    return db.get(PathwayTemplate, tid)
