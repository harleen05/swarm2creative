let audioCtx = null;
let audioEnabled = false;
let masterGain = null;

function getCtx() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = audioCtx.createGain();
    masterGain.gain.value = 0.3;
    masterGain.connect(audioCtx.destination);
  }
  return audioCtx;
}


export function enableAudio() {
  const ctx = getCtx();
  if (ctx.state === "suspended") {
    ctx.resume();
  }
  audioEnabled = true;
  console.log("🔊 Audio enabled");
}

export function playNotes(notes) {
  if (!notes || notes.length === 0) {
    playNotes([{ pitch: 60, velocity: 40, duration: 0.4 }]);
    return;
  }  
  if (!audioEnabled || !notes || notes.length === 0) return;

  const ctx = getCtx();
  const now = ctx.currentTime;
  if (notes.length > 5) notes = notes.slice(0, 5);
  notes.forEach((n, i) => {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    const freq = 440 * Math.pow(2, (n.pitch - 69) / 12);
    osc.frequency.value = freq;

    if (n.layer === "bass") {
      osc.type = "sine";
      gain.gain.value = 0.04;
    } else {
      osc.type = "triangle";
      gain.gain.value = Math.min(0.15, ((n.velocity || 60) / 127) * 0.12);
    }

    osc.connect(gain);
    gain.connect(masterGain);

    const start = now + i * 0.02;
    const end = start + (n.layer === "bass"
    ? Math.min(n.duration || 1.5, 2.2)
    : Math.min(n.duration || 0.25, 0.18));

    osc.start(start);
    osc.stop(end);
  });
}