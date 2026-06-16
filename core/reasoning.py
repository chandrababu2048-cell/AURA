import json
import logging
from datetime import datetime
from enum import Enum

from typing import List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("AURA.reasoning")

REASONING_MODEL = "claude-haiku-4-5-20251001"


class ReasoningMode(str, Enum):
    SKIP = "skip" # simple message - zero cost, no thinking
    LIGHT = "light"  # normal question - quick response
    DEEP ="deep"  # deep thinking for learning - full cross-domain reasoning
    pass


class ReasoningOutput(BaseModel):
    core_need : str = Field(..., description = "what boss actually needs, not just what he said")
    cross_domain_insight: Optional[str] = Field(None, description = "connection from another domain that illuminates this")
    suggested_approach : str = Field(..., description = "how AURA should frame the response")
    reasoning_mode : ReasoningMode = Field(..., description = "which mode fired?")
    from_cache : bool = Field(False, description="True if retrieved from notebook")

    def to_prompt_injection(self) -> str:
        lines =[
            "### INNER REASONING ###" ,
            f"Core need: {self.core_need}",
            f"Approach: {self.suggested_approach}",
        ]
        if self.cross_domain_insight:
            lines.append(f"Cross-domain : {self.cross_domain_insight}")
        if self.from_cache:
            lines.append("(recalled from notebook)")
        return "\n".join(lines)

    pass


class ReasoningNotebook:
    _TAGS = {
        # Engineering
        "database", "function", "sql", "query", "performance",
        "python", "class", "loop", "algorithm", "architecture",
        "api", "http", "request", "endpoint", "rest", "websocket",
        "memory", "cache", "storage", "ram", "disk", "index",
        "code", "debug", "error", "refactor", "test", "deploy",
        "async", "thread", "latency", "optimize", "pipeline",
        # AURA-specific
        "aura", "vault", "symbiote", "bond", "personality", "perception",
        "reasoning", "learning", "feedback", "spec", "brain", "router",
        "jepa", "embedding", "vector", "twin", "operator", "watcher",
        "character", "pattern", "signal", "state", "prompt", "injection",
        # Life / goals
        "goal", "plan", "deadline", "priority", "focus", "progress",
        "invest", "savings", "expense", "budget", "money",
        "health", "sleep", "exercise", "stress", "diet", "energy",
        # Career
        "career", "job", "interview", "resume", "salary", "startup",
        "ml", "model", "training", "investor", "pitch",
    }
    def __init__(self,db):
        self._db = db

    def extract_tags(self, text: str) -> List[str]:
        words = set(text.lower().split())
        return list(words& self._TAGS)


    def save(self, user_id: int, question: str, output: ReasoningOutput) -> None:
        tags = self.extract_tags(question)
        if not tags:
            return
        self._db.notebook_save({
            "user_id": user_id,
            "question": question,
            "tags" : json.dumps(tags),
            "core_need" : output.core_need,
            "cross_domain_insight" : output.cross_domain_insight or "",
            "suggested_approach" : output.suggested_approach,
            "created_at" : datetime.now().isoformat(),

        })
        logger.info("Notebook saved | tags: %s", tags)


    def retrieve(self, user_id: int, question: str) -> Optional[ReasoningOutput]:
        tags = self.extract_tags(question)
        if not tags:
            return None
        rows = self._db.notebook_find(user_id, tags)
        if not rows:
            return None
        best = rows[0]
        self._db.notebook_increment_hit(best["id"])
        logger.info("Notebook cache hit | id=%d | hits=%d", best["id"] ,best["hit_count"])
        return ReasoningOutput(
            core_need=best["core_need"],
            cross_domain_insight=best["cross_domain_insight"] or None,
            suggested_approach=best["suggested_approach"] ,
            reasoning_mode= ReasoningMode.DEEP,
            from_cache = True
        )


class ReasoningEngine:
    def __init__(self, client, db):
        self._client = client
        self._notebook = ReasoningNotebook(db)

    def should_reason(self, signals: dict) -> ReasoningMode:
        if signals.get("is_aggressive") or signals.get("is_goal_win"):
            return  ReasoningMode.SKIP
        if signals.get("is_short") and not signals.get("is_technical") and not signals.get("is_learning"):
            return ReasoningMode.SKIP
        if signals.get("is_technical") or signals.get("is_learning"):
            return ReasoningMode.DEEP
        return ReasoningMode.LIGHT

    def think_for_user(self, user_id: int , user_message: str, perception_snippet: str , signals :dict) -> Optional[ReasoningOutput]:
        mode = self.should_reason(signals)
        if mode == ReasoningMode.SKIP:
            return None
        cached = self._notebook.retrieve(user_id, user_message)
        if cached:
            logger.info("reasoning: notebook cache hit")
            return cached
        output = self._call_claude(user_message, perception_snippet, mode)
        if output:
            self._notebook.save(user_id, user_message, output)
        return output




    def _call_claude(self, user_message: str, perception_snippet: str, mode: ReasoningMode) -> Optional[ReasoningOutput]:
        try:
            prompt = self._build_reasoning_prompt(user_message, perception_snippet, mode)
            response = self._client.messages.create(
                model=REASONING_MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").strip()
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            if not raw:
                return None
            data = json.loads(raw)
            return ReasoningOutput(
                core_need=data["core_need"],
                cross_domain_insight=data.get("cross_domain_insight"),
                suggested_approach=data["suggested_approach"],
                reasoning_mode=mode,
                from_cache=False,
            )
        except Exception as e:
            logger.warning("Reasoning call failed: %s", e)
            return None


    def _build_reasoning_prompt(self, user_message: str, perception_snippet: str, mode: ReasoningMode) -> str:
        if mode == ReasoningMode.DEEP:
            schema = '{"core_need": "...", "cross_domain_insight": "...", "suggested_approach": "..."}'
            insight_instructions ='cross_domain_insight: one unexpected connection from another field that illuminate this problem'
        else:
            schema = '{"core_need": "...", "cross_domain_insight": null, "suggested_approach": "..."}'
            insight_instructions = 'cross_domain_insight: null'
        return f"""You are AURA's inner reasoning layer. Think before AURA responds.

Boss said: "{user_message}"

Boss context:
{perception_snippet}

Return ONLY valid JSON matching this schema:
{schema}

Rules:
- core_need: what Boss actually needs, not just what he literally said
- {insight_instructions}
- suggested_approach: how AURA should frame the response — tone, depth, angle
- No explanation. No markdown. Just the JSON object."""
