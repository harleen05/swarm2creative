import { useEffect, useRef } from "react";

export default function ArchitectureCanvas({ frame }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!frame) return;

    const canvas = ref.current;
    const ctx = canvas.getContext("2d");

    const openness = frame.spatial_openness ?? "medium";
    const privacy = frame.room_privacy ?? "medium";
    const circulation = frame.circulation_style ?? "linear";

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#0b0b15";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // -----------------------------
    // PARAMETERS
    // -----------------------------
    const roomCount =
      privacy === "high" ? 5 :
      privacy === "medium" ? 8 : 12;

    const baseSize =
      openness === "open" ? 130 :
      openness === "medium" ? 100 : 75;

    const variance =
      privacy === "high" ? 0.15 :
      privacy === "medium" ? 0.3 : 0.45;

    const cols = Math.ceil(Math.sqrt(roomCount));
    const rows = Math.ceil(roomCount / cols);

    const startX = (canvas.width - cols * baseSize) / 2;
    const startY = (canvas.height - rows * baseSize) / 2;

    const rooms = [];

    function drawRoom(ctx, r, z) {
        const depth = z * 18;
      
        // shadow
        ctx.fillStyle = "rgba(0,0,0,0.35)";
        ctx.fillRect(r.x + depth, r.y + depth + r.h, r.w, 10);
      
        // top face
        ctx.fillStyle = "rgba(200,190,255,0.55)";
        ctx.fillRect(r.x - depth, r.y - depth, r.w, r.h);
      
        // side face
        ctx.fillStyle = "rgba(90,80,150,0.55)";
        ctx.beginPath();
        ctx.moveTo(r.x - depth, r.y - depth);
        ctx.lineTo(r.x, r.y);
        ctx.lineTo(r.x + r.w, r.y);
        ctx.lineTo(r.x + r.w - depth, r.y - depth);
        ctx.closePath();
        ctx.fill();
      
        // front face
        ctx.fillStyle = "rgba(120,110,180,0.75)";
        ctx.fillRect(r.x, r.y, r.w, r.h);
      
        ctx.strokeStyle = "rgba(255,255,255,0.9)";
        ctx.strokeRect(r.x, r.y, r.w, r.h);
      }
      
    // -----------------------------
    // CORE (HIERARCHY)
    // -----------------------------
    const coreSize = baseSize * 1.4;
    const core = {
      x: canvas.width / 2 - coreSize / 2,
      y: canvas.height / 2 - coreSize / 2,
      w: coreSize,
      h: coreSize,
      type: "core"
    };

    rooms.push(core);

    // -----------------------------
    // ROOMS (PUBLIC → PRIVATE)
    // -----------------------------
    let idx = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (idx >= roomCount) break;

        const scale = 1 - Math.random() * variance;
        const w = baseSize * scale;
        const h = baseSize * scale;

        const x = startX + c * baseSize + (baseSize - w) / 2;
        const y = startY + r * baseSize + (baseSize - h) / 2;

        const isPrivate = privacy === "high" && idx % 2 === 0;

        const level =
            r === Math.floor(rows / 2) && c === Math.floor(cols / 2)
                ? 3
                : isPrivate
                ? 1
                : 2;

        rooms.push({ x, y, w, h, private: isPrivate, level });

        ctx.fillStyle = isPrivate
            ? "rgba(70,70,110,0.65)"
            : "rgba(180,170,255,0.35)";

            ctx.strokeStyle = isPrivate
            ? "rgba(200,200,255,0.9)"
            : "rgba(255,255,255,0.8)";

        ctx.fillRect(x, y, w, h);

        ctx.strokeStyle = "rgba(220,210,255,0.9)";
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);

        // DOOR
        ctx.fillStyle = "rgba(255,255,255,0.9)";
        ctx.strokeStyle = "rgba(220,240,255,0.9)";
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.arc(
        x + w / 2,
        y + h,
        8,
        Math.PI,
        Math.PI * 1.5
        );
        ctx.stroke();

        idx++;
      }
    }

    // corridor body
    ctx.strokeStyle = "rgba(100,160,220,0.18)";
    ctx.lineWidth = 28;
    ctx.stroke();

    // corridor edge
    ctx.strokeStyle = "rgba(160,220,255,0.45)";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.lineCap = "round";
    rooms.sort((a, b) => a.level - b.level);

    rooms.forEach(r => {
        if (r === core) return;
      
        const height =
            r.level === 3 ? 48 :
            r.level === 2 ? 30 : 18;
      
        const tx = r.x - height * 0.6;
        const ty = r.y - height * 0.6;
        
        // --- CAST SHADOW ---
        ctx.fillStyle = "rgba(0,0,0,0.35)";
        ctx.beginPath();
        ctx.ellipse(
        r.x + r.w / 2,
        r.y + r.h + height * 0.9,
        r.w * 0.55,
        r.h * 0.18,
        0,
        0,
        Math.PI * 2
        );
        ctx.fill();

        // top face
        ctx.fillStyle = r.private
          ? "rgba(110,110,160,0.6)"
          : "rgba(200,190,255,0.55)";
        ctx.fillRect(tx, ty, r.w, r.h);
      
        // side face
        ctx.fillStyle = "rgba(90,80,150,0.55)";
        ctx.beginPath();
        ctx.moveTo(tx, ty);
        ctx.lineTo(r.x, r.y);
        ctx.lineTo(r.x + r.w, r.y);
        ctx.lineTo(tx + r.w, ty);
        ctx.closePath();
        ctx.fill();
      
        // front face
        ctx.fillStyle = "rgba(120,110,180,0.65)";
        ctx.fillRect(r.x, r.y, r.w, r.h);
      
        ctx.strokeStyle = "rgba(255,255,255,0.85)";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(r.x, r.y, r.w, r.h);
    });      

    // CORE SHADOW (grounds the building)
    ctx.fillStyle = "rgba(0,0,0,0.55)";
    ctx.beginPath();
    ctx.ellipse(
    core.x + core.w / 2,
    core.y + core.h + 42,
    core.w * 0.65,
    core.h * 0.22,
    0,
    0,
    Math.PI * 2
    );
    ctx.fill();

    // CORE MASS
    ctx.fillStyle = "rgba(140,180,255,0.55)";
    ctx.fillRect(core.x, core.y, core.w, core.h);

    // CORE EDGE
    ctx.strokeStyle = "rgba(255,255,255,1)";
    ctx.lineWidth = 3;
    ctx.strokeRect(core.x, core.y, core.w, core.h);

    // -----------------------------
    // BEAMS (STRUCTURE)
    // -----------------------------
    ctx.strokeStyle = "rgba(255,255,255,0.12)";
    ctx.lineWidth = 2;

    // ---- CORRIDORS AS SPACE ----
    ctx.fillStyle = "rgba(100,160,220,0.18)";

    rooms.forEach(r => {
        if (r === core) return;

        const cx = core.x + core.w / 2;
        const cy = core.y + core.h / 2;

        const rx = r.x + r.w / 2;
        const ry = r.y + r.h / 2;

        const w = Math.abs(rx - cx);
        const h = Math.abs(ry - cy);

        ctx.fillRect(
            Math.min(cx, rx) - 8,
            Math.min(cy, ry) - 8,
            w + 16,
            h + 16
        );
    });

    ctx.beginPath();
    ctx.arc(
    core.x + core.w / 2,
    core.y + core.h / 2,
    core.w,
    0,
    Math.PI * 2
    );
    ctx.fill();

    ctx.strokeStyle = "rgba(255,255,255,0.9)";
    ctx.lineWidth = 3;
    ctx.strokeRect(core.x, core.y, core.w, core.h);
    
    // -----------------------------
    // LABELS
    // -----------------------------
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.font = "13px monospace";
    ctx.fillText(`Openness: ${openness}`, 20, 30);
    ctx.fillText(`Privacy: ${privacy}`, 20, 50);
    ctx.fillText(`Circulation: ${circulation}`, 20, 70);

  }, [frame]);

  return (
    <canvas
      ref={ref}
      width={800}
      height={600}
      className="rounded-xl bg-black"
    />
  );
}