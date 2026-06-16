"""
Vault smoke test — proves the full pipeline works end to end.
Run from AURA root: python -m tests.test_vault
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AuraDatabase
from core.vault import VaultEntry, VaultMemory, VaultSearch, VaultContext

def separator(label):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print('='*50)

def test_table_exists():
    separator("TEST 1 — Does vault table exist?")
    db = AuraDatabase()
    conn = db._connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vault'")
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "FAIL — vault table not found in DB"
    print("PASS — vault table exists")

def test_save_and_load():
    separator("TEST 2 — Save and load a VaultEntry")
    db = AuraDatabase()
    memory = VaultMemory(db)

    entry = VaultEntry(
        user_id=1,
        title="JEPA — Joint Embedding Predictive Architecture",
        body="JEPA predicts representations of the world, not just next tokens. Enables consequence modeling before acting.",
        tags=["jepa", "ai", "world-model", "aura-vision"],
        links=["reasoning.py", "vault.py"],
        source="test"
    )

    memory.record(entry)
    print(f"Saved: {entry.title}")

    rows = memory.load(user_id=1, limit=10)
    assert len(rows) > 0, "FAIL — no entries loaded after save"

    found = next((e for e in rows if e.title == entry.title), None)
    assert found is not None, "FAIL — saved entry not found in load"
    assert found.tags == entry.tags, "FAIL — tags corrupted at DB boundary"
    assert found.links == entry.links, "FAIL — links corrupted at DB boundary"
    print(f"PASS — loaded {len(rows)} entries. Tags and links intact.")

def test_upsert():
    separator("TEST 3 — Upsert (no duplicates)")
    db = AuraDatabase()
    memory = VaultMemory(db)

    entry = VaultEntry(
        user_id=1,
        title="JEPA — Joint Embedding Predictive Architecture",
        body="UPDATED: JEPA builds world models that understand causality, not just patterns.",
        tags=["jepa", "ai", "causality"],
        links=["reasoning.py"],
        source="test"
    )

    memory.record(entry)

    rows = memory.load(user_id=1, limit=50)
    jepa_entries = [e for e in rows if e.title == entry.title]
    assert len(jepa_entries) == 1, f"FAIL — duplicate found. Count: {len(jepa_entries)}"
    assert jepa_entries[0].body == entry.body, "FAIL — body not updated"
    print(f"PASS — upsert works. One entry, body updated.")

def test_search():
    separator("TEST 4 — VaultSearch scoring and ranking")
    db = AuraDatabase()
    memory = VaultMemory(db)

    memory.record(VaultEntry(
        user_id=1,
        title="Python Pydantic Models",
        body="Pydantic validates data at construction time using BaseModel and Field.",
        tags=["python", "pydantic", "validation"],
        source="test"
    ))
    memory.record(VaultEntry(
        user_id=1,
        title="Response Router Architecture",
        body="Router classifies messages into data route or Claude route. Reduces latency.",
        tags=["router", "latency", "architecture"],
        source="test"
    ))

    entries = memory.load(user_id=1, limit=50)
    results = VaultSearch.search(entries, query="how does JEPA work in aura vision", top_k=3)

    assert len(results) > 0, "FAIL — search returned nothing"
    assert results[0].title == "JEPA — Joint Embedding Predictive Architecture", \
        f"FAIL — wrong top result: {results[0].title}"
    print(f"PASS — top result: '{results[0].title}'")
    for i, r in enumerate(results):
        print(f"  #{i+1}: {r.title}")

def test_prompt_injection():
    separator("TEST 5 — VaultContext prompt injection")
    db = AuraDatabase()
    ctx = VaultContext(db)

    snippet = ctx.to_prompt_snippet(user_id=1, query="tell me about JEPA and aura vision")
    assert snippet != "", "FAIL — snippet is empty"
    assert "JEPA" in snippet, "FAIL — JEPA not in snippet"
    print("PASS — prompt snippet generated")
    print("\n--- SNIPPET PREVIEW ---")
    print(snippet[:300])
    print("...")

if __name__ == "__main__":
    print("\nAURA VAULT — SMOKE TEST")
    try:
        test_table_exists()
        test_save_and_load()
        test_upsert()
        test_search()
        test_prompt_injection()
        print("\n" + "="*50)
        print("  ALL TESTS PASSED — vault.py is production ready")
        print("="*50 + "\n")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nCRASH: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
