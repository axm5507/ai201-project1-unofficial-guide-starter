"""Streamlit query interface for The Unofficial Guide (Bryan / College Station).

Run from the project root:
    .venv\\Scripts\\streamlit run src\\app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import DEFAULT_MODEL, NO_CONTEXT_MSG, answer_stream  # noqa: E402

st.set_page_config(page_title="The Unofficial Guide — Bryan/CS", page_icon="🤠")

st.title("🤠 The Unofficial Guide")
st.caption(
    "Ask about things to do and events in Bryan & College Station, Texas. "
    "Answers come **only** from the scraped local sources, with citations."
)

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Passages to retrieve (top-k)", min_value=1, max_value=15, value=5)
    st.text_input("Model", value=DEFAULT_MODEL, disabled=True,
                  help="Set GROQ_MODEL in .env to change.")
    st.markdown(
        "Sources: Destination Bryan, Visit College Station, and the Texas A&M "
        "events calendar."
    )

query = st.text_input(
    "Your question",
    placeholder="e.g. Where can I hear live music in downtown Bryan?",
)
ask = st.button("Ask", type="primary")

if ask and query.strip():
    try:
        token_gen, results = answer_stream(query.strip(), top_k=top_k)
    except RuntimeError as e:  # missing API key, etc.
        st.error(str(e))
        st.stop()

    if not results:
        st.warning(NO_CONTEXT_MSG)
        st.stop()

    st.subheader("Answer")
    st.write_stream(token_gen)

    # Deterministic source list mapping each citation number to its source.
    st.subheader("Sources")
    for r in results:
        st.markdown(f"**[{r.rank}]** [{r.source_name}]({r.source_url}) "
                    f"· relevance {r.score:.2f}")

    with st.expander("Show retrieved passages (the exact context sent to the model)"):
        for r in results:
            st.markdown(f"**[{r.rank}] {r.source_name}** — {r.source_url}")
            st.text(r.text)
            st.divider()
elif ask:
    st.warning("Please type a question first.")
