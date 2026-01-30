import { useEffect, useRef, useState } from "react";

export default function ArchitectureCanvas({ frame }) {
  const ref = useRef(null);
  const heightRef = useRef({});
  const animRef = useRef(0);
  const [sectionMode, setSectionMode] = useState(false);
  const floorAnimRef = useRef(0);
  const [, forceRedraw] = useState(0);
  const musicEnergy = frame?.music_energy ?? 0.5;

  const handleKey = e => {
    const tag = document.activeElement?.tagName;
    if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
  
    if (e.key.toLowerCase() === "s") {
      setSectionMode(prev => !prev);
    }
  };  

  const OPENNESS_MAP = {
    open: "open",
    Open: "open",
    OPEN: "open",
  
    medium: "medium",
    Medium: "medium",
    balanced: "medium",
    Balanced: "medium",
  
    tight: "tight",
    Tight: "tight",
    compact: "tight",
    Compact: "tight"
  };
  
  const PRIVACY_MAP = {
    low: "low",
    Low: "low",
    public: "low",
  
    medium: "medium",
    Medium: "medium",
  
    high: "high",
    High: "high",
    private: "high"
  };
  
  const CIRCULATION_MAP = {
    linear: "linear",
    Linear: "linear",
  
    centralized: "centralized",
    Centralized: "centralized",
    radial: "centralized",
  
    distributed: "distributed",
    Distributed: "distributed",
    networked: "distributed"
  };  
  
  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);  

  useEffect(() => {
    if (!frame) return;
    let rafId;

    const draw = () => {
      animRef.current += 0.016;
      rafId = requestAnimationFrame(draw);
    };

    draw();
    const canvas = ref.current;
    const ctx = canvas.getContext("2d");

    const openness =
      OPENNESS_MAP[frame.spatial_openness] ?? "medium";

    const privacy =
      PRIVACY_MAP[frame.room_privacy] ?? "medium";

    const circulation =
      CIRCULATION_MAP[frame.circulation_style] ?? "linear";

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

    const gap =
      openness === "open" ? 28 :
      openness === "medium" ? 18 : 8;

    const startX = (canvas.width - cols * (baseSize + gap)) / 2;
    const startY = (canvas.height - rows * (baseSize + gap)) / 2;

    const rooms = [];
      
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
    const layoutSeed = `${openness}_${privacy}_${circulation}`;
    let idx = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (idx >= roomCount) break;

        const seed = (idx + 1) * (privacy === "high" ? 1.3 : privacy === "medium" ? 1.1 : 0.9);
        const scale = 1 - (Math.sin(seed + layoutSeed.length) * 0.5 + 0.5) * variance;

        const w = baseSize * scale;
        const h = baseSize * scale;

        const x = startX + c * (baseSize + gap) + (baseSize - w) / 2;
        const y = startY + r * (baseSize + gap) + (baseSize - h) / 2;

        const isPrivate = privacy === "high" && idx % 2 === 0;

        const level =
            r === Math.floor(rows / 2) && c === Math.floor(cols / 2)
                ? 3
                : isPrivate
                ? 1
                : 2;

        const program =
          level === 3 ? "Core" :
          isPrivate ? "Private" : "Public";

        rooms.push({ x, y, w, h, private: isPrivate, level, program });

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

        // ---- PROGRAM LABEL ----
        ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.font = "11px monospace";
        ctx.fillText(
          program,
          x + 6,
          y + 14
        );
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
      
        const targetHeight =
          r.level === 3 ? 64 :
          r.level === 2 ? 40 : 22;

        const key = `${r.x}_${r.y}`;

        if (!heightRef.current[key]) {
          heightRef.current[key] = targetHeight;
        }

        heightRef.current[key] += (targetHeight - heightRef.current[key]) * 0.08;
        const height = heightRef.current[key];
      
        const tx = r.x - height * 0.55;
        const ty = r.y - height * 0.75;
        
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
      
        if (sectionMode && r.level >= 2) {
          ctx.fillStyle = "rgba(20,20,40,0.85)";
          ctx.fillRect(
            r.x,
            r.y + r.h * 0.45,
            r.w,
            r.h * 0.55
          );
        }

        ctx.strokeStyle = "rgba(255,255,255,0.85)";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(r.x, r.y, r.w, r.h);
        
        // ---- SECTION CUT ----
        if (sectionMode && r.level >= 2) {
          ctx.fillStyle = "rgba(30,30,50,0.75)";
          ctx.fillRect(r.x, r.y + r.h * 0.45, r.w, r.h * 0.55);
        }

        // ---- ZONING OVERLAY ----
        if (r.private) {
          ctx.fillStyle = "rgba(120,80,160,0.35)";
          ctx.fillRect(r.x, r.y, r.w, r.h);
        } else {
          ctx.fillStyle = "rgba(80,160,200,0.18)";
          ctx.fillRect(r.x, r.y, r.w, r.h);
        }
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
    ctx.fillStyle = "rgba(160,200,255,0.65)";
    ctx.fillRect(core.x, core.y - 14, core.w, core.h + 14);

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

    rooms.forEach((r, i) => {
      if (r === core) return;
    
      const cx = core.x + core.w / 2;
      const cy = core.y + core.h / 2;
      const rx = r.x + r.w / 2;
      const ry = r.y + r.h / 2;
    
      if (circulation === "centralized") {
        ctx.fillRect(
          Math.min(cx, rx) - 8,
          Math.min(cy, ry) - 8,
          Math.abs(rx - cx) + 16,
          Math.abs(ry - cy) + 16
        );
      }
    
      if (circulation === "linear" && i > 0) {
        const prev = rooms[i - 1];
        ctx.fillRect(
          prev.x + prev.w / 2,
          prev.y + prev.h / 2,
          rx - (prev.x + prev.w / 2),
          16
        );
      }
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

    // ---- CIRCULATION DIRECTION ----
    ctx.strokeStyle = "rgba(200,240,255,0.85)";
    ctx.lineWidth = 2;

    rooms.forEach(r => {
      if (r === core) return;

      const cx = core.x + core.w / 2;
      const cy = core.y + core.h / 2;
      const rx = r.x + r.w / 2;
      const ry = r.y + r.h / 2;

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(
        cx + (rx - cx) * 0.85,
        cy + (ry - cy) * 0.85
      );
      ctx.stroke();

      // arrow head
      ctx.beginPath();
      ctx.arc(rx, ry, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // ---- STRUCTURAL GRID ----
    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.lineWidth = 1;

    for (let x = startX; x < startX + cols * baseSize; x += baseSize) {
      ctx.beginPath();
      ctx.moveTo(x, startY);
      ctx.lineTo(x, startY + rows * baseSize);
      ctx.stroke();
    }

    for (let y = startY; y < startY + rows * baseSize; y += baseSize) {
      ctx.beginPath();
      ctx.moveTo(startX, y);
      ctx.lineTo(startX + cols * baseSize, y);
      ctx.stroke();
    }

    // -----------------------------
    // LABELS
    // -----------------------------
    
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.font = "13px monospace";
    ctx.fillText(`Openness: ${openness}`, 20, 30);
    ctx.fillText(`Privacy: ${privacy}`, 20, 50);
    ctx.fillText(`Circulation: ${circulation}`, 20, 70);
    ctx.fillText("Press S → Section View", canvas.width - 200, 50);
    ctx.fillText(
      sectionMode ? "SECTION MODE (S)" : "PLAN MODE",
      canvas.width - 200,
      30
    );
    ctx.save();
    return () => cancelAnimationFrame(rafId);
  }, [frame, sectionMode]);

  function exportCanvas() {
    const link = document.createElement("a");
    link.download = "architecture.png";
    link.href = ref.current.toDataURL("image/png");
    link.click();
  }
  
  return (
    <>
      <canvas
        ref={ref}
        width={800}
        height={600}
        className="rounded-xl bg-black"
      />
      <button
        onClick={exportCanvas}
        className="absolute bottom-6 right-6 px-3 py-1 text-xs bg-white/10 text-white rounded"
      >
        Export
      </button>
    </>
  );  
}