"""Stage 5 — Grounded generation.

Retrieves the top-k chunks for a question, packs them into a context-bounded
prompt, and asks a Groq-hosted LLM to answer *only* from that context, citing
the passage numbers it used.

The API key is read from .env (which is git-ignored), so it never touches the
repo. Configure the model with the GROQ_MODEL env var; defaults to
llama-3.3-70b-versatile.

Terminal test:
    .venv\\Scripts\\python.exe src\\generate.py "where can I hear live music in Bryan?"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

from retrieve import Result, retrieve  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")  # explicit path so it works regardless of CWD

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Grounding instruction: answer only from context, refuse otherwise, cite sources.
SYSTEM_PROMPT = """You are "The Unofficial Guide," a local expert on things to do \
and events in Bryan and College Station, Texas.

Answer the user's question using ONLY the information in the numbered context \
passages provided below. Follow these rules strictly:

1. Use no prior knowledge and add no facts that are not in the context. If the \
context does not contain enough information to answer, reply exactly: \
"I don't have enough information in my sources to answer that." Do not guess or \
fill gaps from general knowledge.
2. After each claim, cite the passage number(s) it came from in square brackets, \
e.g. "Northgate has many bars [2]." Cite multiple passages as [1][3] when relevant.
3. Be concise and specific — name the actual places, events, dates, or addresses \
that appear in the context.
4. Finish with a line that starts with "Sources:" listing the passage numbers you \
actually used (e.g. "Sources: [1], [2]")."""

NO_CONTEXT_MSG = "I don't have enough information in my sources to answer that."


def format_context(results: list[Result]) -> str:
    """Render retrieved chunks as numbered passages with source attribution."""
    blocks = []
    for r in results:
        blocks.append(
            f"[{r.rank}] Source: {r.source_name} — {r.source_url}\n{r.text}"
        )
    return "\n\n".join(blocks)


def build_messages(query: str, results: list[Result]) -> list[dict]:
    context = format_context(results)
    user = (
        f"Context passages:\n\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer using only the passages above, with bracketed citations."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key or key == "your_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is missing — copy .env.example to .env and add your "
            "key from https://console.groq.com"
        )
    from groq import Groq

    return Groq(api_key=key)


def answer(query: str, top_k: int = 5, model: str = DEFAULT_MODEL,
           temperature: float = 0.2):
    """Non-streaming: returns (answer_text, results)."""
    results = retrieve(query, top_k)
    if not results:
        return NO_CONTEXT_MSG, results
    resp = get_client().chat.completions.create(
        model=model,
        messages=build_messages(query, results),
        temperature=temperature,
    )
    return resp.choices[0].message.content, results


def answer_stream(query: str, top_k: int = 5, model: str = DEFAULT_MODEL,
                  temperature: float = 0.2):
    """Streaming: returns (token_generator, results). The generator yields text
    deltas so a UI can render the answer as it arrives."""
    results = retrieve(query, top_k)
    if not results:
        return iter([NO_CONTEXT_MSG]), results

    def gen():
        stream = get_client().chat.completions.create(
            model=model,
            messages=build_messages(query, results),
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    return gen(), results


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the Unofficial Guide (grounded RAG).")
    parser.add_argument("query", nargs="+", help="Your question.")
    parser.add_argument("--k", type=int, default=5, help="Chunks to retrieve as context.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Groq model id.")
    args = parser.parse_args()
    query = " ".join(args.query)

    text, results = answer(query, top_k=args.k, model=args.model)
    print(f"\nQ: {query}\n")
    print(text)
    print("\n" + "-" * 70)
    print("Retrieved passages:")
    for r in results:
        print(f"  [{r.rank}] {r.source_name} ({r.score:.3f}) — {r.source_url}")


if __name__ == "__main__":
    main()
