export async function generateFigurativeImage(optionalPrompt) {
  const res = await fetch("http://127.0.0.1:8000/generate-image", {
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


