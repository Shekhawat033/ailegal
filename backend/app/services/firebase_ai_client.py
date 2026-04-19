from __future__ import annotations

from typing import Any


class FirebaseAIIntegrationPending(RuntimeError):
    pass


async def analyze_with_firebase_ai(message: str, lang: str, city: str | None) -> dict[str, Any]:
    _ = (message, lang, city)
    raise FirebaseAIIntegrationPending(
        "Firebase AI analyze flow is not implemented yet. Add Genkit/Firebase AI Logic here."
    )


async def clarify_with_firebase_ai(lang: str, issue_type: str, missing_fields: list[str]) -> dict[str, Any]:
    _ = (lang, issue_type, missing_fields)
    raise FirebaseAIIntegrationPending(
        "Firebase AI clarify flow is not implemented yet. Add Genkit/Firebase AI Logic here."
    )


async def generate_pathway_with_firebase_ai(payload: dict[str, Any]) -> dict[str, Any]:
    _ = payload
    raise FirebaseAIIntegrationPending(
        "Firebase AI pathway generation is not implemented yet. Add Genkit/Firebase AI Logic here."
    )
