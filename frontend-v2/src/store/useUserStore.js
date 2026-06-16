// src/store/useUserStore.js
// ------------------------------------------------------------
// Global user state. Holds the current logged-in user profile.
// Persists the session to localStorage so a refresh doesn't log
// the Boss out. App.jsx gates Dashboard on isAuthenticated.
// ------------------------------------------------------------

import { create } from "zustand";

const STORAGE_KEY = "symbite_user";

function loadPersisted() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const user = JSON.parse(raw);
    return user?.id ? user : null;
  } catch {
    return null;
  }
}

const persisted = loadPersisted();

export const useUserStore = create((set, get) => ({
  // ---- state ----
  user: persisted, // null until login
  isAuthenticated: Boolean(persisted),

  // ---- actions ----
  setUser: (user) => {
    const merged = { ...(get().user ?? {}), ...user };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    } catch {
      /* storage unavailable — session just won't persist */
    }
    set({ user: merged, isAuthenticated: Boolean(merged?.id) });
  },

  updateAiName: (ai_name) => {
    const merged = { ...(get().user ?? {}), ai_name };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    } catch {
      /* noop */
    }
    set({ user: merged });
  },

  logout: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* noop */
    }
    set({ user: null, isAuthenticated: false });
  },

  // convenience selector
  getUserId: () => get().user?.id ?? null,
}));
