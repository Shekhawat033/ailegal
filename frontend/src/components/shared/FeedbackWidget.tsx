import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function FeedbackWidget({
  recommendationId,
  lang,
  onFeedback,
  sent,
}: {
  recommendationId: number | null;
  lang: Lang;
  onFeedback: (vote: number) => void;
  sent: boolean;
}) {
  if (!recommendationId) return null;
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/40 px-3 py-2">
      <span className="text-sm text-slate-400">{t(lang, "thumbsHelpful")}</span>
      <button
        type="button"
        onClick={() => onFeedback(1)}
        className="rounded-lg bg-slate-800 px-3 py-1 text-sm hover:bg-slate-700"
      >
        👍
      </button>
      <button
        type="button"
        onClick={() => onFeedback(-1)}
        className="rounded-lg bg-slate-800 px-3 py-1 text-sm hover:bg-slate-700"
      >
        👎
      </button>
      {sent && <span className="text-xs text-teal-400">{t(lang, "thanksFeedback")}</span>}
    </div>
  );
}
