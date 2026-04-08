import httpx
import xml.etree.ElementTree as ET
from typing import Dict, Any

class SystemAgent:
    """
    Tribe Specialist: Handles 'World Access' tasks like Weather and News.
    Always returns the standard Agent Handshake format.
    """
    
    NEWS_FEEDS = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",   # BBC World
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",  # NYT World
    ]

    @staticmethod
    def _format_handshake(status: str, confidence: float, data: Any) -> Dict[str, Any]:
        """Ensures all responses conform to the Agent Handshake requirement."""
        return {
            "status": status,
            "confidence": confidence,
            "data": data
        }

    @classmethod
    def get_news(cls) -> Dict[str, Any]:
        """Fetches live global news via RSS."""
        headlines = []
        try:
            for url in cls.NEWS_FEEDS:
                response = httpx.get(
                    url,
                    timeout=5,
                    headers={"User-Agent": "AURA/1.0"},
                    follow_redirects=True,
                )
                root = ET.fromstring(response.content)
                items = root.findall(".//item")[:3]
                
                for item in items:
                    title = item.findtext("title")
                    if title:
                        headlines.append(title.strip())

            if not headlines:
                return cls._format_handshake("error", 0.0, "News feeds are unresponsive.")
            
            summary = "Latest headlines:\n" + "\n".join(f"- {h}" for h in headlines)
            return cls._format_handshake("complete", 0.95, summary)

        except Exception as e:
            return cls._format_handshake("error", 0.0, str(e))

    @classmethod
    def get_weather(cls) -> Dict[str, Any]:
        """Fetches local weather from the core weather module."""
        try:
            from weather import get_weather
            data = get_weather()
            if data and data.get("success"):
                return cls._format_handshake("complete", 0.95, data["summary"])
            else:
                return cls._format_handshake("error", 0.5, "Weather data unavailable.")
        except Exception as e:
            return cls._format_handshake("error", 0.0, str(e))
