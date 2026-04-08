# AURA - Agent Rules & Tactical Style Guide

## 🌌 UI/UX: The Cosmic Protocol
- **The Visuals:** Dynamic, swirling spiral galaxy complex with a starfield background. Use `framer-motion` for smooth, low-CPU orbital animations.
- **The Typography:** **VT323** Mono font is mandatory. 
- **The Glow:** Color `#FFB000` (Amber). Apply `text-shadow: 0 0 8px rgba(255, 176, 0, 0.8)`.
- **The Feel:** Overlay a SVG scanline pattern with a 2% opacity "flicker" animation to mimic a 1980s high-end terminal.
- **Windows:** Use Glassmorphism (blur: 10px, opacity: 0.7) for all chat containers.

## 💻 Coding Standards & Safety
- **Python (Backend):** - Strict **Type Hinting** for all function signatures.
  - Use **Pydantic v2** models for all FastAPI request/response schemas.
  - Logic must be modular (separation of `services`, `models`, and `routers`).
- **React (Frontend):** - Tailwind CSS for layout. 
  - Components must be functional with Hooks (`useEffect`, `useMemo`).
- **Security:** - `load_dotenv()` is mandatory. 
  - Never commit `.env`. Add `.env` to `.gitignore` automatically if missing.

## 🧠 The "Tribe" Architecture (Brain Mimicry)
- **The Executive:** `brain.py` acts as the Frontal Lobe, delegating tasks to sub-agents.
- **The Tribe:** Specialized modules (e.g., `CareerAgent`, `AcademicAgent`, `PhotoAgent`).
- **Agent Handshake:** Sub-agents must return a structured JSON response to the Executive including: `{"status": "complete", "confidence": 0.9, "data": {}}`.
- **Memory Persistence:** - Every agent interaction must log to the `agent_logs` table in **Postgres**.
  - Agents must query the `user_context` table before responding to maintain continuity.

## 🛡️ Operational Guardrails
- **Read-Only Core:** AI agents can READ `brain.py` for context but are BLOCKED from writing to it without a "Manual Override" from Chandu.
- **Cost Control:** Always check token counts before sending large context blocks to Claude.

## 🏠 Path B: The Sanctum Protocol (IoT)
- **Communication:** Use **MQTT** or **WebSockets** for real-time hardware triggers.
- **State Management:** The "Room State" (Lights, Power, Temperature) must be mirrored in the PostgreSQL `room_telemetry` table.
- **Proactive Environmental Logic:** - **Deep Work Mode:** When Chandu opens Cursor/VS Code, dim lights to 20% Amber and enable "Do Not Disturb."
- **Academic Mode:** When a Master's deadline is < 12 hours, pulse the desk LEDs in a slow amber "breathing" pattern.