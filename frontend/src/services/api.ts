import type { AnalyzeResponse, PathwayExplainResponse, PathwayResponse, CityOut } from "../types/api";

const JSON_HDR = { "Content-Type": "application/json" };

/** Production: set VITE_API_BASE_URL=https://your-api.example.com (no trailing slash). Dev: leave unset for Vite proxy. */
function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "";
  return base ? `${base}${path}` : path;
}

export async function analyzeApi(body: {
  message: string;
  lang: "en" | "hi";
  city?: string | null;
  session_token?: string;
}): Promise<AnalyzeResponse> {
  const r = await fetch(apiUrl("/v1/analyze"), {
    method: "POST",
    headers: JSON_HDR,
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function pathwayGenerateApi(body: {
  extraction: AnalyzeResponse;
  lang: "en" | "hi";
  city?: string | null;
  user_notes?: string | null;
  session_token?: string;
}): Promise<PathwayResponse> {
  const r = await fetch(apiUrl("/v1/pathway/generate"), {
    method: "POST",
    headers: JSON_HDR,
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function pathwayExplainApi(body: {
  step_no: number;
  issue_type: string;
  lang: "en" | "hi";
  pathway_snapshot: Record<string, unknown>[];
  rule_id?: number | null;
  template_id?: number | null;
  missing_fields: string[];
  pathway_confidence: number;
}): Promise<PathwayExplainResponse> {
  const r = await fetch(apiUrl("/v1/pathway/explain"), {
    method: "POST",
    headers: JSON_HDR,
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function feedbackApi(body: {
  recommendation_id: number;
  vote: number;
  comment?: string | null;
  helpfulness_score?: number | null;
}): Promise<void> {
  const r = await fetch(apiUrl("/v1/feedback"), {
    method: "POST",
    headers: JSON_HDR,
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
}

export async function citiesApi(): Promise<CityOut[]> {
  const r = await fetch(apiUrl("/v1/cities"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
