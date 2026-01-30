import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { generateStory } from "../api/story";
import { sendIntent } from "../api/interpret";

export default function StoryPanel({ story }) {
    const [enhancing, setEnhancing] = useState(false);
    const [tone, setTone] = useState("neutral");
    const [mood, setMood] = useState("neutral");
    const [pace, setPace] = useState("moderate");
    const [wordLimit, setWordLimit] = useState(500);
    const [paragraphCount, setParagraphCount] = useState(5);
    
    if (!story) {
      return (
        <motion.div
          initial={{ x: -40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -40, opacity: 0 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
          className="h-full w-[360px] bg-glass backdrop-blur-2xl border-r border-white/10 px-6 py-8"
        >
          <div className="text-sm text-white/60">
            No story data available
          </div>
        </motion.div>
      );
    }
  
    const meta = story.meta || {};
    const events = story.story_events || [];
    const updateTimeoutRef = useRef(null);
  
    const handleEnhance = async () => {
      setEnhancing(true);
      try {
        await generateStory(null, true, {
          tone,
          mood,
          pace,
          wordLimit,
          paragraphCount
        });
        // Story will update via websocket
      } catch (error) {
        console.error("Failed to enhance story:", error);
      } finally {
        setEnhancing(false);
      }
    };

    // Auto-update story when word limit or paragraph count changes (debounced)
    useEffect(() => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
      
      // Only update if there are story events (story exists)
      if (events.length > 0) {
        updateTimeoutRef.current = setTimeout(async () => {
          try {
            // Update story with new constraints (without LLM enhancement)
            await generateStory(null, false, {
              tone,
              mood,
              pace,
              wordLimit,
              paragraphCount
            });
          } catch (error) {
            console.error("Failed to update story constraints:", error);
          }
        }, 1000); // 1 second debounce
      }
      
      return () => {
        if (updateTimeoutRef.current) {
          clearTimeout(updateTimeoutRef.current);
        }
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [wordLimit, paragraphCount]); // Only trigger on these changes

    const updateTone = async (newTone) => {
      setTone(newTone);
      sendIntent({
        story: {
          tone: { value: newTone, confidence: 0.9 }
        }
      });
      // Generate story with new tone
      try {
        await generateStory(null, false, {
          tone: newTone,
          mood,
          pace,
          wordLimit,
          paragraphCount
        });
      } catch (error) {
        console.error("Failed to generate story with new tone:", error);
      }
    };

    const updatePace = async (newPace) => {
      setPace(newPace);
      sendIntent({
        story: {
          pace_shift: { value: newPace, confidence: 0.9 }
        }
      });
      // Generate story with new pace
      try {
        await generateStory(null, false, {
          tone,
          mood,
          pace: newPace,
          wordLimit,
          paragraphCount
        });
      } catch (error) {
        console.error("Failed to generate story with new pace:", error);
      }
    };
  
    return (
      <motion.div
        initial={{ x: -40, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: -40, opacity: 0 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
        className="h-full w-[360px] bg-glass backdrop-blur-2xl border-r border-white/10 px-6 py-8 overflow-y-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold">Story Studio</h2>
          <p className="text-sm opacity-60">
            Tone, mood, pace & generation
          </p>
        </div>

        {/* Current Status */}
        <div className="mb-6 p-3 bg-white/5 rounded-lg">
          <div className="text-xs uppercase tracking-wider opacity-60 mb-2">Current Status</div>
          <div className="text-sm space-y-1">
            <div className="opacity-70">
              Phase: <span className="capitalize text-white">{story.phase?.replace("_", " ") || "introduction"}</span>
            </div>
            {meta.total_events !== undefined && (
              <div className="opacity-70">Events: {meta.total_events}</div>
            )}
          </div>
        </div>

        {/* Tone Selection */}
        <section className="mb-6">
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Tone
          </div>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Neutral", value: "neutral" },
              { label: "Dramatic", value: "dramatic" },
              { label: "Poetic", value: "poetic" },
              { label: "Mysterious", value: "mysterious" },
              { label: "Epic", value: "epic" },
              { label: "Intimate", value: "intimate" }
            ].map(t => (
              <button
                key={t.value}
                onClick={() => updateTone(t.value)}
                className={`py-2 rounded-lg text-sm transition ${
                  tone === t.value
                    ? "bg-blue-500/30 border border-blue-400/50"
                    : "bg-white/10 hover:bg-white/20"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </section>

        {/* Mood Selection */}
        <section className="mb-6">
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Mood
          </div>
          <div className="flex flex-wrap gap-2">
            {[
              { label: "Neutral", value: "neutral" },
              { label: "Hopeful", value: "hopeful" },
              { label: "Melancholic", value: "melancholic" },
              { label: "Tense", value: "tense" },
              { label: "Triumphant", value: "triumphant" },
              { label: "Somber", value: "somber" }
            ].map(m => (
              <button
                key={m.value}
                onClick={() => setMood(m.value)}
                className={`px-3 py-2 rounded-full text-sm transition ${
                  mood === m.value
                    ? "bg-purple-500/30 border border-purple-400/50"
                    : "bg-white/10 hover:bg-white/20"
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        </section>

        {/* Pace Selection */}
        <section className="mb-6">
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Pace
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: "Slow", value: "slow" },
              { label: "Moderate", value: "moderate" },
              { label: "Fast", value: "fast" }
            ].map(p => (
              <button
                key={p.value}
                onClick={() => updatePace(p.value)}
                className={`py-2 rounded-lg text-sm transition ${
                  pace === p.value
                    ? "bg-green-500/30 border border-green-400/50"
                    : "bg-white/10 hover:bg-white/20"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </section>

        {/* Word Limit */}
        <section className="mb-6">
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Word Limit: {wordLimit}
          </div>
          <input
            type="range"
            min={200}
            max={2000}
            step={50}
            value={wordLimit}
            onChange={(e) => setWordLimit(Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs opacity-50 mt-1">
            <span>200</span>
            <span>2000</span>
          </div>
        </section>

        {/* Paragraph Count */}
        <section className="mb-6">
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Paragraphs: {paragraphCount}
          </div>
          <input
            type="range"
            min={3}
            max={10}
            step={1}
            value={paragraphCount}
            onChange={(e) => setParagraphCount(Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs opacity-50 mt-1">
            <span>3</span>
            <span>10</span>
          </div>
        </section>

        {/* Enhance Button */}
        {events.length > 0 && (
          <section className="mb-6">
            <button
              onClick={handleEnhance}
              disabled={enhancing}
              className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 rounded-lg text-white text-sm font-medium transition-colors"
            >
              {enhancing ? "Enhancing..." : "✨ Enhance with LLM"}
            </button>
          </section>
        )}

        {/* Recent Events */}
        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Recent Events
          </div>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {events.length === 0 ? (
              <div className="opacity-50 italic text-sm">No events yet</div>
            ) : (
              events.map((e, i) => (
                <div key={i} className="opacity-80 border-l-2 border-white/20 pl-2 py-1 text-sm">
                  <span className="capitalize">{e.story_type}</span>
                  {e.agents && (
                    <span className="opacity-60"> • Agents {e.agents.join(", ")}</span>
                  )}
                  {e.intensity && (
                    <span className="opacity-50 text-xs"> (intensity: {e.intensity})</span>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </motion.div>
    );
  }
  