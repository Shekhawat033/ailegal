from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import LegalReference


def get_by_ids(db: Session, ids: list[int]) -> list[LegalReference]:
    if not ids:
        return []
    return list(db.scalars(select(LegalReference).where(LegalReference.id.in_(ids))).all())
