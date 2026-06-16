// src/components/layout/CenterPanel.jsx
// Aura presence: orb + title + status + voice/camera/connect + ask input.

import { useState } from "react";
import { motion } from "framer-motion";
import { Mic, Camera, Link2, Command, ArrowUpRight } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { AuraOrb } from "@/components/aura/AuraOrb";
import { useAuraStore } from "@/store/useAuraStore";
import { useChatStore } from "@/store/useChatStore";
import { useUserStore } from "@/store/useUserStore";

function StatusDot() {
  return (
    <span className="relative flex h-2 w-2">
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-aura-mint/70" />
      <span className="relative inline-flex rounded-full h-2 w-2 bg-aura-mint" />
    </span>
  );
}

export function CenterPanel() {
  const anchored = useAuraStore((s) => s.anchored);
  const state = useAuraStore((s) => s.state);
  const send = useChatStore((s) => s.send);
  const userId = useUserStore((s) => s.user.id);
  const [draft, setDraft] = useState("");

  const onAsk = () => {
    if (!draft.trim()) return;
    send(userId, draft);
    setDraft("");
  };

  return (
    <GlassCard strong grid className="h-full overflow-hidden flex flex-col">
      {/* top chrome */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-white/10">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-white/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-white/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-white/20" />
        </div>
        <div className="flex items-center gap-2 text-aura-muted">
          <div className="flex items-end gap-[3px] h-4">
            {[2, 3, 4, 3, 2].map((h, i) => (
              <motion.span
                key={i}
                className="w-[3px] rounded-sm bg-aura-accent/70"
                animate={{
                  height:
                    state === "speaking" || state === "thinking"
                      ? [h * 3, h * 5, h * 3]
                      : h * 3,
                }}
                transition={{
                  duration: 0.8,
                  repeat: Infinity,
                  delay: i * 0.1,
                  ease: "easeInOut",
                }}
                style={{ height: h * 3 }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* header text */}
      <div className="text-center pt-8 pb-2">
        <h1 className="font-display text-5xl tracking-[0.42em] font-semibold bg-gradient-to-b from-white via-aura-accentSoft to-aura-accent bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(46,168,255,0.35)]">
          AURA
        </h1>
        <p className="mt-1 text-[11px] tracking-[0.34em] text-aura-soft uppercase">
          Symbiote Intelligence
        </p>
      </div>

      {/* orb area */}
      <div className="flex-1 relative grid place-items-center">
        {anchored ? (
          <AuraOrb size={300} />
        ) : (
          <p className="text-sm text-aura-muted">Roaming…</p>
        )}
      </div>

      {/* status + actions */}
      <div className="pb-6">
        <div className="flex items-center justify-center gap-2 text-xs text-aura-soft mb-5">
          <StatusDot />
          <span className="tracking-wide">
            Online <span className="mx-1 opacity-50">•</span>
            {state === "thinking" && "Thinking…"}
            {state === "speaking" && "Speaking"}
            {state === "idle" && "Ready to assist"}
            {state === "roaming" && "Roaming"}
          </span>
        </div>

        <div className="flex items-center justify-center gap-5">
          <div className="flex flex-col items-center gap-1.5">
            <Button variant="circle" aria-label="Voice">
              <Mic size={20} strokeWidth={1.8} />
            </Button>
            <span className="text-[10px] tracking-widest text-aura-muted uppercase">
              Voice
            </span>
          </div>
          <div className="flex flex-col items-center gap-1.5">
            <Button variant="circle" aria-label="Camera">
              <Camera size={20} strokeWidth={1.8} />
            </Button>
            <span className="text-[10px] tracking-widest text-aura-muted uppercase">
              Camera
            </span>
          </div>
          <div className="flex flex-col items-center gap-1.5">
            <Button variant="circle" aria-label="Connect">
              <Link2 size={20} strokeWidth={1.8} />
            </Button>
            <span className="text-[10px] tracking-widest text-aura-muted uppercase">
              Connect
            </span>
          </div>
        </div>

        {/* ask bar */}
        <div className="px-6 mt-6">
          <div className="glass-inner-pill flex items-center gap-2 pl-5 pr-2 py-2">
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onAsk()}
              placeholder="Ask Aura anything..."
              className="flex-1 bg-transparent outline-none text-sm text-aura-ink placeholder:text-aura-muted"
            />
            <span className="hidden md:inline-flex items-center gap-1 rounded-md border border-white/10 px-1.5 py-0.5 text-[10px] text-aura-muted">
              <Command size={10} /> K
            </span>
            <Button
              variant="circle"
              className="!w-9 !h-9"
              onClick={onAsk}
              aria-label="Send"
            >
              <ArrowUpRight size={16} strokeWidth={2} />
            </Button>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}

export default CenterPanel;
