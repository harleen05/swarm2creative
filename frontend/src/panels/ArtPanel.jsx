export default function ArtPanel() {
  return (
    <div className="h-full w-[360px] bg-glass backdrop-blur-2xl border-r border-white/10 px-6 py-8">
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold">Art Studio</h2>
        <p className="text-sm opacity-60">Shape, emotion & form</p>
      </div>

      <div className="space-y-10">

        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Art Mode
          </div>
          <div className="grid grid-cols-3 gap-3">
            {["Freeform", "Geometric", "Mandala"].map(m => (
              <button
                key={m}
                className="py-3 rounded-xl bg-white/10 hover:bg-white/20 transition text-sm"
              >
                {m}
              </button>
            ))}
          </div>
        </section>

        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Emotion
          </div>
          <div className="flex gap-3">
            {["Calm", "Energetic", "Tense"].map(e => (
              <button
                key={e}
                className="px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition text-sm"
              >
                {e}
              </button>
            ))}
          </div>
        </section>

        <section>
          <div className="text-xs uppercase tracking-wider opacity-60 mb-3">
            Fine Adjustments
          </div>
          <div className="flex flex-col gap-3">
            <button className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm">
              + Symmetry
            </button>
            <button className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm">
              − Noise
            </button>
            <button className="py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm">
              + Flow
            </button>
          </div>
        </section>

      </div>
    </div>
  );
}