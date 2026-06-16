import logging
from datetime import  datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger("AURA.feedback")

class FeedbackType(str, Enum):
    CORRECTION = "correction" # USER SAID "WRONG" "NOT" "NOT THAT" "STOP"
    PREFERENCE= "preference"  # USER SAID "I LIKE" , ALWAYS DO THIS "
    PATTERN = "pattern"  # AURA detected a  repeated behavior

class FeedbackEvent(BaseModel):
    user_id: int   =Field(..., description = "who this belongs to")
    feedback_type: FeedbackType = Field(..., description = "what kind of signal")
    context : str = Field(..., description = "what AURA did or said")
    correction: str = Field(..., description = "what the suer want instead")
    captured_at: str = Field(default_factory = lambda: datetime.now().isoformat())
class FeedbackReport(BaseModel):
    is_satisfactory: bool = Field(..., description = "whether this feedback is satisfactory OR Did the draft pass?")
    quality_score : float = Field(..., description = "0.0 TO 1.0 quality score")
    critique:  Optional[str] = Field(None, description = "what AURA did  wrong ?")
    required_fixes: List[str] = Field(default_factory = list, description = "fix instructions")

class FeedbackJudge:
    def __init__(self, character_model):
        self._character = character_model
        self._threshold = 0.7

    def evaluate(self, draft: str, user_input: str, perception_context: str) ->FeedbackReport:
        fixes =[]
        score = 1.0

        if "as an ai language model" in draft.lower() or "as a ai language model" in draft.lower():
            score = 0.5
            fixes.append("Remove robotic AI phrasing . Maintain symbiote persona.")

        if "stressed" in perception_context.lower() and len(draft)> 500:
            score = 0.3
            fixes.append("user is stressed .Draft too long - make it concise.")
        if "fixed the code" in draft.lower() and "```" not in draft:
            score = 0.4
            fixes.append("claimed to fix code but no code block provided.")

        is_ok = score >= self._threshold
        logger.warning("draft rejected: %s", fixes) if not is_ok else None
        return FeedbackReport(
            is_satisfactory = is_ok,
            quality_score = max(0.0, score),
            critique = "Draft failed quality checks." if not is_ok else "Draft passed.",
            required_fixes = fixes,
        )
class FeedbackMemory:
    def __init__(self, db):
        self._db = db
    def record(self, event: FeedbackEvent) -> None:
        self._db.save_feedback(event.model_dump())
        logger.info("Feedback recorded: %s | %s", event.feedback_type, event.context[:50])
    def load(self, user_id: int, limit: int = 20) -> List[FeedbackEvent]:
        rows = self._db.get_feedback(user_id, limit=limit)
        return [FeedbackEvent(**row) for row in rows]

class FeedbackContext:
    def __init__(self, db):
        self._memory = FeedbackMemory(db)

    def to_prompt_snippet(self, user_id: int) -> str:
        events = self._memory.load(user_id, limit=10)
        if not events:
            return ""
        lines = [f"- [{e.feedback_type.value}] {e.correction}" for e in events]
        return "### USER FEEDBACK HISTORY ###\n" + "\n".join(lines)