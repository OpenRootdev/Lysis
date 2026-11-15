"""Streamlit UI: streamlit run src\\lysis\\app.py"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from lysis.client import ApiError, fetch_model, fetch_rank
from lysis.feedback import log_feedback

load_dotenv()
API = os.getenv("LYSIS_API_URL", "https://lysis-3ocq.onrender.com")
st.set_page_config(page_title="Lysis", page_icon="🧭")


@st.cache_data(ttl=3600, show_spinner=False)
def get_meta():
    return fetch_model(API)


def vote(repo_name, number, score, key, model_date):
    val = st.session_state.get(key)
    if val is not None:
        ok = log_feedback(repo_name, number, score, val == 1, model_date)
        st.toast("Thanks, feedback saved." if ok else "Could not save feedback.")


st.title("Lysis")
st.caption("Beginner-friendly GitHub issue ranker")

try:
    with st.spinner("Connecting to the Lysis API (the first request can take a minute)..."):
        meta = get_meta()
except ApiError as e:
    st.error(str(e))
    st.stop()

st.sidebar.write(
    f"Model trained {meta['trained_at'][:10]} on {meta['n_train']:,} issues. "
    f"CV AP {meta['cv']['ap']}, AUC {meta['cv']['auc']}"
)
if "importance" in meta:
    st.sidebar.subheader("What the model relies on")
    st.sidebar.bar_chart(meta["importance"])

repo = st.text_input("Repository", "psf/requests", placeholder="owner/repo")
top = st.slider("Top N", 5, 30, 10)

if st.button("Rank issues") and "/" in repo:
    try:
        with st.spinner("Fetching and ranking..."):
            st.session_state["res"] = fetch_rank(API, repo.strip(), top)
    except ApiError as e:
        st.session_state.pop("res", None)
        st.error(str(e))

res = st.session_state.get("res")
if res is not None:
    issues = res["issues"]
    if not issues:
        st.warning("No open, unassigned issues found.")
    else:
        out = pd.DataFrame(issues)
        st.bar_chart(out.set_index("number")["score"])
        st.dataframe(
            out[["score", "number", "title", "url"]],
            column_config={"url": st.column_config.LinkColumn("link")},
            hide_index=True,
        )
        st.subheader("Why these fit")
        for r in issues[:5]:
            with st.expander(f"#{r['number']} {r['title']}"):
                st.write(r.get("why") or "Explanation unavailable.")
                key = f"fb_{res['repo']}_{r['number']}"
                st.caption("Is this a good starter issue?")
                st.feedback(
                    "thumbs",
                    key=key,
                    on_change=vote,
                    args=(res["repo"], r["number"], r["score"], key, res["model_date"]),
                )