import { useEffect, useRef } from "react";
const MAX_HISTORY = 64;

export default function MusicCanvas({ notes }) {
  const ref = useRef();
  const history = useRef([]);

  useEffect(() => {
    if (!notes || notes.length === 0) return;

    const timestamp = performance.now();
    notes.forEach(n => {
      history.current.push({
        ...n,
        t: timestamp
      });
    });

    if (history.current.length > MAX_HISTORY) {
      history.current.splice(0, history.current.length - MAX_HISTORY);
    }
  }, [notes]);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let raf;

    const draw = () => {
      ctx.fillStyle = "rgba(10,10,20,0.25)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const now = performance.now();

      history.current.forEach((n, i) => {
        const age = (now - n.t) / 1000;
        if (age > 2) return;

        const x =
          canvas.width -
          age * canvas.width * 0.5;

        const y =
          canvas.height -
          ((n.pitch - 36) / 48) * canvas.height;

        const pulse = Math.sin(age * 8) * 0.5 + 1;
        const r = (4 + (n.velocity || 40) * 0.06) * pulse;

        let color = "rgba(180,150,255,0.9)"; // melody
        if (n.layer === "bass") {
          color = "rgba(120,220,220,0.85)";
        }

        if (n.call === false) {
          color = color.replace("0.9", "0.5");
        }

        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.shadowBlur = 12;
        ctx.shadowColor = color;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      raf = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <canvas
      ref={ref}
      width={700}
      height={280}
      className="rounded-xl bg-black/40"
    />
  );
}