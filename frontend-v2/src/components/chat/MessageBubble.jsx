// src/components/chat/MessageBubble.jsx
// A single chat bubble. User = gradient-blue. Assistant = glass.

import clsx from "clsx";
import { motion } from "framer-motion";
import { useUserStore } from "@/store/useUserStore";

function formatTime(ts) {
  try {
    return new Date(ts).toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function AiAvatar() {
  return (
    <div className="w-7 h-7 rounded-full glass-inner-pill grid place-items-center">
      <div className="w-4 h-4 rounded-full bg-gradient-to-br from-aura-accentSoft to-aura-accentDeep shadow-glow" />
    </div>
  );
}

function UserAvatar() {
  const name = useUserStore((s) => s.user?.name ?? "B");
  return (
    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-aura-accentSoft to-aura-accentDeep grid place-items-center text-[11px] font-semibold text-white shadow-glass">
      {name?.[0]?.toUpperCase() ?? "B"}
    </div>
  );
}

export function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const aiName = useUserStore((s) => s.user?.ai_name ?? "AURA");

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        "flex items-end gap-2",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && <AiAvatar />}

      <div
        className={clsx(
          "max-w-[78%] flex flex-col",
          isUser ? "items-end" : "items-start",
        )}
      >
        <div
          className={clsx(
            "text-[11px] text-aura-muted mb-1 px-1",
            isUser && "text-right",
          )}
        >
          <span className="font-medium text-aura-ink/90">
            {isUser ? "You" : aiName}
          </span>
          <span className="mx-1 opacity-50">·</span>
          <span>{formatTime(message.ts)}</span>
        </div>

        <div
          className={clsx(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            // User = translucent accent tint (NOT a solid color —
            // matches glassmorphism language). Assistant = tint-only
            // glass-inner so the nebula shows through the panel.
            isUser
              ? "glass-accent text-white rounded-br-md"
              : "glass-inner text-aura-ink rounded-bl-md",
          )}
        >
          {message.content}
        </div>
      </div>

      {isUser && <UserAvatar />}
    </motion.div>
  );
}

export default MessageBubble;
