import { motion } from "framer-motion";
import { sendIntent } from "../api/interpret.js";

export default function ArtPanel() {
  return (
    <motion.div
      initial={{ x: -40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -40, opacity: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="h-full w-[360px] bg-glass backdrop-blur-2xl border-r border-white/10 px-6 py-8"
    >
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold">Art Studio</h2>
        <p className="text-sm opacity-60">
          Mode, shape, emotion & refinement
        </p>
      </div>

      <div className="space-y-10">

        {/* ───────────────── Art Mode ───────────────── */}
        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Art Mode
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Freeform", value: "freeform" },
              { label: "Geometric", value: "geometric" },
              { label: "Mandala", value: "mandala" }
            ].map(m => (
              <button
                key={m.value}
                onClick={() =>
                  sendIntent({
                    art: {
                      art_mode: { value: m.value, confidence: 0.9 }
                    }
                  })
                }
                className="py-3 rounded-xl bg-white/10 hover:bg-white/20 transition text-sm"
              >
                {m.label}
              </button>
            ))}
          </div>
        </section>

        {/* ───────────────── Shape ───────────────── */}
        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Shape
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Spiral", value: "spiral" },
              { label: "Ring", value: "ring" },
              { label: "Petal", value: "petal" },
              { label: "Constellation", value: "constellation" },
              { label: "Vortex", value: "vortex" }
            ].map(s => (
              <button
                key={s.value}
                onClick={() =>
                  sendIntent({
                    art: {
                      shape: { value: s.value, confidence: 0.85 }
                    }
                  })
                }
                className="py-2 rounded-lg bg-white/10 hover:bg-white/20 transition text-sm"
              >
                {s.label}
              </button>
            ))}
          </div>
        </section>

        {/* ───────────────── Emotion ───────────────── */}
        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Emotion
          </div>
          <div className="flex gap-3 flex-wrap">
            {[
              { label: "Calm", value: "calm" },
              { label: "Joy", value: "joy" },
              { label: "Anxiety", value: "anxiety" }
            ].map(e => (
              <button
                key={e.value}
                onClick={() =>
                  sendIntent({
                    art: {
                      emotion: { value: e.value, confidence: 0.8 }
                    }
                  })
                }
                className="px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition text-sm"
              >
                {e.label}
              </button>
            ))}
          </div>
        </section>

        {/* ───────────────── Fine Adjustments ───────────────── */}
        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Fine Adjustments
          </div>
          <div className="flex flex-col gap-3">
            <button
              onClick={() =>
                sendIntent({
                  art: {
                    symmetry_delta: { value: 1, confidence: 0.7 }
                  }
                })
              }
              className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
            >
              + Symmetry
            </button>

            <button
              onClick={() =>
                sendIntent({
                  art: {
                    flow_noise_delta: { value: -0.01, confidence: 0.7 }
                  }
                })
              }
              className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
            >
              − Noise
            </button>

            <button
              onClick={() =>
                sendIntent({
                  art: {
                    flow_noise_delta: { value: 0.01, confidence: 0.7 }
                  }
                })
              }
              className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
            >
              + Flow
            </button>
            <button
              onClick={() =>
                sendIntent({
                  art: {
                    paused: { value: true, confidence: 1.0 }
                  }
                })
              }
              className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
            >
              Freeze
            </button>
            <button
              onClick={() => {
                const img = window.captureArt();
                const a = document.createElement("a");
                a.href = img;
                a.download = "swarm-art.png";
                a.click();
              }}              
              className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
            >
              Capture
            </button>
            <button
              onClick={() =>
                sendIntent({
                  art: {
                    paused: { value: false, confidence: 1.0 }
                  }
                })
              }
              className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
            >
              Unfreeze
            </button>
          </div>
        </section>

      </div>
    </motion.div>
  );
}