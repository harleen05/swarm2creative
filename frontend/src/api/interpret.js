const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function sendIntent(payload) {
  // If payload has 'text' field, use /chat endpoint (LLM interpretation)
  // Otherwise, use /interpret endpoint (direct intent)
  const endpoint = payload.text ? "/chat" : "/interpret";
  
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Interpret failed: ${res.status} - ${errorText}`);
  }
  return res.json();
}