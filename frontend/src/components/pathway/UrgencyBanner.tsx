import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function UrgencyBanner({ urgency, confidence, lang }: { urgency: string; confidence: number; lang: Lang }) {
  const tier = urgency === "critical" ? "critical" : urgency === "high" ? "high" : "normal";
  const bg =
    tier === "critical"
      ? "border-red-800 bg-red-950/50 text-red-100"
      : tier === "high"
        ? "border-amber-700 bg-amber-950/40 text-amber-100"
        : "border-slate-700 bg-slate-900/50 text-slate-300";
  const msg =
    tier === "critical" ? t(lang, "urgencyCritical") : tier === "high" ? t(lang, "urgencyHigh") : "";

  return (
    <div className={`flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 ${bg}`}>
      <div className="text-sm">
        {msg && <p className="font-medium">{msg}</p>}
        <p className="text-xs opacity-90">
          {t(lang, "confidence")}: {(confidence * 100).toFixed(0)}%
        </p>
      </div>
    </div>
  );
}
