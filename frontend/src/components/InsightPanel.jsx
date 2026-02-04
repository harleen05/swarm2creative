import { Zap, Layout, Activity } from "lucide-react";

const CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

const StatGroup = ({ title, icon: Icon, children }) => (
  <div className="bg-white/[0.03] rounded-2xl p-5 border border-white/5 backdrop-blur-sm hover:bg-white/[0.05] transition-colors">
    <div className="flex items-center gap-2 mb-4 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">
      <Icon size={14} className="text-white/60" />
      {title}
    </div>
    <div className="space-y-3">
      {children}
    </div>
  </div>
);

const StatRow = ({ label, value, colorClass = "text-white" }) => (
  <div className="flex justify-between items-center text-sm">
    <span className="text-white/60">{label}</span>
    <span className={`font-medium ${colorClass}`}>{value}</span>
  </div>
);

export default function InsightPanel({ artMeta, architecture, musicFrame }) {
  const chord =
    musicFrame?.chord !== undefined && musicFrame?.chord !== null
      ? CHORDS[musicFrame.chord]
      : null;

  return (
    <div className="w-80 h-full min-h-0 flex flex-col bg-glass-heavy border-l border-white/10 shrink-0 z-30 backdrop-blur-2xl">

      {/* Header */}
      <div className="p-8 border-b border-white/10 bg-white/[0.02]">
        <h3 className="text-xl font-bold font-display bg-clip-text text-transparent bg-gradient-to-r from-violet-200 to-cyan-200">
          System State
        </h3>
        <p className="text-[10px] uppercase tracking-widest text-white/40 mt-2 font-bold">
          Real-time Parameters
        </p>
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-6">

        <StatGroup title="Generative Art" icon={Zap}>
          <StatRow label="Emotion" value={artMeta?.emotion || "—"} colorClass="text-pink-300" />
          <StatRow label="Mode" value={artMeta?.art_mode || "—"} />
          <StatRow label="Symmetry" value={artMeta?.symmetry ?? "—"} colorClass="text-cyan-300" />
        </StatGroup>

        <StatGroup title="Architecture" icon={Layout}>
          <StatRow label="Openness" value={architecture?.spatial_openness || "—"} />
          <StatRow label="Privacy" value={architecture?.room_privacy || "—"} colorClass="text-violet-300" />
          <StatRow label="Circulation" value={architecture?.circulation_style || "—"} />
        </StatGroup>

        <StatGroup title="Music Engine" icon={Activity}>
          <StatRow label="Emotion" value={musicFrame?.meta?.emotion || "—"} colorClass="text-emerald-300" />
          <StatRow label="Density" value={musicFrame?.meta?.density?.toFixed?.(2) ?? "—"} />
          <StatRow label="Chord" value={chord || "—"} colorClass="text-yellow-300 font-mono bg-white/10 px-2 py-0.5 rounded text-xs" />
        </StatGroup>

      </div>
    </div>
  );
}  