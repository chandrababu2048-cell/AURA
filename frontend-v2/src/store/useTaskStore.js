// src/store/useTaskStore.js
// ------------------------------------------------------------
// Daily plans / tasks store. Backed by FastAPI /plans endpoints.
// Components NEVER call the API directly — they call these actions.
// ------------------------------------------------------------

import { create } from "zustand";
import {
  fetchPlans,
  createPlan,
  togglePlan,
  removePlan,
} from "@/services/taskService";

export const useTaskStore = create((set, get) => ({
  // ---- state ----
  tasks: [],
  isLoading: false,
  error: null,

  // ---- actions ----
  loadTasks: async (userId, date) => {
    set({ isLoading: true, error: null });
    try {
      const tasks = await fetchPlans(userId, date);
      set({ tasks, isLoading: false });
    } catch (err) {
      set({ error: err.message, isLoading: false, tasks: [] });
    }
  },

  addTask: async (userId, plan_text, planned_for) => {
    // optimistic insert
    const temp = {
      id: `temp-${Date.now()}`,
      user_id: userId,
      plan_text,
      planned_for: planned_for ?? new Date().toISOString().slice(0, 10),
      is_done: 0,
      created_at: new Date().toISOString(),
      __optimistic: true,
    };
    set({ tasks: [...get().tasks, temp] });

    try {
      await createPlan(userId, plan_text, planned_for);
      await get().loadTasks(userId, planned_for);
    } catch (err) {
      // rollback
      set({
        tasks: get().tasks.filter((t) => t.id !== temp.id),
        error: err.message,
      });
    }
  },

  toggleTask: async (userId, planId) => {
    // optimistic toggle
    set({
      tasks: get().tasks.map((t) =>
        t.id === planId ? { ...t, is_done: t.is_done ? 0 : 1 } : t,
      ),
    });
    try {
      await togglePlan(userId, planId);
    } catch (err) {
      // rollback on failure
      set({
        tasks: get().tasks.map((t) =>
          t.id === planId ? { ...t, is_done: t.is_done ? 0 : 1 } : t,
        ),
        error: err.message,
      });
    }
  },

  deleteTask: async (userId, planId) => {
    const snapshot = get().tasks;
    set({ tasks: snapshot.filter((t) => t.id !== planId) });
    try {
      await removePlan(userId, planId);
    } catch (err) {
      set({ tasks: snapshot, error: err.message });
    }
  },

  clearError: () => set({ error: null }),
}));
