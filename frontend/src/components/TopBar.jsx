export default function TopBar() {
    return (
      <div className="h-14 flex items-center justify-between px-6 bg-glass backdrop-blur-xl border-b border-white/10">
        <div className="font-semibold text-lg">Swarm2Creative</div>
  
        <div className="flex gap-3">
          <button className="px-3 py-1 rounded bg-white/10 hover:bg-white/20">
            Save
          </button>
          <button className="px-3 py-1 rounded bg-white/10 hover:bg-white/20">
            Export
          </button>
          <div className="w-8 h-8 rounded-full bg-glow/60" />
        </div>
      </div>
    );
  }  