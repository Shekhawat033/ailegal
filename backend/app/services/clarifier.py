from __future__ import annotations

from app.config import get_settings
from app.services.openai_client import chat_json

_Q = {
    "incident_time": {
        "en": "Roughly when did this happen (date and time if you remember)?",
        "hi": "यह लगभग कब हुआ (याद हो तो तारीख और समय)?",
    },
    "amount_lost": {
        "en": "What amount was lost or at risk (in INR), if any?",
        "hi": "यदि कोई राशि गई या जोखिम में है तो लगभग कितनी (₹ में)?",
    },
    "platform_name": {
        "en": "Which platform or app was affected (e.g. Instagram, WhatsApp)?",
        "hi": "कौन सा प्लेटफ़ॉर्म या ऐप प्रभावित हुआ (जैसे Instagram, WhatsApp)?",
    },
    "perpetrator_handle": {
        "en": "Do you have a profile link, @username, or phone number used by the impersonator?",
        "hi": "क्या आपके पास प्रतिरूपकर्ता की प्रोफ़ाइल लिंक, @यूज़रनेम या फ़ोन नंबर है?",
    },
}


async def best_clarify_question(lang: str, missing_fields: list[str], issue_type: str) -> str:
    lang = "hi" if lang == "hi" else "en"
    for field in missing_fields:
        if field in _Q:
            return _Q[field][lang]
    fallback = (
        "Can you add any extra detail (timeline, platform, or amounts) to improve the checklist?"
        if lang == "en"
        else "क्या आप समयरेखा, प्लेटफ़ॉर्म या राशि जैसी अतिरिक्त जानकारी दे सकते हैं?"
    )
    if not get_settings().openai_api_key:
        return fallback
    try:
        sys = (
            'Return ONLY JSON {"question": string}. One short clarifying question in '
            + ("Hindi." if lang == "hi" else "English.")
        )
        user = f"Issue type: {issue_type}. Missing signals: {missing_fields}. Ask one question only."
        data = await chat_json(sys, user)
        q = data.get("question")
        if isinstance(q, str) and q.strip():
            return q.strip()
    except Exception:
        pass
    return fallback
