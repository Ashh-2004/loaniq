# app.py — auth built-in, no separate auth.py needed

import streamlit as st
import bcrypt
from db import fetch_all
from pathlib import Path

st.set_page_config(page_title="LoanIQ", layout="wide", page_icon="🏦")

# ── Dark theme CSS ──────────────────────────────────────────
st.markdown("""<style>
  .stApp { background-color: #0d1117; color: #e6e6e6; }
  section[data-testid="stSidebar"] { background-color: #0a0f14; }
  .stButton > button {
    background-color: #c9a227; color: #0a0f14;
    font-weight: 600; border: none; border-radius: 6px;
  }
  .stTextInput > div > input, .stSelectbox > div {
    background-color: #111820; border: 1px solid #1e2a35; color: #e6e6e6;
  }
</style>""", unsafe_allow_html=True)

# ── Session state init ──────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# ── Role → allowed pages ────────────────────────────────────
ROLE_PAGES = {
    "admin":   ["Application", "Portfolio", "EMI Calculator", "Risk Analysis"],
    "officer": ["Application", "EMI Calculator"],
    "viewer":  ["Portfolio", "Risk Analysis"],
}

# ── Login page ──────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("## 🏦 Loan**IQ**")
        st.markdown("##### Bank Lending Intelligence System")
        st.divider()

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role     = st.selectbox("Role", ["admin", "officer", "viewer"])

        if st.button("Sign In", use_container_width=True):
            rows = fetch_all(
                "SELECT * FROM users WHERE username = %s AND role = %s",
                (username, role)
            )
            if rows and bcrypt.checkpw(password.encode(),
                                        rows[0]["password_hash"].encode()):
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.role      = role
                st.rerun()
            else:
                st.error("Invalid credentials or role mismatch.")

# ── Sidebar (after login) ───────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### Loan**IQ**")
        st.caption("Bank Lending Intelligence")
        st.divider()

        st.markdown(f"👤 **{st.session_state.username.capitalize()}**")
        st.caption(f"Role: {st.session_state.role.capitalize()}")
        st.divider()

        allowed = ROLE_PAGES[st.session_state.role]
        page = st.radio("Navigate", allowed)

        st.divider()
        st.caption("System Stats")
        st.metric("Active Loans", "3,847")
        st.metric("NPA Rate", "2.4%")

        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username  = None
            st.session_state.role      = None
            st.rerun()

    return page

# ── Main router ─────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
else:
    page = show_sidebar()

    if page == "Application":
        exec(Path("modules/application.py").read_text(encoding="utf-8"))

    elif page == "Portfolio":
        exec(Path("modules/portfolio.py").read_text(encoding="utf-8"))

    elif page == "EMI Calculator":
        exec(Path("modules/emi_calculator.py").read_text(encoding="utf-8"))

    elif page == "Risk Analysis":
        exec(Path("modules/risk_analysis.py").read_text(encoding="utf-8"))