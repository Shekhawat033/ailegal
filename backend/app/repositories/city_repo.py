from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CityAuthority


def list_cities(db: Session) -> list[CityAuthority]:
    return list(db.scalars(select(CityAuthority).order_by(CityAuthority.city)).all())


def get_city(db: Session, city_slug: str) -> CityAuthority | None:
    slug = city_slug.strip().lower()
    if slug == "bangalore":
        slug = "bengaluru"
    return db.execute(select(CityAuthority).where(CityAuthority.city == slug).limit(1)).scalar_one_or_none()
