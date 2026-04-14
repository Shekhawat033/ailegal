import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

type CityContact = {
  city?: string;
  state?: string;
  cyber_portal_url?: string;
  police_portal_url?: string;
  helpline_numbers?: string[];
  notes?: string;
};

export function SourceLinksList({ cityContacts, lang }: { cityContacts: CityContact[]; lang: Lang }) {
  if (!cityContacts.length) return null;
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="text-sm font-semibold text-slate-200">{t(lang, "cityLinks")}</h3>
      <ul className="mt-2 space-y-3 text-sm">
        {cityContacts.map((c, i) => (
          <li key={i} className="text-slate-400">
            <span className="font-medium text-slate-200">
              {c.city ?? ""} — {c.state ?? ""}
            </span>
            {c.helpline_numbers && c.helpline_numbers.length > 0 && (
              <p className="text-xs">Helpline: {c.helpline_numbers.join(", ")}</p>
            )}
            <div className="mt-1 flex flex-wrap gap-2">
              {c.cyber_portal_url ? (
                <a
                  href={c.cyber_portal_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-teal-400 hover:text-teal-300"
                >
                  Cyber portal
                </a>
              ) : null}
              {c.police_portal_url ? (
                <a
                  href={c.police_portal_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-teal-400 hover:text-teal-300"
                >
                  Police
                </a>
              ) : null}
            </div>
            {c.notes ? <p className="mt-1 text-xs">{c.notes}</p> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
