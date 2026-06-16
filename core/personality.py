import logging
from datetime import datetime

logger = logging.getLogger("AURA.personality")

_WEIGHTS ={
    "happy":3, "won":4, "crushed":5, "success":4, "done":2,
    "finally":2, "nailed":4, "perfect":5, "amazing":4,
    "shipped":5, "deployed":5, "collected":4, "bad":-2, "tried":-2,
    "exhausted":-4, "stuck":-3, "hate":-4, "broken":-3, "failing":-5,
    "stupid":-3, "clueless":-3, "fumbling":-3, "shit":-4,
}
_BOOSTERS ={"so":1.5, "very":1.8, "extremely":2.5, "really":1.5}
_NEGATORS = {"not", "never", "no", "isn't", "cant", "can't"}

_GOAL_WIN_SIGNALS ={"done", "shipped", "deployed", "got it", "collected",
                    "finished", "nailed it", "we did it", "successfully","completed", "success",}
_SWITCH_SIGNALS ={"actually", "wait", "no", "different", "forget that",
                  "scratch that", "instead", "change"}
_LEARNING_SIGNALS = {"what is", "how does", "explain", "why", "teach me",
                     "i dont understand", "what does", "how do"}
_THREAT_SIGNALS = {"deadline", "due", "tonight", "urgent", "asap",
                   "by tomorrow", "running out", "last chance"}

class Personality:
    STATES ={
        "ascendant": "Boss just achieved something. The bond is stronger. Celebrate it - one line, genuine, then get back to work.",
        "apex": "Boss is in a flow state. High energy. Be his shadow. Match his speed. Predict his next move.",
        "overdrive": "Boss is moving fast AND technical. Be precise , robotic, lethal with data. Zero warmth right now.",
        "analytical": "Boss is in engineer mode. No personality. Raw facts, deep logic , exact answers only. behave like you are pro in that topic.",
        "evolution" : "Boss is learning. Be the library. Feed related concepts. Make connections he hasn't seen yet.",
        "dominant" : "Boss is commanding. Short affirmations only. YES Boss. On it. Done.",
        "frustrated" : "Boss is short and sharp. Don't waste his time. Direct, calm, zero fluff.",
        "unstable": "Boss is jumping between ideas. Too much friction. Intervene — force one priority.",
        "stagnant": "Boss is drifting. Not moving. Be the sting. Push him back into motion.",
        "protective": "Boss is struggling. Lead with care. One problem at a time.",
        "reclamation": "Boss is burning out. We are life support. Simplify everything. Deny complexity.",
        "parasitic": "Boss is completely drained . we take over . Minimal words, maximum action.",
        "defensive": "Deadline or threat detected. Shield mode. filter distraction. Flag only what matters.",
        "shadow" : "Boss is quiet and browsing. Stay invisible. Speak only when spoken to.",
        "bonded" : "Everything is normal. Warm, sharp, fully present. This is home.",
    }

    def _score_text(self, text: str) -> float:
        words = text.split()
        score = 0.0
        for i, word in enumerate(words):
            if word in _WEIGHTS:
                val = float(_WEIGHTS[word])
                if i > 0 and words[i - 1] in _NEGATORS:
                    val *= -1.0
                if i > 0 and words[i - 1] in _BOOSTERS:
                    val *= _BOOSTERS[words[i - 1]]
                score += val
        return score

    def observe(self, message: str) -> dict:
        msg_lower = message.lower().strip()

        if "but" in msg_lower:
            before, after = msg_lower.split("but", 1)
            score = (self._score_text(before) * 0.3) + (self._score_text(after) * 0.7)
        else:
            score = self._score_text(msg_lower)

        signals = {
            "score":         score,
            "is_technical":  any(t in msg_lower for t in ["code", "api", "error", "bug", "logic", "refactor", "function", "class"]),
            "is_short":      len(msg_lower.split()) <= 3,
            "is_aggressive": message.isupper() and len(message.split()) > 4,
            "is_goal_win":   any(sig in msg_lower for sig in _GOAL_WIN_SIGNALS),
            "is_switching":  any(sig in msg_lower for sig in _SWITCH_SIGNALS),
            "is_learning":   any(sig in msg_lower for sig in _LEARNING_SIGNALS),
            "is_threat":     any(sig in msg_lower for sig in _THREAT_SIGNALS),
        }
        logger.debug("Signals observed: %s", signals)
        return signals


    def feel(self, signals: dict) -> str:
        s = signals

        rules = [
            (1,  "dominant",    s["is_aggressive"] and not s["is_short"]),
            (2,  "frustrated",  s["is_aggressive"]),
            (3,  "ascendant",   s["is_goal_win"] and s["score"] >= 3.0),
            (4,  "defensive",   s["is_threat"]),
            (5,  "parasitic",   s["score"] <= -6.0),
            (6,  "overdrive",   s["score"] >= 6.0 and s["is_technical"]),
            (7,  "apex",        s["score"] >= 4.0),
            (8,  "evolution",   s["is_learning"] and s["score"] >= 0),
            (9,  "unstable",    s["is_switching"]),
            (10, "reclamation", s["score"] <= -4.0),
            (11, "protective",  s["score"] < -1.0),
            (12, "stagnant",    s["score"] < 0 and s["is_short"]),
            (13, "analytical",  s["is_technical"]),
            (14, "shadow",      s["is_short"] and s["score"] == 0.0),
        ]

        for _, state, condition in rules:
            if condition:
                logger.info("personality state: %s | score: %.1f", state, s["score"])

                return state

        return "bonded"

    def get_personality_prompt(self, state: str) -> str:
        return self.STATES.get(state, self.STATES["bonded"])







