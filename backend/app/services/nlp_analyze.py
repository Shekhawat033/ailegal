from __future__ import annotations

import logging
import re
from typing import Any, Optional, Tuple

from app.config import get_settings
from app.models.pydantic_schemas import AnalyzeResponse
from app.services.constants import CITY_ALIASES, V1_CITY_SLUGS, V1_ISSUE_TYPES
from app.services.gemini_client import chat_json, extraction_prompt_for_lang
from app.services.rag_indexer import search_legal_context

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

    if det == "hi":
        chat_resp = f"मैंने समझा कि आप '{issue}' की रिपोर्ट कर रहे हैं। योजना बनाने के लिए कृपया आगे बढ़ें।"
        if missing:
            chat_resp = f"मैंने समझा कि आप '{issue}' की रिपोर्ट कर रहे हैं। कृपया मुझे इन विवरणों के बारे में बताएं: {', '.join(missing)}।"
    else:
        chat_resp = f"I understand you are reporting an issue related to '{issue}'. Please proceed to build your action plan."
        if missing:
            chat_resp = f"I understand you are reporting an issue related to '{issue}'. Could you also provide: {', '.join(missing)}?"

    return AnalyzeResponse(
        intent=intent,
        issue_type=issue,
        entities=entities,
        confidence=round(conf, 2),
        missing_fields=missing,
        clarify_question=None,
        input_lang_detected=det,
        chat_response=chat_resp,
    )


async def analyze_message(message: str, lang: str, city: Optional[str]) -> AnalyzeResponse:
    settings = get_settings()
    det = _detect_input_lang(message, lang)
    settings_lang = "hi" if det == "hi" else lang

    if settings.ai_provider != "firebase" or not settings.gemini_api_key:
        if settings.enable_heuristic_fallback:
            return _heuristic_analyze(message, lang, city)
        raise RuntimeError(
            "No AI analysis provider is configured. Please configure GEMINI_API_KEY or enable heuristic fallback explicitly."
        )

    try:
        # Step 1: Convert raw user message to a precise legal search query
        search_query_prompt = """
Convert the user query into a precise Indian legal search query.
- Add relevant legal keywords (e.g., IPC, CrPC, Constitution of India, Act names)
- Identify legal intent (e.g., bail, contract breach, property dispute)
- Keep it concise and retrieval-friendly

Return ONLY valid JSON with a single key "query" containing the improved query string.
"""
        search_query_data = await chat_json(search_query_prompt, message)
        improved_query = str(search_query_data.get("query", message))
        
        # Step 2: Retrieve legal context using the improved query
        legal_context = search_legal_context(improved_query)
        
        sys_p = extraction_prompt_for_lang(settings_lang)
        # Inject context instructions
        sys_p += "\n\nCRITICAL RULE: For the 'chat_response' field, you MUST base your advice strictly on the provided Indian Legal Context below. If the context does not address the issue, politely state that you can only provide advice based on Indian Law context provided to you.\n\n"
        sys_p += f"--- INDIAN LEGAL CONTEXT ---\n{legal_context}\n----------------------------"

        user_p = f"User Complaint: {message}"
        data = await chat_json(sys_p, user_p)
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
        chat_response = data.get("chat_response")
        return AnalyzeResponse(
            intent=intent,
            issue_type=issue,
            entities=ent,
            confidence=max(0.35, min(0.99, conf)),
            missing_fields=miss,
            clarify_question=None,
            input_lang_detected=det,
            chat_response=str(chat_response) if chat_response else None,
        )
    except Exception as e:
        log.warning("OpenAI analyze failed, heuristic fallback: %s", e)
        if settings.enable_heuristic_fallback:
            return _heuristic_analyze(message, lang, city)
        raise RuntimeError("AI analysis failed and heuristic fallback is disabled.") from e
