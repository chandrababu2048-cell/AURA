# Symbite — Electron Desktop App

Symbite is now a full Mac desktop app. The orb escapes onto your actual
desktop when you minimize or close the main window.

---

## One-time setup

```bash
cd /Users/chandu/Desktop/AURA/frontend-v2
npm install
```

This installs Electron 33, electron-builder, concurrently, wait-on, and
cross-env on top of the existing React/Vite stack.

---

## Run in development

```bash
npm run electron:dev
```

What this does, in order:
1. Starts `vite dev` on `localhost:5173`
2. Waits until the dev server is ready (`wait-on`)
3. Launches Electron — it opens `http://localhost:5173` in the main window
4. DevTools opens detached (you can close it if you don't need it)

The backend API still needs to be running separately:

```bash
# In a separate terminal, from /Users/chandu/Desktop/AURA
uvicorn api.main:app --reload
```

---

## Build a distributable .dmg

```bash
npm run electron:build
```

1. Runs `vite build` with `ELECTRON_BUILD=true` (sets `base: "./"` so
   asset paths work under `file://` protocol)
2. Runs `electron-builder --mac` → produces a `.dmg` in `release/`

**Note:** You need an `assets/icon.icns` for the final packaged app.
For dev/testing this is optional — the app will launch without it.

---

## How it works

### Window architecture

```
Electron Main Process
├── mainWindow  (1400×900, frameless, vibrancy)
│     Loads: http://localhost:5173  (dev)  OR  file://dist/index.html  (prod)
│     Contains: React app — all 3 panels
│
└── roamingWindow  (120×120, transparent, always-on-top)
      Loads: electron/roaming-orb/index.html  (always from file://)
      Contains: Pure HTML/CSS/JS orb — no React, no bundler needed
```

### The orb lifecycle

```
App launch
  └─► mainWindow shows, roamingWindow hidden

User minimizes or hits close button
  └─► main.js intercepts the event (preventDefault)
  └─► mainWindow.hide()
  └─► roamingWindow.show()  ← the orb ESCAPES onto the desktop
  └─► IPC: sends "orb-mode" to mainWindow renderer
  └─► App.jsx receives it → calls enterRoamingMode()

User clicks the roaming orb
  └─► roaming-orb/index.html sends IPC "open-main-window"
  └─► main.js: roamingWindow.hide(), mainWindow.show() + focus()
  └─► IPC: sends "return-home" to mainWindow renderer
  └─► App.jsx receives it → calls exitRoamingMode()
```

### IPC bridge (preload.js)

```js
window.electronAPI = {
  onOrbMode(callback)         // main → renderer: window is hiding
  onReturnHome(callback)      // main → renderer: window is back
  openMainWindow()            // renderer → main: orb clicked
  minimizeToOrb()             // renderer → main: minimize button pressed
  removeOrbModeListener()     // cleanup
  removeReturnHomeListener()  // cleanup
}
```

### System tray

A glowing cyan dot appears in the macOS menu bar.
- Left-click: toggle main window
- Context menu: "Open Symbite" / "Quit Symbite"

Symbite never fully quits when you close the window.
Only "Quit Symbite" from the tray ends the process.

---

## File map

```
frontend-v2/
├── electron/
│   ├── main.js                    ← Electron main process
│   ├── preload.js                 ← IPC bridge (contextIsolation-safe)
│   └── roaming-orb/
│       └── index.html             ← Standalone orb window (pure HTML)
├── src/
│   ├── App.jsx                    ← +IPC listeners wired in
│   └── store/useAuraStore.js      ← enterRoamingMode/exitRoamingMode already existed
├── vite.config.js                 ← +base "./" for ELECTRON_BUILD
└── package.json                   ← +electron, electron-builder, concurrently, wait-on
```

---

## Troubleshooting

**"electron: command not found"**
Run `npm install` first.

**White flash on launch**
Normal — Electron is loading the Vite dev server. The `show: false` +
`ready-to-show` pattern already handles this for production builds.

**Orb window has a coloured background (not transparent)**
macOS requires `transparent: true` AND `frame: false` together.
Both are set in `electron/main.js`. If you see a background, make sure
you're running the Electron process, not the browser.

**DevTools opens automatically**
Only in dev mode (`app.isPackaged === false`). Removed automatically in
production builds.
