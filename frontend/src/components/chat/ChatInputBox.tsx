import type { Lang } from "../../i18n/strings";
import { t } from "../../i18n/strings";

export function ChatInputBox({
  value,
  onChange,
  onSend,
  disabled,
  lang,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  disabled: boolean;
  lang: Lang;
}) {
  return (
    <div className="flex gap-2">
      <textarea
        className="min-h-[4.5rem] flex-1 resize-y rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
        placeholder={t(lang, "chatPlaceholder")}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) onSend();
        }}
      />
      <button
        type="button"
        disabled={disabled || !value.trim()}
        onClick={onSend}
        className="self-end rounded-xl bg-teal-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-teal-400 disabled:opacity-40"
      >
        {t(lang, "send")}
      </button>
    </div>
  );
}
