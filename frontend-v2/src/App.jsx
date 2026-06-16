// src/App.jsx
// App shell. Renders the Dashboard and mounts the roaming layer
// so the Aura orb can float across the whole viewport when
// `anchored` is flipped off in useAuraStore.
//
// Electron IPC wiring:
//   onOrbMode    → enterRoamingMode()  (main window hiding, orb escapes)
//   onReturnHome → exitRoamingMode()   (main window showing again)

import { useEffect } from "react";
import Dashboard from "@/pages/Dashboard";
import Login from "@/pages/Login";
import { AuraOrbRoamingLayer } from "@/components/aura/AuraOrb";
import { useAuraStore } from "@/store/useAuraStore";
import { useUserStore } from "@/store/useUserStore";

export default function App() {
  const enterRoamingMode = useAuraStore((s) => s.enterRoamingMode);
  const exitRoamingMode = useAuraStore((s) => s.exitRoamingMode);
  const isAuthenticated = useUserStore((s) => s.isAuthenticated);

  useEffect(() => {
    // Only wire IPC when running inside Electron (window.electronAPI is
    // injected by the preload script — it doesn't exist in the browser).
    if (!window.electronAPI) return;

    // Main process is hiding this window → enter roaming state so
    // the CenterPanel shows "Roaming…" and AuraOrbRoamingLayer doesn't
    // try to render the orb in-panel.
    window.electronAPI.onOrbMode(() => {
      enterRoamingMode();
    });

    // Main process is showing this window again → restore anchored orb.
    window.electronAPI.onReturnHome(() => {
      exitRoamingMode();
    });

    // Cleanup IPC listeners when this component unmounts.
    return () => {
      window.electronAPI.removeOrbModeListener();
      window.electronAPI.removeReturnHomeListener();
    };
  }, [enterRoamingMode, exitRoamingMode]);

  // Gate: no user session → glass login screen.
  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <>
      <Dashboard />
      <AuraOrbRoamingLayer />
    </>
  );
}
