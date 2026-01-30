import { useEffect, useState } from "react";
import { API_BASE, WS_BASE } from "../config/api";

export function useWebSocket() {
  const [state, setState] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws`);

    ws.onmessage = (event) => {
      setState(JSON.parse(event.data));
    };

    ws.onerror = (e) => {
      console.error("WebSocket error", e);
    };

    ws.onclose = () => {
      console.warn("WebSocket closed");
    };

    return () => ws.close();
  }, []);
  return state;
}