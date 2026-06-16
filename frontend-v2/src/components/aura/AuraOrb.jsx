// src/components/aura/AuraOrb.jsx
// ------------------------------------------------------------
// The symbiote avatar. A liquid glowing orb.
//
// DESIGN NOTES
// - Pure SVG + CSS + Framer Motion. No external 3D lib.
// - State-driven via useAuraStore:
//     idle      → calm gentle float + soft pulse
//     thinking  → amplified glow, faster pulse, particle accel
//     speaking  → amplitude burst + ripple
//     roaming   → unanchored; parent portal positions it absolutely
//
// - The component is positioning-agnostic. It ONLY renders the orb.
//   Where it lives (inside the center panel OR as a roaming overlay)
//   is decided by its parent. Two wrappers are provided:
//     <AuraOrb />                — inline (default, for center panel)
//     <AuraOrbRoamingLayer />    — fixed, full-viewport portal
//
// This is the shape that lets you build "roaming mode" later without
// reworking any component: just flip `anchored` off and render
// <AuraOrbRoamingLayer /> once in App.jsx.
// ------------------------------------------------------------

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";
import { useAuraStore } from "@/store/useAuraStore";

// Per-state visual parameters.
const STATE_PARAMS = {
  idle: {
    glowOpacity: 0.55,
    glowScale: 1,
    floatY: [0, -8, 0],
    floatDuration: 6,
    ringScale: 1,
    particleSpeed: 1,
  },
  thinking: {
    glowOpacity: 0.95,
    glowScale: 1.12,
    floatY: [0, -4, 2, -3, 0],
    floatDuration: 3.2,
    ringScale: 1.08,
    particleSpeed: 2.2,
  },
  speaking: {
    glowOpacity: 1,
    glowScale: 1.18,
    floatY: [0, -6, 0, -4, 0],
    floatDuration: 1.8,
    ringScale: 1.14,
    particleSpeed: 2.6,
  },
  roaming: {
    glowOpacity: 0.8,
    glowScale: 1.06,
    floatY: [0, -10, 0, -12, 0],
    floatDuration: 5,
    ringScale: 1.04,
    particleSpeed: 1.6,
  },
};

export function AuraOrb({ size = 260, className }) {
  const state = useAuraStore((s) => s.state);
  const intensity = useAuraStore((s) => s.intensity);
  const params = STATE_PARAMS[state] ?? STATE_PARAMS.idle;

  // Memoize decorative particles so they don't re-random every render.
  const particles = useMemo(
    () =>
      Array.from({ length: 14 }).map((_, i) => ({
        id: i,
        angle: (i / 14) * Math.PI * 2,
        radius: 0.55 + Math.random() * 0.35,
        delay: Math.random() * 2,
        dur: 3 + Math.random() * 3,
        r: 1.5 + Math.random() * 1.8,
      })),
    [],
  );

  return (
    <motion.div
      className={clsx("relative select-none", className)}
      style={{
        width: size,
        height: size,
        // Glow Engine — the orb's light bleeds onto the grid
        // behind it, illuminating the nebula. Applied on the
        // root so the entire silhouette (halo + ring + core +
        // particles) casts one coherent glow.
        filter: "drop-shadow(0 0 40px rgba(0, 150, 255, 0.45))",
      }}
      animate={{ y: params.floatY }}
      transition={{
        duration: params.floatDuration,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      {/* Outer glow halo */}
      <motion.div
        className="absolute inset-[-40%] rounded-full"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(125,200,255,0.55) 0%, rgba(125,200,255,0.18) 35%, rgba(125,200,255,0) 65%)",
          filter: "blur(12px)",
        }}
        animate={{
          opacity: params.glowOpacity * intensity,
          scale: params.glowScale,
        }}
        transition={{ duration: 1.2, ease: "easeOut" }}
      />

      {/* Outer ring */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          border: "1px solid rgba(125,200,255,0.55)",
          boxShadow:
            "0 0 40px rgba(125,200,255,0.35), inset 0 0 40px rgba(125,200,255,0.25)",
        }}
        animate={{ scale: params.ringScale }}
        transition={{ duration: 1, ease: "easeOut" }}
      />

      {/* Particles orbiting the orb */}
      <svg
        className="absolute inset-0"
        viewBox="0 0 100 100"
        preserveAspectRatio="xMidYMid meet"
      >
        {particles.map((p) => {
          const cx = 50 + Math.cos(p.angle) * 48 * p.radius;
          const cy = 50 + Math.sin(p.angle) * 48 * p.radius;
          return (
            <motion.circle
              key={p.id}
              cx={cx}
              cy={cy}
              r={p.r}
              fill="rgba(125,200,255,0.8)"
              initial={{ opacity: 0 }}
              animate={{
                opacity: [0.2, 0.9, 0.2],
                scale: [1, 1.4, 1],
              }}
              transition={{
                duration: p.dur / params.particleSpeed,
                repeat: Infinity,
                delay: p.delay,
                ease: "easeInOut",
              }}
            />
          );
        })}
      </svg>

      {/* Core liquid orb */}
      <div className="absolute inset-[12%] rounded-full overflow-hidden">
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background:
              "radial-gradient(120% 120% at 30% 25%, #ffffff 0%, #BEE3FF 18%, #5FB7F2 45%, #1E6FB4 75%, #0B3B73 100%)",
          }}
        />
        {/* liquid highlight */}
        <motion.div
          className="absolute left-[15%] top-[12%] w-[40%] h-[28%] rounded-full"
          style={{
            background:
              "radial-gradient(circle at 40% 40%, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0) 70%)",
            filter: "blur(2px)",
          }}
          animate={{
            x: [0, 6, -3, 0],
            y: [0, 4, -2, 0],
            scale: [1, 1.05, 0.98, 1],
          }}
          transition={{
            duration: params.floatDuration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        {/* inner dark droplet that morphs */}
        <motion.div
          className="absolute left-[22%] top-[30%] w-[55%] h-[55%] rounded-full"
          style={{
            background:
              "radial-gradient(circle at 55% 45%, #1D3F75 0%, #0A1E3C 65%, #061229 100%)",
            filter: "blur(0.5px)",
          }}
          animate={{
            scale: [1, 1.04, 0.97, 1.02, 1],
            rotate: [0, 8, -4, 6, 0],
            borderRadius: [
              "50%",
              "48% 52% 55% 45% / 52% 48% 55% 45%",
              "52% 48% 46% 54% / 48% 52% 46% 54%",
              "50%",
            ],
          }}
          transition={{
            duration: params.floatDuration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      {/* Speaking ripple */}
      <AnimatePresence>
        {state === "speaking" && (
          <>
            {[0, 0.35, 0.7].map((d) => (
              <motion.div
                key={d}
                className="absolute inset-0 rounded-full"
                style={{ border: "1px solid rgba(46,168,255,0.55)" }}
                initial={{ scale: 0.9, opacity: 0.7 }}
                animate={{ scale: 1.45, opacity: 0 }}
                exit={{ opacity: 0 }}
                transition={{
                  duration: 1.6,
                  delay: d,
                  repeat: Infinity,
                  ease: "easeOut",
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ------------------------------------------------------------
// <AuraOrbRoamingLayer /> — mount this ONCE in App.jsx.
// When `anchored` is false (roaming mode), it renders a
// full-viewport, pointer-event-passthrough layer with the orb
// absolutely positioned according to useAuraStore().position.
// ------------------------------------------------------------
export function AuraOrbRoamingLayer() {
  const anchored = useAuraStore((s) => s.anchored);
  const position = useAuraStore((s) => s.position);

  if (anchored) return null;

  return (
    <div className="aura-orb-mount fixed inset-0 z-40">
      <motion.div
        className="absolute"
        initial={false}
        animate={{ x: position.x, y: position.y }}
        transition={{ type: "spring", stiffness: 40, damping: 14 }}
      >
        <AuraOrb size={200} />
      </motion.div>
    </div>
  );
}

export default AuraOrb;
