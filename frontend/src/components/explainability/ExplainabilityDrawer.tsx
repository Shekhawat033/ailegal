import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";
import type { PathwayExplainResponse } from "../../types/api";

export function ExplainabilityDrawer({
  open,
  onClose,
  data,
  lang,
  loading,
  stepNo,
}: {
  open: boolean;
  onClose: () => void;
  data: PathwayExplainResponse | null;
  lang: Lang;
  loading: boolean;
  stepNo: number | null;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-sm">
      <div className="h-full w-full max-w-md overflow-y-auto border-l border-slate-800 bg-slate-950 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <h2 className="font-display text-lg font-semibold text-slate-100">
            {t(lang, "whyAdvice")}
            {stepNo != null ? ` · #${stepNo}` : ""}
          </h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
        <div className="space-y-4 p-4 text-sm text-slate-300">
          {loading && <p>{t(lang, "loading")}</p>}
          {data && (
            <>
              <p className="text-xs text-slate-500">
                {t(lang, "confidence")}: {(data.confidence * 100).toFixed(0)}%
              </p>
              <section>
                <h3 className="text-xs uppercase text-slate-500">Rule</h3>
                <p className="mt-1">{data.rule_matched_human}</p>
              </section>
              <section>
                <h3 className="text-xs uppercase text-slate-500">Template</h3>
                <p className="mt-1">{data.template_matched}</p>
              </section>
              <section>
                <h3 className="text-xs uppercase text-slate-500">Legal references</h3>
                <ul className="mt-1 list-disc space-y-2 pl-4">
                  {data.legal_references.map((r) => (
                    <li key={r.id}>
                      <span className="font-medium text-slate-200">
                        {r.act_name} {r.section_code}
                      </span>
                      <p className="text-slate-400">{r.text}</p>
                    </li>
                  ))}
                </ul>
              </section>
              {data.data_missing.length > 0 && (
                <section>
                  <h3 className="text-xs uppercase text-slate-500">Missing data</h3>
                  <p>{data.data_missing.join(", ")}</p>
                </section>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
