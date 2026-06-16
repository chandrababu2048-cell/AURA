import logging
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import json

logger = logging.getLogger("AURA.SPEC")

class SpecStatus(str, Enum):
    SELECTED = "selected"   #GOAL DEFINED - INTENTION SET
    PROJECTED = "projected" # AFFIRMATION GENERATED - VISUALISING IT
    EXPECTED = "expected" # DAILY REINFORCEMENT - BOSS BELIEVES IT'S COMING
    COLLECTED= "collected" # ACHIEVED - SYMBIOTE BOND STRENGTHENS

class Goal(BaseModel):
    """The core objective model. in production , this is a single source of truth
    for a user's id intent"""
    id: Optional[int] = None
    user_id: int
    goal_text : str
    steps : List[str] = Field(default_factory=list)
    deadline : Optional[str] = None
    status : SpecStatus = SpecStatus.SELECTED
    created_at : str = Field(default_factory= lambda: datetime.now().isoformat())
    completed_steps : List[str] = Field(default_factory=list)
    collected_at : Optional[str] = None

    @property
    def progress(self)-> float:
        """Calculate 0.0 to 1.0 progress automatically."""
        if not self.steps: return 0.0
        return min(len(self.completed_steps) / len(self.steps), 1.0)
    @property
    def time_until_due(self) -> Optional[float]:
        """logic for the 'Threat' signal in personality.py"""
        if not self.deadline: return None
        target = datetime.fromisoformat(self.deadline)
        delta = target - datetime.now()
        return delta.total_seconds() / 3600 # returns hours

    @property
    def is_critical(self) -> bool:
        """ heuristic signal : if the deadline is < 12, this is threat."""
        hours = self.time_until_due
        return hours is not None and 0 < hours < 12

class SpecEngine:
    def __init__(self, db):
        self._db = db
    def select(self, user_id: int, goal_text: str)-> Goal:
        goal = Goal(user_id = user_id, goal_text = goal_text)
        goal_id = self._db.spec_create_goal(goal.model_dump())
        goal.id  = goal_id
        logger.info("SPEC SELECT | goal_id=%d |%s", goal_id, goal_text)
        return goal
    def project(self, goal_id: int, user_id: int, steps: List[str]) -> Goal:
        self._db.spec_set_steps(goal_id, user_id, json.dumps(steps))
        logger.info("SPEC PROJECT| goal_id =%d | %d steps", goal_id, len(steps))
        return self._load(goal_id, user_id)

    def expect(self,goal_id: int, user_id: int, deadline:str) -> Goal:
        self._db.spec_set_deadline(goal_id, user_id, deadline)
        logger.info("SPEC EXPECT | goal_id =%d | deadline =%s", goal_id, deadline)
        return self._load(goal_id, user_id,)

    def complete_step(self, goal_id: int , user_id: int, step: str) -> Goal:
        goal = self._load(goal_id, user_id)
        if step in goal.steps and step not in goal.completed_steps:
            goal.completed_steps.append(step)
            self._db.spec_set_completed_steps(goal_id, user_id, json.dumps(goal.completed_steps))
            logger.info("SPEC STEP  | goal_id=%d | step: %s | progress: %.0f%%", goal_id, step, goal.progress * 100)
            return goal
        return goal

    def collect(self , goal_id: int , user_id: int) -> Goal:
        collected_at = datetime.now().isoformat()
        self._db.spec_collect_goal(goal_id , user_id , collected_at)
        logger.info("SPEC COLLECT | goal_id=%d - ascendant", goal_id)
        return self._load(goal_id, user_id)
    def get_active(self, user_id:int ) -> List[Goal]:
        rows = self._db.spec_get_active_goals(user_id)
        return[Goal(**self._parse(r)) for r in rows]

    def to_prompt_snippet(self, user_id: int) -> str:
        goals = self.get_active(user_id)
        if not goals:
            return ""
        lines = []
        for g in goals:
            deadline_str = f"| due: {g.deadline}" if g.deadline else ""
            urgent_str = " URGENT" if g.is_critical else ""
            progress_str = f" | { g.progress:.0%} done" if g.steps else ""
            lines.append(
                f"-[{g.status.value.upper()}] {g.goal_text}"
                f" {deadline_str}{progress_str}{urgent_str}"

            )
        return "### ACTIVE GOALS ###\n" + "\n".join(lines)

    def _load(self, goal_id: int, user_id: int) -> Goal:
        row = self._db.spec_get_goal(goal_id, user_id)
        return Goal(**self._parse(row))
    def _parse(self, row: dict) -> dict:
        for field in ("steps" , "completed_steps"):
            if row.get(field)and isinstance(row[field], str):
                row[field] = json.loads(row[field])
        return row

