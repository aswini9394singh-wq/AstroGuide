"""AstroGuide Streamlit dashboard.
Reuses the data and logic from app.py (same signs, horoscopes, compatibility
and the same SQLite database), so both apps always stay in sync.
Run with:  streamlit run dashboard.py
All content is sample data for entertainment only."""
import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from app import SIGNS, BY_SLUG, CATEGORIES, DB, get_sign_by_date, horoscope_for, compatibility

st.set_page_config(page_title="AstroGuide Dashboard", page_icon="✨", layout="wide")


def sign_label(slug):
    """Readable label for select boxes, e.g. '♈ Aries'."""
    s = BY_SLUG[slug]
    return f"{s['symbol']} {s['name']}"


def load_messages():
    """Read contact messages saved by the Flask app."""
    with sqlite3.connect(DB) as conn:
        return pd.read_sql_query(
            "SELECT id, name, email, subject, message, created_at "
            "FROM contact_messages ORDER BY id DESC", conn)


SLUGS = [s["slug"] for s in SIGNS]

st.sidebar.title("✨ AstroGuide")
page = st.sidebar.radio("Go to", ["Overview", "Zodiac Explorer", "Find Your Sign",
                                  "Daily Horoscope", "Compatibility", "Contact Messages"])
st.sidebar.caption("Sample content for entertainment only. Astrology is not scientifically proven.")

# ---------------- Overview ----------------
if page == "Overview":
    st.title("AstroGuide Dashboard")
    msgs = load_messages()
    c1, c2, c3 = st.columns(3)
    c1.metric("Zodiac signs", len(SIGNS))
    c2.metric("Contact messages", len(msgs))
    c3.metric("Today", date.today().strftime("%d %b %Y"))

    left, right = st.columns(2)
    df = pd.DataFrame(SIGNS)
    with left:
        st.subheader("Signs by element")
        st.bar_chart(df["element"].value_counts())
    with right:
        st.subheader("Signs by ruling planet")
        st.bar_chart(df["planet"].value_counts())
    st.subheader("All signs")
    st.dataframe(df[["symbol", "name", "dates", "element", "planet"]], hide_index=True)

# ---------------- Zodiac Explorer ----------------
elif page == "Zodiac Explorer":
    st.title("Zodiac Explorer")
    s = BY_SLUG[st.selectbox("Choose a sign", SLUGS, format_func=sign_label)]
    st.header(f"{s['symbol']} {s['name']}")
    a, b, c = st.columns(3)
    a.metric("Dates", s["dates"])
    b.metric("Element", s["element"])
    c.metric("Ruling planet", s["planet"])
    st.write(f"**Personality:** {s['traits']}")
    st.success(f"**Strengths:** {s['strengths']}")
    st.warning(f"**Weaknesses:** {s['weaknesses']}")

# ---------------- Find Your Sign ----------------
elif page == "Find Your Sign":
    st.title("Find Your Zodiac Sign")
    dob = st.date_input("Date of birth", value=date(2000, 1, 1),
                        min_value=date(1900, 1, 1), max_value=date.today())
    s = get_sign_by_date(dob.month, dob.day)
    st.header(f"{s['symbol']} You are {s['name']}")
    st.write(f"{s['dates']} · {s['element']} · ruled by {s['planet']}")
    st.write(s["traits"])

# ---------------- Daily Horoscope ----------------
elif page == "Daily Horoscope":
    st.title("Daily Horoscope")
    today = date.today()
    st.caption(today.strftime("%A, %d %B %Y"))
    s = BY_SLUG[st.selectbox("Select your sign", SLUGS, format_func=sign_label)]
    content = horoscope_for(s, today)
    tabs = st.tabs(CATEGORIES)
    for tab, cat in zip(tabs, CATEGORIES):
        tab.info(content[cat])
    st.caption("General entertainment content, not verified predictions.")

# ---------------- Compatibility ----------------
elif page == "Compatibility":
    st.title("Compatibility Checker")
    c1, c2 = st.columns(2)
    a = BY_SLUG[c1.selectbox("First sign", SLUGS, format_func=sign_label, key="s1")]
    b = BY_SLUG[c2.selectbox("Second sign", SLUGS, index=4, format_func=sign_label, key="s2")]
    r = compatibility(a, b)
    st.metric(f"{a['name']} & {b['name']}", f"{r['score']}%")
    st.progress(r["score"] / 100)
    st.write(r["desc"])
    x, y = st.columns(2)
    x.success("**Strengths**\n\n" + "\n".join(f"- {i}" for i in r["strengths"]))
    y.warning("**Possible challenges**\n\n" + "\n".join(f"- {i}" for i in r["challenges"]))
    st.write(f"**Summary:** {r['summary']}")

    st.subheader(f"{a['name']} with every sign")
    scores = pd.Series({o["name"]: compatibility(a, o)["score"] for o in SIGNS}, name="Compatibility %")
    st.bar_chart(scores)

# ---------------- Contact Messages ----------------
else:
    st.title("Contact Messages")
    msgs = load_messages()
    if msgs.empty:
        st.info("No messages yet. Submit one from the Flask site's Contact page.")
    else:
        q = st.text_input("Search name, email, subject or message").strip().lower()
        if q:
            mask = msgs.apply(lambda r: q in " ".join(map(str, r.values)).lower(), axis=1)
            msgs = msgs[mask]
        st.caption(f"{len(msgs)} message(s)")
        st.dataframe(msgs, hide_index=True)
        st.download_button("Download CSV", msgs.to_csv(index=False), "contact_messages.csv", "text/csv")
