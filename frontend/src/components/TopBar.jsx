import PromptBar from "./PromptBar";

export default function TopBar() {
  return (
    <header className="bg-glass backdrop-blur-xl border-b border-white/10 shrink-0">
      <div className="min-h-[36px] flex items-center gap-5 px-3 py-1.5">
        <h1
          className="font-semibold select-none shrink-0"
          style={{
            fontFamily: '"Plus Jakarta Sans", system-ui, sans-serif',
            fontSize: "20px",
            textShadow: [
              "0 0 18px rgba(191, 90, 242, 0.75)",
              "0 0 36px rgba(191, 90, 242, 0.45)",
              "0 0 54px rgba(191, 90, 242, 0.25)",
              "0 1px 3px rgba(0, 0, 0, 0.3)"
            ].join(", "),
            letterSpacing: "-0.015em"
          }}
        >
          Swarm2Creative
        </h1>

        <div className="flex-1 flex items-center min-w-0 max-w-xl ml-6">
          <PromptBar inline />
        </div>

        <div className="flex items-center gap-3 flex-nowrap shrink-0">
          <button className="px-4 py-2 min-h-[40px] flex items-center justify-center whitespace-nowrap">
            Save
          </button>
          <button className="px-4 py-2 min-h-[40px] flex items-center justify-center whitespace-nowrap">
            Export
          </button>
          <div className="w-8 h-8 rounded-full bg-glow/60 shrink-0" />
        </div>
      </div>
    </header>
  );
}