# A.U.R.A — Personal AI Companion

> **Autonomous Utility & Response Assistant**
> Built by Chandu — AI Engineer in Progress

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://efjvpchjghfiglwtheawct.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-FFB000?style=for-the-badge&logo=python)](https://python.org)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude%20Haiku-8B5CF6?style=for-the-badge)](https://anthropic.com)

---

## What is AURA?

AURA is a retro-themed personal AI companion with a full CRT terminal aesthetic. It remembers your goals, tracks your daily plans, shows live weather, and lets you chat with an AI that actually knows who you are — because it reads your real data on every message.

---

## Features

| Feature | Details |
|---------|---------|
| AI Chat | Powered by Claude Haiku — 3 modes: Personal, Pro, Hybrid |
| Daily Plans | Add tasks, check them off, track progress |
| Long-term Goals | Set and track goals with deadlines |
| Live Weather | Real-time weather via OpenWeatherMap |
| System Stats | Live CPU, RAM, Disk monitoring via psutil |
| Weekly Report | AI-generated summary of your week |
| User Accounts | Secure login/register with bcrypt password hashing |
| CRT UI | Full retro terminal aesthetic with scanlines, glitch effects |

---

## Tech Stack

```
Frontend   → Streamlit (Python)
AI Engine  → Anthropic Claude Haiku
Database   → SQLite (local)
Auth       → bcrypt password hashing
Weather    → OpenWeatherMap API
Styling    → Custom CSS — VT323 font, CRT effects
```

---

## Project Structure

```
AURA/
├── streamlit_app.py   # Main UI — boot, auth, dashboard pages
├── brain.py           # Claude AI engine — prompt building, chat
├── database.py        # All SQLite reads/writes (DAO pattern)
├── memory.py          # Context builder — injects user data into AI
├── weather.py         # OpenWeatherMap API integration
├── helper.py          # Utility functions (greetings, etc.)
├── requirements.txt   # Python dependencies
└── aura_data/         # SQLite DB lives here (gitignored)
```

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/chandrababu2048-cell/AURA.git
cd AURA
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create your `.env` file**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENWEATHER_API_KEY=your-openweather-key
WEATHER_CITY=Your City
```

**4. Run the app**
```bash
streamlit run streamlit_app.py
```

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo
3. Set `streamlit_app.py` as the main file
4. Add secrets in **Settings → Secrets**:
```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
OPENWEATHER_API_KEY = "your-openweather-key"
WEATHER_CITY = "Your City"
```

---

## API Keys Needed

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) |

---

## Architecture Notes

- **Why Streamlit?** Rapid prototyping — full UI in pure Python
- **Why SQLite?** Zero setup for v1 — easy to swap to Postgres later
- **Why bcrypt?** Industry standard — passwords never stored in plain text
- **Why Claude Haiku?** Fast, cheap, great for conversational AI
- **Context injection** — every message to Claude includes the user's name, plans, goals, and weather so AURA genuinely feels like it knows you

---

## Roadmap

- [ ] Migrate to PostgreSQL (persistent storage on cloud)
- [ ] Morning briefing — daily AI summary on login
- [ ] Voice input/output
- [ ] Mobile responsive layout
- [ ] Proactive suggestions based on patterns

---

## Built by

**Chandu** — AI Engineer in Progress

> *"Building the AI companion I always wanted"*
