import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";
import type { PathwayStep } from "../../types/api";

export function PathwayStepCard({
  step,
  lang,
  onWhy,
}: {
  step: PathwayStep;
  lang: Lang;
  onWhy: () => void;
}) {
  return (
    <div className="rounded-2xl border border-white/12 bg-black/70 p-4 transition-transform duration-150 hover:-translate-y-0.5">
      <div className="flex items-start gap-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-sky-900 to-sky-600 text-sm font-bold text-white shadow-[0_8px_22px_rgba(56,189,248,0.5)]">
          {step.step_no}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-medium text-white">{step.title}</h3>
          <p className="mt-1 text-sm text-slate-300">{step.action}</p>
          {step.expected_time && (
            <p className="mt-2 text-xs text-slate-400">{step.expected_time}</p>
          )}
          {step.docs_required.length > 0 && (
            <p className="mt-2 text-xs text-slate-400">
              {t(lang, "stepOptionalDocs")}: {step.docs_required.join(", ")}
            </p>
          )}
          {step.links.length > 0 && (
            <ul className="mt-2 flex flex-wrap gap-2">
              {step.links.map((l) => (
                <li key={l.url + l.label}>
                  <a
                    href={l.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-medium text-sky-400 hover:text-sky-300"
                  >
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          )}
          <button
            type="button"
            onClick={onWhy}
            className="mt-3 text-xs font-medium text-slate-300 underline hover:text-sky-300"
          >
            {t(lang, "whyStep")}
          </button>
        </div>
      </div>
    </div>
  );
}
