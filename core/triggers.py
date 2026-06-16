import logging
from datetime import datetime, timedelta
from database import AuraDatabase
from connectors.calendar import CalendarConnector

logger = logging.getLogger("AURA.triggers")


class TriggerEngine:
    """Detects conditions worth speaking about. Never speaks itself —
    the watcher decides what actually gets delivered."""

    def __init__(self, db: AuraDatabase, calendar: CalendarConnector) -> None:
        self._db = db
        self._calendar = calendar

    def check(self, user_id: int) -> list[dict]:
        alerts: list[dict] = []

        calendar_alerts = self._check_calendar(user_id)
        alerts.extend(calendar_alerts)

        overdue_alerts = self._check_overdue(user_id)   # ← overdue, not calendar again
        alerts.extend(overdue_alerts)

        if alerts:
            logger.debug(
                "Trigger conditions matched for user %s: %d alerts",
                user_id, len(alerts),
            )
        return alerts

    def _check_calendar(self, user_id: int) -> list[dict]:
        # TODO(chunk3) : alert when an event starts within 15 minutes
        return []

    def _check_overdue(self, user_id: int) -> list[dict]:
        """condition clock: after 12:00, alert if today's plans are still open """
        now = datetime.now()

        if now.hour < 12:
            logger.debug(" guard 1 activate : before noon . overdue clock suppressed.")
            return []
        plans = self._db.get_today_plans(user_id)

        open_plans = [ p for p in plans if not p["is_done"]]

        if not open_plans:
            logger.debug(" guard 2: activate : No uncompleted tasks found of today for user %s", user_id)
            return []

        today = now.strftime("%Y-%m-%d")
        count = len(open_plans)
        return[{
            "key": f"{user_id}_overdue_{today}",
            "message":f"Boss , {count} task{'s' if count > 1 else ''} from today still open - want to pick one? "
        }]





