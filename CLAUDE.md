# AURA - Project Context & Manifest
AURA (Automated Unified Reasoning Assistant) is a proactive, Jarvis-style companion. It is designed to bridge the gap between a standard LLM and a functional digital partner with persistent memory and a "Tribe" architecture.

## 🏗️ System Architecture
- **The Brain (CORE):** Python logic in `backend/brain.py`. 
  - **🚨 CRITICAL:** AI Agents are FORBIDDEN from modifying `brain.py` or `logic/` without explicit permission from Chandu.
- **The Face (UI):** React (Vite) + Tailwind CSS. 
  - **Aesthetic:** "Cosmic Terminal" (Amber Glow VT323 + Parallax Galaxy).
- **The Bridge (API):** FastAPI handling requests between UI and Brain.
- **The Vault (DB):** PostgreSQL (Supabase/Neon) for production-grade persistence.

## 🎯 Current Roadmap & Goals
### Phase 1: Infrastructure (Active)
- [ ] **DB Migration:** Port SQLite logic to PostgreSQL/Supabase.
- [ ] **Cosmic UI:** Build the React frontend with VT323 font and galaxy parallax.
- [ ] **FastAPI Setup:** Create secure endpoints for the Brain-to-UI communication.

### Phase 2: Professional Utility
- **Career/Academic Agents:** Automation for .NET job apps and Master's deadlines.
- **Creative Suite:** AI background removal for photography/social media.

## 🛠️ Dev Commands
- **Install Dependencies:** - Frontend: `cd frontend && npm install`
  - Backend: `pip install -r requirements.txt`
- **Execution:**
  - Start Backend: `uvicorn backend.main:app --reload`
  - Start Frontend: `npm run dev --prefix frontend`

## 📜 Rules of Engagement for AI Agents
1. **Design Protocol:** All UI elements must use Hex `#FFB000` for text and a 2% CRT flicker effect.
2. **Database Protocol:** Never use raw SQL strings; use SQLAlchemy or the Repository Pattern in `database.py`.
3. **Communication:** Be proactive. If a change in the UI might break the Brain, alert Chandu immediately.

