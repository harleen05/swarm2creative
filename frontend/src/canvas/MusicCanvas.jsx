import { useEffect, useRef } from "react";

export default function MusicCanvas({ notes }) {
  const ref = useRef();

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || !notes) return;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    notes.forEach((n, i) => {
      const x = 50 + i * 80;
      const h = n.velocity;
      ctx.fillStyle = "rgba(180,150,255,0.8)";
      ctx.fillRect(x, 200 - h, 40, h);
    });
  }, [notes]);

  return <canvas ref={ref} width={600} height={300} />;
}