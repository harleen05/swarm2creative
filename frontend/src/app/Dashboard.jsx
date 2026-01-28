import { useState } from "react";
import TopBar from "../components/TopBar";
import SmartDock from "../components/SmartDock";
import InsightPanel from "../components/InsightPanel";
import ArtCanvas from "../canvas/ArtCanvas";
import { useWebSocket } from "../hooks/useWebSocket";
import ArtPanel from "../panels/ArtPanel";
import { AnimatePresence } from "framer-motion";
import PromptBar from "../components/PromptBar";
import { playNotes } from "../audio/MusicEngine";
import { useEffect } from "react";
import MusicPanel from "../panels/MusicPanel";

export default function Dashboard() {
  const state = useWebSocket("ws://127.0.0.1:8000/ws");
  const [activePanel, setActivePanel] = useState(null);
  const [captureFn, setCaptureFn] = useState(null);

  const [latestNotes, setLatestNotes] = useState([]);
  useEffect(() => {
    if (state?.music_frame?.notes) {
      setLatestNotes(state.music_frame.notes);
    }
  }, [state?.music_frame]);
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() < 0.7) {
        playNotes(latestNotes);
      }
    }, 180);
  
    return () => clearInterval(interval);
  }, [latestNotes]);

  return (
    <div className="h-screen flex flex-col relative">
      <TopBar />
  
      <div className="flex flex-1 overflow-hidden relative">
        {/* LEFT */}
        <div className="flex h-full">
          <SmartDock active={activePanel} setActive={setActivePanel} />
          <AnimatePresence>
            {activePanel === "art" && <ArtPanel />}
            {activePanel === "music" && <MusicPanel />}
          </AnimatePresence>
        </div>
          <div className="flex-1 flex items-center justify-center px-16">
          <div
          className="relative"
          style={{ width: 800, height: 600 }}
          >
            <ArtCanvas
              artFrame={state?.art_frame}
              onCaptureReady={setCaptureFn}
            />
          </div>
        </div>
          <InsightPanel art={state?.art} />
      </div>
  
      <PromptBar />
    </div>
  );  
}