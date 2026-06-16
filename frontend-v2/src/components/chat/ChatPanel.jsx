// src/components/chat/ChatPanel.jsx
// Right panel — conversation list + composer.

import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Clock,
  Bookmark,
  Volume2,
  RefreshCw,
  Sparkles,
  MoreHorizontal,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { useChatStore } from "@/store/useChatStore";
import { useUserStore } from "@/store/useUserStore";

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex items-center gap-2 px-3 py-2 glass-inner text-aura-muted w-fit"
    >
      {[0, 0.15, 0.3].map((d) => (
        <motion.span
          key={d}
          className="w-1.5 h-1.5 rounded-full bg-aura-accent"
          animate={{ y: [0, -3, 0] }}
          transition={{ duration: 0.9, repeat: Infinity, delay: d }}
        />
      ))}
    </motion.div>
  );
}

export function ChatPanel() {
  const messages = useChatStore((s) => s.messages);
  const isSending = useChatStore((s) => s.isSending);
  const hydrate = useChatStore((s) => s.hydrateHistory);
  const send = useChatStore((s) => s.send);
  const aiName = useUserStore((s) => s.user?.ai_name ?? "AURA");
  const userId = useUserStore((s) => s.user?.id);

  const scrollRef = useRef(null);

  useEffect(() => {
    if (userId) hydrate(userId);
  }, [userId, hydrate]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, isSending]);

  return (
    <GlassCard grid className="h-full overflow-hidden flex flex-col">
      {/* header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-[10px] tracking-[0.28em] font-semibold text-aura-muted uppercase">
            Chat with {aiName}
          </span>
        </div>
        <MoreHorizontal
          size={18}
          className="text-aura-muted cursor-pointer hover:text-aura-ink"
        />
      </div>

      {/* messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto aura-scroll px-4 py-4 space-y-4"
      >
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} />
          ))}
          {isSending && (
            <motion.div
              key="typing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <TypingIndicator />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* composer */}
      <div className="px-4 pb-4 space-y-3">
        <ChatInput
          disabled={isSending}
          onSend={(text) => send(userId, text)}
        />
        <div className="flex items-center justify-between px-2 text-aura-muted">
          <div className="flex items-center gap-4">
            <Clock size={14} className="hover:text-aura-ink cursor-pointer" />
            <Bookmark
              size={14}
              className="hover:text-aura-ink cursor-pointer"
            />
            <Volume2
              size={14}
              className="hover:text-aura-ink cursor-pointer"
            />
            <RefreshCw
              size={14}
              className="hover:text-aura-ink cursor-pointer"
            />
          </div>
          <Sparkles size={14} className="text-aura-accent" />
        </div>
      </div>
    </GlassCard>
  );
}

export default ChatPanel;
