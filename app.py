# ============================================================
# app.py — AURA Voice Entry Point
# ============================================================
# Pure voice interface. No keyboard needed.
# Speak → AURA thinks → AURA acts + speaks back.
#
# USAGE:
#   .venv/bin/python app.py
#
# EXIT:
#   Say "stop", "quit", "goodbye" — or press Ctrl+C
# ============================================================

import getpass
from datetime import datetime
from brain import AuraBrain
from database import AuraDatabase
from core.helper import get_greeting
from core.voice import AuraVoice


def setup_aura() -> tuple[AuraBrain, dict]:
    """
    Load or create the user, speak the greeting.
    First-time setup uses keyboard (one time only).
    Every run after that is fully voice.
    """
    db   = AuraDatabase()
    user = db.get_user_by_id(1)

    print("\n" + "=" * 50)
    print("          A U R A")
    print("     Your Personal AI Companion")
    print("=" * 50)

    if not user:
        # First-time setup — keyboard only happens once ever
        print("\n[ First-Time Setup — one time only ]\n")
        name      = input("Your name: ").strip()
        ai_name   = input("Name your AI (e.g. Symbite): ").strip() or "Symbite"
        email     = input("Email: ").strip()
        password  = getpass.getpass("Password: ")
        wake_time = input("Wake-up time (e.g. 07:00): ").strip() or "07:00"

        result = db.register_user(
            name=name, email=email,
            password=password, ai_name=ai_name,
            wake_time=wake_time,
        )
        if not result["success"]:
            print(f"Setup failed: {result.get('message')}")
            exit(1)

        user = db.get_user_by_id(1)

    voice    = AuraVoice()
    greeting = get_greeting(datetime.now().hour)
    brain    = AuraBrain(user["id"])

    print(f"\n{greeting}, {user['name']}. {user['ai_name']} is online.\n")
    voice.speak(f"{greeting}, Boss. I'm online and ready. Just talk.")

    return brain, user, voice


def run(brain: AuraBrain, user: dict, voice: AuraVoice):
    """
    Main voice loop.
    Listens continuously — no wake word, no keyboard.
    Every spoken sentence goes to Claude.
    Claude can speak back AND open apps/browser.
    """
    ai_name = user["ai_name"]

    print("=" * 50)
    print(f"  Just speak. {ai_name} is always listening.")
    print("  Say 'stop' or 'quit' to exit.")
    print("=" * 50 + "\n")

    while True:
        try:
            # Listen for whatever the user says (8 seconds max)
            user_input = voice.listen()

            # Nothing heard — listen again silently
            if not user_input:
                continue

            print(f"\nYou: {user_input}")

            # Exit commands
            if any(w in user_input.lower() for w in ["stop", "quit", "goodbye", "shut down", "shutdown"]):
                farewell = "Shutting down. Talk soon, Boss."
                print(f"{ai_name}: {farewell}")
                voice.speak(farewell)
                break

            # Send to Claude — it decides what to do
            # (speak, fetch news, open browser, check weather, search web, etc.)
            print(f"{ai_name}: ", end="", flush=True)
            reply = brain.think(user_input)
            print(f"{reply}\n")
            voice.speak(reply)

        except (KeyboardInterrupt, EOFError):
            farewell = "Goodbye, Boss."
            print(f"\n{ai_name}: {farewell}")
            voice.speak(farewell)
            break


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    brain, user, voice = setup_aura()
    run(brain, user, voice)
