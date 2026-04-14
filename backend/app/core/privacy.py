from __future__ import annotations

import hashlib
import re


def hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def redact_pii(text: str) -> str:
    s = text
    s = re.sub(r"\b\d{10}\b", "[PHONE]", s)
    s = re.sub(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b", "[PHONE]", s)
    s = re.sub(r"\b\d{12,18}\b", "[ACCOUNT]", s)
    s = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", "[PAN]", s)
    return s
