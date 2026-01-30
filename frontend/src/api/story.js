export async function getStory() {
  const res = await fetch("https://swarm2creative.onrender.com/story", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    console.warn("Story fetch failed", res.status);
    return null;
  }

  const data = await res.json();
  return data;
}

export async function generateStory(prompt = null, enhance = false, options = {}) {
  const res = await fetch("https://swarm2creative.onrender.com/story/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt: prompt || null,
      enhance: enhance,
      tone: options.tone || null,
      mood: options.mood || null,
      pace: options.pace || null,
      word_limit: options.wordLimit || null,
      paragraph_count: options.paragraphCount || null,
    }),
  });

  if (!res.ok) {
    console.warn("Story generation failed", res.status);
    return null;
  }

  const data = await res.json();
  return data;
}

export async function getFullStory() {
  const res = await fetch("https://swarm2creative.onrender.com/story/full", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    console.warn("Full story fetch failed", res.status);
    return null;
  }

  const data = await res.json();
  return data;
}

