from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.pydantic_schemas import CityOut
from app.repositories import city_repo

router = APIRouter(prefix="/v1", tags=["metadata"])


@router.get("/cities", response_model=List[CityOut])
def list_cities(db: Session = Depends(get_db)) -> List[CityOut]:
    rows = city_repo.list_cities(db)
    return [
        CityOut(
            city=r.city,
            state=r.state,
            cyber_portal_url=r.cyber_portal_url,
            police_portal_url=r.police_portal_url,
            helpline_numbers=list(r.helpline_numbers or []),
            notes_en=r.notes_en,
            notes_hi=r.notes_hi,
        )
        for r in rows
    ]
