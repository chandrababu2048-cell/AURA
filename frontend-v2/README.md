# AURA — frontend-v2

Production-ready React + Vite frontend for AURA. Glassmorphism, cyan/blue accent,
Zustand for state, Framer Motion for animation, axios for API, Tailwind for styling.
Fully wired to the existing FastAPI backend (`api/main.py`).

## Stack

- **React 18** + **Vite 5**
- **Tailwind CSS 3**
- **Zustand 5** — global state
- **Framer Motion 11** — animation
- **axios** — HTTP client
- **lucide-react** — icons

## Folder structure

```
frontend-v2/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env.example
├── .gitignore
├── README.md
└── src/
    ├── main.jsx                 # Vite entry
    ├── App.jsx                  # shell + roaming orb layer
    ├── styles/
    │   └── globals.css          # Tailwind + glass tokens
    ├── pages/
    │   └── Dashboard.jsx        # 3-panel desktop layout
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.jsx
    │   │   ├── LeftPanel.jsx
    │   │   └── CenterPanel.jsx
    │   ├── ui/
    │   │   ├── GlassCard.jsx
    │   │   ├── Button.jsx
    │   │   └── ProgressBar.jsx
    │   ├── aura/
    │   │   └── AuraOrb.jsx      # + <AuraOrbRoamingLayer/>
    │   ├── tasks/
    │   │   ├── TaskList.jsx
    │   │   └── TaskItem.jsx
    │   ├── chat/
    │   │   ├── ChatPanel.jsx
    │   │   ├── MessageBubble.jsx
    │   │   └── ChatInput.jsx
    │   └── dashboard/
    │       ├── WeeklyProgress.jsx
    │       ├── FocusScore.jsx
    │       ├── SkillLevel.jsx
    │       └── Recommendation.jsx
    ├── features/
    │   ├── chat/useChat.js
    │   └── tasks/useTasks.js
    ├── hooks/
    │   └── useAuraState.js
    ├── store/
    │   ├── useUserStore.js
    │   ├── useTaskStore.js
    │   ├── useChatStore.js
    │   └── useAuraStore.js
    └── services/
        ├── api.js               # axios instance + error normalizer
        ├── chatService.js       # /chat/think, /conversations
        ├── taskService.js       # /plans CRUD
        ├── goalService.js       # /goals CRUD
        └── memoryService.js     # /memory/*, /weather, /news
```

## Run

From the project root:

```bash
cd frontend-v2
cp .env.example .env.local       # adjust VITE_API_BASE_URL if needed
npm install
npm run dev                      # → http://localhost:5173
```

In another terminal, start the backend:

```bash
cd ..
.venv/bin/uvicorn api.main:app --reload --port 8000
```

The frontend expects the backend on `http://localhost:8000` by default.
Override via `VITE_API_BASE_URL` in `.env.local`.

## Endpoints consumed

All wired to `api/main.py`:

| Purpose               | Endpoint                                           |
| --------------------- | -------------------------------------------------- |
| Send chat             | `POST /chat/think`                                 |
| Chat history          | `GET /conversations?user_id&limit`                 |
| Clear session         | `DELETE /chat/session/{user_id}`                   |
| List plans            | `GET /plans?user_id&date?`                         |
| Add plan              | `POST /plans`                                      |
| Toggle plan           | `PATCH /plans/{id}/toggle`                         |
| Delete plan           | `DELETE /plans/{id}?user_id`                       |
| List goals            | `GET /goals?user_id`                               |
| Add goal              | `POST /goals`                                      |
| Complete / delete     | `PATCH /goals/{id}/complete`, `DELETE /goals/{id}` |
| Memory context/report | `GET /memory/context`, `/memory/report`            |
| Weather / news        | `GET /weather`, `/news`                            |

Components never hit axios directly — they go through Zustand stores,
which call the service modules in `src/services/`.

## Aura avatar — anchored vs roaming

The orb is positioning-agnostic:

- **Anchored mode (default)** — `<AuraOrb />` renders inline in the center panel.
- **Roaming mode** — call `useAuraStore().enterRoamingMode()`. The orb unanchors
  and `<AuraOrbRoamingLayer />` (mounted in `App.jsx`) renders it as a fixed,
  viewport-level overlay positioned by `useAuraStore().position`.

Example:

```js
import { useAuraStore } from "@/store/useAuraStore";

// Kick off roaming mode and move the orb to (x, y) in the viewport:
useAuraStore.getState().enterRoamingMode();
useAuraStore.getState().setPosition(640, 320);
```

The orb's visual state is independent of position — `state` can be
`idle | thinking | speaking | roaming` at any time, regardless of whether
it is anchored or not.

## State flow

- **useChatStore** — optimistic user push → `POST /chat/think` →
  append reply → triggers `useAuraStore.pulseSpeaking()`.
- **useTaskStore** — optimistic toggle/add/delete with rollback on error.
- **useUserStore** — current user + fallback to `VITE_DEFAULT_USER_ID=1`.
- **useAuraStore** — orb state machine + position + anchored flag.

## Design tokens

See `tailwind.config.js` (`aura.*` colors) and `src/styles/globals.css`:

- `glass`, `glass-strong`, `glass-grid` — layered glassmorphism surfaces.
- `aura-app-bg` — soft blurred cloudy gradient background.
- Accent color: `#2EA8FF` (cyan/blue), gradient pair with `#7DC8FF` → `#1A78D2`.

## Next steps

- Swap the legacy `frontend/` for `frontend-v2/` in `start.py` when you're ready.
- Wire real values into `WeeklyProgress`, `FocusScore`, `SkillLevel` by reading
  from `/memory/report` inside a new `useInsightsStore`.
- Hook the Voice circle button into Web Speech API or your backend STT.
- Add auth screens that call `/auth/login` → `useUserStore.setUser(result.user)`.
