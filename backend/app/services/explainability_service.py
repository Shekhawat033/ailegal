from __future__ import annotations

from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.models.pydantic_schemas import PathwayExplainResponse
from app.repositories import legal_refs_repo, rules_repo, template_repo


def explain_step(
    db: Session,
    step_no: int,
    issue_type: str,
    lang: str,
    rule_id: Optional[int],
    template_id: Optional[int],
    pathway_snapshot: List[dict[str, Any]],
    missing_fields: List[str],
    pathway_confidence: float,
) -> PathwayExplainResponse:
    lang = "hi" if lang == "hi" else "en"
    rule = rules_repo.get_rule(db, rule_id) if rule_id else None
    tmpl = template_repo.get_template_by_id(db, template_id) if template_id else None

    if rule:
        rule_human = (
            f"Rule #{rule.id} ({rule.issue_type}), priority {rule.priority}. "
            f"Conditions: {rule.conditions_json}. Actions: urgency {rule.actions_json.get('urgency', 'normal')}."
        )
        if lang == "hi":
            rule_human = (
                f"नियम #{rule.id} ({rule.issue_type}), प्राथमिकता {rule.priority}। "
                f"शर्तें व कार्रवाई डेटाबेस से जुड़ी हैं।"
            )
    else:
        rule_human = "No rule row matched; template-only pathway." if lang == "en" else "कोई नियम पंक्ति नहीं; केवल टेम्पलेट।"

    tmpl_line = (
        f"Template #{tmpl.id} ({tmpl.issue_type}, {tmpl.lang})" if tmpl else "Default template missing."
    )
    if lang == "hi" and tmpl:
        tmpl_line = f"टेम्पलेट #{tmpl.id} ({tmpl.issue_type}, {tmpl.lang})"

    ref_ids: list[int] = []
    if rule:
        ref_ids = list(rule.legal_ref_ids or [])
    refs = legal_refs_repo.get_by_ids(db, ref_ids)
    legal_out: List[dict[str, Any]] = []
    for r in refs:
        legal_out.append(
            {
                "id": r.id,
                "act_name": r.act_name,
                "section_code": r.section_code,
                "text": r.short_text_hi if lang == "hi" else r.short_text_en,
                "source_url": r.source_url,
            }
        )

    conf = pathway_confidence
    if missing_fields:
        conf = max(0.2, conf - 0.04 * len(missing_fields))

    return PathwayExplainResponse(
        step_no=step_no,
        rule_matched_human=rule_human,
        template_matched=tmpl_line,
        legal_references=legal_out,
        data_missing=list(missing_fields),
        confidence=round(conf, 2),
    )
