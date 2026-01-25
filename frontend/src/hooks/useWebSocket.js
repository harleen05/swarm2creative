import { useEffect, useRef, useState } from "react";

export function useWebSocket(url) {
  const wsRef = useRef(null);
  const [state, setState] = useState(null);

  useEffect(() => {
    wsRef.current = new WebSocket(url);

    wsRef.current.onmessage = (e) => {
      setState(JSON.parse(e.data));
    };

    return () => wsRef.current.close();
  }, [url]);

  return state;
}