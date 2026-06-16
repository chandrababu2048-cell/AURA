import logging
from anthropic import Anthropic
from database import AuraDatabase
from core.memory import AuraMemory

logger = logging.getLogger("AURA.evening")


class EveningSummary:

    def __init__(self, client: Anthropic, db: AuraDatabase):
        self._client = client
        self._db = db
        self._memory_cache: dict[int, AuraMemory] = {}

    def _get_memory(self, user_id: int) -> AuraMemory:
        if user_id not in self._memory_cache:
            self._memory_cache[user_id] = AuraMemory(user_id)
        return self._memory_cache[user_id]
    def _gather_context(self, user_id: int) -> dict:
        memory = self._get_memory(user_id)
        return {
            "today" : memory.get_today_schedule(),
            "goals": self._db.get_active_goals(user_id),
            "convos": self._db.get_conversations(user_id, limit=10),
            "tomorrow": self._db.get_tomorrow_plans(user_id),

        }
    def generate(self, user_id: int) -> str:
        try:
            ctx = self._gather_context(user_id)

            goals = ctx["goals"]
            if goals:
                lines = []
                for goal in goals:
                    deadline = f" (due: {goal['deadline']})" if goal.get("deadline") else ""
                    lines.append(f"  - {goal['goal_text']}{deadline}")
                goals_text = "\n".join(lines)
            else:
                goals_text = "  No active goals."

            tomorrow = ctx["tomorrow"]
            if tomorrow:
                lines = []
                for plan in tomorrow:
                    lines.append(f"  - {plan['plan_text']}")
                tomorrow_text = "\n".join(lines)
            else:
                tomorrow_text = "  Nothing scheduled yet."

            recent_convos = ctx["convos"]
            convo_count = len(recent_convos) if recent_convos else 0

            prompt = (
                f"Today's schedule:\n{ctx['today']}\n\n"
                f"Active Goals:\n{goals_text}\n\n"
                f"Tomorrow:\n{tomorrow_text}\n\n"
                f"Boss had {convo_count} recent messages today.\n\n"
                "Write a warm, honest evening summary for Boss. "
                "Mention what he completed today, what slipped, "
                "what's coming tomorrow, and one motivating line to end the day. "
                "Under 150 words. Speak directly to Boss."
            )

            response = self._client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            summary = response.content[0].text.strip()
            logger.info("Evening summary generated for user %s", user_id)
            return summary

        except Exception as e:
            logger.error("Evening summary failed: %s", e)
            return "Good evening Boss. Summary unavailable — rest well, tomorrow is a new day."


