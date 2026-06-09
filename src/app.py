"""Streamlit query interface for The Unofficial Guide (Bryan / College Station).

Chat-style: every question and its grounded answer stays on screen, and new
questions append to the conversation instead of replacing it. History is held
in st.session_state for the browser session.

Run from the project root with the launcher (NOT `streamlit run`):
    .venv\\Scripts\\python.exe run_app.py

The launcher pre-imports chromadb on the main thread to dodge a Python 3.14 +
Streamlit + OpenTelemetry import crash. See run_app.py for details.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import DEFAULT_MODEL, NO_CONTEXT_MSG, answer_stream  # noqa: E402

st.set_page_config(page_title="The Unofficial Guide — Bryan/CS", page_icon="🤠")

st.title("The Unofficial Guide")
st.caption(
    "Ask about things to do and events in Bryan & College Station, Texas. "
    "Answers come **only** from the scraped local sources, with citations."
)

# ---- Session history ----
# Each message: {"role": "user"|"assistant", "content": str, "sources": [Result]}
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Passages to retrieve (top-k)", min_value=1, max_value=15, value=5)
    st.text_input("Model", value=DEFAULT_MODEL, disabled=True,
                  help="Set GROQ_MODEL in .env to change.")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown(
        "Sources: Destination Bryan, Visit College Station, and the Texas A&M "
        "events calendar."
    )


def render_sources(results) -> None:
    """Render the deterministic source list + the exact retrieved passages."""
    if not results:
        return
    st.markdown("**Sources**")
    for r in results:
        st.markdown(f"**[{r.rank}]** [{r.source_name}]({r.source_url}) "
                    f"· relevance {r.score:.2f}")
    with st.expander("Show retrieved passages (the exact context sent to the model)"):
        for r in results:
            st.markdown(f"**[{r.rank}] {r.source_name}** — {r.source_url}")
            st.text(r.text)
            st.divider()


# ---- Replay the whole conversation so nothing is lost on rerun ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg.get("sources", []))


# ---- New question ----
query = st.chat_input("Ask a question…")
if query and query.strip():
    query = query.strip()
    st.session_state.messages.append({"role": "user", "content": query, "sources": []})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        try:
            token_gen, results = answer_stream(query, top_k=top_k)
        except RuntimeError as e:  # missing API key, etc.
            st.error(str(e))
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Error: {e}", "sources": []})
            st.stop()

        if not results:
            st.warning(NO_CONTEXT_MSG)
            content, results = NO_CONTEXT_MSG, []
        else:
            content = st.write_stream(token_gen)  # streams and returns full text
            render_sources(results)

    st.session_state.messages.append(
        {"role": "assistant", "content": content, "sources": results})
