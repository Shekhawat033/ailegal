import { LanguageToggle } from "../components/shared/LanguageToggle";
import type { Lang } from "../i18n/strings";
import { t } from "../i18n/strings";

const CITIES: { slug: string; label: string }[] = [
  { slug: "", label: "—" },
  { slug: "mumbai", label: "Mumbai" },
  { slug: "delhi", label: "Delhi" },
  { slug: "bengaluru", label: "Bengaluru" },
];

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
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="mx-auto flex max-w-lg flex-col gap-8 px-4 py-16">
        <header>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-teal-400/90">{t(lang, "tagline")}</p>
          <h1 className="mt-2 font-display text-3xl font-semibold text-slate-50">{t(lang, "appTitle")}</h1>
          <p className="mt-3 text-sm text-slate-400">{t(lang, "landingHint")}</p>
        </header>

        <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <LanguageToggle lang={lang} onChange={setLang} />
          <label className="block text-sm text-slate-300">
            {t(lang, "chooseCity")}
            <select
              className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            >
              {CITIES.map((c) => (
                <option key={c.slug || "none"} value={c.slug}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <p className="text-xs text-slate-500">{t(lang, "disclaimerShort")}</p>
          <label className="flex cursor-pointer items-start gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={disclaimerOk}
              onChange={(e) => setDisclaimerOk(e.target.checked)}
              className="mt-1 rounded border-slate-600"
            />
            <span>{t(lang, "acceptDisclaimer")}</span>
          </label>
          <button
            type="button"
            disabled={!disclaimerOk}
            onClick={onStart}
            className="w-full rounded-xl bg-teal-500 py-3 text-sm font-semibold text-slate-950 hover:bg-teal-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {t(lang, "startNow")}
          </button>
        </div>

        <p className="text-center text-xs text-slate-600">{t(lang, "lawyerCta")}</p>
      </div>
    </div>
  );
}
