import logging
from anthropic import Anthropic
from database import AuraDatabase
from core.memory import AuraMemory
from weather import get_weather
from connectors.calendar import CalendarConnector

logger = logging.getLogger("AURA.morning")


class MorningBriefing:

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
        try:
            calendar = CalendarConnector()
            calendar_snippet = calendar.to_prompt_snippet()
        except Exception as e:
            logger.warning("calendar sync failed: %s", e)
            calendar_snippet = "Calendar unavailable."

        try:
            current_weather = get_weather()
        except Exception as e:
            logger.warning("weather sync failed: %s", e)
            current_weather = "Weather unavailable"

        return {
            "context":   memory.get_morning_context(),
            "weather":   current_weather,
            "goals":     self._db.get_active_goals(user_id),
            "yesterday": self._db.get_yesterday_plans(user_id),
            "calendar" : calendar_snippet,
            "health":    None,  # Phase 4 — health connector not built yet
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

            yesterday = ctx["yesterday"]
            if yesterday:
                lines = []
                for plan in yesterday:
                    status = "✅" if plan["is_done"] else "❌"
                    lines.append(f"  {status} {plan['plan_text']}")
                yesterday_text = "\n".join(lines)
            else:
                yesterday_text = "  No plans recorded yesterday."

            health_line = ""
            if ctx["health"]:
                health_line = f"\nHealth: {ctx['health']}"

            prompt = (
                f"{ctx['context']}\n\n"
                f"Weather: {ctx['weather']}\n"
                f"Calendar: {ctx['calendar']}\n"
                f"{health_line}\n"
                f"Yesterday:\n{yesterday_text}\n\n"
                f"Active Goals:\n{goals_text}\n\n"
                "Write a warm, concise morning briefing for Boss. "
                "Mention what slipped yesterday, what's due today, "
                "the weather if relevant, and one motivating line. "
                "Under 200 words. Speak directly to Boss."
            )

            response = self._client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            briefing = response.content[0].text.strip()
            logger.info("morning briefing generated for user %s", user_id)
            return briefing

        except Exception as e:
            logger.error("morning briefing failed: %s", e)
            return "Good morning Boss. Briefing unavailable — check your plans manually."
