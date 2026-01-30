const CHORDS = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];

export default function InsightPanel({ artMeta, architecture, musicFrame }) {
  const chord =
    musicFrame?.chord !== undefined && musicFrame?.chord !== null
      ? CHORDS[musicFrame.chord]
      : null;

  return (
    <div className="w-[320px] bg-glass backdrop-blur-xl border-l border-white/10 px-6 py-8 text-sm space-y-6">
      <h3 className="text-lg font-semibold mb-2">System State</h3>

      <section>
        <div className="opacity-70 mb-1 text-xs uppercase">Art</div>
        <div>Emotion: {artMeta?.emotion || "—"}</div>
        <div>Mode: {artMeta?.art_mode || "—"}</div>
        <div>Symmetry: {artMeta?.symmetry ?? "—"}</div>
      </section>

      <section>
        <div className="opacity-70 mb-1 text-xs uppercase">Architecture</div>
        <div>Openness: {architecture?.spatial_openness || "—"}</div>
        <div>Privacy: {architecture?.room_privacy || "—"}</div>
        <div>Circulation: {architecture?.circulation_style || "—"}</div>
      </section>

      <section>
        <div className="opacity-70 mb-1 text-xs uppercase">Music</div>
        <div>Emotion: {musicFrame?.meta?.emotion || "—"}</div>
        <div>Density: {musicFrame?.meta?.density?.toFixed?.(2) ?? "—"}</div>
        <div>Chord: {chord || "—"}</div>
      </section>
    </div>
  );
}  