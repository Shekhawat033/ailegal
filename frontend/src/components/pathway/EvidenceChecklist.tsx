import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function EvidenceChecklist({ items, lang }: { items: string[]; lang: Lang }) {
  if (!items.length) return null;
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="text-sm font-semibold text-slate-200">{t(lang, "evidenceTitle")}</h3>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-400">
        {items.map((x) => (
          <li key={x}>{x}</li>
        ))}
      </ul>
    </div>
  );
}
