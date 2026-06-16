// src/components/chat/ChatInput.jsx
// Chat composer at the bottom of the right panel.

import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend?.(text);
    setValue("");
  };

  return (
    <div className="glass-inner-pill flex items-center gap-2 pl-4 pr-2 py-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder="Type your message..."
        className="flex-1 bg-transparent outline-none text-sm text-aura-ink placeholder:text-aura-muted"
        disabled={disabled}
      />
      <Button
        variant="circle"
        className="!w-9 !h-9"
        onClick={submit}
        aria-label="Send"
      >
        <Send size={16} strokeWidth={2} />
      </Button>
    </div>
  );
}

export default ChatInput;
