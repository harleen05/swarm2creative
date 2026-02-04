import PromptBar from "./PromptBar";


export default function TopBar() {
  return (
    <header className="h-[72px] bg-glass backdrop-blur-xl border-b border-white/10 shrink-0 z-40 relative">
      <div className="h-full flex items-center justify-between px-6 gap-8">

        {/* Logo */}
        <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-purple-300 via-pink-300 to-cyan-300 shrink-0">
          Swarm2Creative
        </h1>

        {/* Prompt Input */}
        <div className="flex-1 max-w-2xl">
          <PromptBar inline />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 shrink-0">


          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 p-0.5 ml-2 shadow-[0_0_15px_rgba(236,72,153,0.3)]">
            <div className="w-full h-full rounded-full bg-black/50 backdrop-blur-sm" />
          </div>
        </div>

      </div>
    </header>
  );
}