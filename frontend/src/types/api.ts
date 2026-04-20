export type AnalyzeResponse = {
  intent: string;
  issue_type: string;
  entities: Record<string, unknown>;
  confidence: number;
  missing_fields: string[];
  clarify_question?: string | null;
  chat_response?: string | null;
  input_lang_detected: string;
};

export type PathwayStep = {
  step_no: number;
  title: string;
  action: string;
  expected_time?: string | null;
  links: { label: string; url: string }[];
  docs_required: string[];
  why?: string | null;
  legal_ref_ids: number[];
};

export type CityContact = {
  city?: string;
  state?: string;
  cyber_portal_url?: string;
  police_portal_url?: string;
  helpline_numbers?: string[];
  notes?: string;
};

export type PathwayResponse = {
  pathway: PathwayStep[];
  evidence_checklist: string[];
  city_contacts: CityContact[];
  explanation_map: Record<string, unknown>;
  disclaimer: string;
  confidence: number;
  recommendation_id?: number | null;
  urgency: string;
  rule_id_matched?: number | null;
  template_id?: number | null;
};

export type PathwayExplainResponse = {
  step_no: number;
  rule_matched_human: string;
  template_matched: string;
  legal_references: { id: number; act_name: string; section_code: string; text: string; source_url?: string | null }[];
  data_missing: string[];
  confidence: number;
};

export type CityOut = {
  city: string;
  state: string;
  cyber_portal_url: string;
  police_portal_url: string;
  helpline_numbers: string[];
  notes_en: string;
  notes_hi: string;
};
