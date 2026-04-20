from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import httpx

from app.config import get_settings

log = logging.getLogger(__name__)
_PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def _read_prompt(name: str) -> str:
    return (_PROMPTS / name).read_text(encoding="utf-8")


async def chat_json(system: str, user: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("Gemini API key not configured (set GEMINI_API_KEY)")
    
    model = settings.firebase_model or "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.gemini_api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user}]
            }
        ],
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": system}]
        },
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        resp_data = r.json()
        content = resp_data["candidates"][0]["content"]["parts"][0]["text"]
        
    m = re.search(r"\{[\s\S]*\}", content)
    if not m:
        raise ValueError("no json in model output")
    return json.loads(m.group())


def extraction_prompt_for_lang(lang: str) -> str:
    return _read_prompt("extraction_hi.txt" if lang == "hi" else "extraction_en.txt")


def pathway_polish_prompt_for_lang(lang: str) -> str:
    return _read_prompt("pathway_polish_hi.txt" if lang == "hi" else "pathway_polish_en.txt")
