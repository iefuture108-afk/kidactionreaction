"""
quota.py — Daily credit manager for KidsCreate AI
"""
import streamlit as st
from datetime import date

DAILY_LIMIT = 5


def _key(zone: str = "kids") -> str:
    return f"quota_{zone}_{date.today().isoformat()}"


def get_remaining(zone: str = "kids") -> int:
    return max(0, DAILY_LIMIT - st.session_state.get(_key(zone), 0))


def consume(zone: str = "kids") -> bool:
    k = _key(zone)
    used = st.session_state.get(k, 0)
    if used >= DAILY_LIMIT:
        return False
    st.session_state[k] = used + 1
    return True


def render_credit_bar(zone: str = "kids") -> bool:
    remaining = get_remaining(zone)
    dots = "".join(
        f'<div class="cdot {"on" if i < remaining else "off"}"></div>'
        for i in range(DAILY_LIMIT)
    )
    color = "#FF6B6B" if remaining > 1 else ("#FF9E53" if remaining == 1 else "#ccc")
    label = (
        f"{remaining} of {DAILY_LIMIT} free credits left today"
        if remaining > 0
        else "All used — resets at midnight 🌙"
    )
    st.markdown(
        f"""
        <div class="credit-bar">
          <span class="credit-emoji">🎯</span>
          <div>
            <div class="credit-label">Daily Credits</div>
            <div class="credit-value" style="color:{color}">{label}</div>
          </div>
          <div class="credit-dots">{dots}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return remaining > 0
