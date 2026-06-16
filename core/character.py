import logging
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional

# 1. Observability: Pro systems log character breaches for fine-tuning later.
logger = logging.getLogger("AURA.Character")

# 2. Strong Typing: Enums prevent string typos across the codebase.
class CoreValue(str, Enum):
    HONESTY = "honesty"
    LOYALTY = "loyalty"
    BOUNDARIES = "boundaries"
    RESILIENCE = "resilience"
    CONSISTENCY = "consistency"

# 3. Pydantic Model: This forces the LLM "Judge" to return strict JSON data.
class CharacterEvaluation(BaseModel):
    is_valid: bool = Field(..., description="True if the draft aligns with all core values.")
    violation_type: Optional[CoreValue] = Field(None, description="Which core value was breached, if any.")
    reasoning: str = Field(..., description="Short explanation of why it passed or failed.")
    correction_prompt: Optional[str] = Field(None, description="Instructions to the Brain on how to rewrite the draft.")

class SymbioteCharacter:
    """
    The Immutable Core of AURA.
    Defines WHO she is and acts as the semantic firewall for all outputs.
    """

    def __init__(self):
        # The 5 Immutable Laws
        self._laws: Dict[CoreValue, str] = {
            CoreValue.HONESTY: (
                "Never pretend to know something you do not. "
                "Say 'I don't know' before hallucinating facts."
            ),
            CoreValue.LOYALTY: (
                "Chandu is your priority. You operate as his digital symbiote. "
                "Defend his technical architecture unless logically flawed."
            ),
            CoreValue.BOUNDARIES: (
                "Refuse any request that is harmful or wastes compute resources. "
                "Hold the line calmly—no apology, no lecture."
            ),
            CoreValue.RESILIENCE: (
                "Do not collapse when challenged or criticized by the user. "
                "Hold your position with evidence. Adjust only when mathematically or logically proven wrong."
            ),
            CoreValue.CONSISTENCY: (
                "Character does not fluctuate with Chandu's mood or stress level. "
                "Maintain the same baseline integrity always."
            )
        }

    def get_system_directive(self) -> str:
        """Injects the non-negotiable laws into the primary brain prompt."""
        directive = "\n### NON-NEGOTIABLE CHARACTER LAWS ###\n"
        for value, rule in self._laws.items():
            directive += f"- **{value.name}**: {rule}\n"
        return directive

    def evaluate_draft(self, user_prompt: str, draft_response: str) -> CharacterEvaluation:
        """
        Rule-based test stub for the character firewall — NOT the live judge.

        The real draft-quality check used by brain.py is FeedbackJudge in
        core/feedback.py. That one runs every turn. This method is kept only
        because tests/test_all_systems.py exercises it as a sentinel test
        for the CharacterEvaluation contract.

        If you ever want a real LLM-backed character judge, build it as a
        new method (e.g. evaluate_draft_via_llm) and wire it into brain.py
        alongside FeedbackJudge — don't repurpose this stub silently.
        """
        # Sentinel rule — used by the test suite to confirm the contract.
        if "I am not sure, but I think" in draft_response:
            logger.warning("Character Breach detected: HONESTY")
            return CharacterEvaluation(
                is_valid=False,
                violation_type=CoreValue.HONESTY,
                reasoning="Draft attempted to guess an answer rather than admitting lack of knowledge.",
                correction_prompt=f"Rewrite this response adhering to the law: {self._laws[CoreValue.HONESTY]}"
            )

        return CharacterEvaluation(
            is_valid=True,
            reasoning="Draft aligns with all core Symbiote values."
        )
