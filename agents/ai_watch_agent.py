# agents/ai_watch_agent.py - AI Watch Agent
# purpose:
#   monitors top AI companies for new releases.
#   filters what's relevant to SYMBITE.
#   returns ranked updates so you know what to adapt.

import httpx
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from datetime import datetime
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


class AIWatchAgent:

    AI_FEEDS = [
        {"company": "Anthropic",    "url": "https://www.anthropic.com/rss.xml"},
        {"company": "OpenAI",       "url": "https://openai.com/blog/rss"},
        {"company": "Google",       "url": "https://blog.google/technology/ai/rss"},
        {"company": "Meta AI",      "url": "https://engineering.fb.com/category/ai-research/feed"},
        {"company": "Hugging Face", "url": "https://huggingface.co/blog/feed.xml"},
    ]

    SYMBITE_KEYWORDS = [
        "emotion", "memory", "voice", "agent", "reasoning",
        "multimodal", "personality", "adaptive", "real-time",
        "context", "local", "efficient", "tool", "function calling",
        "speech", "audio", "vision", "behavior",
        # JEPA / world model research — Yann LeCun / Meta
        "jepa", "world model", "joint embedding", "predictive architecture",
        "representation learning", "self-supervised", "causal",
        # SPEC — goal setting, behavioral adaptation, manifestation
        "goal", "habit", "behavior tracking", "proactive", "motivation",
        "long-term", "reinforcement", "reward", "planning", "intention",
    ]

    @staticmethod
    def _format_handshake(status: str, confidence: float, data: Any) -> Dict[str, Any]:
        return {
            "status": status,
            "confidence": confidence,
            "data": data
        }

    @staticmethod
    def _is_relevant(title: str, summary: str) -> bool:
        text = (title + " " + summary).lower()
        return any(keyword in text for keyword in AIWatchAgent.SYMBITE_KEYWORDS)

    @staticmethod
    def _score_relevance(title: str, summary: str) -> int:
        text = (title + " " + summary).lower()
        return sum(1 for keyword in AIWatchAgent.SYMBITE_KEYWORDS if keyword in text)

    @classmethod
    def _fetch_feed(cls, company: str, url: str) -> List[Dict]:
        results = []
        try:
            response = httpx.get(
                url,
                timeout=8,
                headers={"User-Agent": "SYMBITE/1.0"},
                follow_redirects=True,
            )
            root = ET.fromstring(response.content)
            items = root.findall(".//item")[:5]

            for item in items:
                title   = item.findtext("title", "").strip()
                summary = item.findtext("description", "").strip()
                link    = item.findtext("link", "").strip()

                if not title:
                    continue

                if cls._is_relevant(title, summary):
                    results.append({
                        "company": company,
                        "title":   title,
                        "link":    link,
                        "score":   cls._score_relevance(title, summary),
                    })

        except Exception:
            pass

        return results

    @classmethod
    def scan(cls) -> Dict[str, Any]:
        all_updates = []

        for feed in cls.AI_FEEDS:
            updates = cls._fetch_feed(feed["company"], feed["url"])
            all_updates.extend(updates)

        if not all_updates:
            return cls._format_handshake("error", 0.0, "No relevant AI updates found.")

        # sort by relevance score — highest first
        all_updates.sort(key=lambda x: x["score"], reverse=True)

        return cls._format_handshake("complete", 0.95, all_updates)

    @classmethod
    def notify(cls, updates: List[Dict]) -> bool:
        if not updates:
            return False

        sender   = os.getenv("SYMBITE_EMAIL")
        password = os.getenv("SYMBITE_EMAIL_PASSWORD")
        receiver = os.getenv("YOUR_EMAIL")

        # build the email body
        body = "SYMBITE AI WATCH REPORT\n"
        body += "=" * 40 + "\n\n"

        for update in updates:
            body += f"[{update['company']}]\n"
            body += f"  {update['title']}\n"
            body += f"  Relevance score: {update['score']}\n"
            body += f"  {update['link']}\n\n"

        body += "=" * 40 + "\n"
        body += "Review these and decide what to build next, Boss."

        # build the email
        msg = MIMEMultipart()
        msg["From"]    = sender
        msg["To"]      = receiver
        msg["Subject"] = f"SYMBITE — {len(updates)} AI updates worth your attention"
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False

    @classmethod
    def run(cls) -> Dict[str, Any]:
        result = cls.scan()

        if result["status"] == "complete":
            sent = cls.notify(result["data"])
            result["email_sent"] = sent

        return result
