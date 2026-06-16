// src/components/dashboard/WeeklyProgress.jsx
// Weekly goal card — LIVE. Reads the goal list from useGoalStore
// (loaded by HomeView) and shows the first active goal's progress.
// Falls back gracefully when there are no goals yet.

import { useGoalStore } from "@/store/useGoalStore";

export function WeeklyProgress() {
  const goals = useGoalStore((s) => s.goals);

  const active = goals.find((g) => !g.is_completed);
  const total = goals.length;
  const done = goals.filter((g) => g.is_completed).length;

  // Active goal → its own progress. No active but some done → 100%.
  // No goals at all → empty state.
  const value = active ? (active.progress ?? 0) : total > 0 ? 100 : 0;
  const label = active
    ? active.goal_text
    : total > 0
      ? `All ${done} goal${done > 1 ? "s" : ""} complete`
      : "No active goals — set one in Goals";

  return (
    <div
      className="rounded-2xl p-5"
      style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
    >
      <p className="text-[10px] tracking-[0.22em] text-aura-muted uppercase font-semibold mb-3">
        Weekly Goal
      </p>

      <div className="flex items-end justify-between mb-3">
        <div>
          <span className="text-4xl font-display font-bold text-aura-ink leading-none">
            {value}
          </span>
          <span className="text-lg text-aura-muted font-display ml-0.5">%</span>
        </div>
        <p className="text-xs text-aura-soft text-right max-w-[120px] leading-relaxed">
          {label}
        </p>
      </div>

      {/* Full-width progress bar */}
      <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${value}%`,
            background: "linear-gradient(90deg, #1A78D2, #2EA8FF)",
            boxShadow: "0 0 12px rgba(46,168,255,0.5)",
          }}
        />
      </div>
    </div>
  );
}

export default WeeklyProgress;
