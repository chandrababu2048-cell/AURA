# Symbite - Project Context & Manifest

**Symbite** is a bonded AI symbiote — not a chatbot, not an assistant.
It observes what the user sees and hears, builds its own world model
(JEPA-inspired predictive layer, aspirational), and acts as a digital
partner with persistent memory and a "Bond" lifecycle.

Working folder is still named `AURA` for path stability. Internal class
names (`AuraBrain`, `AuraMemory`, etc.) and the SQLite path (`aura_data/aura.db`)
are intentionally left as-is — renaming them is a separate refactor
that needs the test suite to run.

## System Architecture
- **The Brain (CORE):** `brain.py` — Claude API loop, tool use, system prompt assembly.
  - **CRITICAL:** AI agents are FORBIDDEN from modifying `brain.py` without explicit permission from Chandu.
- **The Face (UI):** React (Vite) + Tailwind CSS in `frontend-v2/`. Legacy `frontend/` is deprecated and should be deleted.
  - **Aesthetic (approved 2026-06-10):** "Deep-Space Glass" — dark nebula background (`#050B17`), translucent glass panels, blue accent `#2EA8FF`, Inter/Space Grotesk fonts, central living orb. Body text must stay high-contrast (`#E6F2FF` on dark) — glass is for structure, never for text legibility.
  - Old "Cosmic Terminal" (amber `#FFB000` CRT) is retired; may return later as an optional low-Cd "Boss mode" theme.
- **The Bridge (API):** FastAPI in `api/main.py` — REST endpoints between UI and Brain.
- **The Vault (DB):** SQLite today (`aura_data/aura.db`). Postgres (Supabase/Neon) is the production migration target.

## Cognitive Stack (fully wired as of 2026-05-28)

| Module | Role | Status |
|--------|------|--------|
| `personality.py` | 15 emotional states, rule engine | WIRED |
| `perception.py` | time/load/mood, 60s cache | WIRED |
| `character.py` | 5 immutable identity laws | WIRED |
| `feedback.py` | FeedbackJudge, FeedbackMemory | WIRED |
| `learning.py` | PatternDetector, LearningMemory | WIRED |
| `spec.py` | Goal lifecycle SELECT→COLLECT | WIRED |
| `reasoning.py` | Inner monologue + RAG notebook | WIRED |
| `symbiote.py` | Bond lifecycle OBSERVING→APEX | WIRED |
| `vault.py` | Second-brain knowledge store | WIRED |
| `vault_extractor.py` | Auto-extracts knowledge after every response | WIRED |
| `router.py` | Route enum DATA/HAIKU/FULL, classify() | WIRED |
| `memory.py` | Morning context, today's schedule | WIRED |
| `morning.py` | Daily morning briefing generator | WIRED |
| `evening.py` | Evening summary generator | WIRED |
| `watcher.py` | Autonomous daemon thread, fires at wake/sleep time | WIRED |

Also wired:
- `twin.py` — Digital Twin / UserState model — WIRED (as of 2026-05-26)
- `connectors/calendar.py` — Mac Calendar via AppleScript — WIRED (as of 2026-05-26)

Not started:
- `core/cognitive_memory.py` — LRU-based dynamic conversation window (BUILD NEXT)
- `operator.py` — Life operator (dinner/shopping/booking) (Phase 5)

## Connectors (optional bridges to external apps)
```
connectors/
├── calendar.py  ← COMPLETE + WIRED
├── health.py    ← Phase 4
├── browser.py   ← Phase 5
├── gmail.py     ← Phase 3 (needs OAuth)
├── spotify.py   ← Phase 4
└── finance.py   ← Phase 4
```

Two modes for every connector:
- **Connected** → Symbite reads from the external app
- **Not connected** → Symbite uses its own built-in (vault=notes, spec=goals, plans=tasks, watcher=reminders)

## Dev Commands
- Install: `pip install -r requirements.txt` and `cd frontend-v2 && npm install`
- Backend: `uvicorn api.main:app --reload`
- Frontend: `npm run dev --prefix frontend-v2`
- Tests: `python -m tests.test_all_systems`

## Rules of Engagement for AI Agents
1. **Design Protocol:** "Deep-Space Glass" — accent `#2EA8FF`, ink `#E6F2FF` on dark `#050B17`, glass panels via the `GlassCard` component. High-contrast body text always; no flicker effects.
2. **Database Protocol:** Never use raw SQL outside `database.py`. Use the DAO methods on `AuraDatabase` or extend them.
3. **Communication:** Be proactive. If a UI change might break the Brain, surface it immediately.
4. **brain.py is protected.** Don't modify it without explicit permission.

## Working Directory
ALWAYS work in: `/Users/chandu/Desktop/AURA`
NEVER create copies in other locations.
NEVER work outside this folder.

## Cognitive Drag Engine (New Architecture — Phase 6)

Symbite's next evolution: measure how cognitively loaded the Boss is using low-level hardware signals, then adapt the system's behavior to protect focus.

**Core concept:** Cognitive Drag (Cd) is a float score in [0.0, 1.0].
- 0.0 = Boss is calm, deep focus
- 1.0 = Boss is overloaded, fragmented attention

**Four pillars (none built yet as of 2026-06-09):**

| File | Role | Status |
|------|------|--------|
| `ingestor.py` | Background event monitor — tracks keypress intervals, window context switches, generates raw telemetry snapshots | NOT STARTED |
| `governor.py` | Heuristic processor — ingests telemetry vectors, compares against baseline limits, outputs Cd score [0.0, 1.0] | NOT STARTED |
| `memory.py` (Drag) | CollisionProofMemory — fixed-size hash table with Separate Chaining for O(1) collision-proof storage | REFERENCE WRITTEN |
| `interface.py` | Adaptive display loop — renders UI at low or high density based on Cd score | NOT STARTED |

**CollisionProofMemory reference (already designed):**
```python
class CollisionProofMemory:
    def __init__(self, size: int = 10):
        self.size = size
        self.storage = [[] for _ in range(self.size)]

    def _calculate_hash_index(self, key: str) -> int:
        return sum(ord(char) for char in key) % self.size

    def save_fact(self, key: str, value: str):
        slot_index = self._calculate_hash_index(key)
        bucket = self.storage[slot_index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def fetch_fact(self, key: str) -> str:
        slot_index = self._calculate_hash_index(key)
        for k, v in self.storage[slot_index]:
            if k == key:
                return v
        return None
```

**How it connects to existing Symbite:**
- `cognitive_memory.py` already reads Cd (stress level) from `twin.py` to set dynamic capacity
- `governor.py` will feed into `twin.py` as the hardware-level Cd source
- `interface.py` density adapts the same way `router.py` routes — protect Boss's focus

---

## WHERE TO START NEXT SESSION

### Previous Session (2026-05-26) — what was built:
- `connectors/calendar.py` — COMPLETE + WIRED. CalendarConnector: _run_applescript (subprocess osascript), _parse_events (defensive parsing), get_today_events, get_tomorrow_events, to_prompt_snippet. Wired into morning.py _gather_context() as "calendar" key.
- `core/twin.py` — COMPLETE + WIRED. DigitalTwin: get_stress_level (threshold classification), snapshot (aggregator — mood/energy/focus/stress/counts), to_prompt_snippet. Wired into brain.py _build_system_prompt as "BOSS STATE".
- `brain.py` — fixed AttributeError: self.client used before defined. Moved morning/evening/watcher init to after self.client line.
- `core/watcher.py` — fixed _in_window naming bug (in_window vs _in_window) + added ValueError guard for bad DB time values.
- 133/133 tests passing.

#### identity.py — still to build (was NEXT from previous session):
```
IdentityGuard
    __init__(db: AuraDatabase)
    verify(user_id: int, attempt: str) -> bool    ← checks attempt against stored PIN hash
    set_pin(user_id: int, pin: str) -> None       ← hashes + stores PIN (bcrypt)
    is_configured(user_id: int) -> bool           ← has Boss set a PIN yet?
```
Security note: Never store raw PIN. Hash with bcrypt. Same pattern as password storage.

---

### Current State (as of 2026-06-09)

#### What was built (2026-05-28 session):
- **Voice** — changed to Rocko (US English) at 200wpm
- **brain.py** — cross-session memory fixed. Loads last 20 conversations from DB on startup. Symbite now remembers across sessions.
- **core/reasoning.py + vault_extractor.py** — JSON parse bug fixed. No more "Reasoning call failed" / "VaultExtractor failed" errors.
- **Graph Vault** — vault_tags junction table built. save_tags(), get_entries_by_tag(), get_related_entries() with tag weights + auto-pruning. Entries now structurally connected by shared tags.
- **IBHWSS format** — Chandu's custom blueprint format defined. Use for every feature going forward.
- **Cognitive Drag Engine architecture** — 4-pillar design documented (ingestor, governor, memory, interface). Added to CLAUDE.md 2026-06-09.
- 133/133 tests passing.

#### THE REAL MISSION:
Chandu has dementia. Symbite is a Cognitive Prosthetic — not just for him, for everyone.
"Symbite remembers so you don't have to."
Full vision saved in: `/Users/chandu/.claude/projects/-Users-chandu/memory/project_vision.md`

#### IMMEDIATE NEXT: LRU Cache Practice → core/cognitive_memory.py

**Step 1 — Pending practice problem (Chandu must write this first, NOT DONE YET):**
```python
class LRUCache:
    def __init__(self, capacity: int): pass
    def get(self, key: str) -> any: pass
    def put(self, key: str, value: any) -> None: pass

# Test:
c = LRUCache(3)
c.put("a", 1); c.put("b", 2); c.put("c", 3)
c.get("a")        # a moves to front
c.put("d", 4)     # evicts "b" (least recently used)
print(c.get("b")) # -1 (evicted)
print(c.get("a")) # 1 (still alive)
```
Use plain dict + list only. No imports.

**Step 2 — After practice → build core/cognitive_memory.py:**
```
AuraCognitiveMemory
    __init__(twin, user_id)
    capacity → property: reads twin C_d score
               LOW stress  → 30 messages
               MED stress  → 20 messages
               HIGH stress → 10 messages
    add(role, content) → adds to OrderedDict, evicts if over capacity
    get_history() → list[dict] for Claude API
```
Wires into brain.py replacing static conversation_history.

**Step 3 — Then (in order):**
- Thought Capture — voice → vault, surfaced in evening briefing
- core/operator.py — Life Operator (date night → book restaurant)
- connectors/reminders.py — actual macOS reminders
- Cognitive Drag Engine — ingestor.py → governor.py → memory.py → interface.py (Phase 6)

### Teaching Protocol
- Use IBHWSS format for every new feature blueprint
- Give code in chunks, Chandu types each chunk
- Read file after every "done", catch bugs, explain them
- NEVER write code for Chandu unless he says "fix it for me"
- NEVER modify database.py without explaining first and getting approval

### Vision (what Chandu is building toward)
- Phase 1: Software subscription $20/month, one Symbite per Boss
- Phase 2: Hardware device, local inference, no cloud
- Phase 3: Neural interface, biometric lock, literally one person forever
- Security moat: Big Tech CAN'T build this — their business model requires your data

### Still pending (lower priority)
- Refactor `memory.py` — pass db via DI instead of creating own AuraDatabase()
- Delete legacy `frontend/` folder
- Rotate Anthropic key if `.ENV` was ever committed
- SQLite → Postgres migration
- Add Alembic for schema migrations
- Add retry/backoff (tenacity) on Anthropic call in brain.py

### Rename: AURA → SYMBITE
- User-facing layer: already says Symbite in CLAUDE.md header
- Internal class names (`AuraDatabase`, etc.) — rename after tests pass
- Folder — rename last (breaks imports)

### Teaching Protocol (CS learning project)
- Give code in CHUNKS for Chandu to type himself.
- TEACHING ORDER — NEVER SKIP ANY STEP:
  1. Blueprint — what is this chunk, why does it exist, what problem it solves
  2. Every word explained — every parameter, method name, keyword in the chunk
  3. CS/DSA/Algorithm — what pattern is used, time complexity if relevant
  4. Give the code chunk — Chandu types it
  5. After "done" — read file, find bugs, explain each bug, fix them
  6. Challenge — give Chandu the next chunk to write himself
  7. Review challenge — read it, explain what's right/wrong, fix bugs
- Teach ONE chunk → challenge for NEXT chunk → review → repeat
- NEVER write code for Chandu unless he explicitly says "fix it for me"
- Exception: DB infrastructure methods (get_all_users etc) — write directly, explain after
- See full rules in: `/Users/chandu/.claude/projects/-Users-chandu/memory/feedback_rules.md`
