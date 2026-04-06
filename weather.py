# ============================================================
# weather.py — AURA Weather Module
# ============================================================
# PURPOSE:
#   Fetches real-time weather data from OpenWeatherMap API
#   and returns it in a clean, structured format.
#
# WHY A SEPARATE MODULE?
#   Single Responsibility Principle — weather logic lives here,
#   not scattered across brain.py or streamlit_app.py.
#   If you swap to a different weather API later, you only
#   change THIS file. Nothing else breaks.
#
# USED BY:
#   - streamlit_app.py  (sidebar weather panel)
#   - brain.py          (injects weather into AI context)
# ============================================================

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .ENV file.
# This is how we keep API keys out of source code.
load_dotenv()


def get_weather(city: str = None) -> dict:
    """
    Fetch current weather for a city from OpenWeatherMap.

    WHY return a dict instead of a string?
        A dict lets the caller pick what they need.
        brain.py wants a text summary for the AI prompt.
        streamlit_app.py wants individual values (temp, humidity)
        to render them separately in the UI.

    Args:
        city: City name. Falls back to WEATHER_CITY env var,
              then defaults to 'Boston' (your home city).

    Returns:
        dict with keys:
            success   (bool)   — True if API call worked
            city      (str)    — city name from API
            temp      (float)  — temperature in Celsius
            feels_like(float)  — feels-like temp in Celsius
            humidity  (int)    — humidity percentage
            condition (str)    — e.g. "Clear Sky"
            wind      (float)  — wind speed in m/s
            summary   (str)    — one-line text for AI prompt
            error     (str)    — error message if success=False
    """
    # Resolve city: argument → env var → hardcoded default (Boston)
    target_city = city or os.environ.get("WEATHER_CITY", "Boston")

    # API key lives in .ENV, never hardcoded in source
    api_key = os.environ.get("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "OPENWEATHER_API_KEY not set in .ENV",
            "summary": "Weather unavailable — API key missing.",
        }

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": target_city,
        "appid": api_key,
        "units": "metric",   # Celsius
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()   # raises on 4xx / 5xx HTTP errors
        data = response.json()

        temp       = round(data["main"]["temp"], 1)
        feels_like = round(data["main"]["feels_like"], 1)
        humidity   = data["main"]["humidity"]
        condition  = data["weather"][0]["description"].title()
        wind       = round(data["wind"]["speed"], 1)
        city_name  = data["name"]

        return {
            "success":    True,
            "city":       city_name,
            "temp":       temp,
            "feels_like": feels_like,
            "humidity":   humidity,
            "condition":  condition,
            "wind":       wind,
            # summary is injected into the AI system prompt
            "summary": (
                f"{temp}°C, {condition}, "
                f"Humidity {humidity}%, Wind {wind}m/s in {city_name}"
            ),
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Weather API timed out.",
            "summary": "Weather unavailable — request timed out.",
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "summary": "Weather unavailable — network error.",
        }
    except (KeyError, IndexError) as e:
        return {
            "success": False,
            "error": f"Unexpected API response: {e}",
            "summary": "Weather unavailable — API response error.",
        }


# ── Quick test ─────────────────────────────────────────────
# Run: python weather.py
# to verify your API key and city are working correctly.
if __name__ == "__main__":
    result = get_weather()
    if result["success"]:
        print(f"City      : {result['city']}")
        print(f"Temp      : {result['temp']}°C (feels {result['feels_like']}°C)")
        print(f"Condition : {result['condition']}")
        print(f"Humidity  : {result['humidity']}%")
        print(f"Wind      : {result['wind']} m/s")
        print(f"Summary   : {result['summary']}")
    else:
        print(f"Error: {result['error']}")
