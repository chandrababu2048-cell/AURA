import logging
from database import AuraDatabase
from core.perception import AuraPerception

logger = logging.getLogger("AURA.twin")

class DigitalTwin:
    """ Twin class """
    def __init__(self,db :AuraDatabase, perception : AuraPerception) -> None:
        self._db = db
        self._perception = perception

    def get_stress_level(self, user_id: int) -> str:
        goals = self._db.get_active_goals(user_id)
        overdue = self._db.get_yesterday_plans(user_id)

        score = len(goals)+len(overdue)
        if score <= 2:
            return "low"
        if score <= 5:
            return "medium"
        return "high"
    def snapshot(self,user_id: int)->dict:
        perception = self._perception.observe(user_id)
        stress = self.get_stress_level(user_id)
        goals = self._db.get_active_goals(user_id)
        overdue = self._db.get_yesterday_plans(user_id)

        return {
            "stress": stress,
            "mood": perception.mood_signal.value,
            "energy": perception.day_load.value,
            "focus" : perception.time_of_day.value,
            "active_goals":len(goals),
            "overdue_tasks" :len(overdue),
        }
    def to_prompt_snippet(self, user_id: int)->str:
        s = self.snapshot(user_id)
        return(
            f"Boss state: {s['stress']} stress | "
            f"mood: {s['mood']} | "
            f"energy: {s['energy']} | "
            f"focus: {s['focus']} | "
            f"goals: {s['active_goals']} active | "
            f"overdue: {s['overdue_tasks']} tasks"

        )


