// src/components/dashboard/Recommendation.jsx
// Symbite Recommends card — LIVE. Recommendation is derived in
// useStateStore from the Digital Twin snapshot: overdue tasks →
// clear backlog; high stress → lighter day; else deep-work window.

import { Zap } from "lucide-react";
import { useStateStore } from "@/store/useStateStore";

const FALLBACK = {
  title: "Best time for deep work",
  window: "7:00 PM – 10:00 PM",
  subtitle: "You're most productive during this window today.",
};

export function Recommendation() {
  const rec = useStateStore((s) => s.recommendation) ?? FALLBACK;

  return (
    <div
      className="rounded-2xl p-5"
      style={{
        background: "linear-gradient(135deg, rgba(46,168,255,0.08), rgba(10,22,40,0.6))",
        border: "1px solid rgba(46,168,255,0.18)",
      }}
    >
      <div className="flex items-center gap-2 mb-3">
        <div
          className="w-7 h-7 rounded-xl grid place-items-center"
          style={{ background: "rgba(46,168,255,0.15)" }}
        >
          <Zap size={14} className="text-aura-accent" strokeWidth={2} />
        </div>
        <p className="text-[10px] tracking-[0.22em] text-aura-accent uppercase font-semibold">
          Symbite Recommends
        </p>
      </div>

      <p className="text-xs text-aura-soft mb-1">{rec.title}</p>
      <p className="text-2xl font-display font-bold text-aura-ink leading-tight mb-1">
        {rec.window}
      </p>
      <p className="text-xs text-aura-muted leading-relaxed">{rec.subtitle}</p>
    </div>
  );
}

export default Recommendation;
