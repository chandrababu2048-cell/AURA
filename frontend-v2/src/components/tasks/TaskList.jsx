// src/components/tasks/TaskList.jsx

import { useEffect, useMemo } from "react";
import { AnimatePresence } from "framer-motion";
import { TaskItem } from "./TaskItem";
import { useTaskStore } from "@/store/useTaskStore";
import { useUserStore } from "@/store/useUserStore";

export function TaskList() {
  const userId = useUserStore((s) => s.user.id);
  const tasks = useTaskStore((s) => s.tasks);
  const isLoading = useTaskStore((s) => s.isLoading);
  const loadTasks = useTaskStore((s) => s.loadTasks);
  const toggleTask = useTaskStore((s) => s.toggleTask);

  useEffect(() => {
    if (userId) loadTasks(userId);
  }, [userId, loadTasks]);

  const { done, total } = useMemo(() => {
    const d = tasks.filter((t) => t.is_done).length;
    return { done: d, total: tasks.length };
  }, [tasks]);

  return (
    <div
      className="rounded-2xl p-5"
      style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-[10px] tracking-[0.22em] text-aura-muted uppercase font-semibold mb-1">
            Today
          </p>
          <div className="flex items-baseline gap-1.5">
            <span className="text-4xl font-display font-bold text-aura-ink leading-none">
              {done}
            </span>
            <span className="text-lg text-aura-muted font-display">/ {total || 0}</span>
          </div>
          <p className="text-xs text-aura-soft mt-1">tasks complete</p>
        </div>

        {/* Mini arc progress */}
        <div className="relative w-14 h-14">
          <svg viewBox="0 0 56 56" className="w-full h-full -rotate-90">
            <circle cx="28" cy="28" r="22" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
            <circle
              cx="28" cy="28" r="22"
              fill="none"
              stroke="#2EA8FF"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 22}`}
              strokeDashoffset={`${2 * Math.PI * 22 * (1 - (total ? done / total : 0))}`}
              style={{ transition: "stroke-dashoffset 0.6s ease" }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-[11px] font-semibold text-aura-accentSoft">
              {total ? Math.round((done / total) * 100) : 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-white/5 mb-3" />

      {/* Task list */}
      <ul>
        <AnimatePresence initial={false}>
          {tasks.length === 0 && !isLoading && (
            <li className="py-3 text-xs text-aura-muted">
              {isLoading ? "Syncing…" : "No tasks yet — tell Symbite what you're working on."}
            </li>
          )}
          {tasks.map((t) => (
            <TaskItem
              key={t.id}
              task={t}
              onToggle={(task) => toggleTask(userId, task.id)}
            />
          ))}
        </AnimatePresence>
      </ul>
    </div>
  );
}

export default TaskList;
