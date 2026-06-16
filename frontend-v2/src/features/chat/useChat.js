// src/features/chat/useChat.js
// Feature hook — thin wrapper around useChatStore for components
// that only need the send/hydrate verbs. Keeps components clean.

import { useChatStore } from "@/store/useChatStore";
import { useUserStore } from "@/store/useUserStore";

export function useChat() {
  const messages = useChatStore((s) => s.messages);
  const isSending = useChatStore((s) => s.isSending);
  const error = useChatStore((s) => s.error);
  const mode = useChatStore((s) => s.mode);
  const setMode = useChatStore((s) => s.setMode);
  const send = useChatStore((s) => s.send);
  const clear = useChatStore((s) => s.clear);
  const hydrate = useChatStore((s) => s.hydrateHistory);

  const userId = useUserStore((s) => s.user?.id);

  return {
    messages,
    isSending,
    error,
    mode,
    setMode,
    clear,
    send: (text) => send(userId, text),
    hydrate: () => hydrate(userId),
  };
}
