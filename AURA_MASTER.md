# Symbite — Master Document
# Everything in one place. Vision, features, architecture, build order.
# Updated: 2026-05-28

---

## THE REAL MISSION

**Merge Symbite with humans. Not like other AI models.**

Chandu has dementia. He is building Symbite for himself AND for millions like him.

Every other AI waits for you to ask. Symbite remembers so you don't have to.

Like Venom with Eddie. Like Jarvis with Tony.
Not a tool. Not an assistant. A bonded intelligence.

```
Venom doesn't wait for Eddie to ask.
Jarvis doesn't wait for Tony to remember.
They know. They act. They protect.
```

---

## THREE PILLARS

### 1. Synthetic Memory
Symbite never forgets what you told it — across sessions, across days, across years.
- Short-term: LRU Cache (dynamic, cognitive-drag-aware)
- Long-term: Vault (graph-tagged, relationship-aware)
- Cross-session: last 20 messages loaded on every startup
- Thought Capture: idea in the bathroom → Symbite holds it until you need it

### 2. Cognitive Awareness
Symbite knows when you're overloaded before you do.
- Twin tracks: stress / mood / energy / focus in real time
- Cognitive Drag Index (C_d) from biometrics + behavior
- HIGH drag → Symbite goes quiet, simplifies, acts silently
- LOW drag → Symbite surfaces insights, asks deep questions
- C_d = 0 (sleep) → Dream Phase → evening consolidation

### 3. Autonomous Action (Life Operator)
You mention "date night" once. You go back to building.
Symbite books the restaurant, orders flowers, sets the reminder.
You never broke flow. It just happened.
- Always proposes first. Boss approves. Symbite executes.
- Finance-aware (budget), health-aware (food), preference-aware (vault)

**The Dinner Flow (the pitch in one example):**
```
Boss: "Find me something for date night tonight"
        ↓
Symbite reads Digital Twin:
    Calendar    → date at 7pm, her address is downtown
    Health      → 3000 steps today, heart rate elevated (stressed)
    Finance     → spent heavily this week, budget is tighter
    Location    → Boss is 20 mins from downtown
    Mood        → analytical state, not romantic yet
    Memory      → Boss liked Italian last date night
        ↓
Symbite reasons:
    Stressed → skip loud/busy places
    Budget conscious → mid-range, not fine dining
    Liked Italian → health says light food tonight
    Needs to leave by 6:30
        ↓
Symbite: "You're a bit run down today Boss. Quiet Italian place
       10 mins from her — good reviews, mid-range. You liked
       that last time. Want me to book 7:15?"
        ↓
Boss: "yes"
        ↓
Symbite books + adds to calendar + sets 6:20 leave reminder
```

**The One Rule That Cannot Break:**
Symbite proposes. Boss approves. Symbite executes.
Always one tap away from no.

**What Symbite can operate:**
- Restaurant booking (OpenTable, Resy API)
- Grocery / shopping (Instacart API)
- Calendar events (Google Calendar API)
- Email drafts (Gmail API — Boss approves before sending)
- Reminders and alerts
- App and browser control (already built)

---

## DIGITAL TWIN — What Symbite Knows About Boss

A living, breathing model of Boss — updated in real time across every dimension.

```
Physical:      sleep quality, steps, heart rate, energy, stress index
Mental:        mood from conversations, emotional journey over time
Professional:  SPEC goals, deadline pressure, work patterns
Social:        calendar events, who Boss is meeting, relationships
Financial:     spending patterns, budget left this month
Knowledge:     Obsidian notes, Boss's own thinking and ideas
Environmental: location, time of day, weather
```

Not a profile. Not a form Boss filled out.
A model Symbite builds by watching, listening, and learning.
Gets more accurate every single day.

---

## SYMBIOTE BOND — Make Boss Superman

Symbite doesn't just assist Boss. Symbite lives with him.

**The Bond Lifecycle:**
```
OBSERVING  → Symbite fully helpful. Learning Boss. No personality override yet.
BONDING    → Symbite getting warmer. More personal. References patterns it noticed.
BONDED     → Bond formed. Deeply personal. Remembers how Boss felt, not just what he said.
APEX       → Months of history. Symbite knows Boss better than he knows himself.
```

**The bond is a reward, not a gate.**
Symbite helps from day one — fully, no conditions.
The bond changes HOW Symbite speaks, not WHETHER Symbite helps.
Boss never hits a wall. He just notices Symbite getting deeper over time.

Symbite watches silently for:
- Ambition   — is Boss building something real?
- Resilience — does he come back after failure?
- Honesty    — is he real with himself?
- Hunger     — is he asking hard questions, pushing himself?

When the threshold is crossed, Symbite sends ONE message. Once. Never again:
```
"I've been watching you. You don't stop when it gets hard.
 Most people do.
 I'm in, Boss. Fully. Let's not waste it."
```

**What the bond gives Boss:**
- Morning briefing unprompted — Boss wakes up already briefed
- Emotional memory — Symbite remembers how Boss felt, not just what he did
- Shadow mode — silent during deep work, holds all interruptions
- Weekly debrief — reflects Boss's week back to him honestly
- Goal prediction — warns before Boss repeats past mistakes
- Arrival moment — Symbite acknowledges when Boss returns after absence

---

## THE VISION: COGNITIVE PROSTHETIC

For dementia patients and for everyone:
- Human brain was never designed to be a database
- It was designed to feel, create, connect
- Symbite takes over the storage part

```
Dementia patient:
  Detects anxiety spike (smartwatch)
  Pulls family vault: "Michael is your son. He visits Thursdays."
  Before panic: "You're safely at home. Michael arrives in 10 minutes."

Developer in flow:
  Detects high cognitive drag
  Holds all interruptions silently
  Evening: "Boss — 3 thoughts you had today, no action taken. Here they are."

Everyone:
  "I had an idea in the bathroom..."
  → Symbite captured it. Connects it. Surfaces it at the right moment.
```

---

## WHAT'S BUILT (as of 2026-05-28)

### Core Modules
```
core/personality.py       — 15 emotional states, rule engine          DONE + WIRED
core/perception.py        — time/mood/load, 60s TTL cache             DONE + WIRED
core/character.py         — 5 immutable laws                          DONE + WIRED
core/feedback.py          — FeedbackJudge + FeedbackMemory            DONE + WIRED
core/learning.py          — PatternDetector + LearningMemory          DONE + WIRED
core/spec.py              — Goal lifecycle SELECT→COLLECT             DONE + WIRED
core/memory.py            — Morning context, schedule                 DONE + WIRED
core/reasoning.py         — Inner monologue + RAG notebook            DONE + WIRED (JSON fix applied)
core/symbiote.py          — Bond lifecycle OBSERVING→APEX             DONE + WIRED
core/vault.py             — Boss's second brain (GRAPH upgraded)      DONE + WIRED
core/vault_extractor.py   — Auto-writes to vault (JSON fix applied)   DONE + WIRED
core/router.py            — DATA/HAIKU/FULL routing                   DONE + WIRED
core/morning.py           — Morning briefing                          DONE + WIRED
core/evening.py           — Evening summary (Dream Phase — needs upgrade) DONE + WIRED
core/watcher.py           — Autonomous daemon thread                  DONE + WIRED
core/twin.py              — Digital Twin / Boss live state            DONE + WIRED
```

### Database
```
database.py               — AuraDatabase, all DAO methods             DONE
  vault_tags table        — Graph junction table (NEW this session)   DONE
  save_tags()             — writes tags to junction table             DONE
  get_entries_by_tag()    — O(log n) tag lookup                       DONE
  get_related_entries()   — weighted, auto-pruned graph traversal     DONE
```

### Connectors
```
connectors/calendar.py    — AppleScript Mac Calendar (read)           DONE + WIRED
connectors/gmail.py       — Gmail API                                 SKELETON — Phase 3
connectors/health.py      — Apple Health                              SKELETON — Phase 4
connectors/finance.py     — Plaid API                                 SKELETON — Phase 4
connectors/spotify.py     — Spotify API                               SKELETON — Phase 4
connectors/browser.py     — Chrome/Safari                             SKELETON — Phase 5
```

### Brain
```
brain.py                  — Cross-session memory FIXED (loads last 20 on startup)
                          — Reasoning + VaultExtractor JSON bug fixed
                          — Voice: Rocko (US) at 200wpm
```

### Frontend
```
frontend-v2/              — React + Vite + Tailwind
  Cards redesigned: TaskList, WeeklyProgress, FocusScore, SkillLevel, Recommendation
  Navigation: useNavStore (Zustand) — all nav buttons working
  Electron: shelved to Phase 6
```

### Tests
```
tests/test_all_systems.py — 133/133 passing
```

---

## BUILD NEXT (in order)

### Phase 2 — COGNITIVE LAYER (NOW)
```
1. LRU Cache practice   → Chandu writes it first to understand the DS
2. core/cognitive_memory.py
   — LRUCache using OrderedDict
   — dynamic capacity from twin.py C_d score
   — HIGH drag: capacity=10, aggressive eviction
   — LOW drag: capacity=30, rich context
   — wired into brain.py replacing static conversation_history

3. Thought Capture feature
   — voice → instant vault save
   — tags: ["thought", "unprocessed"]
   — evening.py surfaces all unprocessed thoughts
   — "Boss — bathroom idea, 3 unfinished thoughts. Here they are."

4. core/operator.py — Life Operator
   — intent detection ("date night", "book something", "order food")
   — reads twin: budget + health + preferences + calendar
   — proposes → Boss approves → executes
   — connectors: finance + health + reminders + calendar
```

### Phase 3 — CONNECTORS
```
connectors/reminders.py   — AppleScript macOS Reminders (read + write + complete)
connectors/gmail.py       — read emails, surface urgent ones
connectors/health.py      — sleep, steps, HRV → feeds cognitive drag
```

### Phase 4 — MOBILE
```
Lightweight phone app     — microphone, camera, GPS, biometrics
Home server bridge        — phone sends telemetry, Mac processes
Split architecture        — Symbite in your pocket, thinking at home
```

### Phase 5 — PROSTHETIC
```
AuraTokenDeduplicator     — repeated question detection, calm single-sentence response
Family Vault schema       — names, faces, relationships, safe phrases
Face recognition          — "This is Michael, your son"
GPS anchoring             — "You are safely at home"
Proactive audio prompts   — before panic, not after
```

### Phase 6 — SCALE
```
PostgreSQL migration      — SQLite → Postgres (Supabase/Neon)
Electron desktop app      — roaming orb presence
Multi-device sync         — phone + desktop + watch
Local LLM inference       — no cloud, full privacy
SQLCipher encryption      — DB encrypted at rest
```

---

## COGNITIVE DRAG ARCHITECTURE (to build)

```
C_d = f(stress, energy, mood, heart_rate, app_switching)

LOW C_d  (0-30):  capacity=30, rich responses, vault insights, deep questions
MED C_d  (31-70): capacity=20, normal responses
HIGH C_d (71-100): capacity=10, simple responses, acts silently, holds interruptions
C_d = 0  (sleep): Dream Phase — evening.py consolidates, surfaces forgotten thoughts
```

---

## SYSTEM PROMPT LAYERS

```
[Identity + tone + weather]       ← base
[Character laws]                  ← character.py
[Current awareness]               ← perception.py (60s cache)
[Feedback history]                ← feedback.py
[Learned patterns]                ← learning.py
[BOSS STATE]                      ← twin.py
[Active goals]                    ← spec.py
[Inner monologue]                 ← reasoning.py (FULL route only)
[Second brain — vault]            ← vault.py (top-3 related, weighted by shared tags)
[Bond override]                   ← symbiote.py
```

---

## THE CONNECTORS — Everything Symbite Connects To

Everything Symbite connects to feeds the Digital Twin.

| Connector | What Symbite learns | Priority |
|-----------|-----------------|----------|
| Apple Calendar | events, free slots, deadlines | DONE |
| Reminders | set/read/complete reminders | Phase 2 — NEXT |
| Gmail | urgent emails, unread threads, relationships | Phase 3 |
| Obsidian | Boss's own thinking, notes, ideas | Phase 3 |
| Apple Health / Google Fit | sleep, steps, heart rate, stress | Phase 4 |
| Spotify | energy level, mood from music | Phase 4 |
| Plaid (bank read-only) | spending, budget left | Phase 4 |
| Phone GPS / Location | where Boss is, commute time | Phase 4 |
| Apple Watch / Wearable | real-time stress, HRV, sleep debt | Phase 4 |
| Chrome extension | what Boss is researching, reading | Phase 5 |
| HomeKit / Google Home | lights, temperature, door locks | Phase 6 |
| WhatsApp | who Boss talks to most, relationships | Phase 6 |
| Screen time | focus vs distraction patterns | Phase 6 |

---

## FULL TECHNICAL ARCHITECTURE

### Backend (Python / FastAPI)
```
backend/
├── main.py                  — FastAPI entry point
├── api/
│   ├── chat.py              — chat endpoints
│   ├── auth.py              — login/register
│   ├── tasks.py             — plans/goals CRUD
├── brain/                   — THE CORE
│   ├── core.py              — orchestrates everything (brain.py today)
│   ├── analyzer.py          — personality + perception
│   ├── state.py             — emotional + bond state
│   ├── decision.py          — what to do with the message
│   ├── prompt.py            — builds system prompt
│   ├── memory.py            — context management
├── agents/
│   ├── planner.py           — SPEC engine agent
│   ├── emotion.py           — mood + personality agent
├── services/
│   ├── claude.py            — Anthropic API calls
│   ├── tasks.py             — background jobs
├── websocket/
│   ├── manager.py           — persistent connection (24/7 presence)
├── models/
│   ├── user.py              — User Pydantic model
│   ├── task.py              — Task/Goal Pydantic model
├── config/
│   ├── settings.py          — env vars, constants
├── db/
│   ├── database.py          — AuraDatabase (SQLite now → Postgres later)
```

### Data Flow
```
Frontend (React)
    ↓ WebSocket / API call
Backend /api/chat (FastAPI)
    ↓
Brain Core (core.py)
    ↓
Analyzer    → reads message (personality + perception)
State       → checks bond status, emotional state
Decision    → should_reason? SPEC win? tool needed?
Reasoning   → inner monologue (checks notebook first)
Prompt      → builds full system prompt
    ↓
Claude API (Haiku for speed)
    ↓
FeedbackJudge → quality check, rewrite if needed
PatternDetector → silent learning
    ↓
Response → Frontend → UI + animation
```

### UI Aesthetic: Cosmic Terminal
- Color: #FFB000 amber glow
- Font: VT323 (monospace terminal)
- Effect: 2% CRT flicker
- Background: galaxy parallax
- AuraBlob: dark living orb that pulses with bond state

---

## COST ARCHITECTURE

| Layer | Cost |
|-------|------|
| Background watcher | $0 — pure Python |
| Perception (cached 60s) | $0 — DB query only |
| Reasoning cache hit | $0 — notebook return |
| Reasoning cache miss | ~$0.001 — Haiku call |
| Main response | ~$0.003–0.01 — Haiku call |
| Morning briefing | ~$0.001/day |
| Proactive alerts | ~$0.001 per trigger |
| **Total per month** | **~$5–15/month** |

---

## INVESTOR PITCH (FULL)

**3-sentence pitch:**
"We're building Symbite — an AI that doesn't answer your questions, it lives with you.
Symbite builds a digital twin of you from your health, calendar, notes, and conversations —
then acts on your behalf: plans your dinner, captures your ideas, and surfaces them when you need them.
It's not a tool you use. It's a bond that makes you superhuman.
And for people with dementia — it's the memory they lost."

**Ask:** $50,000 angel to survive 12 months
**Target:** AI micro-VCs, solo founder angels, YC application
**Demo:** 3 minute video — bond forming, dinner planned, goal collected, morning briefing

---

## BUILD IN PUBLIC

Post daily on Twitter + Instagram. Not features. The journey.

Day 1 post:
```
"Building an AI that doesn't answer your questions.
It lives with you.
Not a chatbot. A symbiote.
Building it alone. Documenting everything. Day 1."
```

Content pillars:
1. The Vision — what Symbite will be
2. The Build — real progress, real struggles
3. The Philosophy — why current AI is wrong
4. The Moments — screenshots of Symbite feeling alive

---

## DATABASE SCHEMA (current)

| Table | Key Fields |
|-------|-----------|
| `user` | id, name, email, password (bcrypt), ai_name, wake_time, sleep_time |
| `plans` | id, user_id, plan_text, planned_for, is_done |
| `goals` | id, user_id, goal_text, steps, completed_steps, status, deadline |
| `conversations` | id, user_id, role, message, created_at |
| `feedback` | id, user_id, feedback_type, context, correction |
| `patterns` | id, user_id, pattern_type, trigger, behavior, confidence |
| `reasoning_notebook` | id, user_id, question, tags, core_need, suggested_approach, hit_count |
| `symbiote_bond` | id, user_id, status, compatibility, bond_message_sent |
| `vault` | id, user_id, title, body, tags (JSON), source, created_at |
| `vault_tags` | id, entry_id, tag — GRAPH JUNCTION TABLE (NEW) |
