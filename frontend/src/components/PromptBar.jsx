import { useState } from "react";

export default function PromptBar() {
  const [text, setText] = useState("");

  async function sendPrompt() {
    if (!text.trim()) return;

    await fetch("http://127.0.0.1:8000/interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    setText("");
  }

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[720px] bg-glass backdrop-blur-xl border border-white/10 rounded-2xl px-4 py-3 flex gap-3">
      <input
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => e.key === "Enter" && sendPrompt()}
        placeholder="Describe the space, mood, or movement…"
        className="flex-1 bg-transparent outline-none text-sm text-white/90 placeholder-white/40"
      />
      <button
        onClick={sendPrompt}
        className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 transition text-sm"
      >
        Send
      </button>
    </div>
  );
}