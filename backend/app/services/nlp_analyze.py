from __future__ import annotations

import logging
import re
from typing import Any, Optional, Tuple

from app.config import get_settings
from app.models.pydantic_schemas import AnalyzeResponse
from app.services.constants import CITY_ALIASES, V1_CITY_SLUGS, V1_ISSUE_TYPES
from app.services.openai_client import chat_json, extraction_prompt_for_lang

log = logging.getLogger(__name__)


def _detect_input_lang(text: str, ui_lang: str) -> str:
    for c in text:
        if "\u0900" <= c <= "\u097f":
            return "hi"
    return ui_lang if ui_lang in ("en", "hi") else "en"


def _normalize_city_name(name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not name:
        return None, None
    key = name.strip().lower()
    slug = CITY_ALIASES.get(key)
    if not slug or slug not in V1_CITY_SLUGS:
        return None, None
    titles = {"mumbai": "Mumbai", "delhi": "Delhi", "bengaluru": "Bengaluru"}
    return slug, titles[slug]


def _heuristic_issue(text_l: str) -> str:
    scores = {
        "payment_fraud": 0,
        "account_hacking": 0,
        "impersonation": 0,
        "cyber_stalking_harassment": 0,
    }
    pay_kw = ["upi", "gpay", "phonepe", "paytm", "fraud", "scam", "stolen money", "transaction", "bank", "otp fraud"]
    acc_kw = ["hack", "hacked", "takeover", "instagram", "facebook", "whatsapp", "account", "login", "password"]
    imp_kw = ["fake profile", "impersonat", "catfish", "fake id", "pretending"]
    stalk_kw = ["stalk", "harass", "threat", "blackmail", "abuse", "extort"]
    for w in pay_kw:
        if w in text_l:
            scores["payment_fraud"] += 2
    for w in acc_kw:
        if w in text_l:
            scores["account_hacking"] += 2
    for w in imp_kw:
        if w in text_l:
            scores["impersonation"] += 2
    for w in stalk_kw:
        if w in text_l:
            scores["cyber_stalking_harassment"] += 2
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "account_hacking"
    return best


def _missing_fields(issue: str, text_l: str, entities: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    time_kw = [
        "today",
        "yesterday",
        "hour",
        "day ago",
        "week",
        "मैंने",
        "कल",
        "आज",
        "बजे",
        "दिन",
    ]
    has_time_hint = any(k in text_l for k in time_kw) or bool(entities.get("incident_time_hint"))
    if issue == "payment_fraud":
        if not has_time_hint:
            missing.append("incident_time")
        amt = entities.get("amount_inr")
        if amt is None and not re.search(r"\d{3,}", text_l) and "rupee" not in text_l and "₹" not in text_l:
            missing.append("amount_lost")
    if issue == "account_hacking":
        if not entities.get("platform") and not any(
            x in text_l for x in ["instagram", "facebook", "whatsapp", "twitter", "email", "ग्राम"]
        ):
            missing.append("platform_name")
    if issue == "impersonation":
        if "@" not in text_l and "profile" not in text_l and "url" not in text_l and "link" not in text_l:
            missing.append("perpetrator_handle")
    return missing


def _heuristic_analyze(message: str, lang: str, city_param: Optional[str]) -> AnalyzeResponse:
    det = _detect_input_lang(message, lang)
    text_l = message.lower()
    issue = _heuristic_issue(text_l)
    slug, city_title = _normalize_city_name(city_param)
    if not slug:
        for alias, s in CITY_ALIASES.items():
            if alias in text_l and s in V1_CITY_SLUGS:
                slug, city_title = s, {"mumbai": "Mumbai", "delhi": "Delhi", "bengaluru": "Bengaluru"}[s]
                break
    urgency = "normal"
    if any(x in text_l for x in ["urgent", "emergency", "kidnap", "suicide", "right now", "तुरंत", "खतरा"]):
        urgency = "high"
    if issue == "payment_fraud" and "critical" in text_l:
        urgency = "critical"

    platform = None
    for p in ["instagram", "facebook", "whatsapp", "twitter", "telegram"]:
        if p in text_l:
            platform = p.title()
            break

    entities: dict[str, Any] = {
        "urgency": urgency,
        "city": city_title,
        "city_slug": slug,
        "platform": platform,
    }
    amt_m = re.search(r"(?:₹|rs\.?|rupees?)\s*([\d,]+)|\b([\d,]+)\s*(?:rs|rupees)", text_l)
    if amt_m:
        raw = (amt_m.group(1) or amt_m.group(2) or "").replace(",", "")
        if raw.isdigit():
            entities["amount_inr"] = int(raw)

    missing = _missing_fields(issue, text_l, entities)
    conf = 0.88 - 0.07 * len(missing)
    if det != lang:
        conf -= 0.03
    conf = max(0.35, min(0.97, conf))

    intent = "file_cybercrime_complaint"
    if any(x in text_l for x in ["how to", "what should", "क्या करूं", "समझाए"]):
        intent = "legal_guidance"

    return AnalyzeResponse(
        intent=intent,
        issue_type=issue,
        entities=entities,
        confidence=round(conf, 2),
        missing_fields=missing,
        clarify_question=None,
        input_lang_detected=det,
    )


async def analyze_message(message: str, lang: str, city: Optional[str]) -> AnalyzeResponse:
    det = _detect_input_lang(message, lang)
    settings_lang = "hi" if det == "hi" else lang

    if not get_settings().openai_api_key:
        return _heuristic_analyze(message, lang, city)

    try:
        sys_p = extraction_prompt_for_lang(settings_lang)
        data = await chat_json(sys_p, message)
        issue = str(data.get("issue_type", "account_hacking"))
        if issue not in V1_ISSUE_TYPES:
            issue = _heuristic_issue(message.lower())
        ent = dict(data.get("entities") or {})
        slug, city_title = _normalize_city_name(city or ent.get("city"))
        if city_title:
            ent["city"] = city_title
            ent["city_slug"] = slug
        elif ent.get("city"):
            s2, t2 = _normalize_city_name(str(ent.get("city")))
            ent["city"] = t2
            ent["city_slug"] = s2
        conf = float(data.get("confidence") or 0.8)
        miss = list(data.get("missing_fields") or [])
        miss = [m for m in miss if isinstance(m, str)]
        # recompute missing merge heuristic
        miss = list(dict.fromkeys(miss + _missing_fields(issue, message.lower(), ent)))
        intent = str(data.get("intent", "file_cybercrime_complaint"))
        return AnalyzeResponse(
            intent=intent,
            issue_type=issue,
            entities=ent,
            confidence=max(0.35, min(0.99, conf)),
            missing_fields=miss,
            clarify_question=None,
            input_lang_detected=det,
        )
    except Exception as e:
        log.warning("OpenAI analyze failed, heuristic fallback: %s", e)
        return _heuristic_analyze(message, lang, city)
