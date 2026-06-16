// src/components/dashboard/SkillLevel.jsx

import { motion } from "framer-motion";

export function SkillLevel({ area = "Backend", level = "Advanced" }) {
  return (
    <div
      className="rounded-2xl p-4 flex-1"
      style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
    >
      <p className="text-[10px] tracking-[0.22em] text-aura-muted uppercase font-semibold mb-2">
        Skill
      </p>
      <p className="text-xs text-aura-soft mb-1">{area}</p>
      <p className="text-xl font-display font-bold text-aura-accentSoft mb-2">
        {level}
      </p>
      <motion.svg
        width="100%" height="28"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <defs>
          <linearGradient id="skillGrad2" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#8FF0D1" />
            <stop offset="100%" stopColor="#2EA8FF" />
          </linearGradient>
        </defs>
        <motion.path
          d="M0 24 Q 20 18 40 20 T 80 12 T 120 4"
          stroke="url(#skillGrad2)"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.4, ease: "easeOut" }}
        />
      </motion.svg>
    </div>
  );
}

export default SkillLevel;
