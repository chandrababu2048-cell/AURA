// electron/main.js
// ============================================================
// Symbite — Electron Main Process
//
// Window architecture:
//   mainWindow    — 1400×900, frameless, vibrancy glass, the full 3-panel UI
//   roamingWindow — 120×120, transparent, always-on-top, the escaped orb
//
// Lifecycle:
//   App launch         → show mainWindow, roamingWindow hidden
//   Window minimise    → hide mainWindow, show roamingWindow (orb escapes)
//   Window close btn   → same (do NOT quit — symbiote never dies)
//   Roaming orb click  → hide roamingWindow, show + focus mainWindow
//   Tray → "Quit"      → app.quit() for real
// ============================================================

const {
  app,
  BrowserWindow,
  Tray,
  Menu,
  ipcMain,
  nativeImage,
  screen,
} = require("electron");
const path = require("path");

// ── Dev vs production URL ──────────────────────────────────────────────────
const isDev = !app.isPackaged;
const MAIN_URL = isDev
  ? "http://localhost:5173"
  : `file://${path.join(__dirname, "../dist/index.html")}`;

const ROAMING_URL = isDev
  ? `file://${path.join(__dirname, "roaming-orb/index.html")}`
  : `file://${path.join(__dirname, "roaming-orb/index.html")}`;

// ── Module-level handles ───────────────────────────────────────────────────
let mainWindow = null;
let roamingWindow = null;
let tray = null;

// ── createMainWindow ───────────────────────────────────────────────────────
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    frame: false,          // custom titlebar / frameless
    transparent: false,
    // macOS vibrancy — gives a frosted-glass feel behind the window
    vibrancy: "under-window",
    visualEffectState: "active",
    titleBarStyle: "hidden",
    trafficLightPosition: { x: 16, y: 16 },
    backgroundColor: "#050B17", // aura-void fallback while page loads
    show: false,           // wait until ready-to-show
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,      // needed so preload can use require('electron')
    },
  });

  mainWindow.loadURL(MAIN_URL);

  // Show when painted to avoid white flash
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    if (isDev) mainWindow.webContents.openDevTools({ mode: "detach" });
  });

  // MINIMISE → escape to orb instead
  mainWindow.on("minimize", (e) => {
    e.preventDefault();
    hideMainShowOrb();
  });

  // CLOSE button → escape to orb instead of quitting
  mainWindow.on("close", (e) => {
    if (!app.isQuitting) {
      e.preventDefault();
      hideMainShowOrb();
    }
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ── createRoamingWindow ────────────────────────────────────────────────────
function createRoamingWindow() {
  // Place the orb in the bottom-right of the primary display initially
  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const OW = 120;
  const OH = 120;
  const startX = sw - OW - 40;
  const startY = sh - OH - 40;

  roamingWindow = new BrowserWindow({
    width: OW,
    height: OH,
    x: startX,
    y: startY,
    frame: false,
    transparent: true,         // desktop shows through — ONLY the orb is visible
    alwaysOnTop: true,
    skipTaskbar: true,         // no dock/taskbar entry for the orb window
    resizable: false,
    movable: true,             // user can drag the orb around the desktop
    hasShadow: false,
    show: false,               // starts hidden, revealed when main window hides
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  roamingWindow.loadURL(ROAMING_URL);

  // Keep the orb always-on-top across all workspaces
  roamingWindow.setAlwaysOnTop(true, "floating", 1);
  roamingWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: false });

  roamingWindow.on("closed", () => {
    roamingWindow = null;
  });
}

// ── createTray ─────────────────────────────────────────────────────────────
function createTray() {
  // Build a tiny 16×16 cyan circle as the tray icon (no external asset needed)
  const icon = buildTrayIcon();
  tray = new Tray(icon);
  tray.setToolTip("Symbite — your AI symbiote");

  const menu = Menu.buildFromTemplate([
    {
      label: "Open Symbite",
      click: showMainHideOrb,
    },
    { type: "separator" },
    {
      label: "Quit Symbite",
      click: () => {
        app.isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(menu);

  // Left-click on tray icon → toggle main window
  tray.on("click", () => {
    if (mainWindow && mainWindow.isVisible()) {
      hideMainShowOrb();
    } else {
      showMainHideOrb();
    }
  });
}

// ── Transition helpers ─────────────────────────────────────────────────────
function hideMainShowOrb() {
  if (mainWindow) {
    // Tell the renderer it's going roaming before we hide
    mainWindow.webContents.send("orb-mode", true);
    mainWindow.hide();
  }
  if (roamingWindow) {
    roamingWindow.show();
  }
}

function showMainHideOrb() {
  if (roamingWindow) {
    roamingWindow.hide();
  }
  if (mainWindow) {
    mainWindow.show();
    mainWindow.focus();
    // Tell the renderer it's home
    mainWindow.webContents.send("return-home", true);
  }
}

// ── IPC handlers ───────────────────────────────────────────────────────────

// Roaming orb clicked → bring main window back
ipcMain.on("open-main-window", () => {
  showMainHideOrb();
});

// Renderer requests minimize-to-orb
ipcMain.on("minimize-to-orb", () => {
  hideMainShowOrb();
});

// ── Tiny tray icon (programmatic, no external asset file needed) ──────────
function buildTrayIcon() {
  // Build a 16×16 RGBA PNG in raw bytes.
  // PNG structure: signature + IHDR + IDAT + IEND
  // We draw a filled cyan circle (#2E, #A8, #FF) on transparent background.
  //
  // For simplicity we skip raw PNG encoding and use nativeImage.createEmpty()
  // with a size hint, then let the OS render a default icon.
  // In production you'd replace this with a real .icns file in assets/.
  //
  // Reliable cross-machine approach: encode a 16×16 solid-colour PNG
  // using only Node's built-in zlib (no canvas/sharp deps).

  const zlib = require("zlib");

  const W = 16;
  const H = 16;
  const CX = 8;
  const CY = 8;
  const R = 6;

  // Build raw RGBA scanlines
  const scanlines = [];
  for (let y = 0; y < H; y++) {
    const row = Buffer.alloc(1 + W * 4, 0); // filter byte + RGBA pixels
    row[0] = 0; // filter type None
    for (let x = 0; x < W; x++) {
      const dx = x - CX;
      const dy = y - CY;
      if (dx * dx + dy * dy <= R * R) {
        const i = 1 + x * 4;
        row[i] = 0x2e;     // R
        row[i + 1] = 0xa8; // G
        row[i + 2] = 0xff; // B
        row[i + 3] = 0xff; // A (fully opaque)
      }
    }
    scanlines.push(row);
  }

  const raw = Buffer.concat(scanlines);
  const compressed = zlib.deflateSync(raw);

  function crc32(buf) {
    const table = crc32.table || (crc32.table = (() => {
      const t = new Uint32Array(256);
      for (let i = 0; i < 256; i++) {
        let c = i;
        for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
        t[i] = c;
      }
      return t;
    })());
    let crc = 0xffffffff;
    for (const b of buf) crc = table[(crc ^ b) & 0xff] ^ (crc >>> 8);
    return (crc ^ 0xffffffff) >>> 0;
  }

  function chunk(type, data) {
    const typeB = Buffer.from(type, "ascii");
    const lenB = Buffer.alloc(4);
    lenB.writeUInt32BE(data.length);
    const crcInput = Buffer.concat([typeB, data]);
    const crcB = Buffer.alloc(4);
    crcB.writeUInt32BE(crc32(crcInput));
    return Buffer.concat([lenB, typeB, data, crcB]);
  }

  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(W, 0);
  ihdrData.writeUInt32BE(H, 4);
  ihdrData[8] = 8;  // bit depth
  ihdrData[9] = 6;  // color type RGBA
  ihdrData[10] = 0; // compression
  ihdrData[11] = 0; // filter
  ihdrData[12] = 0; // interlace

  const png = Buffer.concat([
    sig,
    chunk("IHDR", ihdrData),
    chunk("IDAT", compressed),
    chunk("IEND", Buffer.alloc(0)),
  ]);

  try {
    return nativeImage.createFromBuffer(png, { scaleFactor: 1 });
  } catch (_) {
    return nativeImage.createEmpty();
  }
}

// ── App lifecycle ──────────────────────────────────────────────────────────
app.whenReady().then(() => {
  createMainWindow();
  createRoamingWindow();
  createTray();

  app.on("activate", () => {
    // macOS: clicking dock icon when all windows are hidden → restore
    if (mainWindow) {
      showMainHideOrb();
    } else {
      createMainWindow();
    }
  });
});

// Intercept the default quit so close-button doesn't kill the process
app.on("before-quit", () => {
  app.isQuitting = true;
});

// macOS: don't quit when last window is closed (we want orb to live)
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
