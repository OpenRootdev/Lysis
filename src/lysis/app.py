"""Streamlit UI: streamlit run src\\lysis\\app.py"""

import httpx
import streamlit as st
from dotenv import load_dotenv

from lysis.cli import rank_repo
from lysis.ingestion.github_client import GitHubClient
from lysis.models.evaluate import load_dataset
from lysis.models.gbm import make_gbm_ranker

load_dotenv()
st.set_page_config(page_title="Lysis", page_icon="🧭")


@st.cache_resource
def get_model():
    df = load_dataset()
    return make_gbm_ranker(df), len(df), df["first_timer"].mean()


ranker, n, base = get_model()
st.title("Lysis")
st.caption("Beginner-friendly GitHub issue ranker")
st.sidebar.write(f"Model trained on {n:,} closed issues. Base rate: {base:.2f}")
repo = st.text_input("Repository", "psf/requests", placeholder="owner/repo")
top = st.slider("Top N", 5, 30, 10)

if st.button("Rank issues") and "/" in repo:
    try:
        with st.spinner("Fetching and ranking..."):
            out = rank_repo(GitHubClient(), repo.strip(), ranker, top)
    except httpx.HTTPError as e:
        st.error(f"GitHub error: {e}")
    else:
        if out.empty:
            st.warning("No open, unassigned issues found.")
        else:
            st.bar_chart(out.set_index("number")["score"])
            st.dataframe(
                out,
                column_config={"url": st.column_config.LinkColumn("link")},
                hide_index=True,
            )