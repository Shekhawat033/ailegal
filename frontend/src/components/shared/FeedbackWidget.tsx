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
    <div className="flex flex-wrap items-center gap-3 rounded-xl border border-white/10 bg-black/60 px-3 py-2">
      <span className="text-sm text-slate-300">{t(lang, "thumbsHelpful")}</span>
      <button
        type="button"
        onClick={() => onFeedback(1)}
        className="rounded-lg bg-white/10 px-3 py-1 text-sm text-slate-100 transition-colors duration-150 hover:bg-white/20"
      >
        👍
      </button>
      <button
        type="button"
        onClick={() => onFeedback(-1)}
        className="rounded-lg bg-white/10 px-3 py-1 text-sm text-slate-100 transition-colors duration-150 hover:bg-white/20"
      >
        👎
      </button>
      {sent && <span className="text-xs text-sky-400">{t(lang, "thanksFeedback")}</span>}
    </div>
  );
}
