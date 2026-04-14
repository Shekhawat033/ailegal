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
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI not configured")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_model,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    m = re.search(r"\{[\s\S]*\}", content)
    if not m:
        raise ValueError("no json in model output")
    return json.loads(m.group())


def extraction_prompt_for_lang(lang: str) -> str:
    return _read_prompt("extraction_hi.txt" if lang == "hi" else "extraction_en.txt")


def pathway_polish_prompt_for_lang(lang: str) -> str:
    return _read_prompt("pathway_polish_hi.txt" if lang == "hi" else "pathway_polish_en.txt")
