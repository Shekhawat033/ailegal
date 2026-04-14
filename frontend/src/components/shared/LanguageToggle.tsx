import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function LanguageToggle({
  lang,
  onChange,
}: {
  lang: Lang;
  onChange: (l: Lang) => void;
}) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2">
      <span className="text-xs text-slate-400">{t(lang, "chooseLang")}</span>
      <div className="flex rounded-lg bg-slate-950 p-0.5">
        {(["en", "hi"] as const).map((l) => (
          <button
            key={l}
            type="button"
            onClick={() => onChange(l)}
            className={`rounded-md px-2 py-1 text-xs font-medium ${
              lang === l ? "bg-teal-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {l.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
