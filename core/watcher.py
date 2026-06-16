import time
import threading
import logging
from datetime import datetime
from core.morning import MorningBriefing
from core.evening import EveningSummary
from database import AuraDatabase

logger = logging.getLogger("AURA.watcher")

class SymbiteWatcher:

    def __init__(self, morning: MorningBriefing, evening: EveningSummary,db: AuraDatabase):
        self._morning = morning
        self._evening = evening
        self._db = db
        self._fired : set[str] = set()
    def _in_window(self, target_time: str)->bool:
        try:
            now = datetime.now().strftime("%H:%M")
            now_dt = datetime.strptime(now, "%H:%M")
            target_dt = datetime.strptime(target_time, "%H:%M")
            diff = abs((now_dt - target_dt).total_seconds()/60)
            return diff <=5
        except ValueError:
            return False

    def _run(self) -> None:
        logger.info("SymbiteWatcher started")
        while True:
            try:
                now_hour = datetime.now().hour
                if now_hour == 0:
                    self._fired.clear()

                users = self._db.get_all_users()
                for user in users:
                    user_id    = user["id"]
                    wake_time  = user.get("wake_time")
                    sleep_time = user.get("sleep_time")

                    morning_key = f"{user_id}_morning"
                    if wake_time and self._in_window(wake_time) and morning_key not in self._fired:
                        self._fired.add(morning_key)
                        briefing = self._morning.generate(user_id)
                        self._db.save_message(user_id, "assistant", briefing)
                        logger.info("Morning briefing fired for user %s", user_id)

                    evening_key = f"{user_id}_evening"
                    if sleep_time and self._in_window(sleep_time) and evening_key not in self._fired:
                        self._fired.add(evening_key)
                        summary = self._evening.generate(user_id)
                        self._db.save_message(user_id, "assistant", summary)
                        logger.info("Evening summary fired for user %s", user_id)

            except Exception as e:
                logger.error("Watcher loop error: %s", e)

            time.sleep(60)
    def start(self) -> None:
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        logger.info("SymbiteWatcher armed")



