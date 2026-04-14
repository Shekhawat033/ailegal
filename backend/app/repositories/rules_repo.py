from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Rule


def active_rules_for_issue(db: Session, issue_type: str) -> list[Rule]:
    return list(
        db.scalars(
            select(Rule)
            .where(Rule.issue_type == issue_type, Rule.active.is_(True))
            .order_by(Rule.priority.desc())
        ).all()
    )


def get_rule(db: Session, rule_id: int):
    return db.get(Rule, rule_id)
