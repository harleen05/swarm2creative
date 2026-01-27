import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

export default function ArtCanvas({ artFrame, onCaptureReady }) {
  const canvasRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    if (!artFrame || !artFrame.agents) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const WIDTH = 800;
    const HEIGHT = 600;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = WIDTH * dpr;
    canvas.height = HEIGHT * dpr;
    canvas.style.width = `${WIDTH}px`;
    canvas.style.height = `${HEIGHT}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    window.captureArt = () => canvas.toDataURL("image/png");
    
    function draw() {
      ctx.fillStyle = "rgba(0, 0, 0, 0.06)";
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
      ctx.strokeStyle = "rgba(255,0,0,0.4)";
      ctx.beginPath();
      ctx.moveTo(WIDTH / 2 - 8, HEIGHT / 2);
      ctx.lineTo(WIDTH / 2 + 8, HEIGHT / 2);
      ctx.moveTo(WIDTH / 2, HEIGHT / 2 - 8);
      ctx.lineTo(WIDTH / 2, HEIGHT / 2 + 8);
      ctx.stroke();

      artFrame.agents.forEach(agent => {
        const [r, g, b] = agent.color;

        // draw trail
        const mode = artFrame.meta?.art_mode;
        if (mode !== "flow") {
          ctx.strokeStyle = `rgba(${r},${g},${b},0.12)`;
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          agent.trail.forEach((p, i) => {
            if (i === 0) ctx.moveTo(p[0], p[1]);
            else ctx.lineTo(p[0], p[1]);
          });
          ctx.stroke();
        }

        // glow head
        ctx.shadowBlur = 8;
        ctx.shadowColor = `rgb(${r},${g},${b})`;
        ctx.fillStyle = `rgb(${r},${g},${b})`;
        const vx = agent.trail.length > 1
          ? agent.x - agent.trail[agent.trail.length - 2][0]
          : 0;
        const vy = agent.trail.length > 1
          ? agent.y - agent.trail[agent.trail.length - 2][1]
          : 0;

        const len = Math.hypot(vx, vy) || 1;
        const nx = vx / len;
        const ny = vy / len;

        const strokeLen =
          artFrame.meta.art_mode === "flow" ? 10 : 6;

        ctx.strokeStyle = `rgb(${r},${g},${b})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(agent.x - nx * strokeLen, agent.y - ny * strokeLen);
        ctx.lineTo(agent.x + nx * strokeLen, agent.y + ny * strokeLen);
        ctx.stroke();

        ctx.shadowBlur = 0;
        
        // draw agent
        ctx.fillStyle = `rgb(${r},${g},${b})`;
        ctx.beginPath();
        ctx.arc(agent.x, agent.y, 2.5, 0, Math.PI * 2);
        ctx.fill();
      });

      rafRef.current = requestAnimationFrame(draw);
    }

    draw();

    return () => cancelAnimationFrame(rafRef.current);
  }, [artFrame]);

  return (
    <motion.canvas
      ref={canvasRef}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="rounded-lg"
    />
  );
}