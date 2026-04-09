# ============================================================
# core/helper.py — Utility functions + Desktop Action Executor
# ============================================================
# Two things live here:
#   1. Simple utility functions (greetings etc.)
#   2. SystemExecutive — opens browser windows on your desktop
#
# HOW DESKTOP ACTIONS WORK:
#   Python's built-in `webbrowser` module can open any URL
#   in your default browser with one line of code.
#   No API key, no extra library needed.
#   When AURA calls open_world_briefing(), Python tells macOS
#   "open this URL" — macOS opens Chrome/Safari automatically.
#
#   For side-by-side windows we open two URLs back to back.
#   macOS opens each as a new tab. You arrange them yourself
#   or we can use AppleScript in Phase 2 to auto-tile them.
# ============================================================

import time
import webbrowser   # Python built-in — talks directly to macOS to open URLs


# ── Greeting Utilities ────────────────────────────────────

def say_hello(name):
    return f"Hello {name}, welcome to AURA."

def add_numbers(a, b):
    return a + b

def get_day_motivation(name):
    return f"You've got this {name}. Keep building."

def get_greeting(hour: int) -> str:
    """Returns time-appropriate greeting based on the hour (0-23)."""
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    elif hour < 21:
        return "Good Evening"
    else:
        return "Good Night"


# ── SystemExecutive ───────────────────────────────────────
# Handles all physical desktop actions.
# brain.py calls these when Claude decides to open something.

class SystemExecutive:

    @staticmethod
    def open_browser(url: str) -> str:
        """
        Opens a URL in the default browser.

        webbrowser.open() is a Python standard library function.
        On macOS it calls the system's 'open' command which
        launches whatever browser you've set as default.
        Returns a string so brain.py can send it back to Claude
        as tool result confirmation.
        """
        try:
            webbrowser.open(url)
            return f"Opened in browser."
        except Exception as e:
            return f"Couldn't open browser: {e}"

    @staticmethod
    def open_world_briefing() -> str:
        """
        Opens the full world intelligence view — two windows:
          1. worldmonitor.app  — live world map with conflict/event markers
          2. Bloomberg live    — live financial + geopolitical news stream

        WHY TWO URLS?
        This mimics exactly what FRIDAY shows Tony — a world map
        on the left, live news feeds on the right.
        We open them 1.5 seconds apart so the browser has time
        to load the first tab before opening the second.
        """
        # Tab 1 — Live world map (same site as in the screenshot)
        webbrowser.open("https://worldmonitor.app/")

        # Small pause so macOS opens them as separate tabs, not at the same instant
        time.sleep(1.5)

        # Tab 2 — Bloomberg live news (geopolitics, markets, world events)
        webbrowser.open("https://www.bloomberg.com/live")

        return "World briefing open, Boss. Map and live feed are up."

    @staticmethod
    def open_live_news() -> str:
        """
        Opens BBC News live — breaking news, world events.
        Used when user asks about news without needing the full map.
        """
        webbrowser.open("https://www.bbc.com/news")
        return "BBC News is open."

    @staticmethod
    def open_weather_map() -> str:
        """
        Opens zoom.earth — live satellite weather map.
        Shows real cloud cover, storms, temperature overlays globally.
        Much more visual than a text weather report.
        """
        webbrowser.open("https://zoom.earth/")
        return "Live weather map is open."

    @staticmethod
    def open_youtube_news() -> str:
        """
        Opens YouTube's live news stream.
        Good for: Bloomberg TV, BBC World live, Al Jazeera English live.
        """
        # Al Jazeera English — 24/7 live stream, free, no login
        webbrowser.open("https://www.youtube.com/watch?v=F6sLTWKoq0s")
        return "Live news stream is open."

    @staticmethod
    def open_url(url: str) -> str:
        """
        Open any URL the user asks for.
        Used by the open_url tool in brain.py for
        'open my GitHub', 'open YouTube', anything.
        """
        if not url.startswith("http"):
            url = "https://" + url
        return SystemExecutive.open_browser(url)
