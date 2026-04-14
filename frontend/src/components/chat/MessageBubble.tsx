export function MessageBubble({ role, text }: { role: "user" | "assistant"; text: string }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed ${
          isUser ? "bg-teal-700 text-white" : "border border-slate-700 bg-slate-900/80 text-slate-200"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
