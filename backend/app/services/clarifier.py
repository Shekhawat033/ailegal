from __future__ import annotations

from app.config import get_settings
from app.services.openai_client import chat_json

async def best_clarify_question(lang: str, missing_fields: list[str], issue_type: str) -> str:
    settings = get_settings()
    lang = "hi" if lang == "hi" else "en"
    fallback = (
        "Please share any additional detail that could help the assistant understand the incident better."
        if lang == "en"
        else "कृपया ऐसी अतिरिक्त जानकारी साझा करें जिससे सहायक घटना को बेहतर समझ सके।"
    )
    if settings.ai_provider != "openai" or not settings.openai_api_key:
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
