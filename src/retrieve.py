"""Stage 4 — Retrieval.

`retrieve(query, top_k)` embeds the query with all-MiniLM-L6-v2 (via the
collection's attached embedding function) and returns the top-k most similar
chunks, each paired with its source metadata and a similarity score.

Test it from the command line:
    .venv\\Scripts\\python.exe src\\retrieve.py "where can I see live music in Bryan?"
    .venv\\Scripts\\python.exe src\\retrieve.py "nightlife in College Station" --k 3

With no query, it runs the 5 evaluation questions from planning.md as a demo.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vectorstore import get_collection  # noqa: E402

# The 5 test questions from planning.md, used as the default demo.
EVAL_QUESTIONS = [
    "What nightlife is present in College Station?",
    "Are there any scenic nature spots in Bryan?",
    "Is there anything in College Station for a history buff?",
    "Where can I exercise in College Station?",
    "Are there any organic food markets in College Station?",
]


@dataclass
class Result:
    rank: int
    score: float          # cosine similarity in [-1, 1]; higher is closer
    chunk_id: str
    text: str
    source_name: str
    source_url: str
    description: str

    def short(self, width: int = 220) -> str:
        body = " ".join(self.text.split())
        if len(body) > width:
            body = body[:width].rstrip() + "…"
        return body


def retrieve(query: str, top_k: int = 5) -> list[Result]:
    """Return the top_k chunks most relevant to `query`, with source info."""
    collection = get_collection()
    res = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results: list[Result] = []
    ids = res["ids"][0]
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    for i, (cid, doc, meta, dist) in enumerate(zip(ids, docs, metas, dists), start=1):
        results.append(Result(
            rank=i,
            score=1.0 - dist,  # collection uses cosine distance
            chunk_id=cid,
            text=doc,
            source_name=meta.get("source_name", "?"),
            source_url=meta.get("source_url", ""),
            description=meta.get("description", ""),
        ))
    return results


def print_results(query: str, results: list[Result]) -> None:
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    if not results:
        print("  (no results)")
        return
    for r in results:
        print(f"\n[{r.rank}] score={r.score:.3f} | {r.source_name} | {r.chunk_id}")
        print(f"    {r.source_url}")
        print(f"    {r.short()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test retrieval against the guide index.")
    parser.add_argument("query", nargs="*", help="Query string (omit to run the eval questions).")
    parser.add_argument("--k", type=int, default=5, help="Number of chunks to return (top-k).")
    args = parser.parse_args()

    if args.query:
        query = " ".join(args.query)
        print_results(query, retrieve(query, top_k=args.k))
    else:
        print(f"No query given — running the {len(EVAL_QUESTIONS)} planning.md eval questions.")
        for q in EVAL_QUESTIONS:
            print_results(q, retrieve(q, top_k=args.k))


if __name__ == "__main__":
    main()
