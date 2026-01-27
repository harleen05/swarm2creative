export async function sendIntent(payload) {
  await fetch("http://127.0.0.1:8000/interpret", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}