import { useState } from "react";
import { motion } from "framer-motion";
import { Building2, Layers, Box, Maximize, ArrowLeftRight, Component } from "lucide-react";
import { sendIntent } from "../api/interpret";

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

const PRESETS = {
  gallery: {
    spatial_openness: "open",
    room_privacy: "low",
    circulation_style: "centralized"
  },
  house: {
    spatial_openness: "medium",
    room_privacy: "high",
    circulation_style: "distributed"
  },
  office: {
    spatial_openness: "tight",
    room_privacy: "medium",
    circulation_style: "linear"
  }
};

export default function ArchitecturePanel() {
  const [openness, setOpenness] = useState("tight");
  const [privacy, setPrivacy] = useState("medium");
  const [circulation, setCirculation] = useState("linear");

  const updateArch = (type, val) => {
    // Optimistic Update
    if (type === "spatial_openness") setOpenness(val);
    if (type === "room_privacy") setPrivacy(val);
    if (type === "circulation_style") setCirculation(val);

    sendIntent({
      architecture: {
        architecture_intent: {
          [type]: { value: val, confidence: 1.0 }
        }
      }
    });
  };

  const applyPreset = (key) => {
    const p = PRESETS[key];
    setOpenness(p.spatial_openness);
    setPrivacy(p.room_privacy);
    setCirculation(p.circulation_style);

    sendIntent({
      architecture: {
        architecture_intent: {
          spatial_openness: { value: p.spatial_openness, confidence: 1 },
          room_privacy: { value: p.room_privacy, confidence: 1 },
          circulation_style: { value: p.circulation_style, confidence: 1 }
        }
      }
    });
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
          <Building2 className="text-purple-400 rotate-12" size={80} />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg backdrop-blur-md border border-purple-500/20">
              <Layers className="text-purple-300" size={18} />
            </div>
            <h2 className="text-2xl font-bold font-display tracking-tight bg-gradient-to-br from-white via-white to-purple-200 bg-clip-text text-transparent">
              Architect
            </h2>
          </div>
          <p className="text-[10px] text-purple-300/50 uppercase tracking-[0.2em] font-bold ml-1">
            Spatial & Structural Logic
          </p>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar mask-gradient">

        <ControlGroup label="Quick Presets" icon={Box}>
          <div className="grid grid-cols-3 gap-2">
            {Object.keys(PRESETS).map(key => (
              <motion.button
                key={key}
                whileHover={{ scale: 1.05, backgroundColor: "rgba(255, 255, 255, 0.1)" }}
                whileTap={{ scale: 0.95 }}
                onClick={() => applyPreset(key)}
                className="py-2.5 rounded-xl bg-white/5 border border-white/5 text-xs font-medium capitalize text-purple-200/80 hover:text-white transition-all"
              >
                {key}
              </motion.button>
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Spatial Openness" icon={Maximize}>
          <div className="grid grid-cols-1 gap-2">
            {["tight", "balanced", "open"].map(v => (
              <SelectButton
                key={v}
                label={v.charAt(0).toUpperCase() + v.slice(1)}
                active={openness === v}
                onClick={() => updateArch("spatial_openness", v)}
              />
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Privacy Gradient" icon={Component}>
          <div className="flex gap-2">
            {["low", "medium", "high"].map(v => (
              <div key={v} className="flex-1">
                <SelectButton
                  label={v.charAt(0).toUpperCase() + v.slice(1)}
                  active={privacy === v}
                  onClick={() => updateArch("room_privacy", v)}
                />
              </div>
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Circulation" icon={ArrowLeftRight}>
          <div className="grid grid-cols-1 gap-2">
            {["centralized", "linear", "distributed"].map(v => (
              <SelectButton
                key={v}
                label={v.charAt(0).toUpperCase() + v.slice(1)}
                active={circulation === v}
                onClick={() => updateArch("circulation_style", v)}
              />
            ))}
          </div>
        </ControlGroup>

      </div>
    </motion.div>
  );
}