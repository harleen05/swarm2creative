import { useState, useEffect, useRef } from "react";
import TopBar from "../components/TopBar";
import SmartDock from "../components/SmartDock";
import InsightPanel from "../components/InsightPanel";
import ArtCanvas from "../canvas/ArtCanvas";
import MusicCanvas from "../canvas/MusicCanvas";
import ArtPanel from "../panels/ArtPanel";
import MusicPanel from "../panels/MusicPanel";
import { AnimatePresence } from "framer-motion";
import { playNotes } from "../audio/MusicEngine";
import ArchitecturePanel from "../panels/ArchitecturePanel";
import ArchitectureCanvas from "../canvas/ArchitectureCanvas";
import StoryPanel from "../panels/StoryPanel";
import StoryCanvas from "../canvas/StoryCanvas";
import { useBackendState } from "../hooks/useBackendState";
import { useWebSocket } from "../hooks/useWebSocket";

const CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

export default function Dashboard() {
  // Use WebSocket for real-time updates, fallback to REST API for initial state
  const wsState = useWebSocket();
  const { state: restState, refresh } = useBackendState();
  // Prefer WebSocket state if available, otherwise use REST state
  const state = wsState || restState;
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

  useEffect(() => {
    // Console log removed for cleaner prod builds
  }, [state]);

  return (
    <div className="h-screen w-screen flex flex-col relative overflow-hidden">
      <TopBar />

      <div className="flex flex-1 min-h-0 relative overflow-hidden">

        {/* Left Section: Dock + Active Panel */}
        <div className="flex h-full shrink-0 z-30 shadow-2xl shadow-black/20">
          <SmartDock
            active={activePanel}
            setActive={(panel) =>
              setActivePanel(prev => (prev === panel ? null : panel))
            }
          />
          <div className="relative h-full">
            <AnimatePresence mode="wait">
              {activePanel === "art" && <ArtPanel key="art" />}
              {activePanel === "music" && <MusicPanel key="music" />}
              {activePanel === "architecture" && (
                <ArchitecturePanel key="architecture" />
              )}
              {activePanel === "story" && (
                <StoryPanel story={state?.story_frame} />
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Center: Canvas Area */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-10 min-w-0 relative z-0">
          <div className="relative w-full h-full max-w-7xl bg-glass-heavy rounded-[2rem] border border-white/10 shadow-2xl overflow-hidden backdrop-blur-2xl">
            {activePanel === "architecture" ? (
              <ArchitectureCanvas frame={state?.architecture ?? null} />
            ) : activePanel === "music" ? (
              <MusicCanvas
                notes={state?.music_frame?.notes || []}
                chord={state?.music_frame?.chord}
              />
            ) : activePanel === "story" ? (
              <StoryCanvas frame={state?.story_frame} />
            ) : (
              <ArtCanvas
                artFrame={state?.art_frame}
                onCaptureReady={setCaptureFn}
              />
            )}

            {activePanel === "music" &&
              state?.music_frame?.chord !== undefined && (
                <div className="absolute top-6 right-8 text-sm font-medium text-white/80 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-lg">
                  Chord: <span className="text-violet-300 ml-1 font-mono">{CHORDS[state.music_frame.chord]}</span>
                </div>
              )}
          </div>
        </div>

        {/* Right: Insight Panel */}
        <InsightPanel
          artMeta={state?.art_frame?.meta}
          architecture={state?.architecture}
          musicFrame={state?.music_frame}
        />
      </div>
    </div>
  );
}