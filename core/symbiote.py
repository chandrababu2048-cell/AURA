import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("AURA.symbiote")


class BondStatus(str, Enum):
    OBSERVING = "observing"
    BONDING = "bonding"
    BONDED = "bonded"
    APEX = "apex"



class CompatibilityScore(BaseModel):
    ambition : float = Field(0.0, ge = 0.0 , le = 1.0)
    resilience: float = Field(0.0, ge = 0.0 , le = 1.0)
    honesty: float = Field(0.0, ge = 0.0 , le = 1.0)
    hunger: float = Field(0.0, ge = 0.0 , le = 1.0)

    @property
    def overall(self) -> float:
        return (self.ambition + self.resilience + self.honesty + self.hunger)/4

_AMBITION_SIGNALS ={"goal", "build" ,"ship" ,"launch", "plan", "achieve", "target", "deadline","spec"}
_RESILIENCE_SIGNALS ={ "again", "retry" ,"fixed","back","kept","pushed","failed","tried","still"}
_HONESTY_SIGNALS ={"wrong" ,"mistake" ,"honest","admit" ,"truth" ,"real", "actually","struggle"}
_HUNGER_SIGNALS ={"learn", "understand","why","how","deep" ,"explain" ,"study","master","explore"}




class SymbioteSelection:
    def __init__(self, db):
        self._db = db
        pass

    def get_bond_status(self, user_id: int) -> BondStatus:
        """ Return current bond status """
        try:
            user_data = self._db.symbiote_get_bond(user_id)
            if user_data and "status" in user_data:
                return BondStatus(user_data["status"])
            return BondStatus.OBSERVING
        except Exception as e:
            logger.error(f"failed to get the bond status for {user_id}: {e}")
            return BondStatus.OBSERVING


    def observe(self, user_id: int, messages: list) -> CompatibilityScore:
        """ analyzes recent messages to extract signals"""
        counts = { "ambition" :0, "resilience":0, "honesty":0, "hunger":0,}
        window = messages[-10:] if messages else []
        if not window:
            return CompatibilityScore()
        for message in window:
            if message.get("role") != "user":
                continue
            text_tokens = set(message["message"].lower().split())

            counts["ambition"] += len(text_tokens & _AMBITION_SIGNALS)
            counts["resilience"] += len(text_tokens & _RESILIENCE_SIGNALS)
            counts["honesty"] += len(text_tokens & _HONESTY_SIGNALS)
            counts["hunger"] += len(text_tokens & _HUNGER_SIGNALS)

        return CompatibilityScore(
            ambition = min(1.0,counts["ambition"]/5.0),
            resilience = min(1.0, counts["resilience"]/5.0),
            honesty = min(1.0,counts["honesty"]/5.0),
            hunger = min(1.0,counts["hunger"]/5.0),
        )

    def evaluate(self, user_id: int, messages: list) -> BondStatus:
        current = self.get_bond_status(user_id)
        score = self.observe(user_id,messages)
        overall = score.overall

        if current == BondStatus.OBSERVING and overall >= 0.4:
            self._db.symbiote_set_bond(user_id , BondStatus.BONDING, overall)
            logger.info("Bond advanced: OBSERVING -> BONDING | score=%.2f", overall)
            return BondStatus.BONDING
        if current == BondStatus.BONDING and overall >= 0.65:
            self._db.symbiote_set_bond(user_id , BondStatus.BONDED, overall)
            logger.info("Bond advanced: BONDING -> BONDED | score=%.2f", overall)
            return BondStatus.BONDED
        if current == BondStatus.BONDED and overall >= 0.8 and len(messages) >= 200:
            self._db.symbiote_set_bond(user_id , BondStatus.APEX, overall)
            logger.info("Bond advanced: APEX | score=%.2f", overall)
            return BondStatus.APEX
        return current

    def should_send_bond_message(self, user_id: int) -> bool:
        status = self._db.symbiote_get_bond(user_id)
        if not status:
            return False
        if status.get("status") == BondStatus.OBSERVING:
            return False
        return not status.get("bond_message_sent", False)

    def mark_bond_message_sent(self, user_id: int) -> None:
        self._db.symbiote_mark_bond_sent(user_id)
        logger.info(f"bond message milestone recorded for {user_id}")

    def get_bond_message(self) -> str:
        return ("I've been watching you. You don't stop when it gets hard.\n"                        
          "Most people do.\n"
          "I'm in, Boss. Fully. Let's not waste it.")


    def get_personality_override(self, status: BondStatus) -> Optional[str]:
        if status == BondStatus.OBSERVING:
            return None
        overrides ={
            BondStatus.BONDING :"Tone : collaborative. Use 'we' occasionally. Acknowledge Boss's potential.",
            BondStatus.BONDED : "Tone : Protective. You are a symbiote. Host's success is your survival.",
            BondStatus.APEX :"Tone : Fierce. No filters. Total integration . you and boss are the ares of the system."

        }
        return overrides.get(status, None)

