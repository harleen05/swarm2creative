const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function sendIntent(payload) {
  const res = await fetch('${API_BASE}/interpret', {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Interpret failed: ${res.status}`);
  }
  return res.json();
}