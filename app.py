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
