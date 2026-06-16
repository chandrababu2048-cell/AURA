# CHANDU'S LEARNING NOTEBOOK
# SYMBITE / Personal Intelligence Project
# Started: April 2026
# Rule: Read this before building anything new.

---

## HOW TO USE THIS FILE
- Read top to bottom before starting a new feature
- Every concept has: what it is → why it matters → how we used it
- Add to it every session

---

## SESSION 1 — FOUNDATIONS

### Classes & Objects
A class is a blueprint. An object is the thing built from it.
```python
class Personality:          # blueprint
    def __init__(self):     # constructor — runs when object is created
        self.score = 0      # self = this specific object, not all objects
```
- `__init__` = constructor. Runs automatically when you create the object.
- `self` = refers to THIS specific instance, not the class itself.
- 3 cars driving = 3 objects from 1 Car class. Each has its own data.

---

### Functions — Two Types
```python
# Type 1: RETURNS something (makes a promise)
def get_morning_briefing() -> str:   # -> str means "I promise to return a string"
    return "Good morning Boss."

# Type 2: DOES something (no return)
def speak(text: str):
    subprocess.Popen(["say", text])  # just acts, returns nothing
```
Rule: If it has `return`, it gives you data. If not, it just does work.

---

### HTTP — How Systems Talk
```
GET  = "give me data"   → requests.get(url)
POST = "take my data and reply" → requests.post(url, json={...})
```
- `response.json()` converts JSON text → Python dict/list
- `timeout=5` = give up after 5 seconds if no reply
- `params={"user_id": 1}` = adds ?user_id=1 to the URL

---

### Dictionaries as Lookup Tables
```python
STATES = {
    "bonded":    "Warm, sharp, fully present.",
    "protective": "Boss is struggling. Lead with care.",
}
# Instead of 10 if/else statements — one lookup
result = STATES.get("bonded")   # returns the value, no crash if missing
```
Key insight: dicts replace long if/else chains. O(1) lookup speed.

---

### `**r` Unpacking
```python
data = {"name": "Chandu", "email": "c@gmail.com"}
UserResponse(**data)
# same as:
UserResponse(name="Chandu", email="c@gmail.com")
```
`**` unpacks a dict into keyword arguments. Used everywhere in FastAPI/Pydantic.

---

### timedelta — Time Math
```python
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
```
`timedelta` is a duration. Subtract it from a datetime to go back in time.

---

### subprocess.Popen vs run
```python
subprocess.Popen(["say", text])   # non-blocking — code keeps running
subprocess.run(["say", text])     # blocking — code WAITS for it to finish
```
We use Popen for voice so SYMBITE keeps responding while Samantha speaks.

---

## SESSION 2 — EMOTION ENGINE

### The Venom Emotion Engine — Architecture
```
observe(message) → returns signals dict
feel(signals)    → returns state string
get_personality_prompt(state) → returns instruction text
→ injected into Claude system prompt
```
Three layers. Each has one job. Zero API calls.

---

### Weighted Scoring System
```python
WEIGHTS = {"happy": 3, "stuck": -3, "exhausted": -4}
# Loop through words, add up weights → score
# Positive score = good state, Negative = stress state
```
- BOOSTERS: multiply weight ("very happy" = happy * 1.8)
- NEGATORS: flip weight ("not happy" = happy * -1)
- Pivot rule: "but" splits the sentence — only score the part after "but"

---

### `@staticmethod` vs `@classmethod`
```python
@staticmethod           # no self, no cls — pure function
def _is_relevant(title, summary):
    # doesn't need anything from the object
    return True/False

@classmethod            # gets cls — reference to the class itself
def scan(cls):
    cls._fetch_feed()   # can call other class methods
```
Rule: If the function doesn't need object data → staticmethod.
      If it needs to call other class methods → classmethod.

---

### `any()` with generator
```python
any(keyword in text for keyword in KEYWORDS)
# reads: "is ANY keyword from KEYWORDS found in text?"
# stops as soon as it finds the first match — efficient
```

### `sum()` with generator
```python
sum(1 for keyword in KEYWORDS if keyword in text)
# counts HOW MANY keywords matched
```

---

### Separation of Concerns — WHY
- `brain.py` = dispatcher only. Does not detect emotions.
- `personality.py` = emotion engine only. Does not call Claude.
- `memory.py` = history only. Does not build prompts.
Each file has ONE job. Change one without breaking others.

---

## SESSION 3 — SYSTEM ARCHITECTURE

### The Wiring Pattern (brain.py → personality.py)
```python
# In think():
signals = self.personality.observe(user_message)   # layer 1
state   = self.personality.feel(signals)            # layer 2
instruction = self.personality.get_personality_prompt(state)  # layer 3
system_prompt = self._build_system_prompt(mode, instruction)  # injected
```
Order matters: observe → feel → prompt → API call.
If you call build_system_prompt before observe, instruction doesn't exist yet.

---

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
OPENWEATHER_API_KEY=...
WEATHER_CITY=Springfield,MA,US
SYMBITE_EMAIL=symbite.ai@gmail.com
```
- Never commit .env to GitHub
- `os.getenv("KEY_NAME")` reads a value
- `load_dotenv()` loads the file into memory

---

### FastAPI — How Endpoints Work
```python
@app.post("/chat/think")        # POST to this URL
def think(body: ThinkRequest):  # Pydantic validates the request body
    reply = brain.think(...)    # call the brain
    return ThinkResponse(reply=reply)  # Pydantic formats the response
```
Pydantic models = contracts. Define what goes in and what comes out.

---

### Tool Use Loop (Claude API)
```
1. Send message + tools list to Claude
2. Claude replies with tool_use → run the tool → send result back
3. Claude replies with end_turn → return the text
The while True loop handles this automatically.
```

---

## SESSION 4 — AI & CS CONCEPTS

### Personality vs Character (Human → Code translation)
```
Human Concept     →  SYMBITE Module       →  Function
─────────────────────────────────────────────────────
Genetics          →  Claude (base LLM)    →  raw intelligence
Temperament       →  personality.py       →  tone, emotional states
Ethics/Character  →  character.py         →  values, rules, guardrails
Experience        →  memory.py            →  conversation history
Senses            →  perception.py        →  observes your environment
Self/Learning     →  feedback.py          →  evolves from corrections
```

### OCEAN Model (Big Five) → personality.py
```
Openness          → curiosity, new ideas (evolution state)
Conscientiousness → discipline, structure (analytical state)  
Extraversion      → energy level (apex vs shadow state)
Agreeableness     → cooperation (bonded vs dominant state)
Neuroticism       → stress handling (protective vs reclamation state)
```

### LLMs — How They Actually Work
```
Input tokens → attention mechanism → predict next token → repeat
```
They don't "understand." They pattern-match at massive scale.
LeCun's critique: no world model, no causality, no true reasoning.

### JEPA — Joint Embedding Predictive Architecture
```
LLM:  predicts next WORD (surface level)
JEPA: predicts next REPRESENTATION (abstract understanding)
```
Goal: build world models that understand causality and physics.
Relevance to SYMBITE: future feedback.py should predict your INTENT,
not just your next word.

---

## SPEC FRAMEWORK — Goal Engine
```
S — Select it   → define the goal in one sentence
P — Project it  → visualise already having it (present tense)
E — Expect it   → firm belief it's coming (daily affirmation)
C — Collect it  → receive and acknowledge when it manifests
```
SYMBITE implementation: goals table + daily briefing injection + Collect celebration.

---

## SESSION 5 — CHARACTER LAYER (character.py)

### Enum — Named Constants with Type Safety
```python
class CoreValue(str, Enum):
    HONESTY = "honesty"
```
- Prevents string typos. `CoreValue.HONESTYY` crashes immediately. `"honestyy"` silently fails.
- `(str, Enum)` = multiple inheritance. Gets string behaviour (JSON-serializable) + enum strictness.
- `.name` → `"HONESTY"` (the attribute name). `.value` → `"honesty"` (the assigned value).

---

### Pydantic `Field(...)` vs `Field(None)`
```python
is_valid: bool = Field(...)        # required — must be supplied, no default
violation_type: Optional[CoreValue] = Field(None, ...)  # optional — defaults to None
```
- `...` = Ellipsis. Python's symbol for "required, no default."
- `Optional[X]` = shorthand for `Union[X, None]`. Can be X or nothing.
- Pydantic validates at construction time — bad data raises `ValidationError` immediately.

---

### Encapsulation — `_` prefix convention
```python
self._laws: Dict[CoreValue, str] = { ... }
```
- `_` prefix = "private, internal use only." Not enforced by Python — it's a trust contract.
- Signals to other developers: don't reach in here from outside the class.

---

### Prompt Injection Pattern
```python
def get_system_directive(self) -> str:
    directive = "### NON-NEGOTIABLE CHARACTER LAWS ###\n"
    for value, rule in self._laws.items():
        directive += f"- **{value.name}**: {rule}\n"
    return directive
```
- Define personality in code once. Inject into every system prompt programmatically.
- `.items()` on a dict gives `(key, value)` tuples. `for value, rule` unpacks in one line.
- Change the law in one place → all prompts across the system update automatically.

---

### LLM-as-Judge Pattern
```
User → Brain (Haiku) → draft response
                             ↓
                     evaluate_draft()  ← Judge LLM (Haiku again, cheap)
                             ↓
                 is_valid=True → send to UI
                 is_valid=False → correction_prompt → Brain retries
```
- A second LLM reviews the first LLM's output before it reaches the user.
- Used in production AI for safety, quality control, and alignment.
- `correction_prompt` tells the brain HOW to fix the violation specifically.

---

### Mock-First Development
```python
if "I am not sure, but I think" in draft_response:   # keyword sentinel
    return CharacterEvaluation(is_valid=False, ...)
```
- Build the plumbing with fake data first. Wire in the real LLM call later.
- Tests all the surrounding logic (logging, return types, data flow) without needing the API.
- Standard TDD (Test-Driven Development) practice.

---

### Structured Logging
```python
logger = logging.getLogger("AURA.Character")
logger.warning("Character Breach detected: HONESTY")
```
- `logging` > `print()` because: can save to file, filterable by level, has timestamps.
- Levels: `DEBUG → INFO → WARNING → ERROR → CRITICAL`
- `"AURA.Character"` creates a hierarchy. `AURA` parent, `Character` child. Control them together.
- In real AI systems: every breach is logged for future fine-tuning of the model.

---

## SESSION 6 — PERCEPTION LAYER (perception.py)

### The Purpose of perception.py
Before brain.py answers you, perception.py runs silently and builds a snapshot of right now.
Three questions it answers:
- What time of day is it? (Time context)
- How busy is today? (Schedule context)
- What is Chandu's likely mood? (Mood signal)
One output: a `PerceptionContext` object injected into the brain's system prompt.

---

### Data vs Logic — Separation of Concerns
```python
# BAD — data buried inside logic
if hour >= 5 and hour < 9:
    return "early_morning"
elif hour >= 9 and hour < 12:
    return "morning"

# GOOD — data is a table, logic is a loop
_TIME_BUCKETS = [
    (5,  9,  TimeOfDay.EARLY_MORNING),
    (9,  12, TimeOfDay.MORNING),
]
for start, end, label in _TIME_BUCKETS:
    if start <= hour < end:
        return label
```
- Data in one place. Logic in one place. To add a new time slot → add one row to the list, touch nothing else.
- This is the Table-Driven Design pattern. Used everywhere in production systems.

---

### Tuple Unpacking
```python
for start, end, label in _TIME_BUCKETS:
```
- Each item in the list is a tuple: `(5, 9, TimeOfDay.EARLY_MORNING)`
- Python unpacks all 3 values into named variables in one line.
- Without it: `bucket[0]`, `bucket[1]`, `bucket[2]` — unreadable.
- With it: reads like English. `start <= hour < end` tells the story.

---

### Chained Comparisons
```python
if start <= hour < end:   # Python only
# same as:
if start <= hour and hour < end:
```
- Python allows chaining. Most languages don't. Shorter and clearer.

---

### Early Return Pattern
```python
def _classify_day(plans):
    if total <= 2:
        return DayLoad.LIGHT    # exits here if true
    if total <= 5:
        return DayLoad.NORMAL   # exits here if true
    return DayLoad.HEAVY        # only if both above were false
```
- Each `return` exits the function immediately. No need for `elif`.
- Reads top to bottom like a checklist. Cleaner than nested if/else.
- Rule: if a branch returns, the next `if` doesn't need `elif`.

---

### Edge Case First
```python
def _classify_time(hour: int) -> TimeOfDay:
    if hour >= 21 or hour < 5:   # handle the weird case FIRST
        return TimeOfDay.NIGHT
    for start, end, label in _TIME_BUCKETS:  # then clean logic
        ...
```
- Night wraps midnight: hour 22 AND hour 2 are both night — opposite ends of 0–23.
- Handle the edge case before the loop. Loop only runs for clean hours (5–20).
- Rule: identify what breaks the pattern first, handle it, then write the happy path.

---

### Frequency Analysis (Mood Detection)
```python
stress_score   += sum(1 for kw in _STRESS_SIGNALS   if kw in text)
positive_score += sum(1 for kw in _POSITIVE_SIGNALS if kw in text)
```
- Scan a list of messages. Count keyword hits in each bucket.
- Whichever bucket has more hits wins → that's the mood signal.
- No LLM call. No API cost. Pure string pattern matching. O(n×k) — n messages, k keywords.
- This is the same pattern as personality.py's observe(). You've seen it before.
- `.lower()` on the message before scanning → "ERROR", "Error", "error" all match.

---

### List vs Dict — When to Use Which
```python
# Use a LIST when you only care if something EXISTS
_STRESS_SIGNALS = ["stuck", "broken", "error"]
if "stuck" in _STRESS_SIGNALS   # membership check

# Use a DICT when you need to MAP a key to a value
_LAWS = {CoreValue.HONESTY: "Never pretend..."}
rule = _LAWS[CoreValue.HONESTY]  # lookup by key
```
- List = collection of items. Dict = collection of key→value pairs.
- If you don't need the value, use a list. Simpler.

---

### Data Transfer Object (DTO) — PerceptionContext
```python
class PerceptionContext(BaseModel):
    time_of_day:     TimeOfDay
    day_load:        DayLoad
    mood_signal:     MoodSignal
    total_plans:     int
    completed_plans: int
    pending_plans:   int
```
- perception.py produces this ONE object. brain.py consumes it.
- Neither side knows how the other works. They only agree on this shape.
- This is the contract between two modules. Change the internals of either — the contract stays the same.
- Pattern name: DTO (Data Transfer Object). Used in every professional backend system.

---

### Dependency Injection
```python
class AuraPerception:
    def __init__(self, db):   # db is PASSED IN, not created here
        self._db = db
```
- AuraPerception doesn't import or create the database. It receives it.
- Why: in tests, you can pass a fake DB. In production, you pass the real one.
- The class doesn't care WHICH database — only that it has the methods it needs.
- Pattern name: Dependency Injection. Makes code testable and loosely coupled.

---

### to_prompt_snippet() — Rendering Data for the LLM
```python
def to_prompt_snippet(self) -> str:
    return (
        f"- Time: {self.time_of_day.value}\n"
        f"- Day load: {self.day_load.value}\n"
        f"- Mood: {self.mood_signal.value}\n"
    )
```
- The PerceptionContext knows how to describe itself in plain English.
- brain.py calls this one method — it never reads raw fields.
- Rule: the data object should know how to render itself. brain.py shouldn't format strings.

---

### New Bugs Fixed This Session

| Bug | File | Lesson |
|-----|------|--------|
| Auto-imported wrong `TimeOfDay` from google library | perception.py | Editor autocomplete can import the wrong thing — always check line 1–10 |
| `_TIME_BUCKETS` indented inside class | perception.py | Indentation = ownership. Module-level code starts at column 0 |
| `def func(x): ->Type:` | perception.py | Syntax: `def func(x) -> Type:` — colon goes at the END, after the return type |
| `BUSKETS` instead of `BUCKETS` | perception.py | Typos in variable names cause NameError at runtime |

---

## BUGS I'VE FIXED (lessons learned)

| Bug | File | Lesson |
|-----|------|--------|
| `keyboardInterrupt` | start.py | Python is case-sensitive everywhere |
| `self.Personality` vs `self.personality` | brain.py | attributes are case-sensitive |
| Called `_build_system_prompt` before `observe()` | brain.py | order of operations matters |
| `signals["is_score"]` | personality.py | key name must match exactly |
| `scan/notify/run` outside class | ai_watch_agent.py | indentation = ownership in Python |
| `from pyparsing import results` | ai_watch_agent.py | don't import what you don't use |
| `"clam"` instead of `"calm"` | personality.py | typos in strings go into Claude's brain |
| Duplicate imports | api/main.py | import once at the top |

---

## MENTAL MODELS TO REMEMBER

**The restaurant analogy (APIs):**
- You (frontend) = customer
- Waiter (FastAPI) = API layer
- Kitchen (brain.py) = processing
- Chef's tools (Claude, DB, weather) = external services

**Static method = recipe (no kitchen needed)**
**Class method = chef (needs the kitchen)**
**Instance method = specific dish being cooked (needs this kitchen + this order)**

**append vs extend:**
```python
list.append([1,2,3])  → adds one item: [existing, [1,2,3]]
list.extend([1,2,3])  → merges:        [existing, 1, 2, 3]
```

**Blocking vs Non-blocking:**
```python
subprocess.run()   → waits. Nothing else happens until done.
subprocess.Popen() → fires and forgets. Code keeps running.
```

---

## SESSION 7 — FEEDBACK LAYER (feedback.py) + WIRING

### What feedback.py does
Two jobs in one file:
1. **Quality Gate** — grades AURA's draft before it reaches you. Rejects bad drafts.
2. **Preference Memory** — stores your corrections in the DB. Injects them back into the next prompt.

Both answer the same question: *"Is AURA getting better at serving you?"*

---

### FeedbackType Enum
```python
class FeedbackType(str, Enum):
    CORRECTION = "correction"   # "wrong", "stop", "not that"
    PREFERENCE = "preference"   # "I like", "always do this"
    PATTERN    = "pattern"      # AURA detected repeated behaviour
```
Closed vocabulary — Enum prevents typos. If you type `FeedbackType.CORECTION` it crashes at definition, not silently at runtime.

---

### FeedbackEvent — DTO
```python
class FeedbackEvent(BaseModel):
    user_id:       int          = Field(...)
    feedback_type: FeedbackType = Field(...)
    context:       str          = Field(...)   # what AURA said
    correction:    str          = Field(...)   # what you want instead
    captured_at:   str          = Field(default_factory=lambda: datetime.now().isoformat())
```
One correction = one event. Store every event, never delete. State is always derivable from history.
Pattern name: **Event Sourcing** (Netflix watch history, bank ledger).

---

### FeedbackReport — Quality Gate Result
```python
class FeedbackReport(BaseModel):
    is_satisfactory: bool          = Field(...)
    quality_score:   float         = Field(...)        # 0.0 to 1.0
    critique:        Optional[str] = Field(None, ...)  # None = optional
    required_fixes:  List[str]     = Field(default_factory=list)
```
`Optional[str] = Field(None, ...)` — the `None` is mandatory for optional fields. Miss it → Pydantic ValidationError.
`default_factory=list` — never use `default=[]`. Mutable defaults are shared across all instances (Python gotcha).

---

### FeedbackJudge — The Gate
```python
def evaluate(self, draft, user_input, perception_context) -> FeedbackReport:
    score = 1.0   # start at perfect
    if "as a AI language model" in draft.lower():
        score = 0.5   # override — this is a hard floor for this violation
    if "stressed" in perception_context.lower() and len(draft) > 500:
        score = 0.3
```
- `score = 0.5` = override (set to exactly this). `score -= 0.3` = subtract (accumulate). These mean different things — know which you want.
- Threshold: `if score >= 0.7` → pass. Below 0.7 → reject, return required fixes.

---

### FeedbackMemory — DB Layer
```python
class FeedbackMemory:
    def __init__(self, db):
        self._db = db                         # injected, not created

    def record(self, event: FeedbackEvent):
        self._db.save_feedback(event.model_dump())   # Pydantic → dict → DB

    def load(self, user_id, limit=20) -> List[FeedbackEvent]:
        rows = self._db.get_feedback(user_id, limit=limit)
        return [FeedbackEvent(**row) for row in rows]  # dict → Pydantic
```
`model_dump()` = Pydantic model → plain dict. `FeedbackEvent(**row)` = dict → Pydantic.
These two are mirrors of each other. Used at every Pydantic↔DB boundary.

---

### FeedbackContext — Prompt Injection
```python
class FeedbackContext:
    def __init__(self, db):
        self._memory = FeedbackMemory(db)

    def to_prompt_snippet(self, user_id) -> str:
        events = self._memory.load(user_id, limit=10)
        if not events:
            return ""
        lines = [f"- [{e.feedback_type.value}] {e.correction}" for e in events]
        return "### USER FEEDBACK HISTORY ###\n" + "\n".join(lines)
```
This is the payoff. Saved corrections reach the LLM through this method.
Without this → events sit in DB doing nothing. With this → AURA actually learns you.

---

### Wiring character.py into brain.py ✅
```python
# brain.py — 3 places changed:
from core.character import SymbioteCharacter          # 1. import

self.character = SymbioteCharacter()                  # 2. in __init__

system_prompt += self.character.get_system_directive() # 3. in _build_system_prompt
```
5 immutable laws now inject into every Claude API call.

---

### Bugs caught this session
| Bug | Lesson |
|-----|--------|
| `scores = 1.0` (plural) | Used `score` everywhere else → NameError. Variable names must be 100% consistent. |
| `required_fixed` field vs `required_fixes` keyword | Pydantic field name ≠ kwarg name → ValidationError. Both must match exactly. |
| `Optional[str] = Field(description=...)` missing `None` | Optional fields need `None` as first arg. |
| `def recrd(self, ...)` typo | Method name typo — unfindable at runtime. Python doesn't warn you. |
| `self.db` vs `self._db` | Inconsistent with rest of codebase. Always use `_` prefix for internal state. |
| `to_prompt_snippet` indented inside `__init__` | Nested function, not a method. Dies when `__init__` returns. AttributeError on call. |

---

---

## SESSION 8 — FULL WIRING + BUG SWEEP

### What got wired today
All three core modules now inject into every brain.py system prompt call:

```
brain.py _build_system_prompt() now builds:
  1. Base identity + tone + context + weather      (was already there)
  2. + character.get_system_directive()            (wired session 7)
  3. + perception.observe().to_prompt_snippet()    (wired today ✅)
  4. + feedback_ctx.to_prompt_snippet()            (wired today ✅)
```

AURA now knows: WHO she is (character) + WHAT the environment is (perception) + WHAT you've corrected before (feedback). All three hit Claude on every message.

---

### Wiring Pattern (how ALL modules connect to brain.py)
```python
# Step 1 — import at top
from core.perception import AuraPerception
from core.feedback   import FeedbackContext

# Step 2 — instantiate in __init__ (once per session)
self.perception   = AuraPerception(self.memory.db)
self.feedback_ctx = FeedbackContext(self.memory.db)

# Step 3 — inject in _build_system_prompt (every message)
perception_snippet = self.perception.observe(self.user_id).to_prompt_snippet()
system_prompt += f"\n\nCURRENT AWARENESS:\n{perception_snippet}"

feedback_snippet = self.feedback_ctx.to_prompt_snippet(self.user_id)
if feedback_snippet:
    system_prompt += f"\n\n{feedback_snippet}"
```

Key: `self.memory.db` is the AuraDatabase instance. Every module that needs DB gets it this way — no new DB connections, no duplicate instances.

---

### database.py — feedback table added
```python
# New table
CREATE TABLE IF NOT EXISTS feedback (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    feedback_type TEXT    NOT NULL,
    context       TEXT    NOT NULL,
    correction    TEXT    NOT NULL,
    captured_at   TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
)

# New methods
save_feedback(data: dict)              # FeedbackEvent.model_dump() → DB row
get_feedback(user_id, limit=20)        # DB rows → list[dict] → FeedbackEvent objects
```

Pattern: every module that touches the DB follows the same open-use-close pattern. No persistent connection. Safe for SQLite's threading model.

---

### Bugs fixed this session

| Bug | File | What it was | Fix |
|-----|------|------------|-----|
| `now.date()` passed to DB | perception.py | `date` object vs `str` — DB expects `"YYYY-MM-DD"` | `now.strftime("%Y-%m-%d")` |
| `get_recent_conversations` | perception.py | Method doesn't exist on AuraDatabase — name mismatch | `get_recent_messages` |
| `"Draft failede quality checks ."` | feedback.py | Typo in critique string | `"Draft failed quality checks."` |

---

### System Prompt — what AURA sees on every message now
```
[Identity: WHO she is — FRIDAY, Irish, Boss, no markdown]
[Mode tone: Personal / Pro / Hybrid]
[Context: today's schedule, morning briefing]
[Weather: live from OpenWeatherMap]
[Character laws: 5 immutable laws — HONESTY, LOYALTY, BOUNDARIES, RESILIENCE, CONSISTENCY]
[Current awareness: time of day, day load, mood signal]     ← NEW
[Feedback history: your past corrections, formatted list]   ← NEW (if any exist)
```

---

---

## SESSION 9 — LEARNING LAYER (learning.py) + CONTINUOUS SELF-LEARNING

### What learning.py does that feedback.py doesn't
```
feedback.py  → you TELL AURA  "stop doing X"          → explicit memory
learning.py  → AURA NOTICES   "Boss goes quiet after long replies"  → implicit memory
```
No correction needed. AURA watches patterns across sessions and adjusts on its own.

### Architecture — 4 classes
```
PatternType     → Enum: BREVITY / TONE / PROACTIVE / AVOIDANCE
LearnedPattern  → DTO: one detected pattern with confidence score + trigger + behavior
PatternDetector → scans conversation history, detects patterns automatically
LearningMemory  → save/load patterns to DB (same pattern as FeedbackMemory)
LearningContext → to_prompt_snippet() → injects learned rules into brain
```

### The Confidence Score — key concept
```python
confidence: float  # 0.0 to 1.0
```
- Single observation = noise. Five repeated observations at 0.85 = real pattern.
- Gate 1 (LearningMemory.save): only persist if confidence >= 0.5
- Gate 2 (LearningContext): only inject into prompt if confidence >= 0.6
- Low confidence stays in detector. Only proven patterns reach Claude.

### PatternDetector — two detectors
```python
_detect_brevity()   # if stressed mood + Boss sends short follow-ups → keep responses under 60 words
_detect_avoidance() # if AURA's last reply was long + Boss's next message is short → disengagement signal
```
Both scan `get_recent_messages(limit=20)` — pure Python, zero API calls, O(1) bounded.

### Wiring into brain.py
```python
# import
from core.learning import LearningContext

# __init__
self.learning_ctx = LearningContext(self.memory.db)

# _build_system_prompt
learning_snippet = self.learning_ctx.to_prompt_snippet(self.user_id)
if learning_snippet:
    system_prompt += f"\n\n{learning_snippet}"
```

### database.py — patterns table added
```sql
CREATE TABLE IF NOT EXISTS patterns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    pattern_type TEXT    NOT NULL,   -- "brevity" | "tone" | "proactive" | "avoidance"
    trigger      TEXT    NOT NULL,   -- what situation activates this
    behavior     TEXT    NOT NULL,   -- what AURA should do
    confidence   REAL    NOT NULL,   -- float, use REAL not TEXT
    observed_at  TEXT    NOT NULL
)
```
WHY `REAL` not `TEXT` for confidence: storing 0.75 as TEXT gives back the string "0.75" — comparisons and sorting break.

### Full system prompt layers — COMPLETE
```
[Identity + tone + context + weather]
[Character laws]          ← character.py
[Current awareness]       ← perception.py
[Feedback history]        ← feedback.py
[Learned patterns]        ← learning.py   ← NEW
```

### Thinking System Architecture (Month 2–3 plan)
```
Layer 1 — Immediate (DONE):    think() → Claude → answer
Layer 2 — Cross-examination:   generate → "challenge this" → reconcile (needs complexity gate)
Layer 3 — Background (Month 2): scheduler every 30min → deep pattern analysis → aura_thoughts table
Layer 4 — Proactive (Month 3):  score thoughts → interrupt if score > 0.75
```
Layers 3 and 4 both write to/read from the same `patterns` table — real-time detector + deep background analysis compound over time.

### Bugs caught this session
| Bug | File | Lesson |
|-----|------|--------|
| `class learnedPattern` lowercase | learning.py | Class names are PascalCase. `learnedPattern` ≠ `LearnedPattern` — NameError when referenced |
| `observed` vs `observed_at` | learning.py | Consistent `_at` suffix for all timestamps across models and DB columns |
| `def __int__` instead of `__init__` | learning.py | `__int__` = integer conversion. Constructor never ran. AttributeError on every call. |
| `get_recent_messages` in LearningMemory.load | learning.py | Copy-paste error — returns conversations not patterns. Must be `get_patterns` |
| `self.memory` vs `self._memory` | learning.py | Missing underscore — inconsistent with all other classes |
| `CREATE TABLE pattern` (singular) | database.py | Table name `pattern` ≠ INSERT target `patterns`. "No such table" crash |
| `pattern_name` column vs `pattern_type` insert | database.py | Column name mismatch — SQLite rejects the insert |
| `LIMIT ?,` trailing comma | database.py | Invalid SQL syntax — crashes every get_patterns() call |

---

---

## SESSION 10 — PRODUCTION AUDIT + PERSONALITY REWRITE

### Code Audit Results (rated before fixes)
| File | Score | Main Issue |
|------|-------|-----------|
| system_agent.py | 8/10 | No caching, no retry |
| database.py | 7/10 | No indexes, no transactions |
| memory.py | 7/10 | Creates second AuraDatabase instance |
| character.py | 7/10 | evaluate_draft never called |
| perception.py | 6.5/10 | No caching, called every message |
| brain.py | 6/10 | No content check, save_message missing |
| feedback.py | 6/10 | FeedbackJudge never called, record() never called |
| learning.py | 5.5/10 | PatternDetector never called |
| helper.py | 5/10 | Prototype functions, blocking sleep |
| personality.py | 5/10 | 9 of 15 states unreachable |

### personality.py — Full Rewrite
**Problem:** `feel()` was a simple if/elif chain. 9 of 15 states could never fire.

**Solution — Rule Engine Pattern (invented by Chandu):**
```python
rules = [
    (1, "dominant",   condition),
    (2, "frustrated", condition),
    ...
]
for _, state, condition in rules:
    if condition:
        return state
return "bonded"
```
To add a new state: add one tuple. Priority is explicit. Nothing else changes.
This is better than if/elif because data drives logic, not code structure.

**New signals added to observe():**
```
is_goal_win   → "shipped", "deployed", "done" → ascendant
is_switching  → "actually", "wait", "no"       → unstable
is_learning   → "explain", "why", "how does"   → evolution
is_threat     → "deadline", "urgent", "asap"   → defensive
```

**Weighted "but" split — production fix:**
```python
# OLD — throws away everything before "but"
# "I shipped it but I'm exhausted" → score -10 → parasitic (WRONG)

# NEW — both halves score, second weighted more
before * 0.3 + after * 0.7
# "I shipped it but I'm exhausted" → score -5.5 → reclamation (CORRECT)
```
WHY: "but" signals contrast, not total replacement. Both halves carry signal.

**_score_text() extracted as separate method — DRY principle:**
One function, called twice (before + after "but"). No duplication.

### FeedbackJudge wired into brain.py think() loop
```python
# Now happens on every response before it reaches user:
report = judge.evaluate(ai_reply, user_message, perception)
if not report.is_satisfactory:
    → inject fix instruction → Claude retries → judge runs again
else:
    → save to DB → return to user
```
Also added: `if not response.content` guard — never trust external API blindly.

### Bugs caught this session
| Bug | File | Lesson |
|-----|------|--------|
| 9 states unreachable | personality.py | if/elif order determines reachability — use rule engine instead |
| `score >= -1.0` for protective | personality.py | `>=` fires on positive scores too — inverted logic |
| `" stagnant"` leading space | personality.py | Dict key `" stagnant"` ≠ `"stagnant"` — silent fallback to bonded |
| `dominant` condition inverted | personality.py | `and is_short` → `and not is_short` |
| `_score_text` returned nothing | personality.py | Missing `return score` — function returned None silently |
| Syntax error `,message` | personality.py | Leading comma in argument |
| Duplicate `observe()` methods | personality.py | Python uses the last definition — first is silently ignored |
| `import logging as logger` | brain.py | Wrong pattern — use `logger = logging.getLogger("AURA.brain")` |
| `FeedbackJudge` not imported | brain.py | Used but not imported → NameError at runtime |
| `save_messages` plural | brain.py | Method doesn't exist → DB never saved anything |

---

### PatternDetector wired into brain.py think() loop
```python
# Runs silently after every successful response
perception_ctx = self.perception.observe(self.user_id)
patterns = self.pattern_detector.detect(
    self.user_id,
    perception_ctx.mood_signal.value,  # "stressed", "positive" etc.
)
self.learning_memory.save_batch(patterns)
```
WHY wrapped in try/except: Pattern detection is non-critical. If it fails,
AURA still responds. A background job should never crash the main flow.
This is called a "silent failure boundary" — production systems isolate
non-critical work so failures don't cascade.

### The complete think() flow now:
```
1. User message added to history
2. System prompt built (character + perception + feedback + learning)
3. Claude API called
4. Tool use loop if needed
5. Draft generated
6. FeedbackJudge evaluates draft       ← NEW (session 10)
   → fail: inject fix, retry
   → pass: continue
7. Save to DB
8. PatternDetector runs silently       ← NEW (session 11)
9. Return response to user
```

---

## WHAT TO BUILD NEXT (in order)
1. ~~personality.py~~ ✅ REBUILT — all 15 states reachable
2. ~~FeedbackJudge wired~~ ✅ DONE — drafts judged before sending
3. ~~PatternDetector wired~~ ✅ DONE — learning now runs after every response
4. ~~perception caching~~ ✅ DONE — 60s TTL cache + fixed 3x duplicate calls → 1
5. ~~SPEC Engine~~ ✅ DONE + WIRED
6. ~~reasoning.py~~ ✅ DONE + WIRED
7. ~~symbiote.py~~ ✅ DONE + WIRED
8. ~~vault.py~~ ✅ DONE + WIRED (read side only — VaultExtractor next)
9. **VaultExtractor** — auto-write side of vault. Runs after every response.
10. **core/router.py** — Response Router. Fast path / slow path.
11. **core/twin.py** — Digital Twin (Phase 4)
12. **core/operator.py** — Life Operator (Phase 5)

---

## SESSION 11 — VAULT + SYSTEMS THINKING + TESTING

### vault.py — Boss's Second Brain
```
memory.py  → AURA's working memory (what's happening in Boss's LIFE today)
vault.py   → Boss's second brain  (what Boss KNOWS and how he THINKS)
```
Two different brains. One bond. brain.py reads both on every message.

### 4 classes in vault.py
```
VaultEntry    — DTO. One note. title, body, tags[], links[], source, created_at
VaultMemory   — DB layer. record() = upsert (check then insert or update)
VaultSearch   — 3-layer scoring: tag match (+2), title match (+3), body overlap (+0.5 each)
VaultContext  — to_prompt_snippet(user_id, query) → injected into brain.py
```

### Upsert Pattern
```python
existing = db.get_vault_entry_by_title(user_id, title)
if existing:
    db.update_vault_entry(existing["id"], data)   # update
else:
    db.save_vault_entry(data)                      # insert
```
Check before insert. Prevents duplicates. Used in every system that accumulates data over time.

### Set Intersection — O(1) lookup
```python
query_words & body_words   # & = intersection between two sets
```
Set membership check is O(1). List check is O(n). Always convert to set before searching.

### Pipeline Pattern (VaultContext)
```
Load → Search → Format → Return
```
Each step feeds the next. Swap any step without touching others.

### Real Engineering Approach (THIS SESSION'S BIG LESSON)
Before touching code, answer 5 questions:
1. What is the INPUT?
2. What STATE changes?
3. What DATA is needed?
4. What DECISIONS happen?
5. What OUTPUT should come out?

This separates engineers from coders.

### Time Complexity & Response Time Analysis
```
All Python logic combined  →  ~50ms
One Claude API call        →  ~2-4 seconds
Bottleneck: always the API. Optimise Python last.
```

### Response Router concept (NOT YET BUILT)
```
DATA   → answer from DB/Python (~5ms, $0)
HAIKU  → small prompt + Haiku API (~800ms, $0.001)
FULL   → complete pipeline (~3-4s, $0.005)
```
LLMs are reasoning engines, not databases. Fetch data yourself. Never ask LLM to find what you already have.

### DB Indexes — why they matter
```sql
CREATE INDEX IF NOT EXISTS idx_vault_user ON vault(user_id)
```
Without index: SQLite scans every row. O(n).
With index: SQLite jumps directly. O(log n).
Add index on every column you filter by (WHERE user_id = ?).

### Bugs caught this session
| Bug | File | Lesson |
|-----|------|--------|
| AI phrasing check used uppercase "AI" against lowercased draft | feedback.py | `.lower()` only lowercases the target. Search string must also be lowercase. |
| vault table created after conn.close() | database.py | Connection closes once. Any execute after close = crash. |
| perception.observe() called 3× per message | brain.py | Capture result once. Pass it everywhere. |
| `import logging as logger` | database.py | Wrong pattern. Always `logging.getLogger("AURA.X")`. |
| _TAGS vocabulary had 0 AURA-specific words | reasoning.py | Cache never hit for AURA conversations. Add domain vocab. |

### Tests built this session
- `tests/test_vault.py` — 5 tests: table exists, save/load, upsert, search ranking, prompt injection
- `tests/test_all_systems.py` — 133 tests across all 9 modules. Run with: `python -m tests.test_all_systems`

---

## STARTUP NOTES
- Category: Personal Intelligence (not AI assistant)
- Moat: behavioral data that gets harder to replace over time
- Pitch: "What is the one problem SYMBITE solves that nothing else solves?"
- Path: Build → 10 users who can't stop → YCombinator application

---

## SESSION 12 — VAULT EXTRACTOR + ROUTER + MORNING + EVENING + WATCHER

### vault_extractor.py — Auto-writes to Vault after every response
**Problem:** Vault was always empty. Nobody was writing to it.
**Solution:** After every response, Symbite silently checks if the conversation had something worth saving, and if so, extracts it into the vault automatically.

**Architecture:**
```
ExtractionGate._should_extract()  → gate check (cheap, no API)
VaultExtractor.extract_and_save() → gate → prompt → Haiku → parse → save
```

**CS Concepts:**
- **Early exit / Short-circuit** — gate returns False at FIRST disqualifying condition. Saves API cost.
- **Set O(1)** — `_SKIP_WORDS = {"thanks", "ok", "yes"}` set not list. Membership check O(1) vs O(n).
- **Fire-and-forget** — entire extractor wrapped in try/except. Never crashes main flow.
- **Structured prompting** — forcing JSON output from Haiku, then `json.loads()` to parse.
- **Safe dict access** — `.get("title", "Untitled")` not `dict["title"]` — external data is never clean.

---

### router.py — Response Router
**Problem:** Every message went through the full pipeline — ReasoningEngine, vault search, all of it. Expensive and slow for "thanks" or "what time is it?"
**Solution:** Classify the message BEFORE processing. Route to DATA / HAIKU / FULL.

```python
class Route(Enum):
    DATA  = "data"    # fetch from DB, no API
    HAIKU = "haiku"   # small API call
    FULL  = "full"    # full pipeline, reasoning, vault

_DATA_TRIGGERS  = {"plan", "schedule", "goal", "weather", "time", "date"}
_HAIKU_TRIGGERS = {"hey", "hi", "thanks", "cool", "morning", "night"}
```

**CS Concepts:**
- **Enum vs magic strings** — `Route.DATA` not `"data"`. Type safety. Crashes at definition, not runtime.
- **Set intersection** — `words & _DATA_TRIGGERS` O(min(m,n)). Fastest word overlap check.
- **Greedy early exit** — DATA checked first (cheapest), FULL is default (most expensive).
- **Strategy Pattern** — router CLASSIFIES only. brain.py EXECUTES. No circular dependency.

**Key bug caught:**
- `Route = ResponseRouter.classify()` — capital R overwrote the Enum class itself. Fixed to `route =` lowercase.

---

### morning.py — MorningBriefing
**What it does:** Generates Boss's daily morning briefing — memory + weather + calendar + goals + yesterday's tasks → Haiku → briefing string.

**Key patterns:**
- **Lazy init + cache** — `_memory_cache: dict[int, AuraMemory] = {}`. Check before creating. O(1) reuse.
- **Graceful degradation** — each data source (weather, calendar) wrapped independently in try/except. One failure = safe default, not crash.
- **String builder** — list.append() then `"\n".join()`. Never `string +=` in a loop (O(n²)).

**Key bugs caught:**
- `_get_memory` logic inverted — was creating new cache every call. Fix: `if user_id not in cache`
- `health_line` used before defined when health was None

---

### evening.py — EveningSummary
Same DI pattern as morning. Looks BACK at the day — today's tasks + goals + conversations + tomorrow.

---

### watcher.py — SymbiteWatcher (daemon thread)
**What it does:** Runs every 60 seconds in the background. Fires morning briefing at wake_time, evening summary at sleep_time. Fully autonomous — no user message needed.

**Key patterns:**
- **Daemon thread** — `daemon=True` kills thread when main process exits. No orphan threads.
- **Sleep loop** — `time.sleep(60)` between checks. Near-zero CPU.
- **Event deduplication** — `_fired: set[str]` prevents double-firing in 5-minute window.
- **Time window check** — `abs((now_dt - target_dt).total_seconds() / 60) <= 5`
- **Midnight reset** — `if now_hour == 0: self._fired.clear()` resets for next day.

**Key bugs caught:**
- `def in_window` (no underscore) — called as `self._in_window` everywhere → AttributeError
- `start()` calling `self._run()` directly — infinite loop, blocks main thread. Fix: `threading.Thread(daemon=True)`
- DB had `wake_time = 'yes'` — added `try/except ValueError` in `_in_window`, returns False

---

## SESSION 13 — CALENDAR CONNECTOR + DIGITAL TWIN

### connectors/calendar.py — CalendarConnector

**Why AppleScript:** Mac-native. No OAuth. Works with ANY calendar synced to Mac Calendar (iCloud, Google, Outlook). Falls back to empty list if unavailable.

**Architecture:**
```
__init__()                  ← snapshot self._today = datetime.now().strftime("%Y-%m-%d")
_run_applescript(script)    ← subprocess OS bridge → raw string
_parse_events(raw)          ← defensive parsing → list of dicts
get_today_events()          ← AppleScript → _run → _parse → list[dict]
get_tomorrow_events()       ← same but tomorrow's date range
to_prompt_snippet()         ← snapshot() → formatted string for morning briefing
```

**CS Concepts:**
- **Subprocess / OS Bridge** — `subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)`. List not string. text=True for string output. timeout=10 = safety valve.
- **Snapshot vs Live read** — `datetime.now()` once in `__init__`, reuse everywhere. Stable value.
- **Defensive parsing** — always check empty, strip whitespace, skip blanks on external OS output.
- **Single Responsibility** — `_run_applescript` talks to OS. `_parse_events` cleans output. They don't know each other.

**Wired into:** `core/morning.py` `_gather_context()` as `"calendar"` key.

**Key bugs caught:**
- `subprocess.check_output('osascript', ...)` — string not list, returns bytes, no timeout
- `from asyncio import timeout` — wrong import. timeout is just a kwarg, needs no import
- `set the time to theDate to 0` → `set the time of theDate to 0`
- `tomorrowDate` used but variable named `tomorrow`

---

### core/twin.py — DigitalTwin

**What it is:** A live snapshot of Boss's current state. Not history. Not knowledge. Just: who is Boss RIGHT NOW?

**Difference from other modules:**
```
vault.py   → what Boss KNOWS and THINKS    (permanent knowledge)
memory.py  → what Boss PLANNED today       (daily schedule)
twin.py    → what Boss IS right now        (live state, recomputed every call)
```

**Architecture:**
```python
__init__(db: AuraDatabase, perception: AuraPerception)  ← DI, no creating
get_stress_level(user_id) -> str    ← "low/medium/high" — threshold classification
snapshot(user_id) -> dict           ← aggregator — mood, energy, focus, stress, counts
to_prompt_snippet(user_id) -> str   ← formats snapshot for system prompt
```

**CS Concepts:**
- **Threshold Classification** — `score = len(goals) + len(overdue)`. If <= 2: low. <= 5: medium. else: high. O(1).
- **Aggregator Pattern** — `snapshot()` collects from perception + DB, returns one unified dict.
- **Object attribute vs dict** — `perception.mood_signal.value` NOT `perception.get("mood")`. Pydantic model uses dot notation.

**Wired into:** `brain.py` `_build_system_prompt()` as `"BOSS STATE"` layer.

**Key bugs caught:**
- `db = AuraDatabase` (default) vs `db: AuraDatabase` (type hint) — equals not colon
- `self._perception.get_context()` → `.observe(user_id)` — correct method name
- `perception.get("mood", "neutral")` — dict access on Pydantic object. Fix: `perception.mood_signal.value`

---

## SYSTEM PROMPT LAYERS (COMPLETE as of 2026-05-26)

```
[Identity + tone + weather]       ← base
[Character laws]                  ← character.py
[Current awareness]               ← perception.py  (60s cache)
[Feedback history]                ← feedback.py
[Learned patterns]                ← learning.py
[BOSS STATE]                      ← twin.py         ← NEW
[Active goals]                    ← spec.py
[Inner monologue]                 ← reasoning.py (FULL route only)
[Second brain — vault]            ← vault.py (top-3 relevant)
[Bond override]                   ← symbiote.py
```

---

## BUILD STATUS (as of 2026-05-26)

| File | Status |
|------|--------|
| `core/personality.py` | DONE + WIRED |
| `core/perception.py` | DONE + WIRED |
| `core/character.py` | DONE + WIRED |
| `core/feedback.py` | DONE + WIRED |
| `core/learning.py` | DONE + WIRED |
| `core/spec.py` | DONE + WIRED |
| `core/reasoning.py` | DONE + WIRED |
| `core/symbiote.py` | DONE + WIRED |
| `core/vault.py` | DONE + WIRED |
| `core/vault_extractor.py` | DONE + WIRED |
| `core/router.py` | DONE + WIRED |
| `core/memory.py` | DONE + WIRED |
| `core/morning.py` | DONE + WIRED |
| `core/evening.py` | DONE + WIRED |
| `core/watcher.py` | DONE + WIRED |
| `connectors/calendar.py` | DONE + WIRED |
| `core/twin.py` | DONE + WIRED |
| `core/identity.py` | BUILD NEXT |
| `connectors/gmail.py` | SKELETON — Phase 3 |
| `connectors/health.py` | SKELETON — Phase 4 |
| `core/operator.py` | NOT STARTED — Phase 5 |

---

## NEXT SESSION — BUILD `core/identity.py`

**The problem:** Symbite has no idea who is talking to it. Anyone with Mac access IS Boss.
**The solution:** Boss sets a secret PIN at setup. Every session asks for it silently. Wrong PIN = Symbite goes cold. No data. No response.

**Architecture:**
```
IdentityGuard
    __init__(db: AuraDatabase)
    is_configured(user_id) -> bool     ← has Boss set a PIN yet?
    set_pin(user_id, pin) -> None      ← hash with bcrypt, store in DB
    verify(user_id, attempt) -> bool   ← check attempt against stored hash
```

**Security rule:** NEVER store raw PIN. Always bcrypt hash. Same as password storage.

**Tests:** `python -m tests.test_all_systems` (133 passing as of this session)

---

## SESSION 14 — 2026-05-28

### What was fixed this session

#### brain.py — Cross-Session Memory
**Problem:** `conversation_history = []` on every startup. Symbite forgot everything between sessions.
**Fix:** On startup, load last 20 messages from DB and convert format:
```python
_recent = self.memory.db.get_recent_messages(self.user_id, limit=20)
self.conversation_history = [
    {"role": m["role"], "content": m["message"]}
    for m in _recent
]
```
**Key concept:** DB format uses `"message"` key. Claude API uses `"content"` key. Must convert between them.

#### reasoning.py + vault_extractor.py — JSON Parse Bug
**Problem:** `json.loads("")` → `Expecting value: line 1 column 1 (char 0)`. Claude sometimes returns empty string or markdown-wrapped JSON.
**Fix:** Strip markdown fences, guard against empty:
```python
if raw.startswith("```"):
    raw = raw.strip("`").strip()
    if raw.startswith("json"):
        raw = raw[4:].strip()
if not raw:
    return None
data = json.loads(raw)
```

---

### Graph Vault — Junction Table (NEW CONCEPT)

**Problem:** Tags stored as JSON string in vault rows. Finding related entries = O(n) scan.
**Solution:** Junction table `vault_tags(id, entry_id, tag)` — one row per tag.

**CS Concept: Many-to-Many Relationship**
- One entry has many tags
- One tag belongs to many entries
- Junction table is the bridge

**Practice problem completed:**
```python
def related_with_tags(target_id, titles_list):
    # Step 1: find target's tags
    # Step 2: build tag → [titles] adjacency list (defaultdict)
    # Step 3: double-hop — for each tag, grab all titles on that hook
    # Step 4: remove original book from results
```

**Key bugs caught in practice:**
- Missing `:` on function definition
- `title["id "]` — space inside key → KeyError
- Missing `from collections import defaultdict`
- `related_tags` storing IDs, not tags — wrong variable name

**SQL equivalent:**
```sql
SELECT v.*, COUNT(vt.tag) as shared_count
FROM vault v
JOIN vault_tags vt ON v.id = vt.entry_id
WHERE vt.tag IN (
    SELECT tag FROM vault_tags WHERE entry_id = ?
    AND tag IN (
        SELECT tag FROM vault_tags GROUP BY tag HAVING COUNT(entry_id) > 1
    )
)
AND v.id != ?
GROUP BY v.id
ORDER BY shared_count DESC
```
- `COUNT(vt.tag) as shared_count` → tag weights (more shared tags = ranked higher)
- `HAVING COUNT(entry_id) > 1` → auto-pruning (singleton tags are not bridges)
- `GROUP BY v.id` → needed when using COUNT
- `DISTINCT` not needed when using GROUP BY

**New DAO methods:**
- `save_tags(entry_id, tags)` — `executemany` for bulk insert
- `get_entries_by_tag(tag)` — `(tag,)` tuple, not list comprehension
- `get_related_entries(entry_id)` — self-JOIN through vault_tags

**Bugs caught in student code:**
- `vault_tags(entry_id, tags)` → wrong column name, `tag` not `tags`
- `cursor.executemany("")` stray empty string
- `REFERENCES vault(entry_id)` → should be `vault(id)`
- Missing index `idx_vault_tags_tag`
- `cursor.fetchall()` result not stored or returned
- `[(vault_tag, tag) for vault_tag in tags]` — `tags` not in scope

---

### LRU Cache — Concept (PRACTICE PENDING)

**Why:** plain list for conversation_history = O(n) eviction. LRU = O(1).

**The Data Structure:**
- HashMap → O(1) lookup by key
- Doubly Linked List → O(1) move to front (most recent), O(1) evict tail (least recent)
- Python's `OrderedDict` implements both internally

**Human Memory connection (Atkinson-Shiffrin Model):**
```
Sensory input    → ExtractionGate (filter 99%)
Working memory   → conversation_history LRU Cache (capacity = dynamic)
Consolidation    → evening.py Dream Phase (review day, push to vault)
Long-term        → vault.py (permanent, graph-tagged)
Decay            → LRU eviction (least used drops off)
Strengthening    → hit_count in reasoning_notebook
```

**Cognitive Drag Index (C_d):**
- LOW C_d  → capacity=30, rich responses, surface vault insights
- MED C_d  → capacity=20, normal
- HIGH C_d → capacity=10, simple, act silently, hold interruptions
- C_d=0    → sleep → Dream Phase → consolidate

**Practice problem (STILL PENDING — write this next session):**
```python
class LRUCache:
    def __init__(self, capacity: int): pass
    def get(self, key: str) -> any: pass     # -1 if not found, move to front if found
    def put(self, key: str, value: any) -> None: pass  # evict LRU if at capacity
```

---

### The Real Vision (discovered this session)

Chandu has dementia. Symbite is a Cognitive Prosthetic.

**For dementia patients:**
- AuraTokenDeduplicator — same question 3x → calm single-sentence answer, no frustration
- Hyper-stable 2-hour cache — never evicted
- Family Vault — curated names, faces, relationships
- Proactive anchoring — "You're at home. Michael arrives in 10 minutes." BEFORE panic

**For everyone:**
- Thought Capture — "bathroom idea" → voice → vault → surfaces in evening
- Life Operator — mention "date night" once, Symbite books everything
- Mental load transfer — hold every unfinished thought so your brain doesn't have to

---

### IBHWSS Blueprint Format (Chandu's invention)
Every feature gets this format before any code is written:
- **I** — Idea: what problem this feature solves
- **B** — Build: what files/classes/methods we're creating
- **H** — How: syntax and code mechanics explained
- **W** — What: CS concepts and algorithms used
- **S** — Pseudocode: full feature in pseudocode
- **S** — Stretch: future improvements

---

### Build Status (2026-05-28)

| File | Status |
|------|--------|
| `core/personality.py` | DONE + WIRED |
| `core/perception.py` | DONE + WIRED |
| `core/character.py` | DONE + WIRED |
| `core/feedback.py` | DONE + WIRED |
| `core/learning.py` | DONE + WIRED |
| `core/spec.py` | DONE + WIRED |
| `core/reasoning.py` | DONE + WIRED (JSON fix) |
| `core/symbiote.py` | DONE + WIRED |
| `core/vault.py` | DONE + WIRED (graph upgrade) |
| `core/vault_extractor.py` | DONE + WIRED (JSON fix) |
| `core/router.py` | DONE + WIRED |
| `core/memory.py` | DONE + WIRED |
| `core/morning.py` | DONE + WIRED |
| `core/evening.py` | DONE + WIRED |
| `core/watcher.py` | DONE + WIRED |
| `core/twin.py` | DONE + WIRED |
| `brain.py` | DONE (cross-session memory fixed) |
| `database.py` | DONE (vault_tags, save_tags, get_entries_by_tag, get_related_entries) |
| `core/cognitive_memory.py` | BUILD NEXT |
| `connectors/reminders.py` | BUILD AFTER |
| `core/operator.py` | Phase 2 |
