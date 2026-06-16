// src/store/useGoalStore.js
// ------------------------------------------------------------
// Goals store. Backed by FastAPI /goals endpoints.
// Same optimistic-update pattern as useTaskStore.
// ------------------------------------------------------------

import { create } from "zustand";
import {
  fetchGoals,
  createGoal,
  completeGoal,
  removeGoal,
} from "@/services/goalService";

export const useGoalStore = create((set, get) => ({
  // ---- state ----
  goals: [],
  isLoading: false,
  error: null,

  // ---- actions ----
  loadGoals: async (userId) => {
    set({ isLoading: true, error: null });
    try {
      const goals = await fetchGoals(userId);
      set({ goals, isLoading: false });
    } catch (err) {
      set({ error: err.message, isLoading: false, goals: [] });
    }
  },

  addGoal: async (userId, goal_text, deadline) => {
    const temp = {
      id: `temp-${Date.now()}`,
      user_id: userId,
      goal_text,
      deadline: deadline ?? null,
      progress: 0,
      is_completed: 0,
      created_at: new Date().toISOString(),
      __optimistic: true,
    };
    set({ goals: [...get().goals, temp] });
    try {
      await createGoal(userId, goal_text, deadline);
      await get().loadGoals(userId);
    } catch (err) {
      set({
        goals: get().goals.filter((g) => g.id !== temp.id),
        error: err.message,
      });
    }
  },

  markComplete: async (userId, goalId) => {
    set({
      goals: get().goals.map((g) =>
        g.id === goalId ? { ...g, is_completed: 1, progress: 100 } : g,
      ),
    });
    try {
      await completeGoal(userId, goalId);
    } catch (err) {
      set({
        goals: get().goals.map((g) =>
          g.id === goalId ? { ...g, is_completed: 0 } : g,
        ),
        error: err.message,
      });
    }
  },

  deleteGoal: async (userId, goalId) => {
    const snapshot = get().goals;
    set({ goals: snapshot.filter((g) => g.id !== goalId) });
    try {
      await removeGoal(userId, goalId);
    } catch (err) {
      set({ goals: snapshot, error: err.message });
    }
  },

  clearError: () => set({ error: null }),
}));
