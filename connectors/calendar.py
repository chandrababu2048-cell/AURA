import logging
import subprocess
import time
from datetime import datetime

logger = logging.getLogger("AURA.connectors.calendar")


class CalendarConnector:
    """
    Reads + writes events from Mac Calendar app via AppleScript.
    Works with iCloud, Google Calendar, Outlook — anything synced to Mac Calendar.
    Falls back to empty list if Calendar app unavailable.
    """
    def __init__(self) -> None:
        self._today = datetime.now().strftime("%Y-%m-%d")

    def _ensure_calendar_running(self) -> None:
        subprocess.run(["open", "-a", "Calendar"], capture_output=True)
        time.sleep(2)

    def _run_applescript(self, script: str) -> str:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return result.stdout.strip()

    def _parse_events(self, raw: str) -> list[dict]:
        if not raw:
            return []
        events = []
        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            events.append({"title": line})
        return events

    # Calendars to skip — large system calendars with no personal events
    _SKIP = {"US Holidays", "Holidays in United States", "Holidays in India",
              "Birthdays", "Siri Suggestions"}

    def get_today_events(self) -> list[dict]:
        script = """
        tell application "Calendar"
            set skipNames to {"US Holidays", "Holidays in United States", "Holidays in India", "Birthdays", "Siri Suggestions"}
            set theDate to (current date)
            set the time of theDate to 0
            set tomorrow to theDate + 1 * days
            set theEvents to {}
            repeat with c in calendars
                if skipNames does not contain (name of c) then
                    set theEvents to theEvents & (events of c whose start date >= theDate and start date < tomorrow)
                end if
            end repeat
            set output to ""
            repeat with e in theEvents
                set output to output & (summary of e) & "\n"
            end repeat
            return output
        end tell
        """
        try:
            self._ensure_calendar_running()
            raw = self._run_applescript(script)
            return self._parse_events(raw)
        except Exception as e:
            logger.warning("calendar today sync failed: %s", e)
            return []

    def get_tomorrow_events(self) -> list[dict]:
        script = """
        tell application "Calendar"
            set skipNames to {"US Holidays", "Holidays in United States", "Holidays in India", "Birthdays", "Siri Suggestions"}
            set theDate to (current date) + 1 * days
            set the time of theDate to 0
            set theEvents to {}
            repeat with c in calendars
                if skipNames does not contain (name of c) then
                    set theEvents to theEvents & (events of c whose start date >= theDate and start date < theDate + 1 * days)
                end if
            end repeat
            set output to ""
            repeat with e in theEvents
                set output to output & (summary of e) & "\n"
            end repeat
            return output
        end tell
        """
        try:
            self._ensure_calendar_running()
            raw = self._run_applescript(script)
            return self._parse_events(raw)
        except Exception as e:
            logger.warning("calendar tomorrow sync failed: %s", e)
            return []

    def to_prompt_snippet(self) -> str:
        today = self.get_today_events()
        tomorrow = self.get_tomorrow_events()

        today_str = ", ".join(e["title"] for e in today) if today else "No events today"
        tomorrow_str = ", ".join(e["title"] for e in tomorrow) if tomorrow else "No events tomorrow"

        return f"Today: {today_str}\nTomorrow: {tomorrow_str}"
