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
        className="min-h-[4.5rem] flex-1 resize-y rounded-xl border border-white/10 bg-black/70 px-3 py-2 text-sm text-white placeholder:text-slate-500 outline-none transition-colors duration-200 focus:border-sky-400 focus:ring-2 focus:ring-sky-500/60"
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
        className="self-end rounded-xl bg-gradient-to-r from-sky-900 via-sky-700 to-sky-500 px-4 py-2 text-sm font-semibold text-white shadow-[0_8px_24px_rgba(56,189,248,0.4)] transition-all duration-200 hover:from-sky-800 hover:via-sky-600 hover:to-sky-400 hover:shadow-[0_12px_32px_rgba(56,189,248,0.6)] disabled:opacity-40"
      >
        {t(lang, "send")}
      </button>
    </div>
  );
}
