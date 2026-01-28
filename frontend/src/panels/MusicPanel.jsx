import { motion } from "framer-motion";
import { sendIntent } from "../api/interpret";
import { enableAudio } from "../audio/MusicEngine";

export default function MusicPanel() {
  return (
    <motion.div
      initial={{ x: -40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -40, opacity: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="h-full w-[360px] bg-glass backdrop-blur-2xl border-r border-white/10 px-6 py-8"
    >
      <div className="mb-8">
        <h2 className="text-xl font-semibold">Music Studio</h2>
        <p className="text-sm opacity-60">
          Tempo, density & dynamics
        </p>
      </div>

      {/* 🔊 ENABLE AUDIO */}
      <section className="mb-10">
        <button
          onClick={enableAudio}
          className="w-full py-3 rounded-xl bg-white/15 hover:bg-white/25 transition text-sm"
        >
          Enable Audio
        </button>
      </section>

      <div className="space-y-10">

        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Tempo
          </div>
          <input
            type="range"
            min={60}
            max={160}
            defaultValue={120}
            onChange={(e) =>
              sendIntent({
                music: {
                  tempo_shift: {
                    value: Number(e.target.value),
                    confidence: 0.8
                  }
                }
              })
            }
            className="w-full"
          />
        </section>

        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Density
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            defaultValue={0.5}
            onChange={(e) =>
              sendIntent({
                music: {
                  density_shift: {
                    value: Number(e.target.value),
                    confidence: 0.8
                  }
                }
              })
            }
            className="w-full"
          />
        </section>

        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Dynamics
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            defaultValue={0.5}
            onChange={(e) =>
              sendIntent({
                music: {
                  dynamics: {
                    value: Number(e.target.value),
                    confidence: 0.8
                  }
                }
              })
            }
            className="w-full"
          />
        </section>

      </div>
    </motion.div>
  );
}