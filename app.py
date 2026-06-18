"""
app.py — KidsCreate AI home page
FIX: sys.path.append moved BEFORE set_page_config (critical ordering fix)
FIX: st.switch_page requires Streamlit >= 1.36 — pinned in requirements.txt
"""
import sys
import os

# MUST be first — path resolution before any streamlit calls
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="KidsCreate AI 🪄",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🪄 KidsCreate AI</div>
  <div class="hero-sub">Say a word · Watch magic appear · Track every milestone</div>
  <div>
    <span class="hero-pill">🎨 Voice to Art</span>
    <span class="hero-pill">🧠 Brain Tracker</span>
    <span class="hero-pill">💯 100% Free</span>
    <span class="hero-pill">🔑 No Credit Card</span>
    <span class="hero-pill">🎁 5 Credits/Day</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Nav cards ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="kc-card" style="border-color:#FFD93D;border-width:2px;">
      <div style="font-size:2.4rem;margin-bottom:10px">🎨</div>
      <div class="kc-card-title" style="font-size:1.35rem">Kid Zone</div>
      <p style="color:#666;font-size:0.9rem;line-height:1.6;margin:8px 0 18px">
        Say <b>"Humpty Dumpty"</b> and watch it become beautiful art!<br>
        Type or speak — AI creates it instantly.
      </p>
      <div style="display:flex;gap:6px;flex-wrap:wrap;">
        <span style="background:#fff8e1;color:#e67e22;padding:3px 10px;border-radius:50px;font-size:0.78rem;font-weight:700">🖍️ 5 Art Styles</span>
        <span style="background:#fff8e1;color:#e67e22;padding:3px 10px;border-radius:50px;font-size:0.78rem;font-weight:700">🎤 Voice Input</span>
        <span style="background:#fff8e1;color:#e67e22;padding:3px 10px;border-radius:50px;font-size:0.78rem;font-weight:700">💾 Download Art</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎨 Open Kid Zone →", type="primary", use_container_width=True):
        st.switch_page("pages/kid_zone.py")

with col2:
    st.markdown("""
    <div class="kc-card" style="border-color:#6BCB77;border-width:2px;">
      <div style="font-size:2.4rem;margin-bottom:10px">👶</div>
      <div class="kc-card-title" style="font-size:1.35rem">Parent Portal</div>
      <p style="color:#666;font-size:0.9rem;line-height:1.6;margin:8px 0 18px">
        Upload photos &amp; videos of your toddler.<br>
        Track brain &amp; body milestones. Get free AI insights.
      </p>
      <div style="display:flex;gap:6px;flex-wrap:wrap;">
        <span style="background:#f0fff4;color:#27ae60;padding:3px 10px;border-radius:50px;font-size:0.78rem;font-weight:700">🧠 Milestone Tracker</span>
        <span style="background:#f0fff4;color:#27ae60;padding:3px 10px;border-radius:50px;font-size:0.78rem;font-weight:700">📸 Photo Upload</span>
        <span style="background:#f0fff4;color:#27ae60;padding:3px 10px;border-radius:50px;font-size:0.78rem;font-weight:700">🤖 Free AI Insights</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👶 Open Parent Portal →", use_container_width=True):
        st.switch_page("pages/parent_portal.py")

# ── Free API callout ──────────────────────────────────────────────────────────
st.markdown('<div class="kc-divider">Powered entirely by free APIs — zero cost</div>', unsafe_allow_html=True)

api_cols = st.columns(3)
for col, icon, name, desc in zip(api_cols, [
    ("🖼️", "Pollinations.ai",  "Image generation\nNo key · No limits"),
    ("🤖", "Gemini 1.5 Flash", "AI insights (optional free key)\n15 req/min · 1M tokens/day"),
    ("🎤", "Web Speech API",   "Voice recognition\nBuilt into Chrome/Edge"),
]):
    with col:
        st.markdown(f"""
        <div class="how-card">
          <div class="how-icon">{icon}</div>
          <div class="how-title">{name}</div>
          <div class="how-desc">{desc.replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)
"""
pages/kid_zone.py — Kid Zone: word/voice → Pollinations.ai art (100% free)

FIXES vs previous version:
- ASCII filename (no emoji) — safe on Windows git, Linux CI, all runners
- sys.path BEFORE set_page_config
- hash() replaced with deterministic hashlib seed
- voice component carries its own CSS (sandboxed iframe cannot inherit GLOBAL_CSS)
- Pollinations timeout: credit NOT consumed on network failure
- Style buttons use st.radio() to avoid session_state/rerun conflict
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import urllib.parse

import requests
import streamlit as st
import streamlit.components.v1 as components

from utils.quota import render_credit_bar, consume
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Kid Zone 🎨", page_icon="🎨", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
ART_STYLES = {
    "🖍️ Crayon":     "crayon drawing thick colorful lines children artwork bright happy",
    "🎨 Watercolor": "soft watercolor storybook illustration children book gentle pastel",
    "🧸 Toy 3D":     "cute 3D clay render Pixar style toy adorable colorful chibi",
    "📚 Storybook":  "vintage children storybook illustration warm golden whimsical fairy tale",
    "⚡ Bold Toon":  "bold cartoon thick black outlines flat bright colors pop art fun",
}
STYLE_NAMES = list(ART_STYLES.keys())

EXAMPLES = [
    ("🥚", "Humpty Dumpty"),
    ("🐉", "Friendly Dragon"),
    ("🌈", "Rainbow Elephant"),
    ("🦄", "Unicorn Princess"),
    ("🚀", "Space Bunny"),
    ("🐬", "Dancing Dolphin"),
]

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"


def make_image_url(word: str, style_key: str) -> str:
    """Build a deterministic Pollinations URL. Uses hashlib for stable seed."""
    style_mod = ART_STYLES[style_key]
    prompt = (
        f"{word}, {style_mod}, designed for toddlers and young children, "
        "extremely cute friendly safe wholesome, bright saturated colors, "
        "white background, no text no watermark, square composition"
    )
    encoded = urllib.parse.quote(prompt)
    # Deterministic seed: same word → same image (reproducible, not random)
    seed = int(hashlib.md5(f"{word}{style_key}".encode()).hexdigest(), 16) % 99999
    return f"{POLLINATIONS_BASE}/{encoded}?width=768&height=768&model=flux&nologo=true&seed={seed}"


def fetch_image(url: str):
    """Fetch image bytes. Returns None on failure — caller decides whether to show error."""
    try:
        r = requests.get(url, timeout=35)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException:
        pass
    return None


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="pg-header">
  <span class="pg-icon">🎨</span>
  <div>
    <div class="pg-title">Kid Zone</div>
    <div class="pg-desc">Say a word → magical art appears · Free via Pollinations.ai · No API key needed</div>
  </div>
</div>
""", unsafe_allow_html=True)

has_credits = render_credit_bar()

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    # ── Quick picks ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="kc-card">
      <div class="kc-card-title">✨ Quick picks</div>
      <div class="kc-card-sub">Tap any character to try it instantly</div>
    </div>
    """, unsafe_allow_html=True)

    ex_cols = st.columns(3)
    for i, (emoji, word) in enumerate(EXAMPLES):
        with ex_cols[i % 3]:
            if st.button(f"{emoji} {word}", key=f"ex_{i}", use_container_width=True):
                st.session_state["kid_word"] = word
                st.rerun()

    # ── Text input ────────────────────────────────────────────────────────────
    kid_word = st.text_input(
        "Or type any word:",
        value=st.session_state.get("kid_word", ""),
        placeholder="e.g. Humpty Dumpty, Fire Truck, Baby Panda...",
        max_chars=60,
    )
    # Sync back — only update if changed to avoid infinite rerun
    if kid_word != st.session_state.get("kid_word", ""):
        st.session_state["kid_word"] = kid_word

    # ── Voice widget — fully self-contained CSS (iframe sandbox) ─────────────
    st.markdown('<div class="kc-divider">Use your voice 🎤</div>', unsafe_allow_html=True)

    # NOTE: components.html() runs in a sandboxed iframe.
    # GLOBAL_CSS does NOT apply here — all styles are inline below.
    voice_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Nunito', sans-serif; background: transparent; }
  #voiceBtn {
    width: 100%; padding: 11px 0; font-size: 1rem; font-weight: 800;
    color: #fff; border: none; border-radius: 50px; cursor: pointer;
    background: linear-gradient(135deg, #FF6B6B, #FF9E53);
    box-shadow: 0 4px 14px rgba(255,107,107,0.4);
    transition: all 0.18s;
  }
  #voiceBtn:hover { transform: translateY(-1px); }
  #voiceBtn.listening { background: #e74c3c; }
  #status {
    margin-top: 9px; font-size: 0.85rem; color: #888;
    font-weight: 700; min-height: 20px; text-align: center;
  }
  #waveRow {
    display: none; justify-content: center; gap: 4px;
    align-items: center; margin: 9px 0;
  }
  .bar {
    width: 5px; height: 18px; background: #FF6B6B; border-radius: 3px;
    animation: wave 0.9s ease-in-out infinite;
  }
  .bar:nth-child(2) { animation-delay: .15s; }
  .bar:nth-child(3) { animation-delay: .30s; }
  .bar:nth-child(4) { animation-delay: .45s; }
  .bar:nth-child(5) { animation-delay: .60s; }
  @keyframes wave {
    0%,100% { transform: scaleY(1); }
    50%      { transform: scaleY(2.4); }
  }
  #resultBox {
    display: none; margin-top: 8px; width: 100%;
    padding: 9px 13px; border-radius: 12px;
    border: 2px solid #ecddd0; font-size: 1rem;
    font-family: 'Nunito', sans-serif; font-weight: 800;
    color: #333; background: #fff8f0;
  }
  #useBtn {
    display: none; margin-top: 7px; width: 100%;
    padding: 9px; border: none; border-radius: 50px;
    background: #6BCB77; color: #fff;
    font-size: 0.9rem; font-weight: 800; cursor: pointer;
  }
</style>
</head>
<body>
  <button id="voiceBtn" onclick="startVoice()">🎤 Tap to Speak</button>
  <div id="status">Works in Chrome &amp; Edge</div>
  <div id="waveRow">
    <div class="bar"></div><div class="bar"></div><div class="bar"></div>
    <div class="bar"></div><div class="bar"></div>
  </div>
  <input id="resultBox" readonly placeholder="Your word appears here..." />
  <button id="useBtn" onclick="copyWord()">✅ Copy word ↑ then paste above</button>

<script>
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
function startVoice() {
  if (!SR) {
    document.getElementById('status').textContent =
      '❌ Not supported. Use Chrome or Edge.';
    return;
  }
  const rec = new SR();
  rec.lang = 'en-IN';
  rec.interimResults = false;
  rec.maxAlternatives = 1;

  const btn = document.getElementById('voiceBtn');
  const waves = document.getElementById('waveRow');
  const status = document.getElementById('status');

  btn.textContent = '🔴 Listening...';
  btn.classList.add('listening');
  waves.style.display = 'flex';
  status.textContent = 'Speak now...';
  rec.start();

  rec.onresult = (e) => {
    const word = e.results[0][0].transcript;
    document.getElementById('resultBox').value = word;
    document.getElementById('resultBox').style.display = 'block';
    document.getElementById('useBtn').style.display = 'block';
    status.innerHTML = '✅ Heard: <b style="color:#FF6B6B">' + word + '</b> — copy &amp; paste above ↑';
    btn.textContent = '🎤 Tap to Speak';
    btn.classList.remove('listening');
    waves.style.display = 'none';
  };
  rec.onerror = () => {
    status.textContent = '⚠️ Could not hear. Try again.';
    btn.textContent = '🎤 Tap to Speak';
    btn.classList.remove('listening');
    waves.style.display = 'none';
  };
}
function copyWord() {
  const txt = document.getElementById('resultBox').value;
  navigator.clipboard.writeText(txt).then(() => {
    document.getElementById('status').textContent = '📋 Copied! Now paste into the text box above ↑';
  });
}
</script>
</body>
</html>
"""
    components.html(voice_html, height=215, scrolling=False)

    # ── Style picker — st.radio avoids button/session_state conflict ──────────
    st.markdown('<div class="kc-divider">Pick an art style</div>', unsafe_allow_html=True)
    selected_style = st.radio(
        "Art style",
        options=STYLE_NAMES,
        index=st.session_state.get("style_idx", 0),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["style_idx"] = STYLE_NAMES.index(selected_style)

    # ── Generate button ───────────────────────────────────────────────────────
    word_ready = bool(st.session_state.get("kid_word", "").strip())
    can_gen = has_credits and word_ready

    gen_label = (
        "✨ Create the Magic!"
        if can_gen
        else ("🔒 No Credits Left Today" if not has_credits else "👆 Type or pick a word first")
    )
    gen = st.button(gen_label, type="primary", use_container_width=True, disabled=not can_gen)

# ── Result panel ──────────────────────────────────────────────────────────────
with right:
    if "gen_url" in st.session_state and "gen_word" in st.session_state:
        st.image(
            st.session_state["gen_url"],
            caption=f"✨ {st.session_state['gen_word']} · {st.session_state.get('gen_style', '')}",
            use_container_width=True,
        )
        st.markdown("""
        <div class="kc-card" style="text-align:center;border-color:#FFD93D;border-width:2px;">
          <div class="kc-card-title">🎉 Awesome creation!</div>
          <div class="kc-card-sub">Download below or right-click the image to save</div>
        </div>
        """, unsafe_allow_html=True)

        dl1, dl2 = st.columns(2)
        with dl1:
            # Use cached bytes from generation if available, else re-fetch
            img_bytes = st.session_state.get("gen_bytes")
            if img_bytes:
                fname = st.session_state["gen_word"].replace(" ", "_") + "_art.png"
                st.download_button("💾 Save My Art", data=img_bytes,
                                   file_name=fname, mime="image/png",
                                   use_container_width=True)
        with dl2:
            if st.button("🔄 Create Another", use_container_width=True):
                for k in ["gen_url", "gen_word", "gen_style", "gen_bytes"]:
                    st.session_state.pop(k, None)
                st.rerun()
    else:
        st.markdown("""
        <div class="result-dark">
          <div class="result-empty-icon">🪄</div>
          <div class="result-empty-hint">Your magical art appears here!</div>
          <div class="result-empty-text">
            Try:<br>
            <b style="color:#FFD93D">🥚 Humpty Dumpty</b><br>
            <b style="color:#6BCB77">🐉 Friendly Dragon</b><br>
            <b style="color:#4D96FF">🦄 Unicorn Princess</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Generation logic — credit consumed ONLY on success ────────────────────────
if gen:
    current_word = st.session_state.get("kid_word", "").strip()
    if current_word and has_credits:
        img_url = make_image_url(current_word, selected_style)
        with st.spinner(f"🎨 Painting {current_word}... (10–25 sec)"):
            img_bytes = fetch_image(img_url)

        if img_bytes:
            # Consume credit ONLY after confirmed success
            if consume():
                st.session_state["gen_url"]   = img_url
                st.session_state["gen_word"]  = current_word
                st.session_state["gen_style"] = selected_style
                st.session_state["gen_bytes"] = img_bytes
                st.balloons()
                st.rerun()
        else:
            st.error(
                "⚠️ Pollinations.ai is slow right now — no credit used. "
                "Please try again in a moment."
            )

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="kc-divider" style="margin-top:28px">How it works</div>', unsafe_allow_html=True)
h1, h2, h3 = st.columns(3)
for col, icon, title, desc in [
    (h1, "🗣️", "Say or type", "Any character, animal, or thing your child loves"),
    (h2, "🎨", "Pick a style", "5 styles — crayon to watercolor to Pixar 3D"),
    (h3, "✨", "Magic!", "Pollinations AI creates beautiful art — free, always"),
]:
    with col:
        st.markdown(f"""
        <div class="how-card">
          <div class="how-icon">{icon}</div>
          <div class="how-title">{title}</div>
          <div class="how-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
"""
pages/parent_portal.py — Toddler milestone tracker + free Gemini AI insights

FIXES vs previous version:
- ASCII filename (no emoji) — safe on all OS and CI runners
- sys.path BEFORE set_page_config
- Removed unused 'json' import
- analyse button defined at column scope, used at module scope via session flag
- Image file pointer reset with seek(0) before base64 encode
- age_group read once after expander, not twice
- st.secrets used for GEMINI_API_KEY (Streamlit Cloud standard)
- smart_fallback uses local string concat, no chr(10) hack
- Gemini error surfaces cleanly with fallback
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
import re
from datetime import date

import requests
import streamlit as st

from utils.quota import render_credit_bar, consume
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Parent Portal 👶", page_icon="👶", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Gemini config (free tier — optional) ──────────────────────────────────────
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemini-1.5-flash:generateContent"
)

# ── Milestone data ─────────────────────────────────────────────────────────────
MILESTONES = {
    "0–6 months": {
        "color": "#FF9E53", "emoji": "🍼",
        "Motor":    ["Lifts head during tummy time", "Moves arms & legs equally",
                     "Brings hands to mouth", "Holds head steady when held upright"],
        "Social":   ["Social smile (by 6–8 weeks)", "Tracks parent's face",
                     "Coos & makes sounds", "Calms when held"],
        "Cognitive":["Tracks moving objects with eyes", "Responds to loud sounds",
                     "Shows curiosity", "Recognises familiar voices"],
        "Language": ["Startles to sounds", "Makes vowel sounds (ah, oh)",
                     "Quiets to familiar voice", "Cries differently for needs"],
    },
    "6–12 months": {
        "color": "#FFD93D", "emoji": "🧸",
        "Motor":    ["Sits without support (7–9 mo)", "Pulls to stand (9–12 mo)",
                     "Pincer grasp emerging", "Crawls or bottom-shuffles"],
        "Social":   ["Stranger anxiety appears", "Plays peek-a-boo",
                     "Waves bye-bye", "Shows objects to others"],
        "Cognitive":["Looks for hidden objects", "Bangs objects together",
                     "Explores with mouth and hands", "Cause-and-effect play"],
        "Language": ["Babbles (ba-ba, da-da)", "Responds to own name",
                     "Uses gestures", "Imitates sounds"],
    },
    "1–2 years": {
        "color": "#6BCB77", "emoji": "🚶",
        "Motor":    ["Walks independently (12–15 mo)", "Climbs on low furniture",
                     "Stacks 2–4 blocks", "Scribbles with crayon"],
        "Social":   ["Parallel play with peers", "Shows affection to caregivers",
                     "Imitates adult actions", "Hands objects to others"],
        "Cognitive":["Points to objects of interest", "Follows 1-step instructions",
                     "Simple shape sorting", "Pretend play starts"],
        "Language": ["First words (1–3 at 12 mo)", "Vocabulary grows to 50 words by 24 mo",
                     "2-word phrases by 24 mo", "Points to named body parts"],
    },
    "2–3 years": {
        "color": "#4D96FF", "emoji": "🏃",
        "Motor":    ["Runs and jumps", "Pedals tricycle",
                     "Turns pages one at a time", "Stacks 6+ blocks"],
        "Social":   ["Plays near other children", "Follows simple rules",
                     "Shows empathy", "Aware of own gender"],
        "Cognitive":["Sorts by colour and shape", "Completes 4–8 piece puzzles",
                     "Imaginative play", "Understands same vs different"],
        "Language": ["2–3 word sentences", "Names familiar objects",
                     "50% understood by strangers", "Asks what and where"],
    },
    "3–5 years": {
        "color": "#9B59B6", "emoji": "🌟",
        "Motor":    ["Hops on one foot", "Draws simple shapes",
                     "Uses scissors safely", "Dresses with minimal help"],
        "Social":   ["Cooperative play", "Takes turns in games",
                     "Wide emotion range", "Understands basic rules"],
        "Cognitive":["Counts to 10", "Names most colours",
                     "Understands yesterday/tomorrow", "Tells simple stories"],
        "Language": ["Full 4–5 word sentences", "Most speech understood by strangers",
                     "Asks why constantly", "Knows full name"],
    },
}

DOMAIN_COLORS = {"Motor": "#FF6B6B", "Social": "#4D96FF",
                 "Cognitive": "#9B59B6", "Language": "#6BCB77"}
DOMAIN_ICONS  = {"Motor": "🏃", "Social": "🤝", "Cognitive": "🧠", "Language": "🗣️"}


# ── Gemini call ────────────────────────────────────────────────────────────────
def call_gemini(prompt: str, image_b64: str = None, mime: str = "image/jpeg"):
    """Call Gemini 1.5 Flash free tier. Returns text or None on failure."""
    if not GEMINI_KEY:
        return None
    parts = []
    if image_b64:
        parts.append({"inlineData": {"mimeType": mime, "data": image_b64}})
    parts.append({"text": prompt})
    payload = {"contents": [{"parts": parts}]}
    try:
        r = requests.post(GEMINI_URL, json=payload,
                          params={"key": GEMINI_KEY}, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return None  # surface as fallback, not crash
    except Exception:
        return None


def smart_fallback(age_group: str, checked: list, question: str, child_name: str) -> str:
    """Rich rule-based insights when no Gemini key is present."""
    name = child_name or "your child"
    total = sum(len(v) for k, v in MILESTONES[age_group].items() if k not in ("color", "emoji"))
    pct = int(len(checked) / total * 100) if total else 0

    tips_map = {
        "0–6 months":  ["Tummy time 10–15 min/day builds neck strength",
                        "Talk and sing constantly — language wires the brain"],
        "6–12 months": ["Object permanence games (peekaboo) build memory",
                        "Offer safe finger foods to develop pincer grasp"],
        "1–2 years":   ["Read 2–3 picture books daily — fastest language booster",
                        "Let them help with simple tasks to build confidence"],
        "2–3 years":   ["Ask open questions: 'What happened?' not just yes/no",
                        "Playdates 2x/week accelerate social development"],
        "3–5 years":   ["Let them narrate drawings — builds language and imagination",
                        "Simple board games teach turn-taking and early maths"],
    }
    tips = tips_map.get(age_group, tips_map["1–2 years"])
    checked_str = "\n".join("  ✅ " + m for m in checked[:6]) if checked else "  (none recorded yet)"

    q_block = ""
    if question:
        q_lower = question.lower()
        if any(w in q_lower for w in ["normal", "typical", "okay", "ok"]):
            q_block = (
                "\n\n**Your question:** " + question +
                "\n> The milestones observed look typical for " + age_group +
                ". Every child develops at their own pace within a healthy range."
            )
        elif any(w in q_lower for w in ["worry", "concern", "red flag", "problem"]):
            q_block = (
                "\n\n**Your question:** " + question +
                "\n> Key signs to discuss with your pediatrician: regression in achieved skills, "
                "no social smile by 3 months, no babbling by 12 months, or loss of language. "
                "Your instinct matters — always consult your doctor if something feels different."
            )
        else:
            q_block = (
                "\n\n**Your question:** " + question +
                "\n> Great question. Consistent routines, responsive conversation, and safe "
                "exploration are the most impactful things at this stage. "
                "Bring this to your pediatrician at the next visit for personalised guidance."
            )

    return (
        "**Developmental Overview — " + name + " · " + age_group + "**\n\n"
        "**Progress snapshot:** " + str(pct) + "% of tracked milestones observed "
        "(" + str(len(checked)) + "/" + str(total) + ")\n\n"
        "**Milestones noted:**\n" + checked_str + "\n\n"
        "**What's going well 💚**\n"
        + ("Excellent progress! " if pct >= 70 else "Good start — keep observing! ")
        + "The milestones recorded show active, typical development for this stage.\n\n"
        "**Recommended activities 🌱**\n"
        "  · " + tips[0] + "\n"
        "  · " + tips[1] + "\n\n"
        "**When to consult your pediatrician 👩‍⚕️**\n"
        "Book a check if you notice regression in previously achieved milestones, "
        "significant language delays, or anything that gives you pause. "
        "Your parental instinct is always a valid reason to visit your doctor."
        + q_block +
        "\n\n---\n"
        "*Add a free GEMINI_API_KEY (aistudio.google.com) for AI photo analysis.*"
    )


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="pg-header">
  <span class="pg-icon">👶</span>
  <div>
    <div class="pg-title">Parent Portal</div>
    <div class="pg-desc">Track milestones · Upload moments · AI insights via Gemini 1.5 Flash (free)</div>
  </div>
</div>
""", unsafe_allow_html=True)

has_credits = render_credit_bar()

# ── Child profile ──────────────────────────────────────────────────────────────
with st.expander("👤 Child profile (optional)", expanded=not st.session_state.get("profile_saved")):
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        cname = st.text_input("Child's name", value=st.session_state.get("cname", ""),
                              placeholder="e.g. Trijal")
    with pc2:
        dob = st.date_input("Date of birth", value=None,
                            min_value=date(2019, 1, 1), max_value=date.today())
    with pc3:
        age_sel = st.selectbox("Age group", list(MILESTONES.keys()),
                               index=st.session_state.get("age_idx", 2))

    if dob:
        months = (date.today() - dob).days // 30
        yrs, mo = divmod(months, 12)
        label = (str(yrs) + "y " + str(mo) + "mo") if yrs else (str(months) + " months")
        st.markdown('<span class="age-badge">🎂 ' + label + " old</span>", unsafe_allow_html=True)

    if st.button("✅ Save Profile"):
        st.session_state["cname"]        = cname
        st.session_state["age_idx"]      = list(MILESTONES.keys()).index(age_sel)
        st.session_state["profile_saved"] = True
        st.rerun()

# Read age_group ONCE after expander closes — single source of truth
age_group = list(MILESTONES.keys())[st.session_state.get("age_idx", 2)]
cname     = st.session_state.get("cname", "") or "your child"
ms        = MILESTONES[age_group]

# ── Two-column layout ──────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

# ══ LEFT: Milestone tracker ════════════════════════════════════════════════════
with left_col:
    st.markdown(
        '<div class="kc-card" style="border-color:' + ms["color"] + ';border-width:2px;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<span style="font-size:2rem">' + ms["emoji"] + '</span>'
        '<div><div class="kc-card-title">Milestone Tracker</div>'
        '<div class="kc-card-sub">' + age_group + " · " + cname + "</div></div>"
        '<span class="age-badge" style="margin-left:auto;background:linear-gradient(135deg,'
        + ms["color"] + "," + ms["color"] + 'aa)">' + age_group + "</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    checked_all = []
    total_all   = 0

    for domain in ["Motor", "Social", "Cognitive", "Language"]:
        items    = ms[domain]
        total_all += len(items)
        d_color  = DOMAIN_COLORS[domain]
        d_icon   = DOMAIN_ICONS[domain]
        domain_checked = []

        with st.expander(d_icon + " " + domain, expanded=True):
            for item in items:
                k = "ms_" + age_group + "_" + domain + "_" + item
                if st.checkbox(item, key=k):
                    domain_checked.append(item)
                    checked_all.append(item)

            d_pct = int(len(domain_checked) / len(items) * 100) if items else 0
            st.markdown(
                '<div class="ms-bar-wrap">'
                '<div class="ms-bar-fill" style="width:' + str(d_pct) + "%;background:" + d_color + '"></div>'
                "</div>"
                '<div style="font-size:0.75rem;color:#bbb;font-weight:700">'
                + str(len(domain_checked)) + "/" + str(len(items)) + " · " + str(d_pct) + "%</div>",
                unsafe_allow_html=True,
            )

    # Overall progress
    pct = int(len(checked_all) / total_all * 100) if total_all else 0
    stars = "🌟🌟🌟" if pct >= 80 else ("⭐⭐" if pct >= 50 else "⭐")
    st.markdown(
        '<div class="kc-card" style="margin-top:6px;text-align:center;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
        '<span class="kc-card-title">Overall Progress</span>'
        '<span style="font-family:\'Baloo 2\',cursive;font-size:1.6rem;font-weight:800;color:'
        + ms["color"] + '">' + str(pct) + "% " + stars + "</span></div>"
        '<div class="ms-bar-wrap" style="height:14px">'
        '<div class="ms-bar-fill" style="width:' + str(pct) + "%;background:" + ms["color"] + '"></div>'
        "</div>"
        '<div style="margin-top:6px;font-size:0.8rem;color:#bbb;font-weight:600">'
        + str(len(checked_all)) + " of " + str(total_all) + " milestones — " + cname
        + "</div></div>",
        unsafe_allow_html=True,
    )

# ══ RIGHT: Upload + AI ════════════════════════════════════════════════════════
with right_col:
    st.markdown("""
    <div class="kc-card">
      <div class="kc-card-title">📤 Upload Toddler Moments</div>
      <div class="kc-card-sub">Photos or short videos — Gemini AI will analyse development</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-zone">
      📸 Photos &nbsp;|&nbsp; 🎥 Short videos<br>
      <span style="font-size:0.78rem;opacity:0.7">JPG · PNG · MP4 · MOV · max 50 MB</span>
    </div>
    """, unsafe_allow_html=True)

    media_files = st.file_uploader(
        "Upload files",
        type=["jpg", "jpeg", "png", "mp4", "mov"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if media_files:
        img_files = [f for f in media_files if f.type.startswith("image")]
        if img_files:
            prev_cols = st.columns(min(3, len(img_files)))
            for i, f in enumerate(img_files[:3]):
                with prev_cols[i]:
                    st.image(f, use_container_width=True, caption=f.name[:16])

    st.markdown('<div class="kc-divider">Ask about development</div>', unsafe_allow_html=True)

    question = st.text_area(
        "Your question",
        value=st.session_state.get("portal_q", ""),
        placeholder="e.g. Is eye contact normal? What helps language development?",
        height=85,
        label_visibility="collapsed",
    )
    st.session_state["portal_q"] = question

    # Quick question chips
    st.markdown("**Quick questions:**")
    qq_cols = st.columns(2)
    quick_qs = [
        "Is this development normal for the age?",
        "What activities boost brain development?",
        "Any red flags I should watch for?",
        "Tips to encourage language skills?",
    ]
    for i, qq in enumerate(quick_qs):
        with qq_cols[i % 2]:
            if st.button(qq, key="qq_" + str(i), use_container_width=True):
                st.session_state["portal_q"] = qq
                st.rerun()

    if not GEMINI_KEY:
        st.markdown("""
        <div style="background:#fffbe6;border:1.5px solid #FFD93D;border-radius:12px;
                    padding:12px 16px;margin:12px 0;font-size:0.84rem;color:#7a6000;font-weight:600;">
          🔑 <b>Optional free Gemini key</b> → enables AI photo analysis.<br>
          Get one free at <b>aistudio.google.com</b> (2 min, no card needed).<br>
          Set <code>GEMINI_API_KEY</code> in Streamlit Cloud → App Settings → Secrets.<br>
          <span style="opacity:0.7">App works fully without it — smart insights still provided.</span>
        </div>
        """, unsafe_allow_html=True)

    # FIX: button defined here, used via flag outside column scope
    analyse_disabled = not has_credits or (not media_files and not question.strip())
    if st.button(
        "🧠 Get AI Insights" if has_credits else "🔒 No Credits Left Today",
        type="primary",
        use_container_width=True,
        disabled=analyse_disabled,
        key="analyse_btn",
    ):
        st.session_state["run_analysis"] = True

    if not media_files and not question.strip() and has_credits:
        st.caption("Upload a photo or type a question to unlock insights.")

    # Show stored insight
    if "portal_insight" in st.session_state:
        body = st.session_state["portal_insight"]
        body_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", body)
        body_html = body_html.replace("\n", "<br>")
        st.markdown(
            '<div class="insight-wrap">'
            '<div class="insight-title">🧠 AI Developmental Insights · ' + cname + "</div>"
            '<div class="insight-body">' + body_html + "</div></div>",
            unsafe_allow_html=True,
        )
        st.caption("⚠️ Educational information only — not medical advice. Consult your pediatrician.")
        if st.button("🗑️ Clear insights", key="clear_ins"):
            del st.session_state["portal_insight"]
            st.rerun()

# ── Analysis runs outside column scope — no variable scoping issues ────────────
if st.session_state.pop("run_analysis", False) and has_credits:
    if consume():
        prompt = (
            "Child: " + cname + ", age group: " + age_group + ". "
            "Milestones observed: " + (", ".join(checked_all) if checked_all else "none") + ". "
            "Parent question: " + (st.session_state.get("portal_q") or "General check.") + "\n\n"
            "As a warm child development specialist provide:\n"
            "**Observations** (2–3 sentences)\n"
            "**What is going well** (2 encouraging points)\n"
            "**Recommended activities** (2 practical age-appropriate ideas)\n"
            "**When to consult pediatrician** (honest, not alarmist)\n\n"
            "Be warm, parent-friendly, specific. Educational only, not medical advice."
        )

        with st.spinner("🧠 Analysing..."):
            img_b64, img_mime = None, "image/jpeg"
            if media_files:
                img_files = [f for f in media_files if f.type.startswith("image")]
                if img_files:
                    f = img_files[0]
                    f.seek(0)                              # FIX: reset pointer before read
                    raw      = f.read()
                    img_b64  = base64.b64encode(raw).decode()
                    img_mime = f.type

            result = call_gemini(prompt, img_b64, img_mime)
            if result is None:
                result = smart_fallback(age_group, checked_all,
                                        st.session_state.get("portal_q", ""), cname)

        st.session_state["portal_insight"] = result
        st.rerun()
    else:
        st.error("No credits left today!")

# ── Domain explainer ──────────────────────────────────────────────────────────
st.markdown('<div class="kc-divider" style="margin-top:32px">The four development domains</div>',
            unsafe_allow_html=True)
d_cols = st.columns(4)
for col, icon, title, desc in zip(d_cols, [
    ("🏃", "Motor",    "Body control, coordination, and physical movement"),
    ("🤝", "Social",   "Connecting, playing, and understanding emotions"),
    ("🧠", "Cognitive","Thinking, learning, and problem-solving"),
    ("🗣️", "Language", "Communication, understanding, and speaking"),
]):
    with col:
        st.markdown(
            '<div class="how-card">'
            '<div class="how-icon">' + icon + "</div>"
            '<div class="how-title">' + title + "</div>"
            '<div class="how-desc">' + desc + "</div></div>",
            unsafe_allow_html=True,
        )
