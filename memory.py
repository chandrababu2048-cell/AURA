# ============================================================
# memory.py — AURA Memory Engine
# ============================================================
# PURPOSE:
#   Sits between brain.py and database.py.
#   Transforms raw DB rows into rich, readable context
#   that the AI can use to give personalized responses.
#
# WHY A SEPARATE MEMORY LAYER?
#   brain.py shouldn't know HOW data is stored.
#   database.py shouldn't know HOW data is used.
#   memory.py bridges them — it speaks both languages.
#
# THINK OF IT LIKE:
#   database.py  → raw facts ("user has 3 plans")
#   memory.py    → meaningful context ("Chandu has 3 plans today,
#                   1 done yesterday, working toward a coding goal")
#   brain.py     → uses that context to talk like a real companion
# ============================================================

from database import AuraDatabase
from datetime import datetime


class AuraMemory:
    """
    Builds rich context from the database for the AI brain.

    Each AuraMemory instance belongs to ONE user (user_id).
    This ensures memory is always scoped to the right person.
    """

    def __init__(self, user_id: int):
        """
        Args:
            user_id: The logged-in user's database ID.
                     Every query uses this to fetch only their data.
        """
        self.user_id = user_id
        self.db      = AuraDatabase()

    # ── Daily Schedule ─────────────────────────────────────

    def get_today_schedule(self) -> str:
        """
        Returns today's plans as a readable text block.

        WHY return a string and not a list?
        This output goes directly into the AI system prompt.
        The AI reads plain text, not Python lists.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        plans = self.db.get_today_plans(self.user_id)

        if not plans:
            return "No plans for today yet."

        lines = [f"Today ({today}) — Plans:"]
        for i, plan in enumerate(plans, start=1):
            status = "✅" if plan["is_done"] else "⏳"
            lines.append(f"  {i}. {status} {plan['plan_text']}")

        return "\n".join(lines)

    def get_today_plans_list(self) -> list[dict]:
        """
        Returns today's plans as a raw list of dicts.
        Used by the UI (streamlit_app.py) to render checkboxes.
        Different from get_today_schedule() which returns a string for the AI.
        """
        return self.db.get_today_plans(self.user_id)

    # ── Morning Context ────────────────────────────────────

    def get_morning_context(self) -> str:
        """
        Builds the full context block injected into the AI system prompt.

        This is what makes AURA feel like it KNOWS you.
        The AI reads this before every response, so it always
        has a picture of:
          - Who you are
          - What you're doing today
          - How yesterday went
          - What long-term goals you're working toward

        Returns a multi-line string ready for the system prompt.
        """
        user = self.db.get_user_by_id(self.user_id)
        if not user:
            return "No user context available."

        # Today's plan summary
        today_summary = self.get_today_schedule()

        # Yesterday's plans with done/not-done status
        yesterday_plans  = self.db.get_yesterday_plans(self.user_id)
        yesterday_summary = ""
        if yesterday_plans:
            lines = ["Yesterday's Plans:"]
            for plan in yesterday_plans:
                status = "✅ Done" if plan["is_done"] else "❌ Not done"
                lines.append(f"  - {plan['plan_text']}: {status}")
            yesterday_summary = "\n".join(lines)

        # Active long-term goals
        goals      = self.db.get_active_goals(self.user_id)
        goals_text = ""
        if goals:
            lines = ["Long-term Goals:"]
            for goal in goals:
                deadline = f" (deadline: {goal['deadline']})" if goal["deadline"] else ""
                lines.append(f"  - {goal['goal_text']}{deadline}")
            goals_text = "\n".join(lines)

        # Assemble context block
        context = f"""
User Name    : {user['name']}
AI Name      : {user['ai_name']}
Date         : {datetime.now().strftime('%A, %B %d %Y')}
Current Time : {datetime.now().strftime('%I:%M %p')}

{today_summary}

{yesterday_summary}

{goals_text}
        """.strip()

        return context

    # ── Weekly Report ──────────────────────────────────────

    def get_weekly_report(self) -> str:
        """
        Generates a text-based weekly analytics report.

        WHY pandas here?
        We need aggregations (count, filter, percentage) over
        a week of data. pandas makes this 3 lines instead of
        20 lines of SQL + Python loops.

        Returns a formatted string for display in the UI.
        """
        import pandas as pd

        convos = self.db.get_conversations_dataframe(self.user_id)
        plans  = self.db.get_plans_dataframe(self.user_id)

        # Filter conversations to the past 7 days
        if not convos.empty:
            convos["created_at"] = pd.to_datetime(convos["created_at"])
            week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
            week_convos = convos[convos["created_at"] >= week_ago]
            total_msgs  = len(week_convos)
            user_msgs   = len(week_convos[week_convos["role"] == "user"])
        else:
            total_msgs = user_msgs = 0

        # Filter plans to the past 7 days
        if not plans.empty:
            plans["planned_for"] = pd.to_datetime(plans["planned_for"])
            week_ago   = pd.Timestamp.now() - pd.Timedelta(days=7)
            week_plans = plans[plans["planned_for"] >= week_ago]
            total_tasks = len(week_plans)
            done_tasks  = len(week_plans[week_plans["is_done"] == 1])
            completion  = round(done_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
        else:
            total_tasks = done_tasks = completion = 0

        report = f"""
╔══════════════════════════════╗
  WEEKLY AURA REPORT
╠══════════════════════════════╣
  Conversations  : {total_msgs}
  Your Messages  : {user_msgs}
  Tasks Created  : {total_tasks}
  Tasks Done     : {done_tasks}
  Completion Rate: {completion}%
╚══════════════════════════════╝
        """.strip()

        return report
