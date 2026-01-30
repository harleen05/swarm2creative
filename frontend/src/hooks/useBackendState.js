import { useEffect, useState } from "react";
import { HTTP_BASE } from "../configs/api";

export function useBackendState() {
  const [state, setState] = useState(null);

  const fetchState = async () => {
    try {
      const res = await fetch(`${HTTP_BASE}/state`);
      const json = await res.json();
      setState(json);
    } catch (e) {
      console.error("Failed to fetch state", e);
    }
  };
  useEffect(() => {
    fetchState();
  }, []);
  return { state, refresh: fetchState };
}