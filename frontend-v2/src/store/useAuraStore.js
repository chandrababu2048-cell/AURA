// src/store/useAuraStore.js
// ------------------------------------------------------------
// Aura avatar state machine + positioning. Drives AuraOrb.
//
// States:
//   idle      → calm float, soft pulse
//   thinking  → stronger glow, faster pulse, particle acceleration
//   speaking  → rippling outline, brief amplitude burst
//   roaming   → orb leaves center panel and floats freely on screen
//
// The store exposes `position` so AuraOrb can render in a global
// portal/mount with absolute coordinates in roaming mode while
// still being able to render inside the center panel in anchored
// mode. This keeps one source of truth for where the orb is.
// ------------------------------------------------------------

import { create } from "zustand";

const SPEAKING_FLASH_MS = 2200;

export const useAuraStore = create((set, get) => ({
  // ---- state ----
  state: "idle", // 'idle' | 'thinking' | 'speaking' | 'roaming'
  anchored: true, // when true, orb renders inside the center panel layout
  position: { x: 0, y: 0 }, // screen-absolute offset used in roaming mode
  intensity: 1, // 0..2 scale multiplier for glow/particles

  // ---- setters ----
  setState: (next) => set({ state: next }),

  setAnchored: (anchored) => set({ anchored }),

  setPosition: (x, y) => set({ position: { x, y } }),

  setIntensity: (intensity) => set({ intensity }),

  // ---- high-level helpers ----
  pulseSpeaking: () => {
    set({ state: "speaking" });
    setTimeout(() => {
      // only return to idle if we weren't interrupted
      if (get().state === "speaking") set({ state: "idle" });
    }, SPEAKING_FLASH_MS);
  },

  // Unanchor the orb and let it roam the whole viewport.
  // Components can listen to `anchored` + `state === 'roaming'` and
  // render the orb inside a global portal layer sitting above the UI.
  enterRoamingMode: () =>
    set({
      anchored: false,
      state: "roaming",
    }),

  exitRoamingMode: () =>
    set({
      anchored: true,
      state: "idle",
      position: { x: 0, y: 0 },
    }),
}));
