// src/components/ui/ProgressBar.jsx
// Horizontal progress bar with smooth width transition.

import clsx from "clsx";
import { motion } from "framer-motion";

export function ProgressBar({ value = 0, max = 100, className }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div
      className={clsx(
        "relative h-2 w-full overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10",
        className,
      )}
    >
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ type: "spring", stiffness: 90, damping: 18 }}
        className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-aura-accentSoft via-aura-accent to-aura-accentDeep shadow-[0_0_18px_rgba(46,168,255,0.45)]"
      />
    </div>
  );
}

export function CircularProgress({ value = 0, max = 100, size = 44 }) {
  const pct = Math.max(0, Math.min(1, value / max));
  const stroke = 4;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="transparent"
        stroke="rgba(180, 210, 255, 0.15)"
        strokeWidth={stroke}
      />
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="transparent"
        stroke="url(#auraGradient)"
        strokeWidth={stroke}
        strokeLinecap="round"
        initial={{ strokeDasharray: `0 ${c}` }}
        animate={{ strokeDasharray: `${c * pct} ${c}` }}
        transition={{ type: "spring", stiffness: 80, damping: 20 }}
      />
      <defs>
        <linearGradient id="auraGradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#7DC8FF" />
          <stop offset="100%" stopColor="#1A78D2" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default ProgressBar;
