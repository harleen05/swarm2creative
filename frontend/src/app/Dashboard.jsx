import { useState } from "react";
import TopBar from "../components/TopBar";
import SmartDock from "../components/SmartDock";
import InsightPanel from "../components/InsightPanel";
import ArtCanvas from "../canvas/ArtCanvas";
import { useWebSocket } from "../hooks/useWebSocket";
import ArtPanel from "../panels/ArtPanel";

export default function Dashboard() {
  const state = useWebSocket("ws://127.0.0.1:8000/ws");
  const [activePanel, setActivePanel] = useState(null);

  return (
    <div className="h-screen flex flex-col">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <div className="flex h-full">
            <SmartDock active={activePanel} setActive={setActivePanel} />
            {activePanel === "art" && <ArtPanel />}
        </div>
        <div className="flex-1 flex items-center justify-center px-16">
            <div className="w-full h-full max-w-[1100px] max-h-[800px] rounded-3xl bg-black/10 backdrop-blur-xl flex items-center justify-center">
            <ArtCanvas art={state?.art} />
            </div>
        </div>
        <InsightPanel art={state?.art} />
        </div>
    </div>
  );
}