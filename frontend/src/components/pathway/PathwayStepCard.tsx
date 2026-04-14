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
    <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-4">
      <div className="flex items-start gap-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal-500/20 text-sm font-bold text-teal-300">
          {step.step_no}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-medium text-slate-100">{step.title}</h3>
          <p className="mt-1 text-sm text-slate-400">{step.action}</p>
          {step.expected_time && (
            <p className="mt-2 text-xs text-slate-500">{step.expected_time}</p>
          )}
          {step.docs_required.length > 0 && (
            <p className="mt-2 text-xs text-slate-500">
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
                    className="text-xs font-medium text-teal-400 hover:text-teal-300"
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
            className="mt-3 text-xs font-medium text-slate-400 underline hover:text-teal-300"
          >
            {t(lang, "whyStep")}
          </button>
        </div>
      </div>
    </div>
  );
}
