// src/components/tasks/TaskItem.jsx

import clsx from "clsx";
import { motion } from "framer-motion";
import { Check } from "lucide-react";

export function TaskItem({ task, onToggle }) {
  const done = Boolean(task.is_done);
  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      className="flex items-center gap-3 py-2.5"
    >
      <motion.button
        whileTap={{ scale: 0.9 }}
        onClick={() => onToggle?.(task)}
        className={clsx(
          "grid place-items-center w-5 h-5 rounded-full border-2 transition-all shrink-0",
          done
            ? "bg-aura-accent border-aura-accent text-white"
            : "bg-transparent border-white/20 hover:border-aura-accentSoft",
        )}
        aria-label={done ? "Mark undone" : "Mark done"}
      >
        {done && <Check size={11} strokeWidth={3} />}
      </motion.button>
      <span
        className={clsx(
          "text-[13px] leading-tight flex-1",
          done ? "text-aura-muted line-through" : "text-aura-ink",
        )}
      >
        {task.plan_text}
      </span>
    </motion.li>
  );
}

export default TaskItem;
