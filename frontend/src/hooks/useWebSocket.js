import { useEffect, useState } from "react";

export function useWebSocket(url) {
  const [state, setState] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
      setState(JSON.parse(event.data));
    };

    return () => ws.close();
  }, [url]);

  return state;
}