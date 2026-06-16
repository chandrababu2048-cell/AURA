
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("AURA.vault")

class VaultEntry(BaseModel):
    id : Optional[int] =None
    user_id : int
    title : str
    body : str
    tags : List[str] = Field(default_factory=list)
    links : List[str] = Field(default_factory=list)
    source : str = "conversation"
    created_at : str = Field(default_factory = lambda :datetime.now().isoformat())

class VaultMemory():
    def __init__(self, db):
        self._db = db

    def record(self, entry: VaultEntry)-> None:
        existing = self._db.get_vault_entry_by_title(entry.user_id, entry.title)
        if existing:
            self._db.update_vault_entry(existing["id"], entry.model_dump())
            self._db.save_tags(existing["id"], entry.tags)
            logger.info("Vault entry updated| title =%s" , entry.title)
        else:
            new_id = self._db.save_vault_entry(entry.model_dump())
            self._db.save_tags(new_id, entry.tags)

            logger.info("Vault entry saved| title =%s" , entry.title)

    def load(self, user_id: int,  limit: int = 20) -> List[VaultEntry]:
        rows = self._db.load_vault_entries(user_id, limit=limit)
        return[VaultEntry(**row) for row in rows]

class VaultSearch:

    @staticmethod
    def score(entry:VaultEntry , query: str) -> float:
        query_lower = query.lower()
        query_words = set(query_lower.split())

        score = 0.0

        if any(tag in query_words for tag in entry.tags):
            score += 2.0

        if entry.title.lower() in query_words:
            score += 3.0
        body_words = set(entry.body.lower().split())

        overlap = query_words & body_words
        score += len(overlap)* 0.5

        return score

    @staticmethod
    def search(entries: List[VaultEntry] , query : str ,top_k : int = 3) -> List[VaultEntry]:

        scored = [
            (entry, VaultSearch.score(entry, query))
            for entry in entries
        ]

        scored = [ (e, s ) for e,s in scored if s > 0.0]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [ entry for entry , _ in scored[:top_k]]

class VaultContext:
    def __init__(self, db):
        self._memory = VaultMemory(db)

    def to_prompt_snippet(self, user_id :int, query : str) -> str:
        events = self._memory.load(user_id, limit=50)
        if not events:
            return""
        relevant = VaultSearch.search(events, query , top_k=3)

        if not relevant:
            return""
        lines = ["### YOUR SECOND BRAIN - RELEVANT KNOWLEDGE ###"]
        for entry in relevant:
            lines.append(f"**{entry.title}**")
            lines.append(entry.body)
            if entry.tags:
                lines.append(f"Tags: {', '.join(entry.tags)}")
            lines.append("")
        return "\n".join(lines)













