import { useCallback, useState } from "react";
import { ClarificationQuestionCard } from "../components/chat/ClarificationQuestionCard";
import { ChatInputBox } from "../components/chat/ChatInputBox";
import { MessageBubble } from "../components/chat/MessageBubble";
import { ExplainabilityDrawer } from "../components/explainability/ExplainabilityDrawer";
import { EvidenceChecklist } from "../components/pathway/EvidenceChecklist";
import { PathwayStepCard } from "../components/pathway/PathwayStepCard";
import { SourceLinksList } from "../components/pathway/SourceLinksList";
import { UrgencyBanner } from "../components/pathway/UrgencyBanner";
import { FeedbackWidget } from "../components/shared/FeedbackWidget";
import { LanguageToggle } from "../components/shared/LanguageToggle";
import type { Lang } from "../i18n/strings";
import { t } from "../i18n/strings";
import { analyzeApi, feedbackApi, pathwayExplainApi, pathwayGenerateApi } from "../services/api";
import type { AnalyzeResponse, PathwayExplainResponse, PathwayResponse } from "../types/api";

export type ChatMessage = { role: "user" | "assistant"; text: string };

function uuid() {
  return crypto.randomUUID();
}

function summarizeAnalysis(analysis: AnalyzeResponse, lang: Lang): string {
  const parts: string[] = [];
  if (analysis.issue_type && analysis.issue_type !== "unknown") {
    parts.push(lang === "hi" ? `वर्गीकरण: ${analysis.issue_type}` : `Classification: ${analysis.issue_type}`);
  }
  if (analysis.confidence != null) {
    parts.push(
      lang === "hi"
        ? `विश्वास: ${(analysis.confidence * 100).toFixed(0)}%`
        : `Confidence: ${(analysis.confidence * 100).toFixed(0)}%`,
    );
  }
  return parts.join(" · ") || (lang === "hi" ? "विश्लेषण प्राप्त हुआ।" : "Analysis received.");
}

export function AssistantPage({
  lang,
  setLang,
  city,
  onBack,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  city: string;
  onBack: () => void;
}) {
  const [sessionToken] = useState(() => uuid());
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastAnalyze, setLastAnalyze] = useState<AnalyzeResponse | null>(null);
  const [pathway, setPathway] = useState<PathwayResponse | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [explainLoading, setExplainLoading] = useState(false);
  const [explainData, setExplainData] = useState<PathwayExplainResponse | null>(null);
  const [explainStepNo, setExplainStepNo] = useState<number | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);

  const sendUser = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;
    setLoading(true);
    setError(null);
    setFeedbackSent(false);
    setPathway(null);
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    try {
      const analysis = await analyzeApi({
        message: text,
        lang,
        city: city || undefined,
        session_token: sessionToken,
      });
      setLastAnalyze(analysis);
      if (analysis.chat_response) {
        setMessages((m) => [...m, { role: "assistant", text: analysis.chat_response as string }]);
      } else {
        const ent = analysis.entities as Record<string, unknown>;
        const summary = summarizeAnalysis(analysis, lang);
        const cityLine = ent.city ? (lang === "hi" ? ` शहर: ${ent.city}.` : ` City: ${ent.city}.`) : "";
        setMessages((m) => [...m, { role: "assistant", text: summary + cityLine }]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text:
            e instanceof Error
              ? e.message
              : lang === "hi"
                ? "अनुरोध पूरा नहीं हो सका।"
                : "The request could not be completed.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, lang, city, sessionToken]);

  const buildPlan = useCallback(async () => {
    if (!lastAnalyze || loading) return;
    setLoading(true);
    setError(null);
    try {
      const pw = await pathwayGenerateApi({
        extraction: lastAnalyze,
        lang,
        city: city || undefined,
        user_notes: messages.filter((m) => m.role === "user").slice(-1)[0]?.text ?? null,
        session_token: sessionToken,
      });
      setPathway(pw);
      setFeedbackSent(false);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text:
            lang === "hi"
              ? "एक्शन प्लान प्राप्त हुआ। दाएं पैनल में परिणाम देखें।"
              : "Action plan received. Review the results in the right panel.",
        },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  }, [lastAnalyze, loading, lang, city, sessionToken, messages]);

  const openExplain = useCallback(
    async (stepNo: number) => {
      if (!pathway || !lastAnalyze) return;
      setExplainStepNo(stepNo);
      setDrawerOpen(true);
      setExplainLoading(true);
      setExplainData(null);
      try {
        const snap = pathway.pathway.map((s) => ({ ...s }) as Record<string, unknown>);
        const data = await pathwayExplainApi({
          step_no: stepNo,
          issue_type: lastAnalyze.issue_type,
          lang,
          pathway_snapshot: snap,
          rule_id: pathway.rule_id_matched,
          template_id: pathway.template_id,
          missing_fields: lastAnalyze.missing_fields,
          pathway_confidence: pathway.confidence,
        });
        setExplainData(data);
      } catch {
        setExplainData(null);
      } finally {
        setExplainLoading(false);
      }
    },
    [pathway, lastAnalyze, lang],
  );

  const onFeedback = useCallback(
    async (vote: number) => {
      if (!pathway?.recommendation_id) return;
      try {
        await feedbackApi({ recommendation_id: pathway.recommendation_id, vote });
        setFeedbackSent(true);
      } catch {
        /* ignore */
      }
    },
    [pathway?.recommendation_id],
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-slate-950 to-black">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-black/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="space-y-1">
            <button
              type="button"
              onClick={onBack}
              className="inline-flex items-center text-[0.7rem] font-medium uppercase tracking-[0.18em] text-slate-400 transition-colors duration-150 hover:text-sky-400"
            >
              ← Back
            </button>
            <h1 className="font-display text-lg font-semibold text-white">{t(lang, "appTitle")}</h1>
          </div>
          <LanguageToggle lang={lang} onChange={setLang} />
        </div>
        {pathway && (
          <div className="mx-auto max-w-6xl px-4 pb-3">
            <UrgencyBanner urgency={pathway.urgency} confidence={pathway.confidence} lang={lang} />
          </div>
        )}
      </header>

      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
        <section className="flex flex-col gap-4">
          <h2 className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Chat</h2>
          <div className="flex min-h-[12rem] flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_14px_40px_rgba(15,23,42,0.7)] backdrop-blur-sm transition-transform duration-200 ease-out hover:-translate-y-0.5">
            {messages.map((m, i) => (
              <MessageBubble key={i} role={m.role} text={m.text} />
            ))}
            {lastAnalyze?.clarify_question && lastAnalyze.missing_fields.length > 0 && (
              <ClarificationQuestionCard question={lastAnalyze.clarify_question} lang={lang} />
            )}
            {error && <p className="text-sm text-red-400">{error}</p>}
          </div>
          <ChatInputBox
            value={input}
            onChange={setInput}
            onSend={() => void sendUser()}
            disabled={loading}
            lang={lang}
          />
          <button
            type="button"
            disabled={!lastAnalyze || loading}
            onClick={() => void buildPlan()}
            className="rounded-xl bg-gradient-to-r from-sky-900 via-sky-700 to-sky-500 py-2 text-sm font-medium text-white shadow-[0_10px_30px_rgba(56,189,248,0.35)] transition-all duration-200 hover:from-sky-800 hover:via-sky-600 hover:to-sky-400 hover:shadow-[0_16px_40px_rgba(56,189,248,0.55)] disabled:opacity-40"
          >
            {t(lang, "buildPlan")}
          </button>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
            {t(lang, "actionPlan")}
          </h2>
          {!pathway && (
            <p className="text-sm text-slate-500">{loading ? t(lang, "loading") : "—"}</p>
          )}
          {pathway && (
            <div className="space-y-3 rounded-2xl border border-white/12 bg-black/60 p-4 shadow-[0_14px_40px_rgba(15,23,42,0.9)] backdrop-blur-sm">
              <EvidenceChecklist items={pathway.evidence_checklist} lang={lang} />
              <SourceLinksList cityContacts={pathway.city_contacts} lang={lang} />
              <div className="space-y-3">
                {pathway.pathway.map((s) => (
                  <PathwayStepCard key={s.step_no} step={s} lang={lang} onWhy={() => void openExplain(s.step_no)} />
                ))}
              </div>
              <p className="text-xs text-slate-500">{pathway.disclaimer}</p>
              <FeedbackWidget
                recommendationId={pathway.recommendation_id ?? null}
                lang={lang}
                onFeedback={onFeedback}
                sent={feedbackSent}
              />
            </div>
          )}
        </section>
      </div>

      <ExplainabilityDrawer
        open={drawerOpen}
        onClose={() => {
          setDrawerOpen(false);
          setExplainStepNo(null);
        }}
        data={explainData}
        lang={lang}
        loading={explainLoading}
        stepNo={explainStepNo}
      />
    </div>
  );
}
