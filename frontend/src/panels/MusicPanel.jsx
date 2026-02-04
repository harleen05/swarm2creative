import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Music, Mic, Square, Play, Sliders, Activity } from "lucide-react";
import { sendIntent } from "../api/interpret";
import { enableAudio, startRecording, stopRecording } from "../audio/MusicEngine";

// --- Styled Components ---

const ControlGroup = ({ label, children, icon: Icon }) => (
  <div className="mb-8 relative z-10">
    <div className="flex items-center gap-2 mb-4 ml-1">
      {Icon && <Icon size={14} className="text-purple-300/50" />}
      <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-purple-200/50 font-sans">
        {label}
      </div>
    </div>
    <div className="space-y-3">
      {children}
    </div>
  </div>
);

const RangeSlider = ({ value, min, max, step, onChange, label }) => (
  <div className="bg-white/5 rounded-2xl p-4 border border-white/5 hover:border-white/10 transition-colors group">
    <div className="flex justify-between text-xs mb-3">
      <span className="text-purple-200/60 font-medium group-hover:text-purple-200/80 transition-colors">{label}</span>
      <span className="text-white font-mono bg-white/10 px-2 py-0.5 rounded text-[10px] min-w-[2rem] text-center">{value}</span>
    </div>
    <div className="relative h-1.5 w-full">
      <div className="absolute inset-0 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
          style={{ width: `${((value - min) / (max - min)) * 100}%` }}
        />
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      <div
        className="absolute top-1/2 -ml-2 -mt-2 w-4 h-4 bg-white rounded-full shadow-lg pointer-events-none transform scale-0 group-hover:scale-100 transition-transform duration-200"
        style={{ left: `${((value - min) / (max - min)) * 100}%` }}
      />
    </div>
  </div>
);

const ToggleButton = ({ label, active, onChange }) => (
  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
    <span className="text-sm font-medium text-purple-200/80">{label}</span>
    <button
      onClick={() => onChange(!active)}
      className={`relative w-11 h-6 rounded-full transition-colors duration-300 ${active ? "bg-purple-500" : "bg-white/10"
        }`}
    >
      <motion.div
        className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-md"
        animate={{ x: active ? 20 : 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      />
    </button>
  </div>
);

export default function MusicPanel() {
  const [melodyEnabled, setMelodyEnabled] = useState(true);
  const [bassEnabled, setBassEnabled] = useState(true);
  const [tempo, setTempo] = useState(120);
  const [density, setDensity] = useState(0.5);
  const [rhythm, setRhythm] = useState(1);
  const [dynamics, setDynamics] = useState(0.5);
  const [isRecording, setIsRecording] = useState(false);

  const handleTempoChange = (e) => {
    const val = Number(e.target.value);
    setTempo(val);
    sendIntent({ music: { tempo_shift: { value: val, confidence: 0.8 } } });
  };

  const handleDensityChange = (e) => {
    const val = Number(e.target.value);
    setDensity(val);
    sendIntent({ music: { density_shift: { value: val, confidence: 0.8 } } });
  };

  const handleRhythmChange = (e) => {
    const val = Number(e.target.value);
    setRhythm(val);
    sendIntent({ music: { rhythm_intensity: { value: val, confidence: 0.8 } } });
  };

  const handleDynamicsChange = (e) => {
    const val = Number(e.target.value);
    setDynamics(val);
    sendIntent({ music: { dynamics: { value: val, confidence: 0.8 } } });
  };

  const toggleMelody = (val) => {
    setMelodyEnabled(val);
    sendIntent({ music: { melody_enabled: { value: val, confidence: 1.0 } } });
  };

  const toggleBass = (val) => {
    setBassEnabled(val);
    sendIntent({ music: { bass_enabled: { value: val, confidence: 1.0 } } });
  };

  return (
    <motion.div
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -20, opacity: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="h-full flex flex-col bg-glass-heavy border-r border-white/5 relative z-20 w-[360px]"
    >
      {/* Aurora Header */}
      <div className="p-8 pb-6 border-b border-white/5 relative overflow-hidden shrink-0">
        <div className="absolute top-0 right-0 p-8 opacity-20 pointer-events-none">
          <Music className="text-purple-400 rotate-12" size={80} />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg backdrop-blur-md border border-purple-500/20">
              <Music className="text-purple-300" size={18} />
            </div>
            <h2 className="text-2xl font-bold font-display tracking-tight bg-gradient-to-br from-white via-white to-purple-200 bg-clip-text text-transparent">
              Music Studio
            </h2>
          </div>
          <p className="text-[10px] text-purple-300/50 uppercase tracking-[0.2em] font-bold ml-1">
            Sonic Composition & Flow
          </p>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar mask-gradient">

        {/* Audio Engine Start */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={enableAudio}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-purple-900/40 to-indigo-900/40 border border-white/10 text-purple-100 text-sm font-semibold shadow-lg backdrop-blur-md flex items-center justify-center gap-2 group"
        >
          <Play size={16} className="fill-current text-purple-300 group-hover:text-white transition-colors" />
          Initialize Audio Engine
        </motion.button>

        <ControlGroup label="Layers" icon={Activity}>
          <div className="space-y-2">
            <ToggleButton label="Melody" active={melodyEnabled} onChange={toggleMelody} />
            <ToggleButton label="Bass" active={bassEnabled} onChange={toggleBass} />
          </div>
        </ControlGroup>

        <ControlGroup label="Dynamics" icon={Sliders}>
          <div className="space-y-4">
            <RangeSlider label="Tempo" value={tempo} min={60} max={160} step={1} onChange={handleTempoChange} />
            <RangeSlider label="Density" value={density} min={0} max={1} step={0.01} onChange={handleDensityChange} />
            <RangeSlider label="Rhythm" value={rhythm} min={0} max={1.5} step={0.01} onChange={handleRhythmChange} />
            <RangeSlider label="Sensitivity" value={dynamics} min={0} max={1} step={0.01} onChange={handleDynamicsChange} />
          </div>
        </ControlGroup>

        <ControlGroup label="Session" icon={Mic}>
          <div className="grid grid-cols-2 gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => { setIsRecording(true); startRecording(); }}
              className={`py-3 rounded-xl border flex items-center justify-center gap-2 text-xs font-semibold transition-all ${isRecording ? "bg-red-500/20 border-red-500/50 text-red-200" : "bg-white/5 border-white/5 text-purple-200/60 hover:bg-white/10"
                }`}
            >
              <div className={`w-2 h-2 rounded-full ${isRecording ? "bg-red-500 animate-pulse" : "bg-red-500/50"}`} />
              {isRecording ? "Recording..." : "Record"}
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => { setIsRecording(false); stopRecording(); }}
              className="py-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/10 text-xs font-semibold text-purple-200/60 flex items-center justify-center gap-2"
            >
              <Square size={10} className="fill-current" />
              Stop / Save
            </motion.button>
          </div>
        </ControlGroup>

      </div>
    </motion.div>
  );
}