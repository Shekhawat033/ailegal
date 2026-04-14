from __future__ import annotations

import json
import logging
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.pydantic_schemas import (
    AnalyzeResponse,
    PathwayGenerateResponse,
    PathwayStepOut,
)
from app.repositories import city_repo, legal_refs_repo, rules_repo, template_repo
from app.services.openai_client import chat_json, pathway_polish_prompt_for_lang

log = logging.getLogger(__name__)

DISCLAIMER = {
    "en": "Informational use only — not legal advice. For urgent danger call 112/100. Consult a qualified lawyer for your case.",
    "hi": "केवल सूचनात्मक — कानूनी सलाह नहीं। तत्काल खतरे पर 112/100 डायल करें। अपने मामले हेतु योग्य वकील से सलाह लें।",
}


def _filter_prepend_steps(prep: Any, lang: str) -> List[str]:
    if not prep:
        return []
    out: List[str] = []
    for p in prep:
        if not isinstance(p, str):
            continue
        if p.startswith("en:"):
            if lang == "en":
                out.append(p[3:].strip())
        elif p.startswith("hi:"):
            if lang == "hi":
                out.append(p[3:].strip())
        else:
            out.append(p.strip())
    return out


async def _maybe_polish_steps(
    steps: List[dict[str, Any]],
    lang: str,
    allowed_urls: List[str],
    legal_lines: List[str],
) -> List[dict[str, Any]]:
    if not get_settings().openai_api_key or len(steps) == 0:
        return steps
    try:
        sys_p = pathway_polish_prompt_for_lang(lang)
        user = json.dumps(
            {
                "steps": [
                    {"title": s.get("title"), "action": s.get("action"), "expected_time": s.get("expected_time")}
                    for s in steps
                ],
                "allowed_urls": allowed_urls,
                "legal_reference_lines": legal_lines,
            },
            ensure_ascii=False,
        )
        data = await chat_json(sys_p, user)
        polished = data.get("steps")
        if not isinstance(polished, list) or len(polished) != len(steps):
            return steps
        merged = []
        for orig, p in zip(steps, polished):
            merged.append(
                {
                    **orig,
                    "title": str(p.get("title") or orig.get("title", "")),
                    "action": str(p.get("action") or orig.get("action", "")),
                    "expected_time": p.get("expected_time", orig.get("expected_time")),
                }
            )
        return merged
    except Exception as e:
        log.warning("Pathway polish skipped: %s", e)
        return steps


async def generate_pathway(
    db: Session,
    extraction: AnalyzeResponse,
    lang: str,
    city_slug: Optional[str],
    user_notes: Optional[str],
) -> PathwayGenerateResponse:
    lang = "hi" if lang == "hi" else "en"
    issue = extraction.issue_type
    ent = extraction.entities or {}
    slug = city_slug or ent.get("city_slug")
    if isinstance(slug, str):
        slug = slug.strip().lower()
        if slug == "bangalore":
            slug = "bengaluru"
    else:
        slug = None

    rules = rules_repo.active_rules_for_issue(db, issue)
    rule = rules[0] if rules else None
    tmpl = template_repo.get_template(db, issue, lang)
    if not tmpl:
        raise ValueError("No pathway template for issue/lang")

    steps_raw: List[dict[str, Any]] = []
    if rule:
        prep = _filter_prepend_steps(rule.actions_json.get("prepend_steps"), lang)
        for i, text in enumerate(prep):
            steps_raw.append(
                {
                    "title": f"{'तत्काल' if lang == 'hi' else 'Immediate'} — {i + 1}",
                    "action": text,
                    "expected_time": None,
                    "links": [{"label": "1930 / NCRP", "url": "https://www.cybercrime.gov.in/"}],
                    "docs_required": [],
                }
            )

    for s in tmpl.steps_json:
        if isinstance(s, dict):
            steps_raw.append(dict(s))

    legal_ids = list(rule.legal_ref_ids) if rule else []
    refs = legal_refs_repo.get_by_ids(db, legal_ids)
    found_ids = {r.id for r in refs}
    if rule and set(legal_ids) - found_ids:
        log.warning("Some legal_ref_ids missing in DB: %s", set(legal_ids) - found_ids)
        legal_ids = [i for i in legal_ids if i in found_ids]

    city = city_repo.get_city(db, slug) if slug else None
    allowed_urls = ["https://www.cybercrime.gov.in/"]
    if city:
        allowed_urls.extend([city.cyber_portal_url, city.police_portal_url])
    legal_lines = [f"{r.act_name} {r.section_code}" for r in refs]

    steps_raw = await _maybe_polish_steps(steps_raw, lang, allowed_urls, legal_lines)

    pathway: List[PathwayStepOut] = []
    explanation_map: dict[str, Any] = {}
    for i, s in enumerate(steps_raw, start=1):
        links = [dict(x) for x in (s.get("links") or []) if isinstance(x, dict)]
        if i == 1:
            links.append({"label": "NCRP", "url": "https://www.cybercrime.gov.in/"})
        if city and i <= 2:
            links.append({"label": city.city.title() + " Police", "url": city.police_portal_url})
        step = PathwayStepOut(
            step_no=i,
            title=str(s.get("title", "")),
            action=str(s.get("action", "")),
            expected_time=s.get("expected_time"),
            links=links,
            docs_required=[str(x) for x in (s.get("docs_required") or [])],
            why=None,
            legal_ref_ids=legal_ids if i <= min(2, len(steps_raw)) else [],
        )
        pathway.append(step)
        explanation_map[str(i)] = {
            "rule_id": rule.id if rule else None,
            "template_id": tmpl.id,
            "legal_ref_ids": legal_ids,
        }

    evidence = [str(x) for x in (tmpl.evidence_json or [])]
    if user_notes:
        evidence.append(f"{'User note' if lang == 'en' else 'उपयोगकर्ता नोट'}: {user_notes[:500]}")

    city_contacts: List[dict[str, Any]] = []
    if city:
        notes = city.notes_hi if lang == "hi" else city.notes_en
        city_contacts.append(
            {
                "city": city.city,
                "state": city.state,
                "cyber_portal_url": city.cyber_portal_url,
                "police_portal_url": city.police_portal_url,
                "helpline_numbers": list(city.helpline_numbers or []),
                "notes": notes,
            }
        )

    urgency = str(ent.get("urgency") or "normal")
    if rule and rule.actions_json.get("urgency") == "critical":
        urgency = "critical"

    conf = float(extraction.confidence) - 0.06 * len(extraction.missing_fields or [])
    conf = max(0.25, min(0.95, conf))

    return PathwayGenerateResponse(
        pathway=pathway,
        evidence_checklist=evidence,
        city_contacts=city_contacts,
        explanation_map=explanation_map,
        disclaimer=DISCLAIMER[lang],
        confidence=round(conf, 2),
        recommendation_id=None,
        urgency=urgency,
        rule_id_matched=rule.id if rule else None,
        template_id=tmpl.id,
    )
