# ============================================================
# api/main.py — AURA FastAPI Bridge
# ============================================================
# PURPOSE:
#   Exposes all brain.py, database.py, memory.py, and weather.py
#   functionality as REST API endpoints for the React frontend.
#
# ARCHITECTURE:
#   React UI  →  FastAPI (this file)  →  AuraBrain / AuraDatabase
#                                     →  AuraMemory / get_weather
#
# BRAIN SESSION MANAGEMENT:
#   AuraBrain holds conversation_history in memory (stateful).
#   We keep one AuraBrain instance per user_id in _brain_sessions.
#   This survives as long as the FastAPI process runs — the same
#   design Streamlit used via st.session_state["brain"].
#
# HOW TO RUN:
#   uvicorn api.main:app --reload
#   (run from the project root, NOT from inside /api)
#
# PYDANTIC v2 is used for all request/response models.
# ============================================================

import sys
import os

# ── Path Fix ───────────────────────────────────────────────
# api/main.py lives one level below the project root.
# We insert the root so Python can find brain, database,
# memory, and weather without any package restructuring.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from dotenv import load_dotenv

from brain import AuraBrain
from database import AuraDatabase
from core.memory import AuraMemory
from weather import get_weather

load_dotenv()

# ── App Init ───────────────────────────────────────────────
app = FastAPI(
    title="AURA API",
    description="The FastAPI bridge between the AURA React frontend and the Python brain.",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────
# Allow the React dev server (Vite default: 5173) and any
# production origin. Tighten this list before going to prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared DB instance ─────────────────────────────────────
db = AuraDatabase()

# ── Brain Session Store ────────────────────────────────────
# Maps user_id → AuraBrain instance.
# One brain per user keeps conversation_history isolated.
_brain_sessions: dict[int, AuraBrain] = {}


def _get_brain(user_id: int) -> AuraBrain:
    """Return the existing AuraBrain for this user, or create one."""
    if user_id not in _brain_sessions:
        _brain_sessions[user_id] = AuraBrain(user_id)
    return _brain_sessions[user_id]


# ============================================================
# PYDANTIC MODELS — Request / Response Schemas
# ============================================================

# ── Auth ───────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:       str
    email:      EmailStr
    password:   str        = Field(min_length=6)
    ai_name:    str        = "AURA"
    wake_time:  str        = "07:00"
    sleep_time: str        = "22:30"


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class UserResponse(BaseModel):
    id:         int
    name:       str
    email:      str
    ai_name:    str
    wake_time:  str
    sleep_time: str
    created_at: str


class AuthResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    user:    Optional[UserResponse] = None


# ── Chat ───────────────────────────────────────────────────

class ThinkRequest(BaseModel):
    user_id: int
    message: str
    mode:    str = "Personal"   # "Personal" | "Pro" | "Hybrid"


class ThinkResponse(BaseModel):
    reply: str


# ── Plans ──────────────────────────────────────────────────

class AddPlanRequest(BaseModel):
    user_id:     int
    plan_text:   str
    planned_for: Optional[str] = None   # "YYYY-MM-DD"; defaults to today


class PlanResponse(BaseModel):
    id:          int
    user_id:     int
    plan_text:   str
    planned_for: str
    is_done:     int
    created_at:  str


class TogglePlanRequest(BaseModel):
    user_id: int


# ── Goals ──────────────────────────────────────────────────

class AddGoalRequest(BaseModel):
    user_id:   int
    goal_text: str
    deadline:  Optional[str] = None   # "YYYY-MM-DD"


class GoalResponse(BaseModel):
    id:           int
    user_id:      int
    goal_text:    str
    deadline:     Optional[str]
    progress:     int
    is_completed: int
    created_at:   str


class CompleteGoalRequest(BaseModel):
    user_id: int


# ── User Update ────────────────────────────────────────────

class UpdateAiNameRequest(BaseModel):
    ai_name: str


# ── Conversations ──────────────────────────────────────────

class MessageResponse(BaseModel):
    id:         int
    user_id:    int
    role:       str
    message:    str
    created_at: str


# ── Memory ─────────────────────────────────────────────────

class ContextResponse(BaseModel):
    context: str


class ReportResponse(BaseModel):
    report: str


# ── Weather ────────────────────────────────────────────────

class WeatherResponse(BaseModel):
    success:    bool
    city:       Optional[str]   = None
    temp:       Optional[float] = None
    feels_like: Optional[float] = None
    humidity:   Optional[int]   = None
    condition:  Optional[str]   = None
    wind:       Optional[float] = None
    summary:    str
    error:      Optional[str]   = None


# ============================================================
# ROUTES
# ============================================================

# ── Health ─────────────────────────────────────────────────

@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Health check — confirms the API is running."""
    return {"status": "online", "service": "AURA API"}


# ── Auth ───────────────────────────────────────────────────

@app.post("/auth/register", response_model=AuthResponse, tags=["auth"])
def register(body: RegisterRequest) -> AuthResponse:
    """
    Create a new user account.
    Password is bcrypt-hashed inside AuraDatabase.register_user().
    Returns success=True or an error message.
    """
    result = db.register_user(
        name=body.name,
        email=body.email,
        password=body.password,
        ai_name=body.ai_name,
        wake_time=body.wake_time,
        sleep_time=body.sleep_time,
    )
    return AuthResponse(**result)


@app.post("/auth/login", response_model=AuthResponse, tags=["auth"])
def login(body: LoginRequest) -> AuthResponse:
    """
    Verify email + password.
    Returns the user object on success so the frontend can store user_id.
    """
    result = db.login_user(email=body.email, password=body.password)
    if result["success"]:
        user_data = result["user"]
        # Strip the hashed password before sending to the client
        user_data.pop("password", None)
        return AuthResponse(success=True, user=UserResponse(**user_data))
    return AuthResponse(success=False, message=result.get("message"))


# ── Users ──────────────────────────────────────────────────

@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
def get_user(user_id: int) -> UserResponse:
    """Fetch a user's profile by their database ID."""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.pop("password", None)
    return UserResponse(**user)


@app.patch("/users/{user_id}/ai-name", tags=["users"])
def update_ai_name(user_id: int, body: UpdateAiNameRequest) -> dict[str, str]:
    """Rename the user's AI companion (e.g. "AURA" → "Jarvis")."""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.update_ai_name(user_id, body.ai_name)
    return {"message": f"AI name updated to '{body.ai_name}'."}


# ── Chat ───────────────────────────────────────────────────

@app.post("/chat/think", response_model=ThinkResponse, tags=["chat"])
def think(body: ThinkRequest) -> ThinkResponse:
    """
    Send a message to AURA and get a reply.

    Uses the per-user AuraBrain instance so conversation_history
    accumulates across calls within the same server session —
    the same behaviour as the Streamlit app.

    mode: "Personal" | "Pro" | "Hybrid"
    """
    user = db.get_user_by_id(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    brain = _get_brain(body.user_id)
    reply = brain.think(user_message=body.message, mode=body.mode)
    return ThinkResponse(reply=reply)


@app.delete("/chat/session/{user_id}", tags=["chat"])
def clear_chat_session(user_id: int) -> dict[str, str]:
    """
    Clear the in-memory conversation history for a user.
    Call this when the user clicks "New Chat" in the UI.
    Does NOT delete the persistent DB history.
    """
    _brain_sessions.pop(user_id, None)
    return {"message": "Conversation session cleared."}


# ── Plans ──────────────────────────────────────────────────

@app.get("/plans", response_model=list[PlanResponse], tags=["plans"])
def get_plans(
    user_id: int = Query(..., description="The logged-in user's ID"),
    date:    Optional[str] = Query(None, description="YYYY-MM-DD — defaults to today"),
) -> list[PlanResponse]:
    """
    Fetch plans for a user on a given date.
    If date is omitted, returns today's plans.
    """
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    rows = db.get_plans_for_date(user_id, date) if date else db.get_today_plans(user_id)
    return [PlanResponse(**r) for r in rows]


@app.post("/plans", response_model=dict, tags=["plans"], status_code=201)
def add_plan(body: AddPlanRequest) -> dict[str, str]:
    """Add a new daily plan. planned_for defaults to today if omitted."""
    user = db.get_user_by_id(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.add_plan(
        user_id=body.user_id,
        plan_text=body.plan_text,
        planned_for=body.planned_for,
    )
    return {"message": "Plan added."}


@app.patch("/plans/{plan_id}/toggle", tags=["plans"])
def toggle_plan(plan_id: int, body: TogglePlanRequest) -> dict[str, str]:
    """Toggle a plan's done/undone state."""
    db.toggle_plan_done(plan_id=plan_id, user_id=body.user_id)
    return {"message": "Plan toggled."}


@app.delete("/plans/{plan_id}", tags=["plans"])
def delete_plan(
    plan_id: int,
    user_id: int = Query(..., description="The logged-in user's ID"),
) -> dict[str, str]:
    """Delete a plan. user_id prevents cross-user deletion."""
    db.delete_plan(plan_id=plan_id, user_id=user_id)
    return {"message": "Plan deleted."}


# ── Goals ──────────────────────────────────────────────────

@app.get("/goals", response_model=list[GoalResponse], tags=["goals"])
def get_goals(
    user_id: int = Query(..., description="The logged-in user's ID"),
) -> list[GoalResponse]:
    """Fetch all active (incomplete) goals for a user."""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    rows = db.get_active_goals(user_id)
    return [GoalResponse(**r) for r in rows]


@app.post("/goals", response_model=dict, tags=["goals"], status_code=201)
def add_goal(body: AddGoalRequest) -> dict[str, str]:
    """Add a new long-term goal. deadline is optional (YYYY-MM-DD)."""
    user = db.get_user_by_id(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.add_goal(
        user_id=body.user_id,
        goal_text=body.goal_text,
        deadline=body.deadline,
    )
    return {"message": "Goal added."}


@app.patch("/goals/{goal_id}/complete", tags=["goals"])
def complete_goal(goal_id: int, body: CompleteGoalRequest) -> dict[str, str]:
    """Mark a goal as completed."""
    db.complete_goal(goal_id=goal_id, user_id=body.user_id)
    return {"message": "Goal marked as completed."}


@app.delete("/goals/{goal_id}", tags=["goals"])
def delete_goal(
    goal_id: int,
    user_id: int = Query(..., description="The logged-in user's ID"),
) -> dict[str, str]:
    """Delete a goal. user_id prevents cross-user deletion."""
    db.delete_goal(goal_id=goal_id, user_id=user_id)
    return {"message": "Goal deleted."}


# ── Conversations ──────────────────────────────────────────

@app.get("/conversations", response_model=list[MessageResponse], tags=["conversations"])
def get_conversations(
    user_id: int = Query(..., description="The logged-in user's ID"),
    limit:   int = Query(20,  description="Number of recent messages to return"),
) -> list[MessageResponse]:
    """
    Fetch the most recent N messages for a user in chronological order.
    Used by the frontend to restore chat history after a page reload.
    """
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    rows = db.get_recent_messages(user_id=user_id, limit=limit)
    return [MessageResponse(**r) for r in rows]


# ── Memory ─────────────────────────────────────────────────

@app.get("/memory/context", response_model=ContextResponse, tags=["memory"])
def get_context(
    user_id: int = Query(..., description="The logged-in user's ID"),
) -> ContextResponse:
    """
    Return the full morning context block that is injected into
    AURA's system prompt — useful for debugging or displaying
    context in the UI.
    """
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    memory = AuraMemory(user_id)
    return ContextResponse(context=memory.get_morning_context())


@app.get("/memory/report", response_model=ReportResponse, tags=["memory"])
def get_weekly_report(
    user_id: int = Query(..., description="The logged-in user's ID"),
) -> ReportResponse:
    """
    Generate and return the weekly analytics report:
    conversations count, tasks created, tasks completed, completion rate.
    """
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    memory = AuraMemory(user_id)
    return ReportResponse(report=memory.get_weekly_report())


# ── Weather ────────────────────────────────────────────────

@app.get("/weather", response_model=WeatherResponse, tags=["weather"])
def weather(
    city: Optional[str] = Query(None, description="City name — defaults to WEATHER_CITY env var or Boston"),
) -> WeatherResponse:
    """
    Fetch current weather from OpenWeatherMap.
    Returns temperature, humidity, condition, wind, and a summary string.
    """
    data = get_weather(city)
    return WeatherResponse(**data)
