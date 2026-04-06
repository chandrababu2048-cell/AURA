# ============================================================
# streamlit_app.py — AURA Web Interface (v1)
# ============================================================
#
# ARCHITECTURE — why it's structured this way:
#
#   The previous version put everything (buttons, plans, mode
#   switcher) inside components.html(). That NEVER works —
#   components.html() runs in a sandboxed iframe that cannot
#   send any data back to Python. Clicking a button inside it
#   is like clicking a picture of a button.
#
#   CORRECT architecture:
#     • Interactive widgets (buttons, checkboxes, chat input)
#       → Streamlit native widgets. These can talk to Python.
#     • Animated canvas (the orb) → components.html().
#       The orb never needs to send data to Python, so iframe
#       isolation is fine there.
#
#   LAYOUT (chat page):
#     Top bar   → st.markdown() HTML — live clock via JS
#     3 columns → st.columns([2.5, 4, 3.5])
#       Left    → Streamlit widgets: stats, weather, plans, buttons
#       Center  → components.html() orb + st.button() modes below
#       Right   → st.markdown() chat history + st.chat_input()
#
# PAGE FLOW:
#   boot → auth → chat
#
# FILE MAP:
#   brain.py    → Claude API, prompt building, mode support
#   database.py → all SQLite reads/writes
#   memory.py   → context building for the AI
#   weather.py  → OpenWeatherMap API
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import psutil
import os
import html as html_lib

from brain import AuraBrain
from database import AuraDatabase
from weather import get_weather
from helper import get_greeting as _get_greeting

# ── Page Config ──────────────────────────────────────────────
# Must be the FIRST Streamlit call — Streamlit enforces this.
st.set_page_config(
    page_title="AURA — Personal AI Companion",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State ────────────────────────────────────────────
# Streamlit reruns this file from top to bottom on every click.
# session_state is the ONLY thing that survives reruns.
# Initialize each key once — never overwrite existing values.
if "page"          not in st.session_state: st.session_state.page          = "boot"
if "user"          not in st.session_state: st.session_state.user          = None
if "user_id"       not in st.session_state: st.session_state.user_id       = None
if "brain"         not in st.session_state: st.session_state.brain         = None
if "messages"      not in st.session_state: st.session_state.messages      = []
if "mode"          not in st.session_state: st.session_state.mode          = "Personal"
if "weather_cache" not in st.session_state: st.session_state.weather_cache = None
if "show_report"   not in st.session_state: st.session_state.show_report   = False
if "show_goals"    not in st.session_state: st.session_state.show_goals    = True

db = AuraDatabase()

# ── Shared CSS variables injected once ───────────────────────
# These apply globally across all pages.
# We strip ALL Streamlit chrome so our UI owns the full screen.
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Share+Tech+Mono&display=swap');

/* ── Strip Streamlit chrome ── */
header[data-testid="stHeader"],
footer, #MainMenu,
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
.stDeployButton { display:none !important; }

/* ── Remove all default padding ── */
/* WHY? We want the dashboard to touch every edge of the browser */
.stMainBlockContainer, .block-container, .stMain {
    padding:0 !important; max-width:100% !important;
}

/* ── App background + CRT scanlines ── */
.stApp { background:#080300 !important; overflow:hidden;
         animation:crtFlicker 8s infinite; }
.stApp::before {
    content:''; position:fixed; inset:0;
    background:repeating-linear-gradient(
        to bottom, transparent 0, transparent 2px,
        rgba(0,0,0,0.18) 2px, rgba(0,0,0,0.18) 4px);
    pointer-events:none; z-index:9999;
}
/* Vignette — dark edges like a real CRT monitor */
.stApp::after {
    content:''; position:fixed; inset:0;
    box-shadow:inset 0 0 180px rgba(0,0,0,0.85),
               inset 0 0 60px rgba(0,0,0,0.5);
    pointer-events:none; z-index:9998;
}

/* ── Global font + color ── */
*, p, div, span, label, li, h1, h2, h3, h4, h5, h6 {
    font-family:'VT323',monospace !important;
    color:#FFB000 !important;
    text-transform:uppercase;
}

/* ── Inputs ── */
input, textarea {
    font-family:'VT323',monospace !important;
    font-size:17px !important;
    background:#100600 !important;
    color:#FFB000 !important;
    border:1px solid #4a2400 !important;
    border-radius:0 !important;
    caret-color:#FFB000 !important;
    text-transform:uppercase !important;
}
input:focus, textarea:focus {
    border-color:#FFB000 !important;
    box-shadow:0 0 8px rgba(255,176,0,0.25) !important;
    outline:none !important;
}

/* ── Buttons — base style ── */
.stButton > button {
    font-family:'VT323',monospace !important;
    font-size:15px !important;
    background:transparent !important;
    color:#FFB000 !important;
    border:1px solid rgba(255,176,0,0.2) !important;
    border-radius:0 !important;
    letter-spacing:2px;
    width:100%;
    transition:all 0.15s;
    text-shadow:none !important;
}
.stButton > button:hover {
    background:rgba(255,176,0,0.07) !important;
    border-color:#FFB000 !important;
    box-shadow:0 0 10px rgba(255,176,0,0.25) !important;
}

/* ── Form submit buttons ── */
.stFormSubmitButton > button {
    font-family:'VT323',monospace !important;
    font-size:17px !important;
    background:#FFB000 !important;
    color:#080300 !important;
    border:none !important;
    border-radius:0 !important;
    letter-spacing:3px;
    width:100%;
}
.stFormSubmitButton > button:hover {
    box-shadow:0 0 18px rgba(255,176,0,0.6) !important;
}

/* ── Checkboxes ── */
.stCheckbox label {
    font-family:'VT323',monospace !important;
    font-size:13px !important;
    color:#FFB000 !important;
}

/* ── Notifications ── */
.stSuccess { background:#001a00 !important; border:1px solid #00FF41 !important; border-radius:0 !important; }
.stError   { background:#1a0000 !important; border:1px solid #FF3333 !important; border-radius:0 !important; }
.stInfo    { background:#0c0400 !important; border:1px solid rgba(255,176,0,0.4) !important; border-radius:0 !important; font-family:'Share Tech Mono',monospace !important; }

/* ── Dividers ── */
hr { border-color:rgba(255,176,0,0.12) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:3px; }
::-webkit-scrollbar-track { background:#080300; }
::-webkit-scrollbar-thumb { background:#4a2400; }
::-webkit-scrollbar-thumb:hover { background:#FFB000; }

/* ── Strip st.form default border + padding ── */
[data-testid="stForm"] {
    border:none !important;
    padding:0 !important;
    background:transparent !important;
}

/* ── Left column: shrink submit buttons to be compact, not full amber ── */
div[data-testid="stColumn"]:nth-child(1) .stFormSubmitButton > button {
    background:transparent !important;
    color:#FFB000 !important;
    border:1px solid rgba(255,176,0,0.3) !important;
    font-size:12px !important;
    padding:4px 0 !important;
    letter-spacing:2px !important;
}
div[data-testid="stColumn"]:nth-child(1) .stFormSubmitButton > button:hover {
    border-color:#FFB000 !important;
    background:rgba(255,176,0,0.07) !important;
    box-shadow:0 0 8px rgba(255,176,0,0.2) !important;
}

/* ── Fix Settings expander: prevent SVG arrow from rendering as "arrow_" text ── */
[data-testid="stExpander"] {
    border:1px solid rgba(255,176,0,0.15) !important;
    background:transparent !important;
}
[data-testid="stExpander"] summary {
    font-size:13px !important;
    letter-spacing:2px !important;
    padding:5px 8px !important;
}
[data-testid="stExpander"] summary svg {
    display:inline-block !important;
    width:16px !important; height:16px !important;
    flex-shrink:0 !important;
}
[data-testid="stExpander"] summary p {
    display:inline !important;
}

/* ── Left column inner rows: collapse to content height only ── */
/* WHY: plan/goal rows use st.columns() which default to stretch,
   creating giant black rectangles. Force height:auto on every
   inner horizontal block and its children inside left column. */
div[data-testid="stColumn"]:first-child div[data-testid="stHorizontalBlock"],
div[data-testid="stColumn"]:first-child div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    height:auto !important;
    max-height:none !important;
    min-height:0 !important;
    align-items:flex-start !important;
    align-self:flex-start !important;
    flex-shrink:1 !important;
    overflow:visible !important;
}

/* ── Left column: button text visible (transparent bg + amber text) ── */
div[data-testid="stColumn"]:first-child .stFormSubmitButton > button,
div[data-testid="stColumn"]:first-child .stFormSubmitButton > button * {
    color:#FFB000 !important;
    background:transparent !important;
    border:1px solid rgba(255,176,0,0.3) !important;
    text-shadow:none !important;
}

/* ── Settings expander: hide broken SVG arrow text ── */
[data-testid="stExpander"] summary svg {
    visibility:hidden !important;
    width:0 !important;
    margin:0 !important;
}
[data-testid="stExpander"] summary p::before {
    content:"▶ " !important;
    font-family:'VT323',monospace !important;
    opacity:0.5;
}
[data-testid="stExpander"][open] summary p::before {
    content:"▼ " !important;
}

/* ── Shrink vertical gaps between left column items ── */
div[data-testid="stColumn"]:first-child > div > div[data-testid="stVerticalBlock"] > div {
    padding-top:0 !important;
    padding-bottom:2px !important;
}


/* ── Tabs (auth page) ── */
.stTabs [data-baseweb="tab"] {
    font-family:'VT323',monospace !important; font-size:17px !important;
    color:rgba(255,176,0,0.4) !important; letter-spacing:2px;
}
.stTabs [aria-selected="true"] {
    color:#FFB000 !important;
    border-bottom:2px solid #FFB000 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background:transparent !important;
    border-bottom:1px solid #4a2400 !important;
}

/* ── Spinner ── */
.stSpinner > div { color:#FFB000 !important; }

/* ── Animations ── */
@keyframes glitch {
    0%,80%,100% { text-shadow:0 0 10px #FFB000; transform:none; clip-path:none; }
    81% { text-shadow:3px 0 #FF6600,-3px 0 #FFB000,0 0 22px rgba(255,176,0,.9);
          transform:translateX(2px) skewX(-1deg); }
    82% { text-shadow:-4px 0 #FF0000,4px 0 #FFB000;
          transform:translateX(-3px) skewX(2deg);
          clip-path:polygon(0 20%,100% 20%,100% 40%,0 40%); }
    83% { text-shadow:0 0 32px #FFB000; transform:none; clip-path:none; }
    86% { text-shadow:2px 2px #FF6600,-2px -2px #FFB000;
          transform:skewX(-3deg) translateX(1px); }
    87% { text-shadow:-2px 0 #00FFFF,2px 0 #FF0000;
          clip-path:polygon(0 60%,100% 60%,100% 80%,0 80%); }
    88% { text-shadow:0 0 10px #FFB000; transform:none; clip-path:none; }
    93% { text-shadow:3px 0 #FF6600,-3px 0 #FFB000; transform:translateX(2px); }
    94% { text-shadow:0 0 10px #FFB000; transform:none; }
}

@keyframes crtFlicker {
    0%,100%  { opacity:1; }
    92%  { opacity:1; }
    93%  { opacity:0.85; }
    94%  { opacity:1; }
    97%  { opacity:1; }
    98%  { opacity:0.90; }
    99%  { opacity:1; }
}

@keyframes scanMove {
    0%   { background-position:0 0; }
    100% { background-position:0 100vh; }
}

/* ── Column layout + left scroll: chat page only (injected inline) ── */
/* Moved to chat-page inline CSS so auth/boot pages are not affected */

/* ── Center column: fixed, no scroll ── */
div[data-testid="stColumn"]:nth-child(2) {
    overflow:hidden !important;
    height:calc(100vh - 46px) !important;
    max-height:calc(100vh - 46px) !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
}

/* ── Right column: fixed, chat scrolls inside ── */
div[data-testid="stColumn"]:nth-child(3) {
    padding:0 0 0 10px !important;
    overflow:hidden !important;
    height:calc(100vh - 46px) !important;
    max-height:calc(100vh - 46px) !important;
    background:#050200 !important;
    border-left:1px solid rgba(255,176,0,0.15) !important;
    flex-shrink:0 !important;
}

/* ── Mode radio buttons styled as segmented control ── */
div[data-testid="stRadio"] > div {
    display:flex !important;
    flex-direction:row !important;
    gap:6px !important;
    justify-content:center !important;
    flex-wrap:nowrap !important;
}
div[data-testid="stRadio"] label {
    border:1px solid rgba(255,176,0,0.25) !important;
    padding:5px 14px !important;
    cursor:pointer !important;
    font-size:13px !important;
    letter-spacing:2px !important;
    font-family:'VT323',monospace !important;
    color:rgba(255,176,0,0.5) !important;
    background:transparent !important;
    transition:all 0.15s !important;
    white-space:nowrap !important;
}
div[data-testid="stRadio"] label:hover {
    border-color:#FFB000 !important;
    color:#FFB000 !important;
    background:rgba(255,176,0,0.06) !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    border-color:#FFB000 !important;
    color:#FFB000 !important;
    background:rgba(255,176,0,0.08) !important;
    box-shadow:0 0 8px rgba(255,176,0,0.2) !important;
}
div[data-testid="stRadio"] input[type="radio"] {
    display:none !important;
}

/* ── Submit button text fix ── */
.stFormSubmitButton > button * {
    color:#080300 !important;
    text-shadow:none !important;
}

/* ── Amber glow on interactive focus ── */
input:focus, textarea:focus,
.stButton > button:focus,
.stChatInput input:focus {
    box-shadow:0 0 0 1px #FFB000,0 0 18px rgba(255,176,0,0.35) !important;
}

/* ── Chat input bar ── */
[data-testid="stChatInput"] {
    background:#050200 !important;
    border-top:1px solid rgba(255,176,0,0.18) !important;
}
[data-testid="stChatInput"] textarea {
    font-size:14px !important;
    letter-spacing:1px !important;
}

/* ── Left panel section labels glow ── */
div[data-testid="stColumn"]:first-child .stMarkdown div[style*="opacity:.4"] {
    text-shadow:0 0 8px rgba(255,176,0,0.4) !important;
}

/* ── Dividers with subtle glow ── */
hr {
    border-color:rgba(255,176,0,0.10) !important;
    box-shadow:0 0 4px rgba(255,176,0,0.08) !important;
}

/* ── Scrollbar amber glow ── */
::-webkit-scrollbar-thumb:hover { background:#FFB000; box-shadow:0 0 6px #FFB000; }

/* ── Checkbox glow when checked ── */
input[type="checkbox"]:checked {
    accent-color:#FFB000 !important;
    box-shadow:0 0 8px #FFB000 !important;
}

/* ── Radio label active glow ── */
div[data-testid="stRadio"] label:has(input:checked) {
    text-shadow:0 0 8px rgba(255,176,0,0.6) !important;
}

/* ── Orb iframe: remove default frame margin ── */
iframe {
    border:none !important;
    display:block !important;
}

/* ── Topbar iframe flush at top ── */
div[data-testid="stVerticalBlock"] > div:first-child iframe {
    margin-bottom:-4px !important;
}

"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────

def get_cached_weather() -> dict:
    """
    Fetch weather once per session and cache the result.
    WHY cache? The API takes ~500ms and has rate limits.
    We validate the cache is a dict — guards against stale
    string values from older versions of weather.py.
    """
    cached = st.session_state.weather_cache
    if cached is None or not isinstance(cached, dict):
        city = os.environ.get("WEATHER_CITY", "Boston")
        st.session_state.weather_cache = get_weather(city)
    return st.session_state.weather_cache

def get_greeting() -> str:
    return _get_greeting(datetime.now().hour)

def get_system_stats() -> dict:
    """Real CPU/RAM/Disk percentages via psutil."""
    return {
        "cpu":  psutil.cpu_percent(interval=0.1),
        "ram":  psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
    }

def logout():
    """Clear ALL session state and return to auth page."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "auth"


# ══════════════════════════════════════════════════════════════
# PAGE 1 — BOOT SEQUENCE
# ══════════════════════════════════════════════════════════════

if st.session_state.page == "boot":
    components.html("""
<!DOCTYPE html><html>
<head>
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#080300;display:flex;align-items:center;justify-content:center;
     min-height:100vh;font-family:'VT323',monospace;overflow:hidden;}
body::before{content:'';position:fixed;inset:0;
  background:repeating-linear-gradient(to bottom,transparent 0,transparent 3px,rgba(0,0,0,0.1) 3px,rgba(0,0,0,0.1) 4px);
  pointer-events:none;z-index:10;}
body::after{content:'';position:fixed;inset:0;
  box-shadow:inset 0 0 160px rgba(0,0,0,0.85);pointer-events:none;z-index:11;}
.screen{width:680px;padding:44px 50px;animation:flicker 6s infinite;}
@keyframes flicker{0%,90%,95%,100%{opacity:1;}92%{opacity:.82;}96%{opacity:.9;}}
.border{color:#FFB000;font-size:12px;letter-spacing:2px;opacity:.35;margin-bottom:26px;}
.line{font-size:19px;color:#FFB000;text-shadow:0 0 8px rgba(255,176,0,.7);
      text-transform:uppercase;letter-spacing:1px;line-height:2.1;opacity:0;min-height:1.9em;}
.pfx{color:#FF6600;margin-right:8px;}
.ok{color:#00FF41;text-shadow:0 0 8px #00FF41;}
.cur{display:inline-block;width:10px;height:15px;background:#FFB000;
     vertical-align:middle;margin-left:2px;animation:bl .6s step-end infinite;}
@keyframes bl{0%,100%{opacity:1;}50%{opacity:0;}}
</style>
</head>
<body>
<div class="screen">
  <div class="border">
    ╔══════════════════════════════════════════════════════╗<br>
    &nbsp;&nbsp;AURA INDUSTRIES — AURA NEURAL OS v1.0.0<br>
    &nbsp;&nbsp;CLASSIFIED SYSTEM — AUTHORIZED ACCESS ONLY<br>
    ╚══════════════════════════════════════════════════════╝
  </div>
  <div class="line" id="l0"></div><div class="line" id="l1"></div>
  <div class="line" id="l2"></div><div class="line" id="l3"></div>
  <div class="line" id="l4"></div><div class="line" id="l5"></div>
  <div class="line" id="l6"></div><div class="line" id="l7"></div>
</div>
<script>
const lines=[
  {id:"l0",p:"SYS", t:"AURA Neural OS — Build "+new Date().toISOString().slice(0,10)},
  {id:"l1",p:"INIT",t:"Loading companion matrix..."},
  {id:"l2",p:"MEM", t:"Allocating long-term memory layer..."},
  {id:"l3",p:"SEC", t:"Biometric scan complete — identity verified"},
  {id:"l4",p:"AI",  t:"Claude engine online — latency: 0.3s"},
  {id:"l5",p:"WX",  t:"Atmospheric data feed connected"},
  {id:"l6",p:"DB",  t:"User database initialized — encryption active"},
  {id:"l7",p:"AURA",t:"[████████████] 100% — All systems nominal",ok:true},
];
function type(el,full,cb){
  let i=0;el.style.opacity="1";el.innerHTML='<span class="cur"></span>';
  const iv=setInterval(()=>{
    if(i<full.length){el.innerHTML=full.slice(0,++i)+'<span class="cur"></span>';}
    else{el.innerHTML=full;clearInterval(iv);if(cb)cb();}
  },26);
}
function run(i){
  if(i>=lines.length)return;
  const {id,p,t,ok}=lines[i];
  const el=document.getElementById(id);
  const full=`<span class="pfx">${p}:</span>${ok?'<span class="ok">':''} ${t}${ok?'</span>':''}`;
  setTimeout(()=>type(el,full,()=>run(i+1)),i===0?400:220);
}
run(0);
</script>
</body></html>
    """, height=520)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("[ INITIALIZE AURA ]", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════
# PAGE 2 — AUTH (Login / Register)
# ══════════════════════════════════════════════════════════════

if st.session_state.page == "auth":
    st.markdown("""
    <div style="text-align:center;padding:44px 0 20px;">
      <div style="font-size:72px;letter-spacing:18px;font-family:VT323,monospace;color:#FFB000;
                  animation:glitch 5s infinite;
                  text-shadow:3px 0 #FF6600,-3px 0 #FFB000,0 0 30px rgba(255,176,0,0.8);">
        A.U.R.A
      </div>
      <div style="font-size:13px;letter-spacing:6px;opacity:.4;margin-top:8px;">
        Personal AI Companion — Stark Industries
      </div>
      <div style="font-size:11px;color:#FF6600;letter-spacing:4px;margin-top:4px;opacity:.65;">
        ⚡ Authorized Access Only ⚡
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    tab_login, tab_reg = st.tabs(["[ Login ]", "[ New Operator ]"])

    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("Operator Email",   placeholder="Enter email...")
            password = st.text_input("Access Code",      placeholder="Enter password...", type="password")
            _, c, _  = st.columns([1,2,1])
            with c:
                sub = st.form_submit_button("[ Authenticate ]", use_container_width=True)
            if sub:
                if not email or not password:
                    st.error("⚠ All fields required.")
                else:
                    res = db.login_user(email, password)
                    if res["success"]:
                        u = res["user"]
                        st.session_state.user    = u
                        st.session_state.user_id = u["id"]
                        st.session_state.brain   = AuraBrain(u["id"])
                        st.session_state.messages = []
                        st.session_state.page    = "chat"
                        st.rerun()
                    else:
                        st.error(f"⚠ {res['message']}")

    with tab_reg:
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            with c1:
                rname  = st.text_input("Operator Name",  placeholder="Your name...")
                remail = st.text_input("Email Address",   placeholder="Your email...")
            with c2:
                rai    = st.text_input("Name Your AI",    value="AURA")
                rwake  = st.text_input("Wake-Up Time",    value="07:00")
            rpass = st.text_input("Create Access Code", placeholder="Min 6 characters...", type="password")
            _, c, _ = st.columns([1,2,1])
            with c:
                sub = st.form_submit_button("[ Create Profile ]", use_container_width=True)
            if sub:
                if not rname or not remail or not rpass:
                    st.error("⚠ All fields required.")
                elif len(rpass) < 6:
                    st.error("⚠ Min 6 characters.")
                else:
                    res = db.register_user(rname, remail, rpass, rai or "AURA", rwake or "07:00")
                    if res["success"]:
                        st.success(f"✓ Profile created! Welcome, {rname}. Please log in.")
                    else:
                        st.error(f"⚠ {res['message']}")
    st.stop()


# ══════════════════════════════════════════════════════════════
# PAGE 3 — MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════
#
# LAYOUT STRATEGY:
#   We use st.columns() for the 3-column structure.
#   WHY? Native Streamlit columns let us place real widgets
#   (buttons, checkboxes, chat input) that can talk to Python.
#
#   Left   col → stats, weather, plans, action buttons (all native)
#   Center col → components.html() for orb canvas (animation only)
#                + st.button() for mode switcher BELOW the canvas
#   Right  col → st.markdown() for chat history + st.chat_input()
#
#   The orb canvas is the ONLY thing that needs iframe isolation.
#   Everything interactive uses Streamlit widgets.

if st.session_state.page == "chat":

    # Lock scroll only on the chat dashboard (not auth/boot pages)
    st.markdown("""<style>
    html, body { overflow:hidden !important; height:100% !important; }
    .stApp { overflow:hidden !important; height:100vh !important; }
    .stMain { overflow:hidden !important; height:calc(100vh - 46px) !important; }
    .stMainBlockContainer, .block-container {
        overflow:hidden !important; padding:0 !important; max-width:100% !important; }

    /* ── Column layout: chat page only ── */
    [data-testid="stHorizontalBlock"] {
        align-items:flex-start !important;
        height:calc(100vh - 46px) !important;
        overflow:hidden !important;
    }

    /* ── Left column: scrolls internally ── */
    div[data-testid="stColumn"]:nth-child(1) {
        padding:8px 8px 8px 14px !important;
        overflow-y:auto !important;
        height:calc(100vh - 46px) !important;
        max-height:calc(100vh - 46px) !important;
        background:#050200 !important;
        border-right:1px solid rgba(255,176,0,0.15) !important;
        flex-shrink:0 !important;
    }
    /* Fix: Streamlit wraps column content in an intermediate div —
       that wrapper must pass full height through for scroll to work */
    div[data-testid="stColumn"]:nth-child(1) > div {
        height:100% !important;
        overflow-y:auto !important;
        overflow-x:hidden !important;
    }
    div[data-testid="stColumn"]:nth-child(1) > div > div[data-testid="stVerticalBlock"] {
        height:auto !important;
        padding-bottom:24px !important;
    }
    </style>""", unsafe_allow_html=True)

    # Safety guards
    if st.session_state.brain is None and st.session_state.user_id:
        st.session_state.brain = AuraBrain(st.session_state.user_id)
    if not st.session_state.user:
        st.session_state.page = "auth"; st.rerun()

    user    = st.session_state.user
    user_id = st.session_state.user_id
    brain   = st.session_state.brain
    ai_name = user["ai_name"].upper()
    uname   = user["name"]
    mode    = st.session_state.mode

    # ── Gather data ───────────────────────────────────────────
    stats  = get_system_stats()
    wx     = get_cached_weather()
    plans  = brain.memory.db.get_today_plans(user_id)
    now    = datetime.now()

    done_count  = sum(1 for p in plans if p["is_done"])
    total_count = len(plans)
    task_pct    = int(done_count / total_count * 100) if total_count else 0
    all_done    = total_count > 0 and done_count == total_count

    wx_temp  = f"{wx['temp']}°C"       if wx["success"] else "N/A"
    wx_city  = wx.get("city","")       if wx["success"] else ""
    wx_cond  = wx.get("condition","")  if wx["success"] else "Unavailable"
    wx_hum   = f"{wx['humidity']}%"    if wx["success"] else "--"
    wx_wind  = f"{wx['wind']}m/s"      if wx["success"] else "--"
    wx_feels = f"{wx['feels_like']}°C" if wx["success"] else "--"
    wx_top   = f"🌤 {wx_temp} {wx_city}" if wx["success"] else "Weather N/A"

    # ── Top Bar ───────────────────────────────────────────────
    # WHY components.html() and NOT st.markdown()?
    # st.markdown() uses React's dangerouslySetInnerHTML which
    # NEVER executes <script> tags. components.html() creates a
    # real iframe where JavaScript runs properly — clock works.
    components.html(f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{height:46px;overflow:hidden;background:#050200;color:#FFB000;font-family:'VT323',monospace;}}
.bar{{height:46px;background:#050200;border-bottom:1px solid rgba(255,176,0,0.18);
      display:flex;align-items:center;justify-content:space-between;padding:0 22px;}}
.logo{{font-size:22px;letter-spacing:7px;color:#FFB000;text-shadow:0 0 12px #FFB000;
       animation:glitch 5s infinite;}}
@keyframes glitch{{
  0%,84%,100%{{text-shadow:0 0 12px #FFB000;transform:none;}}
  85%{{text-shadow:3px 0 #FF6600,-3px 0 #FFB000,0 0 22px rgba(255,176,0,.9);transform:translateX(2px);}}
  86%{{text-shadow:-4px 0 #FF6600,4px 0 #FFB000;transform:translateX(-2px);}}
  87%{{text-shadow:0 0 32px #FFB000;transform:none;}}
  90%{{text-shadow:2px 2px #FF6600,-2px -2px #FFB000;transform:skewX(-3deg);}}
  91%{{text-shadow:0 0 12px #FFB000;transform:none;}}
}}
.status{{display:flex;align-items:center;gap:8px;}}
.dot{{width:8px;height:8px;background:#00FF41;border-radius:50%;
      box-shadow:0 0 8px #00FF41;animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 4px #00FF41;}}50%{{box-shadow:0 0 16px #00FF41,0 0 32px #00FF41;}}}}
.online{{color:#00FF41;font-size:12px;letter-spacing:2px;}}
.mid{{text-align:center;}}
.clk{{font-size:20px;letter-spacing:4px;color:#FFB000;text-shadow:0 0 10px #FFB000;}}
.dt{{font-size:10px;opacity:.4;letter-spacing:2px;}}
.right{{display:flex;align-items:center;gap:14px;}}
.wx{{font-size:13px;opacity:.65;letter-spacing:1px;}}
.mode{{font-size:12px;letter-spacing:2px;color:#FF6600;
       border:1px solid rgba(255,102,0,.3);padding:3px 10px;text-transform:uppercase;}}
</style>
</head><body>
<div class="bar">
  <div class="status">
    <div class="logo">A.U.R.A</div>
    <div class="dot"></div>
    <div class="online">Online</div>
  </div>
  <div class="mid">
    <div class="clk" id="clk">--:--:--</div>
    <div class="dt"  id="dt">Loading...</div>
  </div>
  <div class="right">
    <div class="wx">{wx_top}</div>
    <div class="mode">{mode} Mode</div>
  </div>
</div>
<script>
var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var D=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
function tick(){{
  var n=new Date();
  document.getElementById('clk').textContent=n.toLocaleTimeString('en-US',{{hour12:false}});
  document.getElementById('dt').textContent=D[n.getDay()]+' '+n.getDate()+' '+M[n.getMonth()]+' '+n.getFullYear();
}}
setTimeout(function(){{tick();setInterval(tick,1000);}},150);
</script>
</body></html>""", height=46, scrolling=False)

    # ── 3-Column Layout ───────────────────────────────────────
    # Proportions: left=2.5, center=4, right=3.5
    # These are relative widths — Streamlit converts to percentages.
    left_col, center_col, right_col = st.columns([2.5, 4, 3.5], gap="medium")

    # ══════════════════════════════════════════════════════════
    # LEFT COLUMN — Stats, Weather, Plans, Actions
    # All native Streamlit widgets → they work correctly.
    # ══════════════════════════════════════════════════════════
    with left_col:

        # ── AURA Identity ─────────────────────────────────────
        st.markdown(f"""
        <div style="padding:10px 0 8px;">
            <div style="font-size:26px;letter-spacing:4px;color:#FFB000;
                        animation:glitch 6s infinite;
                        text-shadow:2px 0 #FF6600,-2px 0 #FFB000,0 0 18px rgba(255,176,0,0.7);">
                {ai_name}
            </div>
            <div style="font-size:11px;opacity:.45;letter-spacing:2px;margin-top:3px;">
                {get_greeting()}, {uname}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── System Stats ──────────────────────────────────────
        # psutil gives real CPU/RAM/Disk — not fake numbers.
        st.markdown("""
        <div style="font-size:10px;opacity:.4;letter-spacing:2px;margin-bottom:6px;">
            ⚙ System Stats
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:12px;line-height:2.2;">
            <div style="margin-bottom:5px;">
                <div style="font-size:9px;opacity:.35;letter-spacing:1px;">CPU Usage</div>
                <div style="height:3px;background:#4a2400;margin-bottom:2px;">
                    <div style="height:100%;width:{stats['cpu']}%;background:#FFB000;box-shadow:0 0 6px #FFB000;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;opacity:.65;">
                    <span>CPU</span><span>{stats['cpu']}%</span>
                </div>
            </div>
            <div style="margin-bottom:5px;">
                <div style="font-size:9px;opacity:.35;letter-spacing:1px;">RAM Usage</div>
                <div style="height:3px;background:#4a2400;margin-bottom:2px;">
                    <div style="height:100%;width:{stats['ram']}%;background:#FFB000;box-shadow:0 0 6px #FFB000;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;opacity:.65;">
                    <span>Memory</span><span>{stats['ram']}%</span>
                </div>
            </div>
            <div>
                <div style="font-size:9px;opacity:.35;letter-spacing:1px;">Disk</div>
                <div style="height:3px;background:#4a2400;margin-bottom:2px;">
                    <div style="height:100%;width:{stats['disk']}%;background:#FFB000;box-shadow:0 0 6px #FFB000;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;opacity:.65;">
                    <span>Storage</span><span>{stats['disk']}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Weather ───────────────────────────────────────────
        st.markdown("""
        <div style="font-size:10px;opacity:.4;letter-spacing:2px;margin-bottom:6px;">
            🌤 Weather
        </div>""", unsafe_allow_html=True)

        if wx["success"]:
            st.markdown(f"""
            <div style="font-size:32px;color:#FFB000;text-shadow:0 0 12px #FFB000;line-height:1;">
                {wx_temp}
            </div>
            <div style="font-size:10px;opacity:.35;letter-spacing:2px;margin:3px 0 7px;">
                {wx_city} — {wx_cond}
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;">
                <div><div style="font-size:8px;opacity:.3;letter-spacing:1px;">Humidity</div>
                     <div style="font-size:13px;">{wx_hum}</div></div>
                <div><div style="font-size:8px;opacity:.3;letter-spacing:1px;">Wind</div>
                     <div style="font-size:13px;">{wx_wind}</div></div>
                <div><div style="font-size:8px;opacity:.3;letter-spacing:1px;">Feels</div>
                     <div style="font-size:13px;">{wx_feels}</div></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='opacity:.3;font-size:13px;'>Weather Unavailable</div>",
                        unsafe_allow_html=True)

        st.divider()

        # ── Today's Plans ─────────────────────────────────────
        # Each plan has a real checkbox — clicking it calls
        # mark_plan_done() in the DB then reruns the page.
        # WHY rerun()? Streamlit needs to regenerate the HTML
        # with the updated checkbox state.
        st.markdown("""
        <div style="font-size:10px;opacity:.4;letter-spacing:2px;margin-bottom:6px;">
            📋 Today's Plans
        </div>""", unsafe_allow_html=True)

        if plans:
            for plan in plans:
                safe_plan_text = html_lib.escape(plan["plan_text"])
                c1, c2, c3 = st.columns([0.10, 0.75, 0.15])
                with c1:
                    checked = st.checkbox(
                        "done",
                        value=bool(plan["is_done"]),
                        key=f"plan_{plan['id']}",
                        label_visibility="collapsed",
                    )
                    # Toggle done ↔ undone on every state change
                    if checked != bool(plan["is_done"]):
                        brain.memory.db.toggle_plan_done(plan["id"], user_id)
                        st.rerun()
                with c2:
                    if plan["is_done"]:
                        st.markdown(
                            f"<div style='font-size:12px;opacity:.2;"
                            f"text-decoration:line-through;padding-top:4px;'>"
                            f"{safe_plan_text}</div>",
                            unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"<div style='font-size:12px;padding-top:4px;'>"
                            f"▸ {safe_plan_text}</div>",
                            unsafe_allow_html=True)
                with c3:
                    if st.button("✕", key=f"del_plan_{plan['id']}"):
                        brain.memory.db.delete_plan(plan["id"], user_id)
                        st.rerun()
        else:
            st.markdown("<div style='opacity:.3;font-size:12px;'>No missions assigned.</div>",
                        unsafe_allow_html=True)

        # ── Task Completion Progress Bar ──────────────────────
        # When all tasks are done → show 100% celebration.
        # The amber bar grows as tasks are checked off.
        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        if total_count > 0:
            bar_color  = "#00FF41" if all_done else "#FFB000"
            bar_shadow = f"0 0 10px {'#00FF41' if all_done else '#FFB000'}"
            label      = "✅ 100% — All Missions Complete!" if all_done else f"{done_count}/{total_count} Complete — {task_pct}%"

            st.markdown(f"""
            <div style="height:3px;background:#4a2400;margin-bottom:4px;">
                <div style="height:100%;width:{task_pct}%;
                            background:{bar_color};
                            box-shadow:{bar_shadow};
                            transition:width 0.4s ease;">
                </div>
            </div>
            <div style="font-size:11px;
                        color:{bar_color};
                        letter-spacing:1px;
                        opacity:.85;">
                {label}
            </div>
            """, unsafe_allow_html=True)

            # Celebration banner when 100% complete
            if all_done:
                st.markdown("""
                <div style="margin-top:8px;padding:7px 10px;
                            border:1px solid #00FF41;background:rgba(0,255,65,0.05);
                            font-size:13px;color:#00FF41;letter-spacing:2px;
                            text-shadow:0 0 8px #00FF41;text-align:center;">
                    ✓ Mission Accomplished!
                </div>
                """, unsafe_allow_html=True)

        # ── Add New Task ──────────────────────────────────────
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        with st.form("add_task", clear_on_submit=True):
            new_task = st.text_input("objective", placeholder="Add new objective...",
                                     label_visibility="collapsed")
            if st.form_submit_button("+ Add Objective", use_container_width=True):
                if new_task.strip():
                    brain.memory.db.add_plan(user_id, new_task.strip())
                    st.rerun()

        st.divider()

        # ── Long-Term Goals ───────────────────────────────────
        st.markdown("""
        <div style="font-size:10px;opacity:.4;letter-spacing:2px;margin-bottom:6px;">
            🎯 Long-Term Goals
        </div>""", unsafe_allow_html=True)

        goals_list = brain.memory.db.get_active_goals(user_id)
        if goals_list:
            for goal in goals_list:
                safe_goal = html_lib.escape(goal["goal_text"])
                deadline_txt = html_lib.escape(f" [{goal['deadline']}]") if goal.get("deadline") else ""
                g1, g2 = st.columns([0.82, 0.18])
                with g1:
                    st.markdown(
                        f"<div style='font-size:12px;padding:3px 0;'>"
                        f"◈ {safe_goal}"
                        f"<span style='opacity:.3;font-size:10px;'>{deadline_txt}</span>"
                        f"</div>",
                        unsafe_allow_html=True)
                with g2:
                    if st.button("✕", key=f"del_goal_{goal['id']}"):
                        brain.memory.db.delete_goal(goal["id"], user_id)
                        st.rerun()
        else:
            st.markdown(
                "<div style='opacity:.3;font-size:12px;'>No long-term goals set.</div>",
                unsafe_allow_html=True)

        with st.form("add_goal_form", clear_on_submit=True):
            new_goal = st.text_input("goal", placeholder="Add long-term goal...",
                                     label_visibility="collapsed")
            if st.form_submit_button("+ Add Goal", use_container_width=True):
                if new_goal.strip():
                    brain.memory.db.add_goal(user_id, new_goal.strip(), None)
                    st.rerun()

        st.divider()

        # ── Settings ──────────────────────────────────────────
        with st.expander("⚙ Settings"):
            with st.form("settings_form", clear_on_submit=False):
                new_ai_name = st.text_input(
                    "AI Companion Name",
                    value=user["ai_name"],
                    placeholder="Name your AI...",
                )
                saved = st.form_submit_button("Save", use_container_width=True)
                if saved:
                    name_val = new_ai_name.strip()
                    if name_val:
                        db.update_ai_name(user_id, name_val)
                        st.session_state.user["ai_name"] = name_val
                        st.rerun()

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # ── Action Buttons ────────────────────────────────────
        if st.button("📊 Weekly Report", use_container_width=True, key="btn_report"):
            st.session_state.show_report = not st.session_state.show_report
            st.rerun()

        if st.session_state.show_report:
            report = brain.memory.get_weekly_report()
            st.info(report)

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        if st.button("🗑 Clear Chat", use_container_width=True, key="btn_clear"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        if st.button("⏻ Logout", use_container_width=True, key="btn_logout"):
            logout(); st.rerun()

    # ══════════════════════════════════════════════════════════
    # CENTER COLUMN — Animated Orb + Mode Switcher
    #
    # The orb is the ONLY thing that needs components.html().
    # It never needs to send data back to Python — it just draws.
    # Mode buttons are BELOW the component as real st.buttons.
    # ══════════════════════════════════════════════════════════
    with center_col:

        # ── Canvas Orb ────────────────────────────────────────
        # Full amber orb with:
        #   1. Outer particle cloud (140 particles in a tilted torus)
        #   2. 3 concentric rotating rings with tick marks
        #   3. Geodesic wireframe sphere (lat/lon + triangle grid)
        #   4. Pulsing center glow dot
        # requestAnimationFrame drives 60fps animation.
        components.html("""
<!DOCTYPE html><html>
<head>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{
    background:#080300;
    display:flex;flex-direction:column;
    align-items:center;justify-content:center;
    height:340px;overflow:hidden;
    font-family:'VT323',monospace;
}
body::before{
    content:'';position:fixed;inset:0;
    background:repeating-linear-gradient(to bottom,transparent 0,transparent 3px,rgba(0,0,0,0.1) 3px,rgba(0,0,0,0.1) 4px);
    pointer-events:none;z-index:9;
}
.label{
    font-size:10px;color:#FFB000;opacity:.28;
    letter-spacing:5px;margin-bottom:14px;
    text-transform:uppercase;
}
.status{
    font-size:13px;color:#FFB000;opacity:.4;
    letter-spacing:4px;margin-top:14px;
    text-transform:uppercase;
    animation:blink 2.8s infinite;
}
@keyframes blink{0%,100%{opacity:.4;}50%{opacity:.1;}}
</style>
</head>
<body>
<div class="label">AI Engine Active</div>
<canvas id="orb" width="320" height="320"></canvas>
<div class="status" id="st">Standby — Awaiting Input_</div>

<script>
// ── Canvas Setup ────────────────────────────────────────────
const canvas = document.getElementById('orb');
const ctx    = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const cx = W/2, cy = H/2;
let t = 0;

// ── Particles ────────────────────────────────────────────────
// 140 dots orbiting in a tilted torus around the orb.
// ry = rx * 0.30 gives the 3D elliptical orbit look.
// Each particle has random speed, size, and wobble phase
// so the cloud looks organic, not mechanical.
const NPART = 140;
const parts = Array.from({length:NPART}, () => ({
    a:   Math.random() * Math.PI * 2,
    r:   106 + Math.random() * 42,
    spd: (0.0018 + Math.random() * 0.0042) * (Math.random()<0.5?1:-1),
    sz:  0.4 + Math.random() * 2.0,
    wb:  Math.random() * Math.PI * 2,
    ws:  0.007 + Math.random() * 0.016,
    op:  0.10 + Math.random() * 0.58,
}));

// ── Mechanical Rings ─────────────────────────────────────────
// 3 rings rotating at different speeds and directions.
// segs = number of tick marks (like a radar/instrument dial).
const RINGS = [
    {r:94,  spd: 0.0028, segs:44, slen:5},
    {r:77,  spd:-0.005,  segs:30, slen:6},
    {r:60,  spd: 0.0085, segs:22, slen:7},
];
const ringA = [0, 0, 0];

function frame() {
    ctx.clearRect(0, 0, W, H);

    // 1. Background halo — soft radial glow behind everything
    const halo = ctx.createRadialGradient(cx,cy,52,cx,cy,140);
    halo.addColorStop(0,   'rgba(255,176,0,0.08)');
    halo.addColorStop(0.6, 'rgba(255,120,0,0.03)');
    halo.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.fillStyle = halo; ctx.fillRect(0,0,W,H);

    // 2. Particle cloud
    parts.forEach(p => {
        p.a  += p.spd;
        p.wb += p.ws;
        const px = cx + Math.cos(p.a) * p.r;
        const py = cy + Math.sin(p.a) * p.r * 0.30 + Math.sin(p.wb) * 20;
        // Particles behind the center axis are dimmer (depth illusion)
        const da = 1 - Math.abs(Math.sin(p.a)) * 0.38;
        ctx.beginPath();
        ctx.arc(px, py, p.sz, 0, Math.PI*2);
        ctx.fillStyle = `rgba(255,176,0,${p.op * da})`;
        ctx.fill();
    });

    // 3. Rotating mechanical rings + tick marks
    RINGS.forEach((ring, i) => {
        ringA[i] += ring.spd;
        const a = ringA[i];

        ctx.beginPath();
        ctx.arc(cx, cy, ring.r, 0, Math.PI*2);
        ctx.strokeStyle = `rgba(255,176,0,${0.09 + i*0.07})`;
        ctx.lineWidth = 1.0; ctx.stroke();

        for(let s=0; s<ring.segs; s++) {
            const sa = a + (s/ring.segs)*Math.PI*2;
            ctx.beginPath();
            ctx.moveTo(cx+Math.cos(sa)*(ring.r-ring.slen), cy+Math.sin(sa)*(ring.r-ring.slen));
            ctx.lineTo(cx+Math.cos(sa)*ring.r,              cy+Math.sin(sa)*ring.r);
            ctx.strokeStyle = `rgba(255,176,0,${0.20+i*0.10})`;
            ctx.lineWidth = 0.9; ctx.stroke();
        }
    });

    // 4. Geodesic sphere core
    const CR    = 46;
    const pulse = 0.5 + 0.5*Math.sin(t*0.038);

    // Core sphere fill — radial gradient for 3D depth feel
    const fill = ctx.createRadialGradient(cx-13,cy-13,2, cx,cy,CR);
    fill.addColorStop(0,   'rgba(255,215,80,0.52)');
    fill.addColorStop(0.5, 'rgba(255,176,0,0.22)');
    fill.addColorStop(1,   'rgba(255,90,0,0.04)');
    ctx.beginPath(); ctx.arc(cx,cy,CR,0,Math.PI*2);
    ctx.fillStyle = fill; ctx.fill();

    // Core border with pulsing amber glow
    ctx.beginPath(); ctx.arc(cx,cy,CR,0,Math.PI*2);
    ctx.strokeStyle = `rgba(255,176,0,${0.65+pulse*0.30})`;
    ctx.lineWidth = 2.0;
    ctx.shadowColor = '#FFB000'; ctx.shadowBlur = 12+pulse*18;
    ctx.stroke(); ctx.shadowBlur = 0;

    // Latitude ellipses (horizontal rings on the sphere surface)
    [[CR,0.52],[CR*0.82,0.40],[CR*0.52,0.26]].forEach(([rx,op]) => {
        ctx.beginPath(); ctx.ellipse(cx,cy,rx,rx*0.30,0,0,Math.PI*2);
        ctx.strokeStyle=`rgba(255,176,0,${op})`; ctx.lineWidth=0.55; ctx.stroke();
    });

    // Longitude ellipses (vertical rings on the sphere surface)
    [[CR,0.52],[CR*0.76,0.34],[CR*0.44,0.20]].forEach(([ry,op]) => {
        ctx.beginPath(); ctx.ellipse(cx,cy,ry*0.30,ry,0,0,Math.PI*2);
        ctx.strokeStyle=`rgba(255,176,0,${op})`; ctx.lineWidth=0.55; ctx.stroke();
    });

    // Main triangle lines (geodesic structure)
    const tp = [
        [cx,       cy-CR],
        [cx-CR*0.866, cy+CR*0.5],
        [cx+CR*0.866, cy+CR*0.5],
    ];
    ctx.strokeStyle='rgba(255,176,0,0.24)'; ctx.lineWidth=0.55;
    ctx.beginPath();
    ctx.moveTo(...tp[0]); ctx.lineTo(...tp[1]);
    ctx.moveTo(...tp[1]); ctx.lineTo(...tp[2]);
    ctx.moveTo(...tp[2]); ctx.lineTo(...tp[0]);
    ctx.moveTo(cx,cy-CR); ctx.lineTo(cx,cy+CR);
    ctx.moveTo(cx-CR,cy); ctx.lineTo(cx+CR,cy);
    ctx.stroke();

    // Sub-triangles — denser geodesic mesh
    const m01 = [(tp[0][0]+tp[1][0])/2,(tp[0][1]+tp[1][1])/2];
    const m12 = [(tp[1][0]+tp[2][0])/2,(tp[1][1]+tp[2][1])/2];
    const m20 = [(tp[2][0]+tp[0][0])/2,(tp[2][1]+tp[0][1])/2];
    ctx.strokeStyle='rgba(255,176,0,0.13)'; ctx.lineWidth=0.4;
    ctx.beginPath();
    ctx.moveTo(...m01); ctx.lineTo(...m12);
    ctx.moveTo(...m12); ctx.lineTo(...m20);
    ctx.moveTo(...m20); ctx.lineTo(...m01);
    ctx.stroke();

    // 5. Center glow dot
    const cg = ctx.createRadialGradient(cx,cy,0,cx,cy,14);
    cg.addColorStop(0,   'rgba(255,245,100,1)');
    cg.addColorStop(0.4, 'rgba(255,176,0,0.85)');
    cg.addColorStop(1,   'rgba(255,176,0,0)');
    ctx.beginPath(); ctx.arc(cx,cy,14,0,Math.PI*2);
    ctx.fillStyle=cg; ctx.fill();
    ctx.beginPath(); ctx.arc(cx,cy,3.5,0,Math.PI*2);
    ctx.fillStyle='#FFFFFF'; ctx.fill();

    t++;
    requestAnimationFrame(frame);
}
frame();
</script>
</body></html>
        """, height=380, scrolling=False)

        # ── Mode Switcher ─────────────────────────────────────
        # REAL Streamlit buttons — these actually work.
        # WHY not inside the canvas HTML?
        # Because components.html() is an iframe — clicks inside
        # it cannot reach Python. These buttons live in Python-land.
        # We style them to look like the preview mode buttons.

        new_mode = st.radio(
            "mode",
            ["Personal", "Pro", "Hybrid"],
            index=["Personal", "Pro", "Hybrid"].index(mode),
            horizontal=True,
            label_visibility="collapsed",
            key="mode_radio",
        )
        if new_mode != mode:
            st.session_state.mode = new_mode
            st.rerun()

        # Mode description only — clean, no extra panels
        MODE_DESC = {
            "Personal": "Warm · Caring · Friend",
            "Pro":      "Sharp · Focused · Efficient",
            "Hybrid":   "Balanced · Warm + Direct",
        }
        st.markdown(f"""
        <div style="text-align:center;font-size:11px;opacity:.3;
                    letter-spacing:2px;margin-top:6px;">
            {MODE_DESC[mode]}
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # RIGHT COLUMN — Chat
    # ══════════════════════════════════════════════════════════
    with right_col:
        # Chat header
        st.markdown(f"""
        <div style="padding:10px 0 8px;border-bottom:1px solid rgba(255,176,0,0.15);
                    margin-bottom:10px;">
            <div style="font-size:14px;letter-spacing:3px;">Conversation</div>
            <div style="font-size:9px;opacity:.3;letter-spacing:2px;margin-top:2px;">
                {ai_name} — {uname}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chat Message History ──────────────────────────────
        # Rendered as styled HTML blocks.
        # WHY not st.chat_message()? We need full control over
        # the look — Share Tech Mono font, no text-transform,
        # green left border for AI, amber for user.
        chat_container = st.container(height=450)

        with chat_container:
            if not st.session_state.messages:
                st.markdown(f"""
                <div style="padding:9px 11px;border:1px solid rgba(255,176,0,0.18);
                            border-left:2px solid #00FF41;background:#0c0400;
                            margin-bottom:8px;max-width:95%;">
                    <div style="font-size:9px;opacity:.3;letter-spacing:2px;
                                margin-bottom:3px;text-transform:uppercase;">
                        &gt; {ai_name}
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:13px;
                                color:#FFB000;text-transform:none;line-height:1.55;">
                        {get_greeting()}, {uname}. All systems online. How can I help you today?
                    </div>
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.messages:
                safe_content = html_lib.escape(msg["content"]).replace("\n", "<br>")
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="padding:9px 11px;border:1px solid rgba(255,176,0,0.18);
                                border-left:2px solid #FFB000;
                                background:rgba(255,176,0,0.04);
                                margin-bottom:8px;margin-left:8px;max-width:95%;">
                        <div style="font-size:9px;opacity:.3;letter-spacing:2px;
                                    margin-bottom:3px;text-transform:uppercase;">
                            Operator &gt;
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:13px;
                                    color:#FFB000;text-transform:none;line-height:1.55;">
                            {safe_content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="padding:9px 11px;border:1px solid rgba(255,176,0,0.18);
                                border-left:2px solid #00FF41;background:#0c0400;
                                margin-bottom:8px;max-width:95%;">
                        <div style="font-size:9px;opacity:.3;letter-spacing:2px;
                                    margin-bottom:3px;text-transform:uppercase;">
                            &gt; {html_lib.escape(ai_name)}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:13px;
                                    color:#FFB000;text-transform:none;line-height:1.55;">
                            {safe_content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Chat Input ────────────────────────────────────────
        # st.chat_input() is a native Streamlit widget.
        # It sits at the bottom of the right column.
        # On submit → add to messages → brain.think() → rerun.
        user_input = st.chat_input(f"Transmit to {ai_name}...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner(""):
                reply = brain.think(user_input, mode=mode)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
