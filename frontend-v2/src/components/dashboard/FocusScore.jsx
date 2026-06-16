// src/components/dashboard/FocusScore.jsx
// Focus card — LIVE. Score is derived in useStateStore from the
// Digital Twin snapshot (GET /state): stress base minus overdue
// penalty. See useStateStore.js for the formula.

import { motion } from "framer-motion";
import { useStateStore } from "@/store/useStateStore";

function Sparkline({ points = [42, 48, 45, 58, 54, 62, 70, 66, 78, 82] }) {
  const w = 80;
  const h = 32;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 1;
  const path = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * w;
      const y = h - ((p - min) / range) * h;
      return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg width={w} height={h} className="overflow-visible opacity-70">
      <motion.path
        d={path}
        stroke="#2EA8FF"
        strokeWidth={2}
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.4, ease: "easeOut" }}
      />
    </svg>
  );
}

export function FocusScore() {
  const focusScore = useStateStore((s) => s.focusScore);
  const stress = useStateStore((s) => s.bossState?.stress);

  return (
    <div
      className="rounded-2xl p-4 flex-1"
      style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
    >
      <p className="text-[10px] tracking-[0.22em] text-aura-muted uppercase font-semibold mb-2">
        Focus
      </p>
      <div className="flex items-baseline gap-1 mb-2">
        <span className="text-4xl font-display font-bold text-aura-ink leading-none">
          {focusScore ?? "–"}
        </span>
        <span className="text-sm text-aura-muted">/100</span>
      </div>
      {stress && (
        <p className="text-[10px] text-aura-muted mb-1 capitalize">
          {stress} stress
        </p>
      )}
      <Sparkline />
    </div>
  );
}

export default FocusScore;
