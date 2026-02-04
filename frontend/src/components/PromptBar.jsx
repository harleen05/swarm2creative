// src/components/PromptBar.jsx

import { useState } from "react";
import { Send } from "lucide-react";
import { sendIntent } from "../api/interpret";

export default function PromptBar({ inline = false }) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);

  async function sendPrompt() {
    if (!text.trim() || sending) return;

    const payload = { text };

    setSending(true);
    try {
      await sendIntent(payload);
      setText("");
    } catch (err) {
      console.error("Prompt failed:", err);
    } finally {
      setSending(false);
    }
  }

  const inputRow = (
    <div className="relative flex items-center w-full min-w-0 bg-white/[0.06] backdrop-blur-xl border border-white/15 rounded-sm transition-all duration-200 focus-within:border-[#bf5af2]/50 focus-within:bg-white/[0.08] focus-within:shadow-[0_0_0_1px_rgba(191,90,242,0.2),0_0_12px_rgba(191,90,242,0.08)]">
      <input
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendPrompt()}
        placeholder="Describe the space, mood, or movement…"
        disabled={sending}
        className="flex-1 min-w-0 py-3 pl-4 pr-2 bg-transparent outline-none border-0 text-sm text-white placeholder-white/40 font-medium tracking-tight focus:placeholder-white/30 [caret-color:rgba(191,90,242,0.9)]"
        style={{ fontFamily: '"Plus Jakarta Sans", system-ui, sans-serif' }}
      />
      <span className="w-px h-5 bg-white/15 shrink-0" aria-hidden />
      <button
        type="button"
        onClick={sendPrompt}
        disabled={!text.trim() || sending}
        className="flex items-center justify-center gap-2 px-4 py-3 text-sm shrink-0 disabled:opacity-40 disabled:cursor-not-allowed text-white/90 hover:text-white transition-colors"
        aria-label="Send prompt"
      >
        <Send className="w-4 h-4" strokeWidth={2.25} />
        <span className="hidden sm:inline">{sending ? "Sending…" : "Send"}</span>
      </button>
    </div>
  );

  if (inline) {
    return inputRow;
  }

  return (
    <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-[740px] px-4 z-10">
      {inputRow}
      <p className="mt-5 text-center text-xs text-white/40 tracking-wide">
        Press <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-white/70 font-mono text-[10px]">Enter</kbd> to send
      </p>
    </div>
  );
}