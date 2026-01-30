import { useState, useEffect, useRef } from "react";
import TopBar from "../components/TopBar";
import SmartDock from "../components/SmartDock";
import InsightPanel from "../components/InsightPanel";
import ArtCanvas from "../canvas/ArtCanvas";
import MusicCanvas from "../canvas/MusicCanvas";
import ArtPanel from "../panels/ArtPanel";
import MusicPanel from "../panels/MusicPanel";
import { AnimatePresence } from "framer-motion";
import PromptBar from "../components/PromptBar";
import { playNotes } from "../audio/MusicEngine";
import ArchitecturePanel from "../panels/ArchitecturePanel";
import ArchitectureCanvas from "../canvas/ArchitectureCanvas";
import StoryPanel from "../panels/StoryPanel";
import StoryCanvas from "../canvas/StoryCanvas";
import {useBackendState} from "../hooks/useBackendState";

const CHORDS = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];

export default function Dashboard() {
  const { state, refresh } = useBackendState();
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
    console.log("FULL WS STATE:", state);
  }, [state]);
  
  return (
    <div className="h-screen flex flex-col relative">
      <TopBar />

      <div className="flex flex-1 overflow-hidden relative">

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
            {activePanel === "architecture" && (
              <ArchitecturePanel key="architecture" />
            )}
            {activePanel === "story" && (
              <StoryPanel story={state?.story_frame} />
            )}
          </AnimatePresence>
        </div>

        <div className="flex-1 flex items-center justify-center px-16">
          <div className="relative" style={{ width: 800, height: 600 }}>
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
                <div className="absolute top-4 right-6 text-sm opacity-70 bg-black/40 px-3 py-1 rounded-lg">
                  Chord: {CHORDS[state.music_frame.chord]}
                </div>
              )}
          </div>
        </div>
        <InsightPanel
          artMeta={state?.art_frame?.meta}
          architecture={state?.architecture}
          musicFrame={state?.music_frame}
        />
      </div>
      <PromptBar />
    </div>
  );
}