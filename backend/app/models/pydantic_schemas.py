from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- /v1/analyze ---
class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=16_000)
    lang: str = Field(default="en", pattern="^(en|hi)$")
    city: Optional[str] = None
    session_token: Optional[str] = None


class AnalyzeResponse(BaseModel):
    intent: str
    issue_type: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    clarify_question: Optional[str] = None
    input_lang_detected: str = "en"


# --- /v1/clarify ---
class ClarifyRequest(BaseModel):
    lang: str = Field(default="en", pattern="^(en|hi)$")
    issue_type: str
    missing_fields: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)


class ClarifyResponse(BaseModel):
    question: str


# --- /v1/pathway/generate ---
class PathwayStepOut(BaseModel):
    step_no: int
    title: str
    action: str
    expected_time: Optional[str] = None
    links: List[Dict[str, str]] = Field(default_factory=list)
    docs_required: List[str] = Field(default_factory=list)
    why: Optional[str] = None
    legal_ref_ids: List[int] = Field(default_factory=list)


class PathwayGenerateRequest(BaseModel):
    extraction: AnalyzeResponse
    lang: str = Field(default="en", pattern="^(en|hi)$")
    city: Optional[str] = None
    user_notes: Optional[str] = None
    session_token: Optional[str] = None


class PathwayGenerateResponse(BaseModel):
    pathway: List[PathwayStepOut]
    evidence_checklist: List[str]
    city_contacts: List[Dict[str, Any]]
    explanation_map: Dict[str, Any] = Field(default_factory=dict)
    disclaimer: str
    confidence: float
    recommendation_id: Optional[int] = None
    urgency: str = "normal"
    rule_id_matched: Optional[int] = None
    template_id: Optional[int] = None


# --- /v1/pathway/explain ---
class PathwayExplainRequest(BaseModel):
    step_no: int
    issue_type: str
    lang: str = Field(default="en", pattern="^(en|hi)$")
    pathway_snapshot: List[Dict[str, Any]] = Field(default_factory=list)
    rule_id: Optional[int] = None
    template_id: Optional[int] = None
    missing_fields: List[str] = Field(default_factory=list)
    pathway_confidence: float = 0.85


class PathwayExplainResponse(BaseModel):
    step_no: int
    rule_matched_human: str
    template_matched: str
    legal_references: List[Dict[str, Any]]
    data_missing: List[str]
    confidence: float


# --- /v1/feedback ---
class FeedbackRequest(BaseModel):
    recommendation_id: int
    vote: int = Field(..., ge=-1, le=1)
    comment: Optional[str] = Field(default=None, max_length=4_000)
    helpfulness_score: Optional[float] = Field(default=None, ge=0.0, le=5.0)


class FeedbackResponse(BaseModel):
    status: str = "ok"


# --- /v1/cities ---
class CityOut(BaseModel):
    city: str
    state: str
    cyber_portal_url: str
    police_portal_url: str
    helpline_numbers: List[str]
    notes_en: str
    notes_hi: str
