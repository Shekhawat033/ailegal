import { LanguageToggle } from "../components/shared/LanguageToggle";
import type { Lang } from "../i18n/strings";
import { t } from "../i18n/strings";

export function LandingPage({
  lang,
  setLang,
  city,
  setCity,
  disclaimerOk,
  setDisclaimerOk,
  onStart,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  city: string;
  setCity: (s: string) => void;
  disclaimerOk: boolean;
  setDisclaimerOk: (v: boolean) => void;
  onStart: () => void;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-slate-950 to-black">
      <div className="mx-auto flex max-w-lg flex-col gap-8 px-4 py-16 animate-fade-in-up">
        <header className="space-y-2">
          <p className="text-[0.65rem] font-semibold uppercase tracking-[0.22em] text-sky-400/90">
            {t(lang, "tagline")}
          </p>
          <h1 className="mt-1 font-display text-3xl font-semibold text-white">{t(lang, "appTitle")}</h1>
          <p className="mt-2 text-sm text-slate-300">{t(lang, "landingHint")}</p>
        </header>

        <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-[0_18px_45px_rgba(15,23,42,0.55)] backdrop-blur">
          <LanguageToggle lang={lang} onChange={setLang} />
          <label className="block text-sm text-slate-200">
            {t(lang, "chooseCity")}
            <input
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/60 px-3 py-2 text-sm text-white outline-none transition-colors duration-200 focus:border-sky-400 focus:ring-2 focus:ring-sky-500/60"
              type="text"
              placeholder={lang === "hi" ? "उदाहरण: जयपुर, दिल्ली, remote" : "Example: Jaipur, Delhi, remote"}
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </label>
          <p className="text-xs text-slate-400">{t(lang, "disclaimerShort")}</p>
          <label className="flex cursor-pointer items-start gap-2 text-sm text-slate-200">
            <input
              type="checkbox"
              checked={disclaimerOk}
              onChange={(e) => setDisclaimerOk(e.target.checked)}
              className="mt-1 rounded border-white/20 bg-black/60 text-sky-400 focus:ring-sky-500"
            />
            <span>{t(lang, "acceptDisclaimer")}</span>
          </label>
          <button
            type="button"
            disabled={!disclaimerOk}
            onClick={onStart}
            className="w-full rounded-xl bg-gradient-to-r from-sky-900 via-sky-700 to-sky-500 py-3 text-sm font-semibold text-white shadow-[0_12px_30px_rgba(56,189,248,0.35)] transition-all duration-200 hover:from-sky-800 hover:via-sky-600 hover:to-sky-400 hover:shadow-[0_18px_45px_rgba(56,189,248,0.55)] disabled:cursor-not-allowed disabled:opacity-40"
          >
            {t(lang, "startNow")}
          </button>
        </div>

        <p className="text-center text-xs text-slate-500">{t(lang, "lawyerCta")}</p>
      </div>
    </div>
  );
}
