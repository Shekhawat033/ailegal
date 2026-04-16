export function MessageBubble({ role, text }: { role: "user" | "assistant"; text: string }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed transition-transform duration-150 ${
          isUser
            ? "bg-gradient-to-r from-sky-700 to-sky-500 text-black shadow-[0_8px_24px_rgba(56,189,248,0.4)]"
            : "border border-white/12 bg-black/70 text-slate-100"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
