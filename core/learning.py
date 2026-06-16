import  logging
from datetime import datetime
from enum import Enum
from typing import Optional ,List
from pydantic import BaseModel, Field

logger = logging.getLogger("AURA.learning")

class PatternType(str, Enum):
    BREVITY = "brevity"
    TONE = "tone"
    PROACTIVE = "proactive"
    AVOIDANCE = "avoidance"

class LearnedPattern(BaseModel):
    user_id:      int         = Field(..., description="who this pattern belongs to")
    pattern_type: PatternType = Field(..., description="what kind of pattern was detected")
    trigger:      str         = Field(..., description="what situation activates this pattern")
    behavior:     str         = Field(..., description="what AURA should do when triggered")
    confidence:   float       = Field(..., description="0.0 to 1.0 — grows with each confirmation")
    observed_at:  str         = Field(default_factory=lambda: datetime.now().isoformat())

class PatternDetector:
    def __init__(self, db):
        self._db = db

    def detect(self, user_id: int, mood: str) -> List[LearnedPattern]:
        messages = self._db.get_recent_messages(user_id, limit=20)
        patterns = []
        patterns += self._detect_brevity(user_id, messages, mood)
        patterns += self._detect_avoidance(user_id, messages)
        return patterns

    def _detect_brevity(self, user_id: int, messages: list, mood: str) -> List[LearnedPattern]:
        if mood != "stressed":
            return []
        user_msgs = [m for m in messages if m["role"] == "user"]
        if not user_msgs:
            return []
        avg_len = sum(len(m["message"].split()) for m in user_msgs) / len(user_msgs)
        if avg_len < 8:
            return [LearnedPattern(
                user_id      = user_id,
                pattern_type = PatternType.BREVITY,
                trigger      = "mood:stressed",
                behavior     = "Keep responses under 60 words. Boss is stressed and wants speed.",
                confidence   = 0.75,
            )]
        return []

    def _detect_avoidance(self, user_id: int, messages: list) -> List[LearnedPattern]:
        ai_msgs   = [m for m in messages if m["role"] == "assistant"]
        user_msgs = [m for m in messages if m["role"] == "user"]
        if len(ai_msgs) < 2 or len(user_msgs) < 2:
            return []
        last_ai   = ai_msgs[-1]["message"].lower()
        last_user = user_msgs[-1]["message"].lower()
        if len(last_ai) > 300 and len(last_user.split()) < 5:
            return [LearnedPattern(
                user_id      = user_id,
                pattern_type = PatternType.AVOIDANCE,
                trigger      = "long_response",
                behavior     = "Boss disengaged after a long reply. Avoid responses over 200 words.",
                confidence   = 0.65,
            )]
        return []

class LearningMemory:
    def __init__(self, db):
        self._db = db

    def save(self, pattern: LearnedPattern)->None:
        if pattern.confidence<0.5:
            return
        self._db.save_pattern(pattern.model_dump())
        logger.info("pattern saved: %s | trigger: %s", pattern.pattern_type, pattern.trigger)


    def load(self, user_id: int, limit: int = 15) -> List[LearnedPattern]:
        rows = self._db.get_patterns(user_id, limit=limit)
        return [LearnedPattern(**row) for row in rows]
    def save_batch(self, patterns: List[LearnedPattern])->None:
        for pattern in patterns:
            self.save(pattern)

class LearningContext:
    def __init__(self, db):
        self._memory = LearningMemory(db)

    def to_prompt_snippet(self, user_id: int) -> str:
        patterns = self._memory.load(user_id, limit=15)
        strong   = [p for p in patterns if p.confidence >= 0.6]
        if not strong:
            return ""
        strong.sort(key=lambda p: p.confidence, reverse=True)
        lines = [f"- [{p.pattern_type.value}] {p.behavior}" for p in strong]
        return "### LEARNED BEHAVIOUR PATTERNS ###\n" + "\n".join(lines)
    