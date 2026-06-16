// src/components/goals/GoalList.jsx
// Goals view — LIVE. Full CRUD against /goals via useGoalStore.
// Mirrors the TaskList visual language: glass card, arc-free list,
// add composer at the bottom.

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Target, Check, Trash2, Plus, CalendarDays } from "lucide-react";
import { useGoalStore } from "@/store/useGoalStore";
import { useUserStore } from "@/store/useUserStore";

function GoalItem({ goal, onComplete, onDelete }) {
  const done = Boolean(goal.is_completed);
  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -10 }}
      className="group flex items-center gap-3 py-2.5 border-b border-white/5 last:border-0"
    >
      <button
        onClick={() => !done && onComplete(goal)}
        disabled={done}
        aria-label={done ? "Completed" : "Mark complete"}
        className={`w-5 h-5 rounded-full grid place-items-center shrink-0 border transition-all ${
          done
            ? "bg-aura-mint/20 border-aura-mint/50 text-aura-mint"
            : "border-white/20 text-transparent hover:border-aura-accent hover:text-aura-accent/60"
        }`}
      >
        <Check size={11} strokeWidth={3} />
      </button>

      <div className="flex-1 min-w-0">
        <p
          className={`text-xs leading-snug truncate ${
            done ? "text-aura-muted line-through" : "text-aura-ink"
          }`}
        >
          {goal.goal_text}
        </p>
        <div className="flex items-center gap-3 mt-0.5">
          {goal.deadline && (
            <span className="flex items-center gap-1 text-[10px] text-aura-muted">
              <CalendarDays size={10} /> {goal.deadline}
            </span>
          )}
          <span className="text-[10px] text-aura-accentSoft">
            {done ? 100 : (goal.progress ?? 0)}%
          </span>
        </div>
      </div>

      <button
        onClick={() => onDelete(goal)}
        aria-label="Delete goal"
        className="opacity-0 group-hover:opacity-100 text-aura-muted hover:text-red-400 transition-opacity"
      >
        <Trash2 size={13} />
      </button>
    </motion.li>
  );
}

export function GoalList() {
  const userId = useUserStore((s) => s.user.id);
  const goals = useGoalStore((s) => s.goals);
  const isLoading = useGoalStore((s) => s.isLoading);
  const loadGoals = useGoalStore((s) => s.loadGoals);
  const addGoal = useGoalStore((s) => s.addGoal);
  const markComplete = useGoalStore((s) => s.markComplete);
  const deleteGoal = useGoalStore((s) => s.deleteGoal);

  const [draft, setDraft] = useState("");
  const [deadline, setDeadline] = useState("");

  useEffect(() => {
    if (userId) loadGoals(userId);
  }, [userId, loadGoals]);

  const onAdd = () => {
    const text = draft.trim();
    if (!text) return;
    addGoal(userId, text, deadline || undefined);
    setDraft("");
    setDeadline("");
  };

  const active = goals.filter((g) => !g.is_completed);
  const completed = goals.filter((g) => g.is_completed);

  return (
    <div
      className="rounded-2xl p-5"
      style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div
          className="w-7 h-7 rounded-xl grid place-items-center"
          style={{ background: "rgba(46,168,255,0.15)" }}
        >
          <Target size={14} className="text-aura-accent" strokeWidth={2} />
        </div>
        <div>
          <p className="text-[10px] tracking-[0.22em] text-aura-muted uppercase font-semibold">
            Goals
          </p>
          <p className="text-xs text-aura-soft">
            {active.length} active · {completed.length} done
          </p>
        </div>
      </div>

      {/* List */}
      <ul>
        <AnimatePresence initial={false}>
          {goals.length === 0 && !isLoading && (
            <li className="py-3 text-xs text-aura-muted">
              No goals yet — what are you building toward?
            </li>
          )}
          {[...active, ...completed].map((g) => (
            <GoalItem
              key={g.id}
              goal={g}
              onComplete={(goal) => markComplete(userId, goal.id)}
              onDelete={(goal) => deleteGoal(userId, goal.id)}
            />
          ))}
        </AnimatePresence>
      </ul>

      {/* Composer */}
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onAdd()}
            placeholder="New goal…"
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs text-aura-ink placeholder:text-aura-muted outline-none focus:border-aura-accent/50"
          />
          <button
            onClick={onAdd}
            aria-label="Add goal"
            className="w-8 h-8 rounded-xl grid place-items-center bg-aura-accent/20 border border-aura-accent/40 text-aura-accentSoft hover:bg-aura-accent/30 transition-colors"
          >
            <Plus size={14} strokeWidth={2.5} />
          </button>
        </div>
        <input
          type="date"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-[11px] text-aura-soft outline-none focus:border-aura-accent/50 [color-scheme:dark]"
        />
      </div>
    </div>
  );
}

export default GoalList;
