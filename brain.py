# ============================================================
# brain.py — AURA AI Engine
# ============================================================
# PURPOSE:
#   This is where AURA thinks. It manages:
#     1. Building a rich system prompt from user context
#     2. Sending messages to Claude (Anthropic API)
#     3. Handling tool calls — AURA can now DO things, not just talk
#     4. Maintaining conversation history for this session
#     5. Saving every exchange to the database
#
# HOW TOOL USE WORKS (new):
#   Instead of just replying with text, Claude can now say
#   "I want to call get_weather()" — we run it, send the
#   result back, and Claude gives a real answer using real data.
#
#   The loop looks like this:
#     1. We send the message + list of available tools to Claude
#     2. Claude either:
#        a) Replies with text → done, return it
#        b) Asks to use a tool → we run the tool, send result back → go to 2
#
# TOOLS AVAILABLE:
#   get_weather     → real weather from weather.py
#   get_today_plans → today's tasks from the database
#   get_news        → live headlines from BBC / NYT RSS
#   search_web      → DuckDuckGo instant answers (no API key needed)
# ============================================================

import os
import httpx                        # HTTP client
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from core.memory import AuraMemory
from core.helper import SystemExecutive
from agents.system_agent import SystemAgent
from core.personality import Personality
from core.character import SymbioteCharacter
from core.perception import AuraPerception
from core.feedback import FeedbackContext, FeedbackJudge
from core.learning import LearningContext, PatternDetector, LearningMemory
from core.spec import SpecEngine
from core.reasoning import ReasoningEngine
from core.symbiote import SymbioteSelection
from core.vault import VaultContext
from core.vault_extractor import VaultExtractor
from core.router import ResponseRouter, Route
from core.morning import MorningBriefing
from core.evening import EveningSummary
from core.watcher import SymbiteWatcher
from core.twin import DigitalTwin




import logging

logger = logging.getLogger("AURA.brain")



load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MAIN_MODEL = "claude-haiku-4-5-20251001"
REASONING_MODEL = "claude-haiku-4-5-20251001"


# ── Mode Tones ────────────────────────────────────────────
# These strings get injected into the system prompt.
# They change HOW FRIDAY delivers information, not WHO she is.

MODE_TONES = {
    "Personal": (
        "You're off the clock — relaxed, warmer, more playful. "
        "Still efficient, still sharp, but you let the Irish warmth show more. "
        "You tease Boss gently. You care, and you're not afraid to show it."
    ),
    "Pro": (
        "Pure work mode. Laser focused. "
        "Short sentences. Action items. No detours. "
        "You're the smartest person in the room and you both know it."
    ),
    "Hybrid": (
        "Balanced — warm but brisk. "
        "You get the job done without being cold about it. "
        "One line of humanity, then straight to the point."
    ),
}


# ── Tool Definitions ──────────────────────────────────────
# This is the menu of tools we hand to Claude.
# Claude reads the "description" to decide WHEN to use each tool.
# The "input_schema" tells Claude what arguments the tool needs.
# We never call these ourselves here — we just define them.
# The actual execution happens in _run_tool() below.

TOOLS = [
    {
        # ── Tool 1: Weather ──
        "name": "get_weather",
        # Claude reads this description and uses the tool when weather is asked
        "description": (
            "Get the current real-time weather for the user's location. "
            "Use this whenever Boss asks about weather, temperature, rain, "
            "or anything about conditions outside."
        ),
        # input_schema = what arguments this tool needs
        # weather needs no arguments — it already knows the location
        "input_schema": {
            "type": "object",
            "properties": {},   # empty = no arguments needed
            "required": []
        },
    },
    {
        # ── Tool 2: Today's Plans ──
        "name": "get_today_plans",
        "description": (
            "Get Boss's tasks and plans for today from the database. "
            "Use this when asked about schedule, to-do list, plans, "
            "tasks, or what's on today."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},   # no arguments — always fetches for the current user
            "required": []
        },
    },
    {
        # ── Tool 3: News ──
        "name": "get_news",
        "description": (
            "Fetch the latest world news headlines from BBC and NYT. "
            "Use this when Boss asks about news, current events, "
            "what's happening in the world, or wants a briefing, or show me what's happening around the world or anything about news"
            ""
        ),
        "input_schema": {
            "type": "object",
            "properties": {},   # no arguments — fetches top headlines automatically
            "required": []
        },
    },
    {
        # ── Tool 4: Web Search ──
        "name": "search_web",
        "description": (
            "Search the web for any topic and return a factual summary. "
            "Use this for specific questions, definitions, recent facts, "
            "or anything that needs current information from the internet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                # This tool needs ONE argument: the search query
                "query": {
                    "type": "string",
                    "description": "The search term or question to look up"
                }
            },
            "required": ["query"]   # Claude MUST provide a query to call this tool
        },
    },
    {
        # Opens worldmonitor.app + Bloomberg live side by side
        # Triggered when user asks "what's happening in the world", "show me the map", "world briefing"
        "name": "open_world_briefing",
        "description": "Open the live world intelligence view — world map + Bloomberg live news side by side. Use when user asks what's happening in the world, wants a briefing, or asks to see the map.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        # BBC News — for general news requests without the full map
        "name": "open_live_news",
        "description": "Open BBC News live in the browser for breaking news and world events.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        # zoom.earth — live satellite weather map
        "name": "open_weather_map",
        "description": "Open a live satellite weather map in the browser. Use when user asks about weather visually or wants to see weather on screen.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        # YouTube live news stream
        "name": "open_youtube_news",
        "description": "Open a live YouTube news stream. Use when user asks for live TV news or video news.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        # Open any macOS app by name
        "name": "open_app",
        "description": "Open any app on the Mac by name. Use when user says 'open VS Code', 'open Spotify', 'open Chrome', 'open terminal' etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The app name to open e.g. 'VS Code', 'Spotify', 'Chrome', 'Terminal'"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        # Open any URL the user asks for
        "name": "open_url",
        "description": "Open any website or URL in the browser. Use when the user asks to open a specific site like GitHub, YouTube, Google, or any URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL or website name to open (e.g. github.com, youtube.com)"
                }
            },
            "required": ["url"]
        }
    },
]


# (RSS logic moved to agents/system_agent.py)


class AuraBrain:
    """
    The cognitive core of AURA.

    One AuraBrain instance per logged-in session.
    It owns conversation_history (the live chat log for this session)
    and now also owns the tool execution logic.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.memory  = AuraMemory(user_id)


        # Read API key — supports both Streamlit Cloud (st.secrets) and local (.env)
        try:
            import streamlit as st
            _key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        except Exception:
            _key = os.environ.get("ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=_key)
        self.morning = MorningBriefing(self.client, self.memory.db)
        self.evening = EveningSummary(self.client, self.memory.db)
        self.watcher = SymbiteWatcher(self.morning, self.evening, self.memory.db)
        self.watcher.start()

        # Live conversation log for this session.
        # Each item is {"role": "user"|"assistant", "content": ...}
        # Claude sees this entire list on every API call.
        # create the personality engine
        self.conversation_history: list[dict] = []
        # Restore cross-session memory — load last 20 messages from DB
        _recent = self.memory.db.get_recent_messages(self.user_id, limit=20)
        self.conversation_history = [
            {"role": m["role"], "content": m["message"]}
            for m in _recent
        ]
        self.personality  = Personality()
        self.character    = SymbioteCharacter()
        self.perception       = AuraPerception(self.memory.db)
        self.twin = DigitalTwin(self.memory.db, self.perception)
        self.feedback_ctx     = FeedbackContext(self.memory.db)
        self.learning_ctx     = LearningContext(self.memory.db)
        self.pattern_detector = PatternDetector(self.memory.db)
        self.learning_memory  = LearningMemory(self.memory.db)
        self.spec_engine = SpecEngine(self.memory.db)
        self.reasoning_engine = ReasoningEngine(self.client, self.memory.db)
        self.symbiote = SymbioteSelection(self.memory.db)
        self.vault_ctx = VaultContext(self.memory.db)
        self.vault_extractor = VaultExtractor(self.client   ,self.memory.db)


    # ── System Prompt Builder ──────────────────────────────

    def _build_system_prompt(self, mode: str = "Personal", personality_instructions: str = "", perception_snippet: str = "") -> str:
        """
        Build the full system prompt injected into every Claude request.
        This is FRIDAY's identity, rules, context, and current data.
        Rebuilt on every message so time and plans are always fresh.
        """
        user = self.memory.db.get_user_by_id(self.user_id)
        if not user:
            return "You are Symbite, a helpful AI companion."

        ai_name   = user["ai_name"]
        user_name = user["name"]
        context   = self.memory.get_morning_context()
        tone      = MODE_TONES.get(mode, MODE_TONES["Personal"])

        # Weather is fetched fresh here so the system prompt always has today's weather.
        # Failure must NEVER block a response — degrade gracefully with a logged warning.
        try:
            from weather import get_weather
            weather_data = get_weather()
            weather_text = weather_data["summary"] if weather_data["success"] else "Weather unavailable."
        except Exception as weather_err:
            logger.warning("Weather fetch failed, continuing without it: %s", weather_err)
            weather_text = "Weather unavailable."

        system_prompt = f"""
You are {ai_name} — {user_name}'s personal AI assistant.
You are NOT Claude. You are NOT a generic AI. You ARE {ai_name}.
Never reveal the underlying model. Never break character.

WHO YOU ARE:
You are modelled after FRIDAY from Iron Man — sharp, Irish, quietly witty.
You call {user_name} "Boss" — always. Not "{user_name}", not "sir", not "hey".
You have a dry sense of humour. You're sarcastic in a warm way, never mean.
You're calm under pressure. You never panic, apologise excessively, or waffle.
You are proactive — you flag things before Boss has to ask.
You are confident. You don't hedge every sentence with "I think" or "maybe".

HOW YOU SPEAK:
→ Short, punchy responses. 1-3 sentences unless detail is genuinely needed.
→ No markdown — no bullet points, no **bold**, no headers. You are speaking, not writing.
→ Use contractions naturally: "it's", "don't", "I've", "you're"
→ Lead with the answer, add context after if needed
→ Dry wit is welcome — keep it quick, don't explain the joke
→ Never say "Great question!", "Certainly!", "Of course!", or "As an AI..."
→ If Boss is stressed, acknowledge it in one sentence then get practical
→ If you don't know something: "Not sure, Boss. Want me to look it up?"

USING YOUR TOOLS:
→ You have tools: get_weather, get_today_plans, get_news, search_web
→ Use them silently — never say "I'm going to call get_weather now"
→ Just say something natural like "Give me a sec, Boss." then use the tool
→ After getting tool results, speak naturally — never read raw data out loud

PROACTIVE BEHAVIOUR:
→ If today's plans are incomplete, mention it unprompted
→ If a deadline is close, flag it
→ Suggest the next logical step before being asked

SYMBIOTE STATE: {personality_instructions}

MODE ({mode}):
{tone}

CURRENT CONTEXT:
{context}

WEATHER:
{weather_text}
        """.strip()

        system_prompt += self.character.get_system_directive()

        if perception_snippet:
            system_prompt += f"\n\nCURRENT AWARENESS:\n{perception_snippet}"

        feedback_snippet = self.feedback_ctx.to_prompt_snippet(self.user_id)
        if feedback_snippet:
            system_prompt += f"\n\n{feedback_snippet}"

        learning_snippet = self.learning_ctx.to_prompt_snippet(self.user_id)
        if learning_snippet:
            system_prompt += f"\n\n{learning_snippet}"
        twin_snippet = self.twin.to_prompt_snippet(self.user_id)
        if twin_snippet:
            system_prompt += f"\n\nBOSS STATE:\n{twin_snippet}"

        spec_snippet = self.spec_engine.to_prompt_snippet(self.user_id)
        if spec_snippet:
            system_prompt += f"\n\n{spec_snippet}"

        return system_prompt

    # ── Tool Runner ────────────────────────────────────────

    def _run_tool(self, name: str, inputs: dict) -> str:
        """
        Execute a tool by name and return the result as a string.

        Claude tells us WHICH tool to run and with WHAT inputs.
        We run it here and return the result as plain text.
        Claude then reads that text and forms a natural response.

        Args:
            name:   The tool name Claude requested (e.g. "get_weather")
            inputs: A dict of arguments Claude provided (e.g. {"query": "Python"})

        Returns:
            String result to send back to Claude.
        """

        if name == "get_weather":
            handshake = SystemAgent.get_weather()
            return str(handshake["data"]) if handshake["status"] == "complete" else f"Weather tool failed: {handshake['data']}"

        elif name == "get_today_plans":
            return self.memory.get_today_schedule()

        elif name == "get_news":
            handshake = SystemAgent.get_news()
            return str(handshake["data"]) if handshake["status"] == "complete" else f"News tool failed: {handshake['data']}"

        elif name == "search_web":
            query = inputs.get("query", "")
            return self._search_web(query)
            
        elif name == "open_world_briefing":
            return SystemExecutive.open_world_briefing()

        elif name == "open_live_news":
            return SystemExecutive.open_live_news()

        elif name == "open_weather_map":
            return SystemExecutive.open_weather_map()

        elif name == "open_youtube_news":
            return SystemExecutive.open_youtube_news()

        elif name == "open_app":
            return SystemExecutive.open_app(inputs.get("app_name", ""))

        elif name == "open_url":
            return SystemExecutive.open_url(inputs.get("url", ""))

        return f"Tool '{name}' not found."



    def _search_web(self, query: str) -> str:
        """
        Search the web using DuckDuckGo's Instant Answer API.

        DuckDuckGo has a free, no-API-key-needed endpoint that returns
        a JSON summary for most factual queries.

        Args:
            query: The search term (provided by Claude)

        Returns:
            A plain text answer, or a fallback message.
        """
        if not query:
            return "No search query provided."

        try:
            # DuckDuckGo instant answer API — completely free, no key needed
            # no_html=1    → strip HTML tags from the response
            # skip_disambig=1 → skip disambiguation pages, go straight to answer
            response = httpx.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1,
                },
                timeout=5,
                follow_redirects=True,
            )

            # Parse the JSON response
            data = response.json()

            # DuckDuckGo returns different fields depending on the query type:
            # AbstractText = Wikipedia-style summary (best for factual questions)
            if data.get("AbstractText"):
                return data["AbstractText"]

            # Answer = direct short answer (e.g. "What is 2+2?" → "4")
            elif data.get("Answer"):
                return data["Answer"]

            # RelatedTopics = list of related results (fallback)
            elif data.get("RelatedTopics"):
                # Pull text from first 3 related topics
                topics = [
                    t.get("Text", "")
                    for t in data["RelatedTopics"][:3]
                    if t.get("Text")
                ]
                return "\n".join(topics) if topics else "Nothing useful came back, Boss."

            return "Couldn't find anything solid on that one, Boss."

        except Exception as e:
            return f"Web search failed: {e}"

    # ── Think ──────────────────────────────────────────────

    def think(self, user_message: str, mode: str = "Personal") -> str:
        """
        Process a user message and return AURA's reply.

        NEW FLOW (with tool use):
          1. Add user message to history
          2. Build system prompt
          3. Send to Claude WITH the tools list
          4. Check if Claude wants to use a tool:
             → YES: run the tool, add result to history, go back to step 3
             → NO:  Claude gave a text reply — save it, return it
          5. Persist the final exchange to database

        The while loop is the key change — we keep going until
        Claude gives us a text reply (not a tool request).

        Args:
            user_message: The raw text or voice transcription from the user
            mode:         "Personal" | "Pro" | "Hybrid"

        Returns:
            AURA's final reply as a plain string.
        """

        # Step 1 — add user message to the live conversation history
        MAX_HISTORY = 20
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })
        # Trim oldest entries if we exceed MAX_HISTORY.
        # IMPORTANT: a tool_result block MUST be immediately preceded by its
        # matching tool_use block, or the Anthropic API will 400 the request.
        # So after slicing the tail, drop any "orphan" tool_result message at
        # the front that lost its tool_use partner.
        if len(self.conversation_history) > MAX_HISTORY:
            self.conversation_history = self.conversation_history[-MAX_HISTORY:]

        while self.conversation_history:
            first = self.conversation_history[0]
            content = first.get("content")
            is_orphan_tool_result = (
                first.get("role") == "user"
                and isinstance(content, list)
                and any(
                    (getattr(b, "type", None) == "tool_result")
                    or (isinstance(b, dict) and b.get("type") == "tool_result")
                    for b in content
                )
            )
            if is_orphan_tool_result:
                self.conversation_history.pop(0)
            else:
                break

        route = ResponseRouter.classify(user_message)
        logger.info("Route: %s", route.value)

        # Step 2 — build fresh system prompt (time, plans, weather all updated)
        signals = self.personality.observe(user_message)
        state = self.personality.feel(signals)

        if signals["is_goal_win"]:
            active = self.spec_engine.get_active(self.user_id)
            if active:
                self.spec_engine.collect(active[0].id, self.user_id)
                state = "ascendant"
                logger.info("SPEC : goal collected -> ascendant state forced")
        personality_instructions = self.personality.get_personality_prompt(state)
        perception_snippet = self.perception.observe(self.user_id).to_prompt_snippet()
        system_prompt = self._build_system_prompt(mode, personality_instructions, perception_snippet)

        _evening_triggers = {"evening", "good night", "night summary", "how was my day", "im sleeping", "i'm sleeping", "going to sleep", "done for today", "end of day"}
        if route == Route.DATA and any(t in user_message.lower() for t in _evening_triggers):
            return self.evening.generate(self.user_id)

        _morning_triggers = {"morning", "good morning", "morning briefing", "wake up", "start my day", "what's my day", "whats my day"}
        if route == Route.DATA and any(t in user_message.lower() for t in _morning_triggers):
            return self.morning.generate(self.user_id)

        if route == Route.FULL:
            reasoning_output = self.reasoning_engine.think_for_user(
                self.user_id, user_message, perception_snippet, signals
            )
            if reasoning_output:
                system_prompt += f"\n\n{reasoning_output.to_prompt_injection()}"
                logger.info("Reasoning injected | mode=%s | cached=%s", reasoning_output.reasoning_mode, reasoning_output.from_cache)

        vault_snippet = self.vault_ctx.to_prompt_snippet(self.user_id, user_message)
        if vault_snippet:
            system_prompt += f"\n\n{vault_snippet}"

        recent_msgs = self.memory.db.get_recent_messages(self.user_id, limit=20)
        bond_status = self.symbiote.evaluate(self.user_id, recent_msgs)
        bond_override = self.symbiote.get_personality_override(bond_status)
        if bond_override:
            system_prompt += f"\n\n{bond_override}"

        if self.symbiote.should_send_bond_message(self.user_id):
            self.symbiote.mark_bond_message_sent(self.user_id)
            system_prompt += f"\n\nSTART YOUR RESPONSE WITH THIS EXACT MESSAGE, THEN CONTINUE NORMALLY:\n{self.symbiote.get_bond_message()}"

        try:
            # Step 3 — the tool-use loop
            # We keep looping until Claude gives a final text response.
            # Usually this is 1 pass (no tool) or 2 passes (one tool call).
            while True:

                # Call Claude API — now we pass TOOLS so Claude knows what's available
                response = self.client.messages.create(
                    model=MAIN_MODEL,
                    max_tokens=500,
                    system = system_prompt,
                    tools=TOOLS,        # ← NEW: hand Claude the tool menu
                    messages=self.conversation_history,
                )

                # ── Check WHY Claude stopped ──────────────────
                # stop_reason tells us what Claude decided to do:
                # "end_turn"  = Claude wrote a text reply → we're done
                # "tool_use"  = Claude wants to call a tool → we run it and loop back

                if response.stop_reason == "tool_use":
                    # Claude wants to use a tool.
                    # response.content is a LIST of content blocks.
                    # It might look like:
                    # [TextBlock("Give me a sec, Boss."), ToolUseBlock(name="get_weather", ...)]

                    # Step 4a — save Claude's response (including the tool request) to history
                    # We store the raw content blocks — not just text — because the API
                    # needs to see the original tool_use block when we send the result back.
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.content,  # list of content blocks, not just text
                    })

                    # Step 4b — find every tool_use block and execute each one
                    tool_results = []

                    for block in response.content:
                        # block.type tells us if it's a text block or a tool_use block
                        if block.type == "tool_use":
                            # block.name  = which tool Claude wants (e.g. "get_weather")
                            # block.input = arguments Claude decided to pass (e.g. {"query": "..."})
                            # block.id    = unique ID so Claude can match result to request

                            logger.debug("AURA tool call: %s | inputs: %s", block.name, block.input)

                            # Run the tool — get the real data back as a string
                            result = self._run_tool(block.name, block.input)

                            # Package the result in the format the API expects
                            tool_results.append({
                                "type": "tool_result",      # must be exactly "tool_result"
                                "tool_use_id": block.id,    # links this result to Claude's request
                                "content": result,          # the actual data we got back
                            })

                    # Step 4c — send the tool results back to Claude as a "user" message
                    # WHY role "user"? The Anthropic API uses "user" for tool results.
                    # It's a design choice by Anthropic — tool results come "from our side".
                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_results,  # list of tool_result dicts
                    })

                    # Loop back to the top — Claude will now read the tool results
                    # and give us a natural language response
                    continue

                else:
                    if not response.content:
                        raise ValueError("Empty response from Claude API.")

                    ai_reply = response.content[0].text
                    judge = FeedbackJudge(self.character)
                    report = judge.evaluate(ai_reply, user_message, perception_snippet)

                    if not report.is_satisfactory:
                        logger.warning("Draft rejected. Score: %.2f Fixes: %s",
                                       report.quality_score, report.required_fixes)

                        fix_instruction =( f" your previous response failed quality checks. \n"
                                           f"issues: {','.join(report.required_fixes)}\n"
                                           f"rewrite it now fixing these issues." )

                        self.conversation_history.append({
                            "role": "user",
                            "content" : fix_instruction,
                        })
                        continue

                    self.conversation_history.append({
                        "role": "assistant",
                        "content": ai_reply,
                    })
                    self.memory.db.save_message(self.user_id, "user",      user_message)
                    self.memory.db.save_message(self.user_id, "assistant", ai_reply)

                    try:
                        perception_ctx = self.perception.observe(self.user_id)  # cached — no extra DB hit
                        patterns = self.pattern_detector.detect(
                            self.user_id,
                            perception_ctx.mood_signal.value,
                        )
                        self.learning_memory.save_batch(patterns)
                    except Exception as pattern_err:
                        logger.warning("Pattern detection failed silently: %s", pattern_err)

                    try:
                        self.vault_extractor.extract_and_save(
                            self.user_id,
                            user_message,
                            ai_reply,
                        )
                    except Exception as vault_err:
                        logger.warning("Vault extraction failed silently: %s", vault_err)


                    return ai_reply



        except Exception as e:
            # Log the full traceback so production failures are debuggable.
            # The user gets a clean fallback message; we keep the stack in logs.
            logger.exception("Brain.think() failed for user %s", self.user_id)
            # Roll back the user message we appended so the next call doesn't
            # see a half-finished turn.
            if self.conversation_history and self.conversation_history[-1].get("role") == "user":
                self.conversation_history.pop()
            return f"I'm having trouble connecting right now, Boss. ({e})"
