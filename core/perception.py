import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("AURA.perception")
_CACHE_TTL_SECONDS = 60


class TimeOfDay(str, Enum):
    EARLY_MORNING = "early_morning"
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

_TIME_BUCKETS: list[tuple[int, int, TimeOfDay]] = [
    (5,9,TimeOfDay.EARLY_MORNING),
    (9,12,TimeOfDay.MORNING),
    (12, 17, TimeOfDay.AFTERNOON),
    (17, 21, TimeOfDay.EVENING),
]
def _classify_time(hour: int) -> TimeOfDay:
    if hour >= 21 or hour <5:
        return TimeOfDay.NIGHT
    for start, end ,label in _TIME_BUCKETS:
        if start <= hour < end:
            return label
    return TimeOfDay.NIGHT
class DayLoad(str, Enum):
    LIGHT = "light"
    NORMAL = "normal"
    HEAVY = "heavy"
def _classify_day(plans: list[dict]) -> DayLoad:
    total = len(plans)
    if total <= 2:
        return DayLoad.LIGHT
    if total <= 5:
        return DayLoad.NORMAL
    return DayLoad.HEAVY

class MoodSignal(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    STRESSED = "stressed"


# perception.py - Sensory Cortex Signals

# STRESS SIGNALS: High-urgency friction
_STRESS_SIGNALS = {
    "stuck", "broken", "error", "failed", "frustrated", "confused",
    "why isn't", "not working", "deadline", "overwhelmed", "tired",
    "exhausted", "behind", "help", "exception", "crash", "bug",
    "timeout", "rejected", "null", "undefined", "logic error",
    "garbage", "mess", "disaster", "pressure", "panicking"
}

#  POSITIVE SIGNALS: Success and Momentum
_POSITIVE_SIGNALS = {
    "done", "finished", "works", "finally", "solved", "great",
    "good", "happy", "excited", "ready", "let's go", "figured it out",
    "got it", "perfect", "amazing", "success", "resolved", "fixed",
    "deployed", "clean", "smooth", "awesome", "winning", "nailed it",
    "speed", "optimized"
}

#  NEGATIVE SIGNALS: General dissatisfaction or technical debt
# (Used for a subtle tone shift before full 'Stress' mode kicks in)
_NEGATIVE_SIGNALS = {
    "slow", "annoying", "tedious", "boring", "redundant", "ugly",
    "dirty code", "workaround", "hacky", "bad", "difficult",
    "hard", "tedious", "waste", "useless", "clunky", "manual",
    "refactor", "debt", "old", "legacy", "messy"
}

def _classify_mood(recent_messages: list[dict]) -> MoodSignal:
    stress_score =0
    positive_score = 0
    negative_score = 0
    for row in recent_messages:
        text = row.get("message", "").lower()
        stress_score += sum(1 for kw in _STRESS_SIGNALS if kw in text)
        positive_score += sum(1 for kw in _POSITIVE_SIGNALS if kw in text)
        negative_score +=sum(1 for kw in _NEGATIVE_SIGNALS if kw in text)

    if stress_score > positive_score:
        return MoodSignal.STRESSED
    if positive_score > stress_score:
        return MoodSignal.POSITIVE
    if negative_score > stress_score:
        return MoodSignal.NEGATIVE
    return MoodSignal.NEUTRAL

class PerceptionContext(BaseModel):
    time_of_day : TimeOfDay = Field(..., description ="current time bucket")
    day_load : DayLoad = Field(..., description ="how busy today is ?")
    mood_signal : MoodSignal = Field(..., description ="user's detected mood signal")
    captured_at :str = Field(..., description ="ISO timestamp of observation")
    plan_count : int = Field(..., description ="number of plans today")

    def to_prompt_snippet(self) -> str:
        return (
            f"current time : {self.time_of_day.value}."
            f"today's schedule load : {self.day_load.value} ({self.plan_count} tasks)."
            f" user mood signal: {self.mood_signal.value}."

        )

class AuraPerception:
    def __init__(self, db):
        self._db = db
        self._cache : dict[int, tuple[PerceptionContext, datetime]] = {}
        self._logger = logging.getLogger("AuraPerception")

    def observe(self, user_id: int) -> PerceptionContext:
        cached = self._cache.get(user_id)
        if cached is not None:
            ctx , captured_at = cached
            age = (datetime.now() - captured_at).total_seconds()
            if age < _CACHE_TTL_SECONDS:
                self._logger.debug("Perception cache hit for user %d (age %.1fs)", user_id, age)
                return ctx
        now = datetime.now()
        plans = self._db.get_plans_for_date(user_id, now.strftime("%Y-%m-%d"))
        messages = self._get_recent_messages(user_id)

        context = PerceptionContext(
            time_of_day = _classify_time(now.hour),
            day_load = _classify_day(plans),
            mood_signal = _classify_mood(messages),
            captured_at = now.isoformat(),
            plan_count = len(plans),
        )
        self._cache[user_id] = (context, now)
        self._logger.info("Perception captured : %s", context.model_dump())
        return context
    def _get_recent_messages(self, user_id: int) -> list[dict]:
        return self._db.get_recent_messages(user_id, limit=10)