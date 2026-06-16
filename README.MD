# SYMBITE — Bonded AI

> **The AI that doesn't just respond. It bonds.**
> Built by Chandu — AI Engineer

[![Python](https://img.shields.io/badge/Python-3.10+-FFB000?style=for-the-badge&logo=python)](https://python.org)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude%20Haiku-8B5CF6?style=for-the-badge)](https://anthropic.com)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/UI-React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react)](https://react.dev)

---

## What is SYMBITE?

SYMBITE is a bonded personal AI — not a chatbot, not an assistant. A digital symbiote.

It observes your patterns. It learns your behavior. It builds a second brain from every conversation. It adapts to your emotional state in real time. The longer you use it, the deeper the bond gets.

Think FRIDAY from Iron Man — sharp, proactive, always one step ahead.

---

## How it thinks

```
You speak
    ↓
Router classifies the message → DATA / HAIKU / FULL
    ↓
FULL only → ReasoningEngine builds inner monologue
    ↓
System prompt assembled from 9 live layers:
    [Identity + tone + weather]
    [5 immutable character laws]
    [Current awareness — time, mood, load]
    [Feedback history — what worked, what didn't]
    [Learned patterns — your habits]
    [Active goals]
    [Inner monologue]
    [Second brain — top-3 relevant vault entries]
    [Bond override — OBSERVING → APEX]
    ↓
Claude API → FeedbackJudge → PatternDetector → VaultExtractor
    ↓
Every fact worth remembering → saved to the Vault automatically
```

---

## Cognitive Stack

| Module | Role | Status |
|--------|------|--------|
| `core/personality.py` | 15 emotional states, rule engine | WIRED |
| `core/perception.py` | Time/mood/load awareness, 60s cache | WIRED |
| `core/character.py` | 5 immutable identity laws | WIRED |
| `core/feedback.py` | FeedbackJudge — rejects low-quality responses | WIRED |
| `core/learning.py` | PatternDetector — learns your habits | WIRED |
| `core/spec.py` | Goal lifecycle SELECT → COLLECT | WIRED |
| `core/reasoning.py` | Inner monologue + RAG notebook | WIRED |
| `core/symbiote.py` | Bond lifecycle OBSERVING → APEX | WIRED |
| `core/vault.py` | Second brain — graph knowledge store | WIRED |
| `core/vault_extractor.py` | Auto-captures facts after every response | WIRED |
| `core/router.py` | Classifies messages DATA / HAIKU / FULL | WIRED |
| `core/memory.py` | Morning context, today's schedule | WIRED |
| `core/morning.py` | Daily morning briefing generator | WIRED |
| `core/evening.py` | Evening summary generator | WIRED |
| `core/watcher.py` | Autonomous daemon — fires briefings at wake/sleep time | WIRED |
| `core/twin.py` | Digital Twin — Boss's live state (stress/mood/energy) | WIRED |

---

## Features

| Feature | Details |
|---------|---------|
| Bonded AI Chat | 3 modes — Personal, Pro, Hybrid |
| Second Brain (Vault) | Auto-extracts facts from every conversation. Graph-connected by tags. |
| Cross-Session Memory | Remembers conversations across restarts |
| Morning Briefing | Speaks your day — plans, weather, goals, yesterday |
| Evening Summary | End-of-day recap — what happened, what's tomorrow |
| Autonomous Watcher | Daemon thread fires briefings at your wake/sleep time |
| Digital Twin | Live model of Boss — stress level adapts conversation window |
| Pattern Learning | Detects your habits and injects them into every response |
| Goal Tracking | SELECT → PROJECT → EXPECT → COLLECT lifecycle |
| Inner Monologue | Reasons before answering on complex messages |
| Bond Lifecycle | Relationship deepens from OBSERVING → BONDED → APEX |
| Tool Use | Weather, news, web search, open any app or URL |
| Calendar | Reads Mac Calendar via AppleScript |
| Voice | TTS (Rocko, 200wpm) + STT (faster-whisper, local) |
| Feedback Judge | Every response graded — rewritten if it fails quality checks |

---

## Tech Stack

```
AI Engine        → Anthropic Claude Haiku
Cognitive Stack  → Pure Python — 16 wired modules
Backend          → FastAPI + uvicorn
Frontend         → React + Vite + Tailwind CSS (Cosmic Terminal aesthetic)
Database         → SQLite — aura.db
Voice            → macOS TTS (Rocko) + faster-whisper STT (100% local)
Calendar         → AppleScript → Mac Calendar
Auth             → bcrypt password hashing
Weather          → OpenWeatherMap API
```

---

## Project Structure

```
SYMBITE/
├── brain.py                    # AI engine — Claude, tool-use loop, system prompt
├── database.py                 # All SQLite reads/writes — never raw SQL outside here
├── weather.py                  # OpenWeatherMap integration
├── start.py                    # Master launcher — backend + frontend
├── app.py                      # Voice entry point
├── core/
│   ├── personality.py          # 15 emotional states, rule engine
│   ├── perception.py           # Time/mood/load, 60s TTL cache
│   ├── character.py            # 5 immutable laws of identity
│   ├── feedback.py             # FeedbackJudge + FeedbackMemory
│   ├── learning.py             # PatternDetector + LearningMemory
│   ├── spec.py                 # Goal lifecycle engine
│   ├── reasoning.py            # Inner monologue + RAG notebook
│   ├── symbiote.py             # Bond lifecycle OBSERVING → APEX
│   ├── vault.py                # Second brain — graph knowledge store
│   ├── vault_extractor.py      # Auto-extracts facts after every response
│   ├── router.py               # Route enum DATA/HAIKU/FULL
│   ├── memory.py               # Morning context, schedule
│   ├── morning.py              # Daily briefing generator
│   ├── evening.py              # Evening summary generator
│   ├── watcher.py              # Autonomous daemon thread
│   ├── twin.py                 # Digital Twin — Boss's live state
│   ├── voice.py                # TTS + STT
│   └── helper.py               # App launcher, URL opener
├── connectors/
│   ├── calendar.py             # Mac Calendar via AppleScript — WIRED
│   ├── gmail.py                # Gmail API — Phase 3
│   ├── health.py               # Apple Health — Phase 4
│   ├── spotify.py              # Spotify — Phase 4
│   └── finance.py              # Plaid — Phase 4
├── agents/
│   └── system_agent.py         # News (BBC/NYT RSS) + Weather
├── api/
│   └── main.py                 # FastAPI — all endpoints
├── frontend-v2/                # React + Vite + Tailwind — Cosmic Terminal UI
├── tests/
│   ├── test_all_systems.py     # 133 tests — full system
│   └── test_vault.py           # Vault smoke tests
└── .env                        # API keys — never commit this
```

---

## Run Locally

**1. Clone**
```bash
git clone https://github.com/chandrababu2048-cell/AURA.git
cd AURA
```

**2. Install**
```bash
pip install -r requirements.txt
cd frontend-v2 && npm install
```

**3. Create `.env`**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENWEATHER_API_KEY=your-key
WEATHER_CITY=YourCity,CountryCode
```

**4. Run**
```bash
# Backend
uvicorn api.main:app --reload

# Frontend (separate terminal)
npm run dev --prefix frontend-v2

# Voice only
python app.py

# Tests
python -m tests.test_all_systems
```

---

## API Keys Needed

| Key | Where |
|-----|-------|
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `OPENWEATHER_API_KEY` | openweathermap.org/api |

---

## Roadmap

### Phase 1 — Bonded Core (Complete)
- [x] 16-module cognitive stack — fully wired
- [x] Second brain (Vault) — graph knowledge store with auto-extraction
- [x] Cross-session memory — Symbite remembers across restarts
- [x] Digital Twin — Boss's live stress/mood/energy state
- [x] Morning briefing + Evening summary — autonomous daemon
- [x] Pattern learning — detects and injects your habits
- [x] Goal lifecycle — SELECT → PROJECT → EXPECT → COLLECT
- [x] Inner monologue — reasons before answering
- [x] Bond lifecycle — OBSERVING → BONDED → APEX
- [x] Tool use — weather, news, web search, open apps and URLs
- [x] Mac Calendar connector — reads your real schedule
- [x] Voice — TTS (Rocko) + STT (faster-whisper, fully local)
- [x] 133 tests passing

### Phase 2 — Proactive Intelligence (Building)
- [ ] Cognitive Memory — importance-based conversation window (replaces recency)
- [ ] Proactive trigger engine — Symbite reaches out, not just responds
- [ ] macOS notifications — delivery when you're not in the app
- [ ] Thought Capture — voice → vault, surfaced in evening briefing

### Phase 3 — Connected
- [ ] Gmail connector — reads and summarises your inbox
- [ ] Reminders connector — actual macOS reminders
- [ ] Life Operator — books restaurants, orders, schedules

### Phase 4 — Hardware
- [ ] Local LLM — data never leaves the machine
- [ ] SQLCipher — encrypted database
- [ ] Neural interface — biometric lock, one person forever

---

## Architecture Philosophy

SYMBITE is not a wrapper around Claude. Claude is the voice. The bond is everything else.

- **Cognitive stack** runs before every Claude call — zero extra API cost
- **Vault** auto-captures facts from every conversation — Symbite builds your second brain while you talk
- **Twin** models your live state — the system adapts to how you're actually doing right now
- **Watcher daemon** fires proactively at your wake and sleep time — no input needed
- **Local voice** — no internet dependency for speech, ever

---

## The Mission

Symbite remembers so you don't have to.

Built as a cognitive prosthetic — for anyone who needs their AI to truly know them.

---

**Built by Chandu** — AI Engineer in Progress

> *"Not just an assistant. A symbiote."*
