import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function LanguageToggle({ lang, onChange }: { lang: Lang; onChange: (l: Lang) => void }) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-black/60 px-3 py-2 backdrop-blur">
      <span className="text-[0.7rem] font-medium uppercase tracking-[0.18em] text-slate-400">
        {t(lang, "chooseLang")}
      </span>
      <div className="flex rounded-lg bg-white/5 p-0.5">
        {(["en", "hi"] as const).map((l) => (
          <button
            key={l}
            type="button"
            onClick={() => onChange(l)}
            className={`rounded-md px-2 py-1 text-xs font-medium ${
              lang === l
                ? "bg-sky-500 text-black shadow-[0_6px_18px_rgba(56,189,248,0.6)]"
                : "text-slate-300 hover:text-white"
            }`}
          >
            {l.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
