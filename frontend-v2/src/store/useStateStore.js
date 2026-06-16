// src/store/useStateStore.js
// ------------------------------------------------------------
// Boss state (Digital Twin snapshot) from GET /state.
// Powers Focus / Boss State / Recommendation cards.
//
// focusScore is DERIVED client-side from real twin data:
//   base by stress  → low: 85, medium: 55, high: 30
//   minus 3 points per overdue task (floor 5)
// Not a measurement — an honest heuristic until the Cognitive
// Drag Engine (governor.py) ships a real Cd score.
// ------------------------------------------------------------

import { create } from "zustand";
import { fetchBossState } from "@/services/stateService";

const STRESS_BASE = { low: 85, medium: 55, high: 30 };

function deriveFocusScore(s) {
  const base = STRESS_BASE[s.stress] ?? 50;
  return Math.max(5, base - (s.overdue_tasks ?? 0) * 3);
}

function deriveRecommendation(s) {
  if ((s.overdue_tasks ?? 0) > 0) {
    return {
      title: "Clear the backlog first",
      window: `${s.overdue_tasks} overdue task${s.overdue_tasks > 1 ? "s" : ""}`,
      subtitle: "Knock these out before starting new work — your focus will thank you.",
    };
  }
  if (s.stress === "high") {
    return {
      title: "Take a lighter day",
      window: "Short sessions",
      subtitle: "Stress is high. Small wins, frequent breaks, no new commitments.",
    };
  }
  return {
    title: "Best time for deep work",
    window: "7:00 PM – 10:00 PM",
    subtitle: "You're most productive during this window today.",
  };
}

export const useStateStore = create((set) => ({
  // ---- state ----
  bossState: null, // { stress, mood, energy, focus, active_goals, overdue_tasks }
  focusScore: null,
  recommendation: null,
  isLoading: false,
  error: null,

  // ---- actions ----
  loadState: async (userId) => {
    set({ isLoading: true, error: null });
    try {
      const bossState = await fetchBossState(userId);
      set({
        bossState,
        focusScore: deriveFocusScore(bossState),
        recommendation: deriveRecommendation(bossState),
        isLoading: false,
      });
    } catch (err) {
      set({ error: err.message, isLoading: false });
    }
  },
}));
