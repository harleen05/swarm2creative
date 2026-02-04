import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { generateStory, getStory } from "../api/story";
import { BookOpen, Sparkles, Zap } from "lucide-react";

// --- Styled Components ---

const ControlGroup = ({ label, children }) => (
  <div className="mb-8 relative z-10">
    <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-purple-200/50 mb-4 ml-1 font-sans">
      {label}
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

const RangeSlider = ({ value, min, max, step, onChange, label, suffix = "" }) => (
  <div className="bg-white/5 rounded-2xl p-5 border border-white/5 hover:border-white/10 transition-colors group">
    <div className="flex justify-between text-xs mb-4">
      <span className="text-purple-200/60 font-medium group-hover:text-purple-200/80 transition-colors">{label}</span>
      <span className="text-white font-mono bg-white/10 px-2 py-1 rounded-md text-[10px] min-w-[3rem] text-center">{value}{suffix}</span>
    </div>
    <div className="relative h-2 w-full">
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

export default function StoryPanel({ story }) {
  const [currentStory, setCurrentStory] = useState(story);
  const [enhancing, setEnhancing] = useState(false);
  const [tone, setTone] = useState("dramatic");
  const [mood, setMood] = useState("hopeful");
  const [pace, setPace] = useState("moderate");
  const [wordLimit, setWordLimit] = useState(800);
  const [paragraphCount, setParagraphCount] = useState(6);

  useEffect(() => {
    if (story?.meta) {
      if (story.meta.tone) setTone(story.meta.tone);
      if (story.meta.mood) setMood(story.meta.mood);
      if (story.meta.pace) setPace(story.meta.pace);
    }
  }, [story?.meta]);

  if (!currentStory) return null;

  const updateTimeoutRef = useRef(null);

  const handleEnhance = async () => {
    setEnhancing(true);
    try {
      await generateStory(null, true, { tone, mood, pace, wordLimit, paragraphCount });
      const updated = await getStory();
      setCurrentStory(updated);
    } catch (error) {
      console.error(error);
    } finally {
      setEnhancing(false);
    }
  };

  useEffect(() => {
    // Manual regeneration only
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }
  }, [wordLimit, paragraphCount, tone, mood, pace]);

  return (
    <motion.div
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -20, opacity: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="h-full flex flex-col bg-glass-heavy border-r border-white/5 relative z-20"
    >
      {/* Aurora Header */}
      <div className="p-8 pb-6 border-b border-white/5 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-20 pointer-events-none">
          <BookOpen className="text-purple-400 rotate-12" size={80} />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg backdrop-blur-md border border-purple-500/20">
              <BookOpen className="text-purple-300" size={18} />
            </div>
            <h2 className="text-2xl font-bold font-display tracking-tight bg-gradient-to-br from-white via-white to-purple-200 bg-clip-text text-transparent">
              Story Engine
            </h2>
          </div>
          <p className="text-[10px] text-purple-300/50 uppercase tracking-[0.2em] font-bold ml-1">
            Artistic Intelligence v2.5
          </p>
        </div>
      </div>

      {/* Constraints & Controls */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar mask-gradient">

        <ControlGroup label="Narrative Style">
          <div className="grid grid-cols-1 gap-2">
            {["Dramatic", "Poetic", "Mysterious"].map(t => (
              <SelectButton key={t} label={t} active={tone === t.toLowerCase()} onClick={() => setTone(t.toLowerCase())} />
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Emotional Resonance">
          <div className="grid grid-cols-1 gap-2">
            {["Hopeful", "Tense", "Melancholic"].map(m => (
              <SelectButton key={m} label={m} active={mood === m.toLowerCase()} onClick={() => setMood(m.toLowerCase())} />
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Pacing & Flow">
          <div className="bg-white/5 p-1.5 rounded-2xl flex gap-1 border border-white/5 backdrop-blur-sm">
            {["Slow", "Moderate", "Fast"].map(p => (
              <button
                key={p}
                onClick={() => setPace(p.toLowerCase())}
                className={`flex-1 py-3 rounded-xl text-xs font-medium transition-all duration-300 relative ${pace === p.toLowerCase()
                    ? "text-white shadow-lg"
                    : "text-purple-200/40 hover:text-white"
                  }`}
              >
                {pace === p.toLowerCase() && (
                  <motion.div
                    layoutId="paceActive"
                    className="absolute inset-0 bg-purple-500/20 rounded-xl border border-purple-500/30"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10">{p}</span>
              </button>
            ))}
          </div>
        </ControlGroup>

        <ControlGroup label="Constraints">
          <div className="space-y-4">
            <RangeSlider
              label="Word Count"
              value={wordLimit}
              min={200} max={2000} step={50}
              onChange={(e) => setWordLimit(Number(e.target.value))}
            />
            <RangeSlider
              label="Paragraphs"
              value={paragraphCount}
              min={3} max={10} step={1}
              onChange={(e) => setParagraphCount(Number(e.target.value))}
            />
          </div>
        </ControlGroup>

      </div>

      {/* Footer Action */}
      <div className="p-8 border-t border-white/5 bg-gradient-to-t from-black/40 to-transparent backdrop-blur-xl">
        <motion.button
          whileHover={{ scale: 1.02, boxShadow: "0 0 40px rgba(168,85,247,0.3)" }}
          whileTap={{ scale: 0.96 }}
          onClick={handleEnhance}
          disabled={enhancing}
          className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-purple-600 via-fuchsia-500 to-pink-500 text-white px-6 py-4 rounded-2xl text-sm font-bold tracking-wide transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-purple-500/20 border border-white/10 group overflow-hidden relative"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
          {enhancing ? <Zap size={18} className="animate-spin text-yellow-300" /> : <Sparkles size={18} className="text-yellow-200" />}
          <span className="relative z-10">{enhancing ? "Weaving Narrative..." : "Regenerate Story"}</span>
        </motion.button>
      </div>

    </motion.div>
  );
}
