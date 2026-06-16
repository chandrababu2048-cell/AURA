// electron/preload.js
// ============================================================
// IPC bridge — contextIsolation-safe.
// Exposes window.electronAPI to the renderer.
//
// Security model:
//   contextIsolation: true  — renderer JS runs in a separate V8 context
//   nodeIntegration: false  — renderer has no access to Node APIs
//   Only these whitelisted channels are exposed.
// ============================================================

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  // ── main → renderer ────────────────────────────────────────
  // Called when the main window hides and the orb escapes to desktop
  onOrbMode: (callback) => {
    ipcRenderer.on("orb-mode", (_event, value) => callback(value));
  },

  // Called when the main window is shown again (orb returned home)
  onReturnHome: (callback) => {
    ipcRenderer.on("return-home", (_event, value) => callback(value));
  },

  // ── renderer → main ────────────────────────────────────────
  // Roaming orb clicked — restore main window
  openMainWindow: () => {
    ipcRenderer.send("open-main-window");
  },

  // Renderer wants to minimize itself to orb mode
  minimizeToOrb: () => {
    ipcRenderer.send("minimize-to-orb");
  },

  // ── cleanup helpers ────────────────────────────────────────
  // Remove listeners to avoid leaks on re-mount
  removeOrbModeListener: () => {
    ipcRenderer.removeAllListeners("orb-mode");
  },

  removeReturnHomeListener: () => {
    ipcRenderer.removeAllListeners("return-home");
  },
});
