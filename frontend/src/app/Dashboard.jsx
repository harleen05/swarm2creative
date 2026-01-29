import { useState, useEffect, useRef } from "react";
import TopBar from "../components/TopBar";
import SmartDock from "../components/SmartDock";
import InsightPanel from "../components/InsightPanel";
import ArtCanvas from "../canvas/ArtCanvas";
import MusicCanvas from "../canvas/MusicCanvas";
import { useWebSocket } from "../hooks/useWebSocket";
import ArtPanel from "../panels/ArtPanel";
import MusicPanel from "../panels/MusicPanel";
import { AnimatePresence } from "framer-motion";
import PromptBar from "../components/PromptBar";
import { playNotes } from "../audio/MusicEngine";

const CHORDS = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];

export default function Dashboard() {
  const state = useWebSocket("ws://127.0.0.1:8000/ws");

  const [activePanel, setActivePanel] = useState(null);
  const [captureFn, setCaptureFn] = useState(null);
  const liveNotesRef = useRef([]);
  const hasNewNotesRef = useRef(false);

  useEffect(() => {
    if (state?.music_frame?.notes && state.music_frame.notes.length > 0) {
      liveNotesRef.current = state.music_frame.notes;
      hasNewNotesRef.current = true;
    }
  }, [state?.music_frame]);  
  
  useEffect(() => {
    const interval = setInterval(() => {
      if (liveNotesRef.current.length > 0) {
        playNotes(liveNotesRef.current);
        hasNewNotesRef.current = false;
      }
    }, 180);
  
    return () => clearInterval(interval);
  }, []);   

  return (
    <div className="h-screen flex flex-col relative">
      <TopBar />

      <div className="flex flex-1 overflow-hidden relative">

        {/* LEFT SIDEBAR */}
        <div className="flex h-full">
        <SmartDock
          active={activePanel}
          setActive={(panel) =>
            setActivePanel(prev => (prev === panel ? null : panel))
          }
        />
          <AnimatePresence mode="wait">
            {activePanel === "art" && <ArtPanel key="art" />}
            {activePanel === "music" && <MusicPanel key="music" />}
          </AnimatePresence>
        </div>

        <div className="flex-1 flex items-center justify-center px-16">
          <div className="relative" style={{ width: 800, height: 600 }}>
            <ArtCanvas
              artFrame={state?.art_frame}
              onCaptureReady={setCaptureFn}
            />

            {state?.music_frame?.notes && (
              <div className="absolute bottom-6 left-6">
                <MusicCanvas notes={state.music_frame.notes} />
              </div>
            )}

            {state?.music_frame?.chord !== undefined && (
              <div className="absolute top-4 right-6 text-sm opacity-70 bg-black/40 px-3 py-1 rounded-lg">
                Chord: {CHORDS[state.music_frame.chord]}
              </div>
            )}

          </div>
        </div>
        <InsightPanel art={state?.art} />
      </div>
      <PromptBar />
    </div>
  );
}