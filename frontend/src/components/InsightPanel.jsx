export default function InsightPanel({ art }) {
    return (
      <div className="w-[320px] bg-glass backdrop-blur-xl border-l border-white/10 px-6 py-8 text-sm">
        <h3 className="text-lg font-semibold mb-4">System State</h3>
        <div className="opacity-70 mb-2">Art State</div>
        <div>Emotion: {art?.emotion || "—"}</div>
        <div>Symmetry: {art?.symmetry || "—"}</div>
      </div>
    );
  }  