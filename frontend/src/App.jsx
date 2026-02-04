import { useState } from "react";
import Dashboard from "./app/Dashboard";
import LandingPage from "./app/LandingPage";

export default function App() {
  const [showLanding, setShowLanding] = useState(true);

  if (showLanding) {
    return <LandingPage onEnter={() => setShowLanding(false)} />;
  }

  return <Dashboard />;
}