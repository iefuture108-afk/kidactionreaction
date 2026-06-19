"""
pages/parent_portal.py — Toddler milestone tracker + free Gemini AI insights
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

GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemini-1.5-flash:generateContent"
)

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


def call_gemini(prompt: str, image_b64: str = None, mime: str = "image/jpeg"):
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
        return None
    except Exception:
        return None


def smart_fallback(age_group: str, checked: list, question: str, child_name: str) -> str:
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

age_group = list(MILESTONES.keys())[st.session_state.get("age_idx", 2)]
cname     = st.session_state.get("cname", "") or "your child"
ms        = MILESTONES[age_group]

left_col, right_col = st.columns([1, 1], gap="large")

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
                    f.seek(0)
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
