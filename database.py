# ============================================================
# database.py — AURA Data Layer
# ============================================================
# PURPOSE:
#   All database read/write logic lives here and ONLY here.
#   No SQL anywhere else in the codebase.
#
# WHY SQLite?
#   - Zero setup: no separate DB server needed
#   - Ships as a single file (aura_data/aura.db)
#   - Perfect for a v1 product — scales to ~100k rows easily
#   - Easy to inspect with tools like DB Browser for SQLite
#
# WHY bcrypt for passwords?
#   Plain-text passwords are a critical security vulnerability.
#   bcrypt hashes are one-way — even if someone steals the DB,
#   they can't recover passwords. Industry standard.
#
# SCHEMA OVERVIEW:
#   user          — one row per registered account
#   plans         — daily tasks/objectives per user
#   goals         — long-term goals per user
#   conversations — full chat history per user
#
# HOW TO SCALE LATER:
#   Replace SQLite with PostgreSQL by swapping the connect()
#   method. Everything else stays the same.
# ============================================================

import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta

# ── File Paths ─────────────────────────────────────────────
# Store the DB in a dedicated folder so it's easy to back up
# or exclude from version control via .gitignore.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "aura_data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH  = os.path.join(DATA_DIR, "aura.db")


class AuraDatabase:
    """
    Data Access Object (DAO) for all AURA persistence.

    Every method opens its own connection, does its work,
    and closes it. WHY? SQLite connections aren't thread-safe
    across Streamlit reruns. Open-use-close is the safest pattern.
    """

    def __init__(self):
        self.db_path = DB_PATH
        self._create_tables()

    # ── Connection ─────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        """
        Open and return a new SQLite connection.
        row_factory = sqlite3.Row lets us access columns by name
        (row["name"]) instead of index (row[0]). Much cleaner.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Table Creation ─────────────────────────────────────

    def _create_tables(self):
        """
        Create all tables if they don't already exist.
        Called once on startup — safe to call repeatedly.
        Also runs schema migrations for older databases.
        """
        conn = self._connect()
        cursor = conn.cursor()

        # USER TABLE
        # email UNIQUE ensures no duplicate accounts
        # password stores bcrypt hash — never plain text
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    NOT NULL UNIQUE,
                password   TEXT    NOT NULL,
                ai_name    TEXT    DEFAULT 'AURA',
                wake_time  TEXT    DEFAULT '07:00',
                sleep_time TEXT    DEFAULT '22:30',
                created_at TEXT    NOT NULL
            )
        """)

        # PLANS TABLE
        # planned_for stores date as "YYYY-MM-DD" string
        # so we can filter by day easily (WHERE planned_for = ?)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                plan_text   TEXT    NOT NULL,
                planned_for TEXT    NOT NULL,
                is_done     INTEGER DEFAULT 0,
                created_at  TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)

        # GOALS TABLE
        # progress is 0–100 (percentage)
        # is_completed is a boolean (0 or 1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                goal_text    TEXT    NOT NULL,
                deadline     TEXT,
                progress     INTEGER DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                created_at   TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)

        # CONVERSATIONS TABLE
        # role is either "user" or "assistant" — matches Claude's API format
        # We store full history so the AI can reference past conversations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                role       TEXT    NOT NULL,
                message    TEXT    NOT NULL,
                created_at TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)

        conn.commit()
        conn.close()

        # Run migrations for older DB files that may be missing columns
        self._migrate()

    def _migrate(self):
        """
        Safe schema migration for legacy databases.
        SQLite doesn't support DROP COLUMN or complex ALTER TABLE,
        so we add missing columns one by one if they don't exist.
        This lets existing users upgrade without losing their data.
        """
        conn = self._connect()
        cursor = conn.cursor()

        # Check existing columns in the user table
        cursor.execute("PRAGMA table_info(user)")
        user_cols = {row["name"] for row in cursor.fetchall()}

        if "email" not in user_cols:
            cursor.execute("ALTER TABLE user ADD COLUMN email TEXT")
        if "password" not in user_cols:
            cursor.execute("ALTER TABLE user ADD COLUMN password TEXT")

        # Enforce unique email index even on upgraded DBs
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email "
            "ON user(email) WHERE email IS NOT NULL AND email != ''"
        )

        # Check existing columns in the plans table
        cursor.execute("PRAGMA table_info(plans)")
        plan_cols = {row["name"] for row in cursor.fetchall()}

        if "user_id"     not in plan_cols:
            cursor.execute("ALTER TABLE plans ADD COLUMN user_id INTEGER")
        if "planned_for" not in plan_cols:
            cursor.execute("ALTER TABLE plans ADD COLUMN planned_for TEXT")
        if "plan_text"   not in plan_cols:
            cursor.execute("ALTER TABLE plans ADD COLUMN plan_text TEXT")
        if "is_done"     not in plan_cols:
            cursor.execute("ALTER TABLE plans ADD COLUMN is_done INTEGER DEFAULT 0")

        # Migrate goals table — old DBs may be missing user_id and other cols
        cursor.execute("PRAGMA table_info(goals)")
        goals_cols = {row["name"] for row in cursor.fetchall()}

        if "user_id"      not in goals_cols:
            cursor.execute("ALTER TABLE goals ADD COLUMN user_id INTEGER")
        if "goal_text"    not in goals_cols:
            cursor.execute("ALTER TABLE goals ADD COLUMN goal_text TEXT")
        if "deadline"     not in goals_cols:
            cursor.execute("ALTER TABLE goals ADD COLUMN deadline TEXT")
        if "progress"     not in goals_cols:
            cursor.execute("ALTER TABLE goals ADD COLUMN progress INTEGER DEFAULT 0")
        if "is_completed" not in goals_cols:
            cursor.execute("ALTER TABLE goals ADD COLUMN is_completed INTEGER DEFAULT 0")

        # Migrate conversations table
        cursor.execute("PRAGMA table_info(conversations)")
        conv_cols = {row["name"] for row in cursor.fetchall()}

        if "user_id"    not in conv_cols:
            cursor.execute("ALTER TABLE conversations ADD COLUMN user_id INTEGER")
        if "role"       not in conv_cols:
            cursor.execute("ALTER TABLE conversations ADD COLUMN role TEXT")
        if "message"    not in conv_cols:
            cursor.execute("ALTER TABLE conversations ADD COLUMN message TEXT")
        if "created_at" not in conv_cols:
            cursor.execute("ALTER TABLE conversations ADD COLUMN created_at TEXT")

        conn.commit()
        conn.close()

    # ── Auth ───────────────────────────────────────────────

    def register_user(
        self,
        name: str,
        email: str,
        password: str,
        ai_name: str   = "AURA",
        wake_time: str = "07:00",
        sleep_time: str = "22:30",
    ) -> dict:
        """
        Create a new user account.

        Password is bcrypt-hashed before storage.
        bcrypt.gensalt() generates a random salt each time,
        so two users with the same password get different hashes.

        Returns:
            {"success": True}  or  {"success": False, "message": "..."}
        """
        try:
            hashed = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            )

            conn   = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user
                    (name, email, password, ai_name, wake_time, sleep_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name.strip(),
                    email.lower().strip(),   # always lowercase for consistent lookup
                    hashed.decode("utf-8"),  # store hash as string, not bytes
                    ai_name.strip() or "AURA",
                    wake_time.strip(),
                    sleep_time.strip(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            return {"success": True}

        except sqlite3.IntegrityError:
            # This fires when email already exists (UNIQUE constraint)
            return {"success": False, "message": "Email already registered."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login_user(self, email: str, password: str) -> dict:
        """
        Verify email + password.

        bcrypt.checkpw() safely compares a plain password against
        a stored hash without ever decrypting the hash.

        Returns:
            {"success": True, "user": {...}}  or
            {"success": False, "message": "..."}
        """
        try:
            conn   = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user WHERE email = ?",
                (email.lower().strip(),)
            )
            user = cursor.fetchone()
            conn.close()

            if not user:
                return {"success": False, "message": "Email not found."}

            password_ok = bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"].encode("utf-8"),
            )

            if password_ok:
                return {"success": True, "user": dict(user)}
            else:
                return {"success": False, "message": "Wrong password."}

        except Exception as e:
            return {"success": False, "message": str(e)}

    # ── User Queries ───────────────────────────────────────

    def get_user_by_id(self, user_id: int) -> dict | None:
        """Fetch a single user by primary key. Returns None if not found."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_ai_name(self, user_id: int, ai_name: str):
        """Let the user rename their AI companion after account creation."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user SET ai_name = ? WHERE id = ?",
            (ai_name.strip(), user_id)
        )
        conn.commit()
        conn.close()

    # ── Plans ──────────────────────────────────────────────

    def add_plan(self, user_id: int, plan_text: str, planned_for: str = None):
        """
        Insert a new daily plan.
        Defaults to today's date if planned_for is not provided.
        """
        date = planned_for or datetime.now().strftime("%Y-%m-%d")
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO plans (user_id, plan_text, planned_for, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, plan_text.strip(), date, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def get_plans_for_date(self, user_id: int, date: str) -> list[dict]:
        """Fetch all plans for a specific user on a specific date (YYYY-MM-DD)."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM plans WHERE user_id = ? AND planned_for = ? ORDER BY id",
            (user_id, date),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_today_plans(self, user_id: int) -> list[dict]:
        """Convenience wrapper — fetch today's plans."""
        return self.get_plans_for_date(
            user_id, datetime.now().strftime("%Y-%m-%d")
        )

    def get_yesterday_plans(self, user_id: int) -> list[dict]:
        """Fetch yesterday's plans — used in morning context summary."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self.get_plans_for_date(user_id, yesterday)

    def mark_plan_done(self, plan_id: int, user_id: int):
        """
        Mark a plan as completed.
        WHY include user_id in the WHERE clause?
        Prevents User A from marking User B's plans as done.
        This is a basic authorization check at the DB level.
        """
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plans SET is_done = 1 WHERE id = ? AND user_id = ?",
            (plan_id, user_id),
        )
        conn.commit()
        conn.close()

    def toggle_plan_done(self, plan_id: int, user_id: int):
        """
        Toggle a plan's done status (1 → 0, 0 → 1).
        Allows unchecking a plan that was accidentally marked done.
        user_id check prevents cross-user tampering.
        """
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plans SET is_done = CASE WHEN is_done = 1 THEN 0 ELSE 1 END "
            "WHERE id = ? AND user_id = ?",
            (plan_id, user_id),
        )
        conn.commit()
        conn.close()

    def delete_plan(self, plan_id: int, user_id: int):
        """Delete a plan. Same user_id safety check as mark_plan_done."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM plans WHERE id = ? AND user_id = ?",
            (plan_id, user_id),
        )
        conn.commit()
        conn.close()

    # ── Goals ──────────────────────────────────────────────

    def add_goal(self, user_id: int, goal_text: str, deadline: str = None):
        """Insert a long-term goal for the user."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals (user_id, goal_text, deadline, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, goal_text.strip(), deadline, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def get_active_goals(self, user_id: int) -> list[dict]:
        """Fetch all incomplete goals for a user."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM goals WHERE user_id = ? AND is_completed = 0 ORDER BY id",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_goal(self, goal_id: int, user_id: int):
        """Delete a goal. user_id check prevents cross-user tampering."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM goals WHERE id = ? AND user_id = ?",
            (goal_id, user_id),
        )
        conn.commit()
        conn.close()

    def complete_goal(self, goal_id: int, user_id: int):
        """Mark a goal as completed."""
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE goals SET is_completed = 1 WHERE id = ? AND user_id = ?",
            (goal_id, user_id),
        )
        conn.commit()
        conn.close()

    # ── Conversations ──────────────────────────────────────

    def save_message(self, user_id: int, role: str, message: str):
        """
        Persist a single chat message to the conversations table.
        Called after every user message and every AI reply.
        This builds the long-term memory that makes AURA feel
        like it actually knows you over time.
        """
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (user_id, role, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, role, message, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def get_recent_messages(self, user_id: int, limit: int = 20) -> list[dict]:
        """
        Fetch the most recent N messages for a user, in chronological order.
        WHY DESC then reverse? We want the LAST 20 messages but displayed
        oldest-first, which is the natural chat order.
        """
        conn   = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM conversations
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    # ── Analytics (for Weekly Report) ─────────────────────

    def get_conversations_dataframe(self, user_id: int):
        """
        Return all conversations as a pandas DataFrame.
        WHY pandas? It makes analytics (counts, filters, groupby)
        trivial compared to writing raw SQL for every metric.
        Used by the weekly report feature.
        """
        import pandas as pd
        conn = self._connect()
        df = pd.read_sql_query(
            """
            SELECT role, message, created_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY created_at ASC
            """,
            conn,
            params=(user_id,),
        )
        conn.close()
        return df

    def get_plans_dataframe(self, user_id: int):
        """Return all plans as a pandas DataFrame for weekly analytics."""
        import pandas as pd
        conn = self._connect()
        df = pd.read_sql_query(
            """
            SELECT plan_text, planned_for, is_done, created_at
            FROM plans
            WHERE user_id = ?
            ORDER BY planned_for ASC
            """,
            conn,
            params=(user_id,),
        )
        conn.close()
        return df
