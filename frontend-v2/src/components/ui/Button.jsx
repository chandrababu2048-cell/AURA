// src/components/ui/Button.jsx
// Minimal, reusable button with 3 variants:
//   primary   → filled cyan gradient (CTAs)
//   ghost     → glass pill
//   circle    → icon-only circular glass button (voice/camera/connect)

import clsx from "clsx";
import { motion } from "framer-motion";

const base =
  "inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 select-none";

// Interactive controls live INSIDE glass panels, so their surfaces
// use tint-only classes (`glass-inner-pill`) rather than stacking a
// second backdrop-filter. Same visible frost treatment, without the
// "solid card" flattening that nested blur produces.
const variants = {
  primary:
    "text-white rounded-full px-5 py-2.5 bg-gradient-to-br from-aura-accentSoft to-aura-accent shadow-glow hover:shadow-glowSoft active:scale-[0.98]",
  ghost:
    "text-aura-ink px-4 py-2 glass-inner-pill glass-inner-hover",
  circle:
    "w-14 h-14 glass-inner-pill glass-inner-hover text-aura-accentSoft ring-accent-soft active:scale-[0.96]",
  soft: "text-aura-accentSoft rounded-full px-3 py-1.5 hover:bg-white/10",
};

export function Button({
  variant = "primary",
  className,
  children,
  as = "button",
  ...rest
}) {
  const Tag = as === "button" ? motion.button : motion[as];
  return (
    <Tag
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.97 }}
      className={clsx(base, variants[variant], className)}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export default Button;
