"""
pages/kid_zone.py — Kid Zone: word/voice → Pollinations.ai art (100% free)
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
    style_mod = ART_STYLES[style_key]
    prompt = (
        f"{word}, {style_mod}, designed for toddlers and young children, "
        "extremely cute friendly safe wholesome, bright saturated colors, "
        "white background, no text no watermark, square composition"
    )
    encoded = urllib.parse.quote(prompt)
    seed = int(hashlib.md5(f"{word}{style_key}".encode()).hexdigest(), 16) % 99999
    return f"{POLLINATIONS_BASE}/{encoded}?width=768&height=768&model=flux&nologo=true&seed={seed}"


def fetch_image(url: str):
    try:
        r = requests.get(url, timeout=35)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException:
        pass
    return None


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

left, right = st.columns([1, 1], gap="large")

with left:
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

    kid_word = st.text_input(
        "Or type any word:",
        value=st.session_state.get("kid_word", ""),
        placeholder="e.g. Humpty Dumpty, Fire Truck, Baby Panda...",
        max_chars=60,
    )
    if kid_word != st.session_state.get("kid_word", ""):
        st.session_state["kid_word"] = kid_word

    st.markdown('<div class="kc-divider">Use your voice 🎤</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="kc-divider">Pick an art style</div>', unsafe_allow_html=True)
    selected_style = st.radio(
        "Art style",
        options=STYLE_NAMES,
        index=st.session_state.get("style_idx", 0),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["style_idx"] = STYLE_NAMES.index(selected_style)

    word_ready = bool(st.session_state.get("kid_word", "").strip())
    can_gen = has_credits and word_ready

    gen_label = (
        "✨ Create the Magic!"
        if can_gen
        else ("🔒 No Credits Left Today" if not has_credits else "👆 Type or pick a word first")
    )
    gen = st.button(gen_label, type="primary", use_container_width=True, disabled=not can_gen)

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

if gen:
    current_word = st.session_state.get("kid_word", "").strip()
    if current_word and has_credits:
        img_url = make_image_url(current_word, selected_style)
        with st.spinner(f"🎨 Painting {current_word}... (10–25 sec)"):
            img_bytes = fetch_image(img_url)

        if img_bytes:
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
