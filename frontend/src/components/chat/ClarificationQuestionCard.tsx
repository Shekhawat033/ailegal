import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function ClarificationQuestionCard({
  question,
  lang,
}: {
  question: string;
  lang: Lang;
}) {
  return (
    <div className="rounded-2xl border border-teal-900/50 bg-teal-950/20 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-teal-400">{t(lang, "clarifyTitle")}</p>
      <p className="mt-2 text-sm text-slate-200">{question}</p>
      <p className="mt-2 text-xs text-slate-500">{t(lang, "continueChat")}</p>
    </div>
  );
}
