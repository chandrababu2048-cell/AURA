import json
import logging
from anthropic import Anthropic
from core.vault import VaultEntry, VaultMemory

logger = logging.getLogger("AURA.vault_extractor")

_SKIP_PREFIXES = (
    "open ", "play ", "search ", "what time", "what's the time",
    "show me", "remind me", "set a timer", "ok ", "okay ",
    "can you play", "can you open", "can you search",
)

_SKIP_WORDS = {
    "thanks", "thank you", "got it", "understood", "cool",
    "nice", "awesome", "ok", "okay", "yes", "no", "bye",
    "fuck", "why", "what",
}


class ExtractionGate:

    @staticmethod
    def _should_extract(user_message: str, aura_response: str) -> bool:
        msg = user_message.strip().lower()

        if len(msg) < 30:
            return False

        if msg.split()[0] in _SKIP_WORDS:
            return False

        for prefix in _SKIP_PREFIXES:
            if msg.startswith(prefix):
                return False

        combined = len(user_message) + len(aura_response)
        if combined < 80:
            return False

        return True


class VaultExtractor:
    def __init__(self , client: Anthropic, db):
        self._client = client
        self._memory = VaultMemory(db)

    def extract_and_save(self, user_id: int, user_message: str, aura_response: str) -> None:
        if not ExtractionGate._should_extract(user_message, aura_response):
            return
        prompt = (
            "Extract the key knowledge from this conversation as JSON.\n"
            "Return ONLY valid JSON, NO explanation.\n"
            "Format:\n"
            '{"title": "short title", "body": "what was learned", "tags": ["tag1", "tag2", "tag3"]}\n\n'
            f"User: {user_message}\n"
            f"Aura: {aura_response}\n"
        )
        try:
            response = self._client.messages.create(
                model = "claude-haiku-4-5-20251001",
                max_tokens= 300,
                messages=[{"role":"user","content":prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").strip()
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            if not raw:
                return
            data = json.loads(raw)
            entry = VaultEntry(
                user_id=user_id,
                title=data.get("title", "Untitled"),
                body = data.get("body", ""),
                tags = data.get("tags", []),
                source = "conversation",

            )
            self._memory.record(entry)
            logger.info("Vault saved: %s" , entry.title)


        except Exception as e:
            logger.warning("VaultExtractor failed: %s" , e)
            





