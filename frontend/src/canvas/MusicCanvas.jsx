import { useEffect, useRef } from "react";

const HISTORY = 96;
const PITCH_MIN = 36;
const PITCH_MAX = 84;

export default function MusicCanvas({ notes }) {
  const ref = useRef();
  const history = useRef([]);

  useEffect(() => {
    if (!notes || notes.length === 0) return;

    const t = performance.now();
    notes.forEach(n => {
      history.current.push({ ...n, t });
    });

    if (history.current.length > HISTORY) {
      history.current.splice(0, history.current.length - HISTORY);
    }
  }, [notes]);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let raf;

    const draw = () => {
      ctx.fillStyle = "rgba(8,8,14,0.35)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // grid
      ctx.strokeStyle = "rgba(255,255,255,0.05)";
      for (let x = 0; x < canvas.width; x += 60) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }

      const now = performance.now();

      history.current.forEach(n => {
        const age = (now - n.t) / 600;
        if (age > 3) return;

        const x = age * 220;
        if (x > canvas.width) return;
        const pitchNorm =
          (n.pitch - PITCH_MIN) / (PITCH_MAX - PITCH_MIN);

        const y = canvas.height - pitchNorm * canvas.height;
        const w = (n.duration || 0.25) * 120;
        const h = n.layer === "bass" ? 10 : 6;

        ctx.fillStyle =
          n.layer === "bass"
            ? "rgba(120,220,220,0.8)"
            : "rgba(190,160,255,0.9)";

        ctx.fillRect(x, y, w, h);
      });

      raf = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <canvas
      ref={ref}
      width={720}
      height={260}
      className="rounded-xl bg-black/50"
    />
  );
}