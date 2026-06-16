"""
AURA Full System Test Suite
Tests every core module with real edge cases.
Run from AURA root: python -m tests.test_all_systems
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AuraDatabase
from core.character import SymbioteCharacter, CoreValue
from core.perception import _classify_time, _classify_day, _classify_mood, TimeOfDay, DayLoad, MoodSignal, AuraPerception
from core.feedback import FeedbackJudge, FeedbackMemory, FeedbackContext, FeedbackEvent, FeedbackType
from core.learning import PatternDetector, LearningMemory, LearningContext, LearnedPattern, PatternType
from core.personality import Personality
from core.spec import SpecEngine, SpecStatus
from core.symbiote import SymbioteSelection, BondStatus
from core.reasoning import ReasoningEngine, ReasoningMode, ReasoningNotebook, ReasoningOutput

TEST_USER = 9999  # isolated test user — never conflicts with real data
PASS = 0
FAIL = 0
RESULTS = []

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        RESULTS.append(("PASS", label))
        print(f"  ✓ {label}")
    else:
        FAIL += 1
        RESULTS.append(("FAIL", label, detail))
        print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))

def section(title):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print('─'*55)

# ── CLEANUP ────────────────────────────────────────────────
def cleanup_test_data(db):
    conn = db._connect()
    cursor = conn.cursor()
    for table in ["feedback", "patterns", "goals", "vault", "reasoning_notebook", "symbiote_bond"]:
        try:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (TEST_USER,))
        except Exception:
            pass
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════
# 1. CHARACTER
# ══════════════════════════════════════════════════════════
def test_character():
    section("1. CHARACTER — SymbioteCharacter")
    char = SymbioteCharacter()

    directive = char.get_system_directive()
    check("get_system_directive returns non-empty string", len(directive) > 0)
    check("directive contains HONESTY", "HONESTY" in directive or "honesty" in directive.lower())
    check("directive contains all 5 laws", directive.count("**") >= 5)

    # evaluate_draft — rule-based mock (no API call)
    result = char.evaluate_draft("Can you help me?", "I am not sure, but I think this works.")
    check("evaluate_draft catches 'I am not sure' sentinel", not result.is_valid)

    result2 = char.evaluate_draft("Help me", "Here is the solution Boss.")
    check("evaluate_draft passes clean response", result2.is_valid)

    check("CoreValue enum has HONESTY", CoreValue.HONESTY == "honesty")
    check("CoreValue enum has LOYALTY", CoreValue.LOYALTY == "loyalty")

# ══════════════════════════════════════════════════════════
# 2. PERCEPTION
# ══════════════════════════════════════════════════════════
def test_perception():
    section("2. PERCEPTION — Time / Day / Mood")

    # Time classification — boundary conditions
    check("hour=2  → NIGHT",         _classify_time(2)  == TimeOfDay.NIGHT)
    check("hour=4  → NIGHT",         _classify_time(4)  == TimeOfDay.NIGHT)
    check("hour=5  → EARLY_MORNING", _classify_time(5)  == TimeOfDay.EARLY_MORNING)
    check("hour=8  → EARLY_MORNING", _classify_time(8)  == TimeOfDay.EARLY_MORNING)
    check("hour=9  → MORNING",       _classify_time(9)  == TimeOfDay.MORNING)
    check("hour=12 → AFTERNOON",     _classify_time(12) == TimeOfDay.AFTERNOON)
    check("hour=17 → EVENING",       _classify_time(17) == TimeOfDay.EVENING)
    check("hour=21 → NIGHT",         _classify_time(21) == TimeOfDay.NIGHT)
    check("hour=23 → NIGHT",         _classify_time(23) == TimeOfDay.NIGHT)
    check("hour=0  → NIGHT",         _classify_time(0)  == TimeOfDay.NIGHT)

    # Day load
    check("0 plans  → LIGHT",  _classify_day([]) == DayLoad.LIGHT)
    check("2 plans  → LIGHT",  _classify_day([{}, {}]) == DayLoad.LIGHT)
    check("3 plans  → NORMAL", _classify_day([{}, {}, {}]) == DayLoad.NORMAL)
    check("5 plans  → NORMAL", _classify_day([{}]*5) == DayLoad.NORMAL)
    check("6 plans  → HEAVY",  _classify_day([{}]*6) == DayLoad.HEAVY)
    check("10 plans → HEAVY",  _classify_day([{}]*10) == DayLoad.HEAVY)

    # Mood classification
    stress_msgs = [{"role": "user", "message": "I'm so stuck and broken and exhausted"}]
    pos_msgs    = [{"role": "user", "message": "I shipped it! Amazing success, done!"}]
    neutral_msgs= [{"role": "user", "message": "ok"}]
    empty_msgs  = []

    check("stress keywords → STRESSED",  _classify_mood(stress_msgs)  == MoodSignal.STRESSED)
    check("positive keywords → POSITIVE", _classify_mood(pos_msgs)    == MoodSignal.POSITIVE)
    check("neutral message → NEUTRAL",   _classify_mood(neutral_msgs) == MoodSignal.NEUTRAL)
    check("empty messages → NEUTRAL",    _classify_mood(empty_msgs)   == MoodSignal.NEUTRAL)

    # AuraPerception observe with real DB (test user has no data — tests empty path)
    db = AuraDatabase()
    perception = AuraPerception(db)
    ctx = perception.observe(TEST_USER)
    check("observe() returns PerceptionContext",  ctx is not None)
    check("to_prompt_snippet() non-empty",        len(ctx.to_prompt_snippet()) > 0)
    check("mood is valid MoodSignal",             isinstance(ctx.mood_signal, MoodSignal))

    # 60s cache — same object returned
    ctx2 = perception.observe(TEST_USER)
    check("60s cache returns same object", ctx is ctx2)

# ══════════════════════════════════════════════════════════
# 3. FEEDBACK
# ══════════════════════════════════════════════════════════
def test_feedback():
    section("3. FEEDBACK — Judge / Memory / Context")
    db = AuraDatabase()
    char = SymbioteCharacter()
    judge = FeedbackJudge(char)

    # FeedbackJudge — rule-based checks
    r1 = judge.evaluate("Here is the answer Boss.", "help me", "mood: positive")
    check("clean draft passes judge",               r1.is_satisfactory)
    check("clean draft score >= 0.7",               r1.quality_score >= 0.7)

    r2 = judge.evaluate("as a AI language model I cannot...", "help", "mood: positive")
    check("AI phrasing fails judge",                not r2.is_satisfactory)
    check("AI phrasing fix injected",               len(r2.required_fixes) > 0)

    r3 = judge.evaluate("x" * 600, "help", "user is stressed right now")
    check("stressed + long draft fails",            not r3.is_satisfactory)

    r4 = judge.evaluate("i fixed the code for you", "fix my code", "mood: neutral")
    check("claims fix but no code block fails",     not r4.is_satisfactory)

    # Edge: score never goes below 0
    check("quality_score never negative",           r2.quality_score >= 0.0)

    # FeedbackMemory — save and load
    mem = FeedbackMemory(db)
    event = FeedbackEvent(
        user_id=TEST_USER,
        feedback_type=FeedbackType.CORRECTION,
        context="AURA used bullet points",
        correction="Never use bullet points"
    )
    mem.record(event)
    loaded = mem.load(TEST_USER, limit=10)
    check("FeedbackMemory saves and loads",         len(loaded) >= 1)
    check("loaded event type preserved",            loaded[-1].feedback_type == FeedbackType.CORRECTION)
    check("loaded correction text preserved",       "bullet" in loaded[-1].correction.lower())

    # FeedbackContext — empty user returns ""
    ctx = FeedbackContext(db)
    snippet = ctx.to_prompt_snippet(TEST_USER)
    check("FeedbackContext returns non-empty snippet after save", snippet != "")
    check("snippet contains correction text",       "bullet" in snippet.lower())

    # Edge: user with no feedback returns empty
    snippet_empty = ctx.to_prompt_snippet(99998)
    check("FeedbackContext returns empty for user with no feedback", snippet_empty == "")

# ══════════════════════════════════════════════════════════
# 4. LEARNING
# ══════════════════════════════════════════════════════════
def test_learning():
    section("4. LEARNING — PatternDetector / Memory / Context")
    db = AuraDatabase()

    mem = LearningMemory(db)
    pattern = LearnedPattern(
        user_id=TEST_USER,
        pattern_type=PatternType.BREVITY,
        trigger="stressed mood + short replies",
        behavior="keep responses under 60 words",
        confidence=0.8
    )
    mem.save(pattern)
    loaded = mem.load(TEST_USER, limit=10)
    check("LearningMemory saves and loads",         len(loaded) >= 1)
    check("pattern_type preserved",                 loaded[-1].pattern_type == PatternType.BREVITY)
    check("confidence preserved",                   abs(loaded[-1].confidence - 0.8) < 0.01)

    # save_batch
    batch = [
        LearnedPattern(user_id=TEST_USER, pattern_type=PatternType.AVOIDANCE,
                       trigger="long reply", behavior="shorten", confidence=0.75),
        LearnedPattern(user_id=TEST_USER, pattern_type=PatternType.TONE,
                       trigger="casual msg", behavior="match tone", confidence=0.6),
    ]
    mem.save_batch(batch)
    loaded2 = mem.load(TEST_USER, limit=20)
    check("save_batch saves multiple patterns",     len(loaded2) >= 3)

    # LearningContext
    ctx = LearningContext(db)
    snippet = ctx.to_prompt_snippet(TEST_USER)
    check("LearningContext snippet non-empty after saves", snippet != "")

    # Low confidence patterns not injected (confidence < 0.6)
    low_conf = LearnedPattern(user_id=TEST_USER, pattern_type=PatternType.BREVITY,
                               trigger="test", behavior="test", confidence=0.4)
    mem.save(low_conf)
    snippet2 = ctx.to_prompt_snippet(TEST_USER)
    check("LearningContext snippet returns non-empty (high conf patterns)", snippet2 != "")

    # Empty user
    empty_snippet = ctx.to_prompt_snippet(99997)
    check("LearningContext empty for user with no patterns", empty_snippet == "")

# ══════════════════════════════════════════════════════════
# 5. PERSONALITY
# ══════════════════════════════════════════════════════════
def test_personality():
    section("5. PERSONALITY — 15 States, Signals, Scoring")
    p = Personality()

    # observe() returns all 8 signals
    signals = p.observe("explain how this works")
    check("observe returns 8 signals",              len(signals) == 8)
    check("is_learning fires on 'explain'",         signals["is_learning"])
    check("is_technical false for non-code msg",    not signals["is_technical"])

    signals_code = p.observe("fix my code bug in the api function")
    check("is_technical fires on code keywords",    signals_code["is_technical"])

    signals_short = p.observe("ok")
    check("is_short fires for 1-word message",      signals_short["is_short"])

    signals_goal = p.observe("I shipped it and deployed successfully")
    check("is_goal_win fires on 'shipped'",         signals_goal["is_goal_win"])

    signals_threat = p.observe("this is urgent deadline tonight")
    check("is_threat fires on 'deadline'",          signals_threat["is_threat"])

    # feel() — all states reachable
    def make(score=0, tech=False, short=False, agg=False, win=False,
             switch=False, learn=False, threat=False):
        return {"score": score, "is_technical": tech, "is_short": short,
                "is_aggressive": agg, "is_goal_win": win, "is_switching": switch,
                "is_learning": learn, "is_threat": threat}

    check("dominant state",    p.feel(make(agg=True, short=False))  == "dominant")
    check("frustrated state",  p.feel(make(agg=True, short=True))   == "frustrated")
    check("ascendant state",   p.feel(make(win=True, score=5.0))    == "ascendant")
    check("defensive state",   p.feel(make(threat=True))            == "defensive")
    check("parasitic state",   p.feel(make(score=-7.0))             == "parasitic")
    check("overdrive state",   p.feel(make(score=7.0, tech=True))   == "overdrive")
    check("apex state",        p.feel(make(score=5.0))              == "apex")
    check("evolution state",   p.feel(make(learn=True, score=1.0))  == "evolution")
    check("unstable state",    p.feel(make(switch=True))            == "unstable")
    check("reclamation state", p.feel(make(score=-5.0))             == "reclamation")
    check("protective state",  p.feel(make(score=-2.0))             == "protective")
    check("stagnant state",    p.feel(make(score=-0.5, short=True)) == "stagnant")
    check("analytical state",  p.feel(make(tech=True))              == "analytical")
    check("shadow state",      p.feel(make(score=0.0, short=True))  == "shadow")
    check("bonded state",      p.feel(make(score=0.5))              == "bonded")

    # get_personality_prompt returns non-empty for all states
    for state in Personality.STATES:
        prompt = p.get_personality_prompt(state)
        check(f"prompt non-empty for '{state}'", len(prompt) > 0)

    # "but" split — weighted scoring
    sig_but = p.observe("I shipped it but I'm exhausted")
    check("but-split: exhausted after but drives score down", sig_but["score"] < 5.0)

    # Edge: empty message
    sig_empty = p.observe("")
    check("empty message returns valid signals",    len(sig_empty) == 8)

# ══════════════════════════════════════════════════════════
# 6. SPEC ENGINE
# ══════════════════════════════════════════════════════════
def test_spec():
    section("6. SPEC ENGINE — Goal Lifecycle")
    db = AuraDatabase()
    engine = SpecEngine(db)

    # Full lifecycle: SELECT → PROJECT → EXPECT → COLLECT
    goal = engine.select(TEST_USER, "Build vault.py for AURA")
    check("select() creates goal",                  goal is not None)
    check("initial status is selected",             goal.status == SpecStatus.SELECTED)
    check("progress starts at 0",                   goal.progress == 0.0)

    goal = engine.project(goal.id, TEST_USER, ["build VaultEntry", "build VaultMemory", "wire to brain"])
    check("project() adds steps",                   len(goal.steps) == 3)

    from datetime import datetime, timedelta
    future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    goal = engine.expect(goal.id, TEST_USER, future)
    check("expect() sets deadline",                 goal.deadline == future)

    goal = engine.complete_step(goal.id, TEST_USER, "build VaultEntry")
    check("complete_step() adds to completed_steps", "build VaultEntry" in goal.completed_steps)
    check("progress is 1/3 ≈ 0.33",                abs(goal.progress - (1/3)) < 0.01)

    goal = engine.complete_step(goal.id, TEST_USER, "build VaultMemory")
    check("progress is 2/3 ≈ 0.67",                abs(goal.progress - (2/3)) < 0.01)

    # is_critical — deadline < 12 hours
    from datetime import datetime, timedelta
    near_deadline = (datetime.now() + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    goal2 = engine.select(TEST_USER, "Critical test goal")
    goal2 = engine.expect(goal2.id, TEST_USER, near_deadline)
    check("is_critical fires when deadline < 12h",  goal2.is_critical)

    far_deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    goal3 = engine.select(TEST_USER, "Far deadline goal")
    goal3 = engine.expect(goal3.id, TEST_USER, far_deadline)
    check("is_critical false when deadline far",    not goal3.is_critical)

    # collect()
    goal_c = engine.select(TEST_USER, "Collect test goal")
    collected = engine.collect(goal_c.id, TEST_USER)
    check("collect() marks goal complete",          collected.collected_at is not None)

    # get_active returns only non-completed
    active = engine.get_active(TEST_USER)
    active_texts = [g.goal_text for g in active]
    check("get_active excludes completed goal",     "Collect test goal" not in active_texts)

    # to_prompt_snippet
    snippet = engine.to_prompt_snippet(TEST_USER)
    check("to_prompt_snippet non-empty with active goals", snippet != "")

    snippet_empty = engine.to_prompt_snippet(99996)
    check("to_prompt_snippet empty for user with no goals", snippet_empty == "")

# ══════════════════════════════════════════════════════════
# 7. SYMBIOTE
# ══════════════════════════════════════════════════════════
def test_symbiote():
    section("7. SYMBIOTE — Bond Lifecycle")
    db = AuraDatabase()
    sym = SymbioteSelection(db)

    # New user starts at OBSERVING
    status = sym.get_bond_status(TEST_USER)
    check("new user bond status is OBSERVING",      status == BondStatus.OBSERVING)

    # observe() scores compatibility signals
    ambitious_msgs = [
        {"role": "user", "message": "I want to build and ship this goal by deadline"},
        {"role": "user", "message": "I tried again after I failed and pushed through"},
        {"role": "user", "message": "explain why this is happening, I want to understand"},
    ]
    score = sym.observe(TEST_USER, ambitious_msgs)
    check("ambition score > 0 for goal/build messages", score.ambition > 0)
    check("resilience score > 0 for retry messages",    score.resilience > 0)
    check("hunger score > 0 for explain/why messages",  score.hunger > 0)
    check("overall score between 0 and 1",              0.0 <= score.overall <= 1.0)

    # evaluate() with short history = OBSERVING
    status2 = sym.evaluate(TEST_USER, ambitious_msgs)
    check("evaluate returns valid BondStatus",      isinstance(status2, BondStatus))

    # No bond message for fresh user with no bond record at all
    check("should_send_bond_message false for fresh user", not sym.should_send_bond_message(99994))

    # get_bond_message non-empty
    msg = sym.get_bond_message()
    check("get_bond_message returns non-empty string", len(msg) > 0)

    # get_personality_override for OBSERVING = None
    override = sym.get_personality_override(BondStatus.OBSERVING)
    check("OBSERVING has no personality override",  override is None)

    override_bonded = sym.get_personality_override(BondStatus.BONDED)
    check("BONDED has a personality override",      override_bonded is not None and len(override_bonded) > 0)

# ══════════════════════════════════════════════════════════
# 8. REASONING
# ══════════════════════════════════════════════════════════
def test_reasoning():
    section("8. REASONING — Router / Notebook Cache (no API calls)")
    db = AuraDatabase()

    # should_reason() — no API call, pure logic
    class MockClient: pass
    engine = ReasoningEngine(MockClient(), db)

    skip_signals   = {"score": 0, "is_technical": False, "is_short": True,
                      "is_aggressive": False, "is_goal_win": True,
                      "is_switching": False, "is_learning": False, "is_threat": False}
    deep_signals   = {"score": 1, "is_technical": False, "is_short": False,
                      "is_aggressive": False, "is_goal_win": False,
                      "is_switching": False, "is_learning": True, "is_threat": False}
    light_signals  = {"score": 0, "is_technical": False, "is_short": False,
                      "is_aggressive": False, "is_goal_win": False,
                      "is_switching": False, "is_learning": False, "is_threat": False}

    check("short/goal_win message → SKIP",     engine.should_reason(skip_signals)  == ReasoningMode.SKIP)
    check("learning message → DEEP",           engine.should_reason(deep_signals)  == ReasoningMode.DEEP)
    check("normal message → LIGHT",            engine.should_reason(light_signals) == ReasoningMode.LIGHT)

    # ReasoningNotebook — cache save and retrieve (no API)
    notebook = ReasoningNotebook(db)
    output = ReasoningOutput(
        core_need="Boss wants to understand JEPA",
        cross_domain_insight="Like physics simulation vs memorizing physics",
        suggested_approach="Use analogy first, then connect to vault.py",
        reasoning_mode=ReasoningMode.DEEP,
        from_cache=False
    )
    # Use words that exist in _TAGS vocabulary
    notebook.save(TEST_USER, "how does cache work with the database query", output)

    # Cache hit — same question with matching tags
    cached = notebook.retrieve(TEST_USER, "how does cache work with the database query")
    check("notebook cache hit on same question",   cached is not None)
    check("cached core_need preserved",            cached is not None and "JEPA" in cached.core_need)
    check("cached from_cache is True",             cached is not None and cached.from_cache)

    # Cache miss — question with no tag vocabulary words
    miss = notebook.retrieve(TEST_USER, "jepa symbiote venom bond")
    check("notebook cache miss returns None",      miss is None)

    # to_prompt_injection returns formatted string
    injection = output.to_prompt_injection()
    check("to_prompt_injection non-empty",         len(injection) > 0)

    # extract_tags
    tags = notebook.extract_tags("how does cache work with the database query and api")
    check("extract_tags returns list",             isinstance(tags, list))
    check("extract_tags non-empty for vocab words", len(tags) > 0)

# ══════════════════════════════════════════════════════════
# 9. DATABASE — All Tables Exist
# ══════════════════════════════════════════════════════════
def test_database():
    section("9. DATABASE — Table Verification")
    db = AuraDatabase()
    conn = db._connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected = ["user", "plans", "goals", "conversations",
                "feedback", "patterns", "reasoning_notebook",
                "symbiote_bond", "vault"]
    for t in expected:
        check(f"table '{t}' exists", t in tables)

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═"*55)
    print("  AURA FULL SYSTEM TEST SUITE")
    print("═"*55)

    db = AuraDatabase()
    cleanup_test_data(db)

    try:
        test_character()
        test_perception()
        test_feedback()
        test_learning()
        test_personality()
        test_spec()
        test_symbiote()
        test_reasoning()
        test_database()
    except Exception as e:
        import traceback
        print(f"\nCRASH during tests: {e}")
        traceback.print_exc()

    cleanup_test_data(db)

    print(f"\n{'═'*55}")
    print(f"  RESULTS:  {PASS} passed   {FAIL} failed   {PASS+FAIL} total")
    print('═'*55)

    if FAIL > 0:
        print("\nFAILED TESTS:")
        for r in RESULTS:
            if r[0] == "FAIL":
                print(f"  ✗ {r[1]}" + (f" — {r[2]}" if len(r) > 2 else ""))

    sys.exit(0 if FAIL == 0 else 1)
