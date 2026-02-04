import { motion, AnimatePresence } from "framer-motion";

export default function StoryCanvas({ frame }) {
  const safeFrame = frame || { paragraphs: [], meta: {} };
  const paragraphs = safeFrame.paragraphs || [];
  const meta = safeFrame.meta || {};
  const phase = safeFrame.phase || "introduction";
  const isEnhanced = safeFrame.enhanced || false;

  // Animation variants
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 15, scale: 0.98 },
    show: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { type: "spring", stiffness: 70, damping: 12 }
    }
  };

  return (
    <div className="p-10 font-sans h-full overflow-y-auto no-scrollbar mask-gradient" style={{ wordBreak: "break-word", overflowWrap: "break-word" }}>

      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20, filter: "blur(10px)" }}
        animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="mb-10 p-8 rounded-3xl bg-glass-heavy border border-white/10 relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 opacity-50 group-hover:opacity-100 transition-opacity duration-500" />

        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-4xl font-bold font-display tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-purple-100 to-purple-200">
              Swarm Narrative
            </h2>
            {isEnhanced && (
              <motion.span
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                whileHover={{ scale: 1.05 }}
                className="px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs font-bold uppercase tracking-wider flex items-center gap-2 shadow-[0_0_15px_rgba(245,158,11,0.15)]"
              >
                <motion.span
                  animate={{ rotate: [0, 15, -15, 0] }}
                  transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
                >✨</motion.span>
                LLM Enhanced
              </motion.span>
            )}
          </div>

          <div className="flex flex-wrap gap-3">
            <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/5 backdrop-blur-md">
              <span className="text-white/40 text-xs uppercase tracking-wider font-bold mr-2">Phase</span>
              <span className="text-white font-medium capitalize">{phase.replace("_", " ")}</span>
            </div>
            {meta.tone && (
              <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/5 backdrop-blur-md">
                <span className="text-white/40 text-xs uppercase tracking-wider font-bold mr-2">Tone</span>
                <span className="text-purple-200 font-medium capitalize">{meta.tone}</span>
              </div>
            )}
            {meta.pace && (
              <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/5 backdrop-blur-md">
                <span className="text-white/40 text-xs uppercase tracking-wider font-bold mr-2">Pace</span>
                <span className="text-blue-200 font-medium capitalize">{meta.pace}</span>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {paragraphs.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-32 opacity-30"
        >
          <div className="w-16 h-1 bg-white/20 rounded-full mb-4 animate-pulse" />
          <p className="font-display text-xl tracking-wide">Waiting for the swarm...</p>
        </motion.div>
      )}

      {/* Story Content */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="max-w-4xl mx-auto pb-16 space-y-8"
      >
        <AnimatePresence mode="popLayout">
          {paragraphs.map((p, i) => {
            const content = typeof p === "object" ? p.content : p;
            const paraType = typeof p === "object" ? p.type : "paragraph";
            const enhanced = typeof p === "object" ? p.enhanced : false;
            const isHeader = paraType === "header" || /^[📖🌱⚡🔥🧠🔄]/.test(content);

            return (
              <motion.div
                key={`${i}-${content.substring(0, 15)}`}
                variants={item}
                layout="position"
                className={`relative ${isHeader ? "pt-8" : ""}`}
              >
                {isHeader ? (
                  <div className="group">
                    <h3 className="text-2xl font-display font-bold text-white mb-4 pl-4 border-l-4 border-purple-500/50 flex items-center gap-3">
                      {content}
                    </h3>
                    <div className="h-px w-full bg-gradient-to-r from-purple-500/30 to-transparent" />
                  </div>
                ) : (
                  <div
                    className={`
                      relative p-6 rounded-2xl transition-all duration-500 group
                      ${enhanced
                        ? "bg-white/[0.02] hover:bg-white/[0.04] border border-white/5 hover:border-white/10"
                        : "text-white/80"
                      }
                    `}
                  >
                    <p className={`text-lg leading-relaxed text-slate-200 tracking-wide ${enhanced ? "font-light" : ""}`}>
                      {content}
                    </p>
                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                  </div>
                )}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}