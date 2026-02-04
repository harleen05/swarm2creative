import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Zap, Palette, Music } from "lucide-react";

export default function LandingPage({ onEnter }) {
    return (
        <div className="h-screen w-screen flex items-center justify-center relative overflow-hidden">
            {/* Background is handled by body auroras, but we add a subtle overlay */}
            <div className="absolute inset-0 bg-black/20 pointer-events-none" />

            {/* Animated background highlights */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    className="absolute w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[100px]"
                    animate={{
                        x: [0, 100, 0],
                        y: [0, -50, 0],
                        scale: [1, 1.2, 1]
                    }}
                    transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
                    style={{ top: "10%", left: "20%" }}
                />
            </div>

            {/* Content */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
                className="relative z-10 text-center max-w-5xl px-8"
            >
                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.2, duration: 0.8 }}
                    className="mb-12"
                >
                    <h1 className="text-8xl md:text-9xl font-bold mb-6 font-display tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-purple-200 drop-shadow-2xl">
                        Creative Swarm
                    </h1>
                    <p className="text-3xl md:text-4xl font-light text-white/90 mb-4 font-display tracking-wide">
                        Where Digital Swarms Become Art
                    </p>
                    <p className="text-lg text-purple-200/60 max-w-2xl mx-auto font-sans leading-relaxed">
                        Simulating emergent creativity through autonomous agents.
                        <br />Witness the birth of art, music, and story in real-time.
                    </p>
                </motion.div>

                {/* Feature highlights */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16 max-w-4xl mx-auto">
                    {[
                        { icon: Palette, label: "Generative Art", color: "text-pink-300" },
                        { icon: Music, label: "Dynamic Music", color: "text-cyan-300" },
                        { icon: Sparkles, label: "AI Stories", color: "text-yellow-300" },
                        { icon: Zap, label: "Architecture", color: "text-violet-300" },
                    ].map(({ icon: Icon, label, color }, i) => (
                        <motion.div
                            key={label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 + (i * 0.1) }}
                            whileHover={{ y: -5, backgroundColor: "rgba(255,255,255,0.05)" }}
                            className="bg-glass rounded-2xl p-6 border border-white/5 flex flex-col items-center justify-center gap-3 backdrop-blur-md hover:border-white/10 transition-colors cursor-default"
                        >
                            <Icon className={color} size={28} strokeWidth={1.5} />
                            <p className="text-sm font-medium text-white/80 font-display tracking-wide">{label}</p>
                        </motion.div>
                    ))}
                </div>

                <motion.button
                    whileHover={{ scale: 1.05, boxShadow: "0 0 40px rgba(168,85,247,0.4)" }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onEnter}
                    className="group relative px-12 py-5 bg-white text-black rounded-full font-bold text-lg tracking-wide overflow-hidden shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-200 via-pink-200 to-purple-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <span className="relative z-10 font-display">Enter the Swarm</span>
                </motion.button>
            </motion.div>
        </div>
    );
}
