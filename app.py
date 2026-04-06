# ============================================================
# app.py — AURA CLI Entrypoint (Terminal Mode)
# ============================================================
# PURPOSE:
#   A simple command-line interface to AURA.
#   Useful for quick testing without launching the full
#   Streamlit web app.
#
# NOTE:
#   The primary interface is streamlit_app.py (the web app).
#   This CLI is a developer tool — not the product itself.
#
# USAGE:
#   python app.py
# ============================================================

import getpass
from brain import AuraBrain
from database import AuraDatabase
from datetime import datetime
from helper import get_greeting


def setup_aura() -> tuple[AuraBrain, dict]:
    """
    Initialize AURA for the CLI session.

    Flow:
      - If no users exist → first-time setup (create account)
      - If a user exists → load the first user and greet them

    WHY use the first user for CLI?
    The CLI is a developer/test tool. Multi-user auth lives in
    the Streamlit web app. The CLI just picks the first account.

    Returns:
        (AuraBrain instance, user dict)
    """
    db = AuraDatabase()

    print("\n" + "=" * 50)
    print("          A U R A")
    print("     Your Personal AI Companion")
    print("=" * 50)

    # Try to load existing user
    # We use get_user_by_id(1) as the default CLI user.
    # For multi-user support, use the web app.
    user = db.get_user_by_id(1)

    if not user:
        # First-time setup
        print("\n[ First-Time Setup ]")
        name      = input("Your name: ").strip()
        ai_name   = input("Name your AI companion: ").strip() or "AURA"
        email     = input("Email: ").strip()
        password  = getpass.getpass("Password: ").strip()
        wake_time = input("Wake-up time (e.g. 07:00): ").strip() or "07:00"

        result = db.register_user(
            name=name,
            email=email,
            password=password,
            ai_name=ai_name,
            wake_time=wake_time,
        )

        if not result["success"]:
            print(f"\nSetup failed: {result.get('message')}")
            exit(1)

        user = db.get_user_by_id(1)
        print(f"\nWelcome, {name}! {ai_name} is ready.")
    else:
        greeting = get_greeting(datetime.now().hour)
        print(f"\n{greeting}, {user['name']}! {user['ai_name']} is online.")

    brain = AuraBrain(user["id"])
    return brain, user


def add_today_plans(brain: AuraBrain, user: dict):
    """
    Prompt the user to add plans for today before chatting.
    Press Enter with no input to skip / finish.
    """
    print("\n[ Today's Plans ]")
    print("Add your plans for today. Press Enter alone when done.\n")

    while True:
        plan = input("  Add plan: ").strip()
        if not plan:
            break
        brain.memory.db.add_plan(user["id"], plan)
        print(f"  ✓ Added: {plan}")


def chat_loop(brain: AuraBrain, user: dict):
    """
    Main REPL (Read-Eval-Print Loop) for CLI chat.

    Commands:
      quit  → exit
      plans → show today's plans
      add   → add a new plan
    """
    ai_name   = user["ai_name"]
    user_name = user["name"]

    print("\n" + "=" * 50)
    print(f"  {ai_name} is listening.")
    print("  Type 'plans' | 'add' | 'quit'")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input(f"{user_name}: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Graceful exit on Ctrl+C or Ctrl+D
            print(f"\n\n{ai_name}: Goodbye! You did great today.")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print(f"\n{ai_name}: Goodbye, {user_name}! You did great today.")
            break

        if user_input.lower() == "plans":
            print(f"\n{brain.memory.get_today_schedule()}\n")
            continue

        if user_input.lower() == "add":
            plan = input("  New plan: ").strip()
            if plan:
                brain.memory.db.add_plan(user["id"], plan)
                print(f"  ✓ Added: {plan}\n")
            continue

        # Regular chat — send to AI
        print(f"\n{ai_name}: ", end="", flush=True)
        reply = brain.think(user_input)
        print(f"{reply}\n")


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    brain, user = setup_aura()
    add_today_plans(brain, user)
    chat_loop(brain, user)
