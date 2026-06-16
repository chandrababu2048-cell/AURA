// src/features/tasks/useTasks.js
// Feature hook for task CRUD bound to the current user.

import { useTaskStore } from "@/store/useTaskStore";
import { useUserStore } from "@/store/useUserStore";

export function useTasks() {
  const userId = useUserStore((s) => s.user?.id);
  const tasks = useTaskStore((s) => s.tasks);
  const isLoading = useTaskStore((s) => s.isLoading);
  const error = useTaskStore((s) => s.error);

  return {
    tasks,
    isLoading,
    error,
    load: (date) => useTaskStore.getState().loadTasks(userId, date),
    add: (plan_text, planned_for) =>
      useTaskStore.getState().addTask(userId, plan_text, planned_for),
    toggle: (planId) =>
      useTaskStore.getState().toggleTask(userId, planId),
    remove: (planId) =>
      useTaskStore.getState().deleteTask(userId, planId),
  };
}
