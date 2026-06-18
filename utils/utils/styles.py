"""
styles.py — Shared CSS design system for KidsCreate AI
Injected via st.markdown(GLOBAL_CSS, unsafe_allow_html=True) on each page.
Note: Components rendered via components.html() run in a sandboxed iframe
      and do NOT inherit this CSS — those components carry their own inline styles.
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;900&family=Baloo+2:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #FFF8F0; }
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1080px !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 50px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.18s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF9E53 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(255,107,107,0.38) !important;
}
.stButton > button[kind="primary"]:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(255,107,107,0.48) !important;
}
.stButton > button[kind="primary"]:disabled {
    background: #ddd !important;
    box-shadow: none !important;
    color: #aaa !important;
}
.stButton > button:not([kind="primary"]) {
    background: #fff !important;
    border: 2px solid #ecddd0 !important;
    color: #555 !important;
}
.stButton > button:not([kind="primary"]):hover:not(:disabled) {
    border-color: #FF9E53 !important;
    color: #FF6B6B !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 14px !important;
    border: 2px solid #ecddd0 !important;
    background: #fff !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #FF9E53 !important;
    box-shadow: 0 0 0 3px rgba(255,158,83,0.14) !important;
}
.stSelectbox > div > div {
    border-radius: 14px !important;
    border: 2px solid #ecddd0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #fff !important;
    border-radius: 16px !important;
    padding: 5px !important;
    gap: 3px !important;
    border: 1.5px solid #ecddd0 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 8px 18px !important;
    color: #999 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B6B, #FF9E53) !important;
    color: #fff !important;
}

/* ── Cards ── */
.kc-card {
    background: #fff;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 3px 16px rgba(0,0,0,0.06);
    border: 1.5px solid #ecddd0;
    margin-bottom: 14px;
}
.kc-card-title {
    font-family: 'Baloo 2', cursive;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 0 0 3px;
    line-height: 1.2;
}
.kc-card-sub { font-size: 0.82rem; color: #aaa; margin: 0; font-weight: 600; }

/* ── Credit bar ── */
.credit-bar {
    background: #fff;
    border-radius: 16px;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 18px;
    border: 1.5px solid #ecddd0;
}
.credit-emoji { font-size: 1.3rem; }
.credit-label { font-size: 0.72rem; color: #bbb; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; line-height: 1; }
.credit-value { font-family: 'Baloo 2', cursive; font-size: 1.2rem; font-weight: 800; line-height: 1; }
.credit-dots { display: flex; gap: 5px; margin-left: auto; align-items: center; }
.cdot { width: 12px; height: 12px; border-radius: 50%; }
.cdot.on  { background: #FFD93D; box-shadow: 0 0 0 2px rgba(255,180,0,0.4); }
.cdot.off { background: #ecddd0; }

/* ── Page header ── */
.pg-header {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 24px; padding-bottom: 18px;
    border-bottom: 2px solid #f5ece4;
}
.pg-icon  { font-size: 2.6rem; line-height: 1; }
.pg-title { font-family: 'Baloo 2', cursive; font-size: 1.9rem; font-weight: 800; color: #1A1A2E; margin: 0; }
.pg-desc  { font-size: 0.85rem; color: #bbb; margin: 2px 0 0; font-weight: 600; }

/* ── Result dark panel ── */
.result-dark {
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    border-radius: 22px;
    min-height: 320px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 28px;
    border: 1.5px solid rgba(255,255,255,0.07);
    box-shadow: 0 8px 28px rgba(0,0,0,0.15);
}
.result-empty-icon { font-size: 3.6rem; margin-bottom: 14px; opacity: 0.35; }
.result-empty-hint { color: rgba(255,255,255,0.55); font-size: 1rem; font-weight: 700; }
.result-empty-text { color: rgba(255,255,255,0.35); font-size: 0.9rem; font-weight: 600; line-height: 2; margin-top: 14px; }

/* ── Milestone progress ── */
.ms-bar-wrap {
    background: #f5ece4; border-radius: 50px;
    height: 10px; overflow: hidden; margin: 8px 0 6px;
}
.ms-bar-fill { height: 100%; border-radius: 50px; transition: width 0.5s ease; }

/* ── Insight card ── */
.insight-wrap {
    background: linear-gradient(135deg, #f0f4ff, #f8f0ff);
    border: 1.5px solid #c8b8f0;
    border-radius: 18px; padding: 22px; margin-top: 14px;
}
.insight-title {
    font-family: 'Baloo 2', cursive; font-size: 1.1rem;
    font-weight: 700; color: #4a3880; margin-bottom: 10px;
}
.insight-body { font-size: 0.9rem; color: #333; line-height: 1.7; }

/* ── Age badge ── */
.age-badge {
    display: inline-block; border-radius: 50px; padding: 4px 13px;
    font-size: 0.78rem; font-weight: 700; color: #fff;
    background: linear-gradient(135deg, #6BCB77, #44aa55);
}

/* ── Divider with text ── */
.kc-divider {
    display: flex; align-items: center; gap: 10px;
    margin: 18px 0; color: #ccc; font-size: 0.75rem;
    font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
}
.kc-divider::before, .kc-divider::after {
    content: ''; flex: 1; height: 1px; background: #ecddd0;
}

/* ── How-it-works cards ── */
.how-card {
    background: #fff; border-radius: 18px; padding: 20px 14px;
    text-align: center; border: 1.5px solid #ecddd0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.how-icon  { font-size: 1.9rem; margin-bottom: 8px; }
.how-title { font-family: 'Baloo 2', cursive; font-size: 1rem; font-weight: 700; color: #1A1A2E; }
.how-desc  { font-size: 0.78rem; color: #aaa; font-weight: 600; margin-top: 3px; }

/* ── Upload zone ── */
.upload-zone {
    background: #fff8f0; border: 2px dashed #f0d4b0;
    border-radius: 16px; padding: 16px; text-align: center;
    font-size: 0.85rem; color: #c0905a; font-weight: 600;
    margin-bottom: 10px;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF9E53 50%, #FFD93D 100%);
    border-radius: 26px; padding: 40px 36px 34px;
    margin-bottom: 28px; position: relative; overflow: hidden;
    box-shadow: 0 10px 40px rgba(255,107,107,0.28);
}
.hero::after {
    content: "🌈🦄🎨✨🐉🌟🎭🚀";
    position: absolute; top: -4px; right: 18px;
    font-size: 40px; opacity: 0.14; line-height: 1.5;
    width: 230px; word-break: break-all; letter-spacing: 4px;
}
.hero-title {
    font-family: 'Baloo 2', cursive; font-size: 2.9rem;
    font-weight: 800; color: #fff; margin: 0 0 6px;
    text-shadow: 0 3px 10px rgba(0,0,0,0.12);
}
.hero-sub { font-size: 1.05rem; color: rgba(255,255,255,0.9); font-weight: 600; margin: 0 0 22px; }
.hero-pill {
    display: inline-block; background: rgba(255,255,255,0.22);
    backdrop-filter: blur(6px); border-radius: 50px;
    padding: 5px 14px; font-size: 0.8rem; font-weight: 700;
    color: #fff; border: 1.5px solid rgba(255,255,255,0.35); margin: 3px;
}

.stSpinner > div { border-top-color: #FF6B6B !important; }
</style>
"""
