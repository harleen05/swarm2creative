export async function sendIntent(payload) {
  await fetch("hhttps://swarm2creative.onrender.com/interpret", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}