import { useEffect, useRef } from "react";

export default function ArtCanvas({ art }) {
  const ref = useRef(null);

  useEffect(() => {
    const ctx = ref.current.getContext("2d");
    let t = 0;

    function draw() {
      ctx.clearRect(0, 0, 800, 800);
      ctx.fillStyle = "rgba(160,120,255,0.8)";

      const r = 120 + (art?.flow_noise || 0.02) * 300;
      ctx.beginPath();
      ctx.arc(
        400 + Math.sin(t) * 10,
        400 + Math.cos(t) * 10,
        r,
        0,
        Math.PI * 2
      );
      ctx.fill();

      t += 0.01;
      requestAnimationFrame(draw);
    }

    draw();
  }, [art]);

  return (
    <canvas
      ref={ref}
      width={800}
      height={800}
      className="mx-auto mt-10"
    />
  );
}