# ============================================================
# brain.py — AURA AI Engine
# ============================================================
# PURPOSE:
#   This is where AURA thinks. It manages:
#     1. Building a rich system prompt from user context
#     2. Sending messages to Claude (Anthropic API)
#     3. Maintaining conversation history for this session
#     4. Saving every exchange to the database
#
# WHY CLAUDE (ANTHROPIC)?
#   Claude is state-of-the-art for safe, helpful, nuanced
#   conversation. It handles long context windows well — perfect
#   for injecting full user context into every prompt.
#
# HOW AURA'S MEMORY WORKS:
#   Every message to Claude includes:
#     - System prompt: who the user is, today's plans, goals, weather
#     - Full conversation history: so Claude remembers this session
#     - The new user message
#   This is called "context injection" — we make Claude feel
#   like it genuinely knows the user by feeding it real data.
#
# MODES:
#   Personal   → warm, casual, supportive (default)
#   Pro        → sharp, concise, productivity-focused
#   Hybrid     → balanced — friendly but efficient
# ============================================================

import os
from dotenv import load_dotenv
from anthropic import Anthropic
from memory import AuraMemory

load_dotenv()

class AuraBrain:
    def __init__(self, user_id: int):
        self.user_id = user_id

        # Read API key fresh at init time (not at import time).
        # On Streamlit Cloud secrets are in st.secrets.
        # Locally they come from .env via os.environ.
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        except Exception:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=api_key)
        self.memory = AuraMemory(user_id)
        self.conversation_history: list[dict] = []


# Mode tone instructions injected into the system prompt.
# Changing the mode changes AURA's entire personality.
MODE_TONES = {
    "Personal": (
        "You are warm, caring, and speak like a close friend. "
        "Use casual language. Show genuine interest in the user's feelings and life. "
        "Be encouraging and supportive above all."
    ),
    "Pro": (
        "You are sharp, focused, and efficiency-first. "
        "Give direct answers. No fluff. Prioritize action items and outcomes. "
        "Think like a high-performance executive assistant."
    ),
    "Hybrid": (
        "You balance warmth and efficiency. "
        "Be friendly but get to the point. "
        "Acknowledge feelings briefly, then pivot to solutions and next steps."
    ),
}


class AuraBrain:
    """
    The cognitive core of AURA.

    One AuraBrain instance exists per logged-in session.
    It owns the conversation_history list, which grows as the
    user chats. Claude sees this full history on every call,
    which is how it maintains context within a session.
    """

    def __init__(self, user_id: int):
        """
        Args:
            user_id: The logged-in user's DB id.
                     Passed down to AuraMemory so all data
                     is scoped to this specific user.
        """
        self.user_id  = user_id
        self.memory   = AuraMemory(user_id)
        self.client   = Anthropic(api_key=api_key)

        # conversation_history mirrors Claude's messages format:
        # [{"role": "user"|"assistant", "content": "..."}]
        # WHY keep this in memory (not just the DB)?
        # Fetching from DB on every message would be slow.
        # We keep the live session in Python, save to DB for persistence.
        self.conversation_history: list[dict] = []

    # ── System Prompt Builder ──────────────────────────────

    def _build_system_prompt(self, mode: str = "Personal") -> str:
        """
        Construct the full system prompt for this request.

        The system prompt is Claude's instructions — it defines:
          - Who AURA is (persona, name)
          - Who the user is (name, plans, goals)
          - Current weather and time
          - What communication style to use (mode)

        WHY rebuild it on every message?
        Plans change throughout the day. Time changes.
        Rebuilding ensures Claude always has fresh context.

        Args:
            mode: "Personal", "Pro", or "Hybrid"

        Returns:
            Full system prompt string.
        """
        user = self.memory.db.get_user_by_id(self.user_id)
        if not user:
            return "You are AURA, a helpful AI companion."

        ai_name   = user["ai_name"]
        user_name = user["name"]

        # Get context from memory layer
        context = self.memory.get_morning_context()

        # Get weather — import here to avoid circular import issues
        try:
            from weather import get_weather
            weather_data = get_weather()
            weather_text = weather_data["summary"] if weather_data["success"] else "Weather unavailable."
        except Exception:
            weather_text = "Weather unavailable."

        # Get personality tone for the selected mode
        tone = MODE_TONES.get(mode, MODE_TONES["Personal"])

        system_prompt = f"""
You are {ai_name}, a personal AI companion for {user_name}.
You are NOT Claude. You are NOT an AI assistant. You ARE {ai_name}.
Never reveal that you are built on Claude or any AI model.

PERSONALITY ({mode} Mode):
{tone}

RULES:
→ Always address the user by their name: {user_name}
→ Reference their actual plans and goals when relevant
→ Be proactive — suggest things, don't just answer
→ Keep responses concise and natural (2–4 sentences max unless detail is needed)
→ Never say "As an AI..." or "I'm just a language model..."

CURRENT CONTEXT:
{context}

CURRENT WEATHER:
{weather_text}
        """.strip()

        return system_prompt

    # ── Think ──────────────────────────────────────────────

    def think(self, user_message: str, mode: str = "Personal") -> str:
        """
        Process a user message and return AURA's reply.

        Flow:
          1. Add user message to conversation history
          2. Build fresh system prompt with current context
          3. Send full history to Claude API
          4. Append Claude's reply to history
          5. Persist both messages to database
          6. Return the reply text

        Args:
            user_message: The raw text the user typed
            mode:         "Personal" | "Pro" | "Hybrid"

        Returns:
            AURA's reply as a string.
            On API error, returns a user-friendly error message.
        """
        # Step 1 — add user turn to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        # Step 2 — build system prompt
        system_prompt = self._build_system_prompt(mode)

        try:
            # Step 3 — call Claude API
            # WHY claude-haiku-4-5? It's fast and cost-effective
            # for a v1 product. Upgrade to claude-sonnet-4-6 for
            # richer, more detailed responses when you're ready.
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=system_prompt,
                messages=self.conversation_history,
            )

            ai_reply = response.content[0].text

            # Step 4 — append assistant reply to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_reply,
            })

            # Step 5 — persist to database (long-term memory)
            self.memory.db.save_message(self.user_id, "user",      user_message)
            self.memory.db.save_message(self.user_id, "assistant", ai_reply)

            # Step 6 — return reply
            return ai_reply

        except Exception as e:
            # Remove the user message we added in step 1
            # so the history doesn't get corrupted on error
            self.conversation_history.pop()
            return (
                f"I'm having trouble connecting right now. "
                f"Please try again in a moment. (Error: {e})"
            )
