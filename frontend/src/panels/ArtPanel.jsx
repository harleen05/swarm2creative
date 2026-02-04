import { useState } from "react";
import { motion } from "framer-motion";
import { Palette, Sparkles, Zap, Layout, Shapes, Smile, Sliders } from "lucide-react";
import { sendIntent } from "../api/interpret.js";
import { generateFigurativeImage } from "../api/generateImage.js";

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

const SelectButton = ({ label, active, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.02, backgroundColor: active ? "rgba(168, 85, 247, 0.3)" : "rgba(255, 255, 255, 0.08)" }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className={`w-full text-left px-4 py-3.5 rounded-xl text-sm font-medium transition-all duration-300 border backdrop-blur-md relative overflow-hidden group ${active
      ? "bg-purple-500/20 border-purple-400/40 text-white shadow-[0_0_20px_rgba(168,85,247,0.15)]"
      : "bg-white/5 border-white/5 text-purple-200/60 hover:border-purple-500/20"}`}
  >
    {active && (
      <motion.div
        layoutId="activeGlow"
        className="absolute inset-0 bg-purple-500/10"
        initial={false}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      />
    )}
    <span className="relative z-10">{label}</span>
  </motion.button>
);

const ActionButton = ({ label, icon: Icon, onClick, variant = "neutral" }) => (
  <motion.button
    whileHover={{ scale: 1.02, backgroundColor: "rgba(255, 255, 255, 0.1)" }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-xs font-medium transition-all duration-300 border backdrop-blur-md ${variant === "primary"
        ? "bg-purple-500/20 border-purple-400/30 text-white shadow-lg shadow-purple-900/20"
        : "bg-white/5 border-white/5 text-purple-200/70 hover:text-white hover:border-white/20"
      }`}
  >
    {Icon && <Icon size={14} className={variant === "primary" ? "text-purple-300" : "text-purple-200/50"} />}
    <span>{label}</span>
  </motion.button>
);

export default function ArtPanel() {
  const [activeMode, setActiveMode] = useState("freeform");
  const [activeShape, setActiveShape] = useState("spiral");
  const [activeEmotion, setActiveEmotion] = useState("joy");
  const [generating, setGenerating] = useState(false);

  // Helper to send intent and update local UI state
  const handleModeChange = (val) => {
    setActiveMode(val);
    sendIntent({ art: { art_mode: { value: val, confidence: 0.9 } } });
  };

  const handleShapeChange = (val) => {
    setActiveShape(val);
    sendIntent({ art: { shape: { value: val, confidence: 0.85 } } });
  };

  const handleEmotionChange = (val) => {
    setActiveEmotion(val);
    sendIntent({ art: { emotion: { value: val, confidence: 0.8 } } });
  };

  const handleCapture = () => {
    const img = window.captureArt();
    const a = document.createElement("a");
    a.href = img;
    a.download = "swarm-art.png";
    a.click();
  };

  const handleGenerateFigurative = async () => {
    setGenerating(true);
    try {
      const result = await generateFigurativeImage();
      if (result && result.image_base64) {
        const a = document.createElement("a");
        a.href = `data:image/png;base64,${result.image_base64}`;
        a.download = "figurative_snapshot.png";
        a.click();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
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
          <Palette className="text-purple-400 rotate-12" size={80} />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg backdrop-blur-md border border-purple-500/20">
              <Palette className="text-purple-300" size={18} />
            </div>
            <h2 className="text-2xl font-bold font-display tracking-tight bg-gradient-to-br from-white via-white to-purple-200 bg-clip-text text-transparent">
              Art Studio
            </h2>
          </div>
          <p className="text-[10px] text-purple-300/50 uppercase tracking-[0.2em] font-bold ml-1">
            Visual Synthesis Engine
          </p>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar mask-gradient">

        <ControlGroup label="Canvas Mode" icon={Layout}>
          <div className="grid grid-cols-1 gap-2">
            {[
              { label: "Freeform", value: "freeform" },
              { label: "Geometric", value: "geometric" },
              { label: "Mandala", value: "mandala" }
            ].map(m => (
              <SelectButton
                key={m.value}
                label={m.label}
                active={activeMode === m.value}
                onClick={() => handleModeChange(m.value)}
              />
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Geometry" icon={Shapes}>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Spiral", value: "spiral" },
              { label: "Ring", value: "ring" },
              { label: "Petal", value: "petal" },
              { label: "Orbit", value: "orbit" },
              { label: "Rays", value: "rays" },
              { label: "Vortex", value: "vortex" }
            ].map(s => (
              <SelectButton
                key={s.value}
                label={s.label}
                active={activeShape === s.value}
                onClick={() => handleShapeChange(s.value)}
              />
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Atmosphere" icon={Smile}>
          <div className="flex gap-2 flex-wrap">
            {[
              { label: "Calm", value: "calm" },
              { label: "Joy", value: "joy" },
              { label: "Anxiety", value: "anxiety" }
            ].map(e => (
              <div key={e.value} className="flex-1 min-w-[30%]">
                <SelectButton
                  label={e.label}
                  active={activeEmotion === e.value}
                  onClick={() => handleEmotionChange(e.value)}
                />
              </div>
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Refinements" icon={Sliders}>
          <div className="grid grid-cols-2 gap-2">
            <ActionButton
              label="+ Symmetry"
              onClick={() => sendIntent({ art: { symmetry_delta: { value: 1, confidence: 0.7 } } })}
            />
            <ActionButton
              label="− Noise"
              onClick={() => sendIntent({ art: { flow_noise_delta: { value: -0.01, confidence: 0.7 } } })}
            />
            <ActionButton
              label="+ Flow"
              onClick={() => sendIntent({ art: { flow_noise_delta: { value: 0.01, confidence: 0.7 } } })}
            />
            <ActionButton
              label="Capture"
              onClick={handleCapture}
            />
          </div>
          <div className="flex gap-2 mt-2">
            <ActionButton
              label="Freeze"
              onClick={() => sendIntent({ art: { paused: { value: true, confidence: 1.0 } } })}
            />
            <ActionButton
              label="Unfreeze"
              onClick={() => sendIntent({ art: { paused: { value: false, confidence: 1.0 } } })}
            />
          </div>
        </ControlGroup>

        <div className="pt-4 border-t border-white/5">
          <div className="text-[10px] uppercase tracking-wider text-purple-200/40 mb-3 ml-1 font-bold">
            Figurative Output
          </div>
          <motion.button
            whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(168,85,247,0.2)" }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGenerateFigurative}
            disabled={generating}
            className="w-full flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 text-purple-100 border border-white/10 px-4 py-3 rounded-xl text-xs font-medium transition-all"
          >
            {generating ? <Zap size={14} className="animate-spin text-purple-400" /> : <Sparkles size={14} className="text-purple-400" />}
            {generating ? "Generating..." : "Generate Snapshot (SDXL)"}
          </motion.button>
        </div>

      </div>
    </motion.div>
  );
}