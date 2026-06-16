#start.py - Aura master launcher
# purpose:
# one command to start everything
#1 .fastAPI backend
#2. React frontend
#3. opens browser automatically
#4. samantha greets you

# usage: python start.py

import subprocess
import time
import webbrowser
import requests
from datetime import datetime, timedelta

def get_greeting()-> str:
    hour = datetime.now().hour
    if hour <12:
        return "good morning"
    elif hour <17:
        return "good afternoon"
    elif hour <21:
        return "good evening"
    else:
        return "good night"

def speak(text: str):
    subprocess.Popen(["say", "-v", "Samantha", "-r", "220", text])


def get_morning_briefing() -> str:
    """
    Calls our own AURA API to get plans and weather.
    Builds a morning briefing script for Samantha to speak.

    WHY call the API instead of importing database directly?
    The backend is already running. We ask it for data the same
    way the browser does. No duplicate database connections.

    HTTP GET = asking a server: "give me this data"
    requests.get(url) sends that ask and waits for the reply.
    response.json() converts the reply from JSON text → Python dict/list.
    """
    parts = []

    # ── Yesterday's summary ────────────────────────────────
    # timedelta(days=1) = subtract 1 day from today = yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        res = requests.get(
            "http://localhost:8000/plans",
            params={"user_id": 1, "date": yesterday},
            timeout=5,
        )
        yesterday_plans = res.json()
        if yesterday_plans:
            done  = sum(1 for p in yesterday_plans if p["is_done"])
            total = len(yesterday_plans)
            parts.append(f"Yesterday you completed {done} out of {total} tasks.")
    except Exception:
        pass  # backend not ready or no data — skip silently

    # ── Today's plans ──────────────────────────────────────
    try:
        res = requests.get(
            "http://localhost:8000/plans",
            params={"user_id": 1},
            timeout=5,
        )
        today_plans = res.json()
        total = len(today_plans)
        if total > 0:
            parts.append(f"You have {total} plans for today.")
        else:
            parts.append("No plans scheduled for today yet.")
    except Exception:
        pass

    # ── Weather ────────────────────────────────────────────
    try:
        res = requests.get("http://localhost:8000/weather", timeout=5)
        weather = res.json()
        if weather.get("success"):
            parts.append(
                f"Weather: {weather['temp']} degrees and {weather['condition']} in {weather['city']}."
            )
    except Exception:
        pass

    greeting = get_greeting()

    if not parts:
        return f"{greeting} Boss. I'm online and ready. What do you need?"

    return f"{greeting} Boss. " + " ".join(parts) + " Ready when you are."


def start_backend():
    return subprocess.Popen(
        ["venv/bin/uvicorn", "api.main:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def start_frontend():
    return subprocess.Popen(
        ["npm", "run", "dev","--prefix", "frontend"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

print("=" * 40)
print("AURA - Starting all systems")
print("=" * 40)

# start backend
print("[1/4] Starting backend...")
start_backend()
time.sleep(3)

# start frontend
print("[2/4] Starting frontend...")
start_frontend()
time.sleep(3)

# open browser
print("[3/4] Opening AURA interface...")
webbrowser.open("http://localhost:5173")
time.sleep(2)

# morning briefing
print("[4/4] AURA is ready!")
briefing = get_morning_briefing()
speak(briefing)
print(f"\nBriefing: {briefing}")
print("=" * 40)
print("AURA is running.")
print("Backend:  http://localhost:8000")
print("Frontend: http://localhost:5173")
print("=" * 40)

# keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    speak("Shutting down. Talk soon Boss.")
    print("\nAURA shut down.")


    
