import { motion } from "framer-motion";
import { sendIntent } from "../api/interpret";

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
  return (
    <motion.div
      initial={{ x: -40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -40, opacity: 0 }}
      transition={{ duration: 0.25 }}
      className="h-full w-[360px] bg-glass backdrop-blur-2xl border-r border-white/10 px-6 py-8"
    >
      <h2 className="text-xl font-semibold mb-2">Architecture Studio</h2>
      <p className="text-sm opacity-60 mb-8">
        Spatial intent & circulation
      </p>

      <section className="space-y-6">
        <label className="block">
          <div className="text-xs uppercase opacity-60 mb-1">
            Spatial Openness
          </div>
          <select
            onChange={(e) =>
              sendIntent({
                architecture: {
                  openness: { value: e.target.value, confidence: 1.0 }
                }
              })
            }
            className="w-full bg-black/40 rounded-lg px-3 py-2"
          >
            <option value="tight">Tight</option>
            <option value="balanced">Balanced</option>
            <option value="open">Open</option>
          </select>
        </label>

        <label className="block">
          <div className="text-xs uppercase opacity-60 mb-1">
            Room Privacy
          </div>
          <select
            onChange={(e) =>
              sendIntent({
                architecture: {
                  privacy: { value: e.target.value, confidence: 1.0 }
                }
              })
            }
            className="w-full bg-black/40 rounded-lg px-3 py-2"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>

        <label className="block">
          <div className="text-xs uppercase opacity-60 mb-1">
            Circulation Style
          </div>
          <select
            onChange={(e) =>
              sendIntent({
                architecture: {
                  circulation: { value: e.target.value, confidence: 1.0 }
                }
              })
            }
            className="w-full bg-black/40 rounded-lg px-3 py-2"
          >
            <option value="centralized">Centralized</option>
            <option value="linear">Linear</option>
            <option value="distributed">Distributed</option>
          </select>
        </label>
      </section>
      <section className="space-y-2 mt-8">
        <div className="text-xs uppercase opacity-60 mb-2">
          Presets
        </div>

        {Object.keys(PRESETS).map(key => (
          <button
            key={key}
            onClick={() =>
              sendIntent({
                architecture: {
                  spatial_openness: {
                    value: PRESETS[key].spatial_openness,
                    confidence: 1
                  },
                  room_privacy: {
                    value: PRESETS[key].room_privacy,
                    confidence: 1
                  },
                  circulation_style: {
                    value: PRESETS[key].circulation_style,
                    confidence: 1
                  }
                }
              })
            }
            className="w-full py-2 rounded-lg bg-white/15 hover:bg-white/25 text-sm capitalize"
          >
            {key}
          </button>
        ))}
        </section>
    </motion.div>
  );
}