// src/store/useChatStore.js
// ------------------------------------------------------------
// Chat state. Optimistic user messages, API-driven AI replies.
// Shape of a message:
//   { id, role: 'user' | 'assistant', content: string, ts: number }
// ------------------------------------------------------------

import { create } from "zustand";
import { sendMessage, fetchRecentMessages } from "@/services/chatService";
import { useAuraStore } from "@/store/useAuraStore";

const makeId = () =>
  `m-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

const seed = [
  {
    id: makeId(),
    role: "assistant",
    content:
      "Good morning, Boss. Systems online. Tell me where to point the attention today.",
    ts: Date.now(),
  },
];

export const useChatStore = create((set, get) => ({
  // ---- state ----
  messages: seed,
  isSending: false,
  error: null,
  mode: "Personal", // Personal | Pro | Hybrid

  // ---- actions ----
  setMode: (mode) => set({ mode }),

  hydrateHistory: async (userId, limit = 20) => {
    try {
      const rows = await fetchRecentMessages(userId, limit);
      if (!rows?.length) return;
      const hydrated = rows.map((r) => ({
        id: `db-${r.id}`,
        role: r.role,
        content: r.message,
        ts: new Date(r.created_at).getTime(),
      }));
      set({ messages: hydrated });
    } catch (err) {
      // non-fatal — keep seed and log
      console.warn("hydrateHistory failed:", err.message);
    }
  },

  send: async (userId, text) => {
    const trimmed = text?.trim();
    if (!trimmed) return;

    const userMsg = {
      id: makeId(),
      role: "user",
      content: trimmed,
      ts: Date.now(),
    };
    // optimistic push + flip avatar to thinking
    set({
      messages: [...get().messages, userMsg],
      isSending: true,
      error: null,
    });
    useAuraStore.getState().setState("thinking");

    try {
      const reply = await sendMessage(userId, trimmed, get().mode);
      const aiMsg = {
        id: makeId(),
        role: "assistant",
        content: reply,
        ts: Date.now(),
      };
      set({ messages: [...get().messages, aiMsg], isSending: false });
      useAuraStore.getState().pulseSpeaking();
    } catch (err) {
      const aiMsg = {
        id: makeId(),
        role: "assistant",
        content:
          "I'm having trouble connecting to the brain right now, Boss. Want me to try again in a bit?",
        ts: Date.now(),
      };
      set({
        messages: [...get().messages, aiMsg],
        isSending: false,
        error: err.message,
      });
      useAuraStore.getState().setState("idle");
    }
  },

  clear: () => set({ messages: seed, error: null, isSending: false }),
}));
