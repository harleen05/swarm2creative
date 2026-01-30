export default function StoryCanvas({ frame }) {
    const safeFrame = frame || { paragraphs: [], meta: {} };
    const paragraphs = safeFrame.paragraphs || [];
    const meta = safeFrame.meta || {};
    const phase = safeFrame.phase || "introduction";
    const isEnhanced = safeFrame.enhanced || false;
  
    return (
      <div className="p-6 text-white font-mono h-full overflow-y-auto" style={{ wordBreak: "break-word", overflowWrap: "break-word" }}>
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-2xl font-bold">Swarm Narrative</h2>
            {isEnhanced && (
              <span className="text-xs bg-yellow-500/20 text-yellow-300 px-2 py-1 rounded border border-yellow-500/30">
                ✨ LLM Enhanced
              </span>
            )}
          </div>
          <div className="flex gap-4 text-sm opacity-70">
            <span>Phase: <span className="capitalize">{phase.replace("_", " ")}</span></span>
            {meta.tone && <span>Tone: {meta.tone}</span>}
            {meta.pace && <span>Pace: {meta.pace}</span>}
            {meta.total_events !== undefined && <span>Events: {meta.total_events}</span>}
          </div>
        </div>
  
        {paragraphs.length === 0 && (
          <div className="opacity-50 italic text-center py-12">
            <p>No story generated yet.</p>
            <p className="text-sm mt-2">The story will emerge as agents interact...</p>
          </div>
        )}
  
        <div className="space-y-4">
          {paragraphs.map((p, i) => {
            // Handle both old string format and new object format
            const paraType = typeof p === "object" ? p.type : null;
            const content = typeof p === "object" ? p.content : p;
            const enhanced = typeof p === "object" ? p.enhanced : false;
            
            // Check if it's a header
            const isHeader = paraType === "header" || /^[📖🌱⚡🔥🧠]/.test(content) || (content.length < 50 && content === content.toUpperCase());
            
            return (
              <div 
                key={i} 
                className={`${
                  isHeader ? "font-bold text-lg mt-6 mb-2" : "mb-4"
                }`}
                style={{
                  width: "100%",
                  maxWidth: "100%",
                  wordWrap: "break-word",
                  overflowWrap: "break-word",
                  wordBreak: "break-word"
                }}
              >
                {isHeader ? (
                  <h3 
                    className={`opacity-90 ${enhanced ? "text-yellow-200" : ""}`}
                    style={{
                      wordBreak: "break-word",
                      overflowWrap: "break-word"
                    }}
                  >
                    {content}
                    {enhanced && <span className="ml-2 text-xs text-yellow-400/70">✨</span>}
                  </h3>
                ) : (
                  <div 
                    className={`flex gap-2 ${
                      enhanced 
                        ? "border-l-4 border-yellow-400/50 bg-yellow-500/5 py-2 px-3 rounded" 
                        : ""
                    }`}
                    style={{
                      width: "100%",
                      maxWidth: "100%"
                    }}
                  >
                    <p 
                      className={`leading-relaxed text-sm flex-1 ${
                        enhanced 
                          ? "opacity-95 text-yellow-50" 
                          : "opacity-90"
                      }`}
                      style={{
                        wordBreak: "break-word",
                        overflowWrap: "break-word",
                        wordWrap: "break-word",
                        minWidth: 0,
                        width: "100%"
                      }}
                    >
                      {content}
                      {enhanced && (
                        <span className="ml-2 text-xs text-yellow-400/60 italic">(LLM enhanced)</span>
                      )}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }  