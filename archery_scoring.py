# archery_scoring.py
import streamlit as st
import pandas as pd
import urllib.parse as _url

st.set_page_config(page_title="Field Archery Scoring", page_icon="🏹", layout="wide")

# --- Constants ---
NUM_TARGETS = 40
SCORE_OPTIONS = [0, 4, 8, 10, 14, 16, 20, 24, 26, 28, 30, 32, 34, 36, 40, 44, 48]
NUM_COLS = 2
TARGETS_PER_COL = NUM_TARGETS // NUM_COLS

# Color map (backgrounds). Text will be black as requested.
COLOR_BG = {
    0:  "#808080",  # grey
    4:  "#1976d2",  # blue
    8:  "#1976d2",  # blue
    10: "#ffffff",  # white
    14: "#ffffff",  # white
    16: "#d32f2f",  # red
    20: "#d32f2f",  # red
    24: "#d32f2f",  # red
    26:  "#808080", # grey
    28:  "#808080", # grey
    30:  "#808080", # grey
    32:  "#808080", # grey
    34:  "#808080", # grey
    36:  "#808080", # grey
    40:  "#808080", # grey
    48:  "#808080", # grey
}

# --- Initialize state ---
if "scores" not in st.session_state:
    st.session_state.scores = [0] * NUM_TARGETS
for i in range(NUM_TARGETS):
    st.session_state.setdefault(f"target_{i}", st.session_state.scores[i])

# --- Title ---
st.title("🏹 Field Archery Scoring")

# ---------- TOP BAR (Name + live Total) ----------
top = st.container()
with top:
    col_name, col_total = st.columns([3, 1])
    archer_name = col_name.text_input("Archer's name", key="archer_name", placeholder="Enter full name")
    total_placeholder = col_total.empty()
    total_placeholder.metric("Total Score", sum(st.session_state.get(f"target_{i}", 0) for i in range(NUM_TARGETS)))

st.divider()

# --- Actions row ---
cols_actions = st.columns([1, 1, 3])
with cols_actions[0]:
    if st.button("Reset All Scores", type="secondary"):
        st.session_state.scores = [0] * NUM_TARGETS
        for i in range(NUM_TARGETS):
            st.session_state[f"target_{i}"] = 0
        st.rerun()

with cols_actions[1]:
    if st.button("Fill Example Round", help="Quickly populate with a repeating pattern for testing"):
        pattern = [24, 20, 16, 14, 10, 8, 4, 0]
        filled = [pattern[i % len(pattern)] for i in range(NUM_TARGETS)]
        st.session_state.scores = filled
        for i, v in enumerate(filled):
            st.session_state[f"target_{i}"] = v
        st.rerun()


# --- Score inputs (40 dropdowns) ---
st.subheader("Targets")
cols = st.columns(NUM_COLS)
for c in range(NUM_COLS):
    with cols[c]:
        start = c * TARGETS_PER_COL
        end = start + TARGETS_PER_COL
        for i in range(start, end):
            st.selectbox(
                f"Target {i+1}",
                options=SCORE_OPTIONS,
                index=SCORE_OPTIONS.index(st.session_state[f"target_{i}"]),
                key=f"target_{i}",
            )

# --- Sync scores & compute total ---
st.session_state.scores = [st.session_state[f"target_{i}"] for i in range(NUM_TARGETS)]
total = sum(st.session_state.scores)

# Update top bar metric
with top:
    total_placeholder.metric("Total Score", total)

# --- CSS for dropdown colors (opened menu + closed control) ---
# 1) Opened menu: color by nth-child mapping (fixed order of SCORE_OPTIONS).
menu_item_css = f"""
/* Larger touch targets and rounded corners */
.stSelectbox [data-baseweb="select"] > div {{
  min-height: 40px;
  border-radius: 8px;
}}

/* Dropdown menu items colored by position in list (0,4,8,10,14,16,20,24) */
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(1)  {{ background: {COLOR_BG[0]};  color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(2)  {{ background: {COLOR_BG[4]};  color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(3)  {{ background: {COLOR_BG[8]};  color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(4)  {{ background: {COLOR_BG[10]}; color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(5)  {{ background: {COLOR_BG[14]}; color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(6)  {{ background: {COLOR_BG[16]}; color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(7)  {{ background: {COLOR_BG[20]}; color:#000; }}
[data-baseweb="select"] [role="listbox"] [role="option"]:nth-child(8)  {{ background: {COLOR_BG[24]}; color:#000; }}

/* Hover/focus feedback */
[data-baseweb="select"] [role="listbox"] [role="option"]:hover {{
  filter: brightness(0.95);
  outline: none;
}}
"""

# 2) Closed control: color per widget based on its current value
per_control_rules = []
for i, v in enumerate(st.session_state.scores):
    key = f"target_{i}"
    bg = COLOR_BG.get(v, "#f5f5f5")
    per_control_rules.append(f"""
/* Selected (closed) control for {key} */
.st-key-{key} [data-baseweb="select"] > div {{
  background: {bg} !important;
  color: #000 !important;
  border-color: #bdbdbd !important;
}}
.st-key-{key} [data-baseweb="select"] svg {{
  color: #000 !important;
}}
""")

st.markdown(f"<style>{menu_item_css}{''.join(per_control_rules)}</style>", unsafe_allow_html=True)

# --- Email input (mailto only) ---
email_row = st.columns([2, 1])
with email_row[0]:
    email_to = st.text_input("Archer's email", key="archer_email", placeholder="name@example.com")

def _compose_subject_body(name: str, scores: list[int]) -> tuple[str, str]:
    total_local = sum(scores)
    subject = f"Field Archery Results: {name or 'Archer'} — {total_local} pts"
    lines = [f"Archer: {name or '—'}", f"Total: {total_local}", ""]
    lines.append("Per-target scores:")
    lines += [f"Target {i+1}: {s}" for i, s in enumerate(scores)]
    body = "\n".join(lines)
    return subject, body

def render_mailto_button(name: str, email_to: str, scores: list[int]):
    if not email_to or "@" not in email_to:
        st.button("📧 Open email app with results", disabled=True)
        return
    subject, body = _compose_subject_body(name, scores)
    mailto = f"mailto:{email_to}?subject={_url.quote(subject)}&body={_url.quote(body)}"
    st.markdown(
        f"""
        {mailto}
            <button style="width:100%;padding:0.6rem 1rem;border-radius:8px;border:1px solid #bbb;background:#f7f7f7;cursor:pointer;">
                📧 Open email app with results
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

with email_row[1]:
    render_mailto_button(archer_name, email_to, st.session_state.scores)


# --- Footer summary & table ---
st.divider()
st.write(f"**Archer:** {archer_name.strip() or '—'}  |  **Total Score:** {total}")

with st.expander("Show score summary table"):
    df = pd.DataFrame({"Target": [f"{i+1}" for i in range(NUM_TARGETS)], "Score": st.session_state.scores})
    df.loc["Total"] = ["—", df["Score"].sum()]
    st.dataframe(df, use_container_width=True)