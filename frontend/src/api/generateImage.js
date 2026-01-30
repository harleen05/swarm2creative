export async function generateFigurativeImage(optionalPrompt) {
  const res = await fetch(`${API_BASE}/generate-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt: optionalPrompt || null,
    }),
  });

  if (!res.ok) {
    console.warn("Figurative image generation failed", res.status);
    return null;
  }

  const data = await res.json();
  return data;
}


