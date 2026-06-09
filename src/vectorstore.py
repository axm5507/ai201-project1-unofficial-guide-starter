"""Stage 3 — Embedding + Vector Store.

Loads the chunks produced by the ingestion pipeline (``chunks.json``), embeds
them with all-MiniLM-L6-v2, and stores them in a persistent ChromaDB collection
together with their source metadata.

The same SentenceTransformer embedding function is attached to the collection,
so query text is embedded with the *identical* model at search time.

Rebuild the index from the current chunks.json:
    .venv\\Scripts\\python.exe src\\vectorstore.py
"""

from __future__ import annotations

import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = ROOT / "chunks.json"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "unofficial_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Cache the embedding function (loading the model is the expensive part).
_embed_fn = None


def embedding_fn():
    global _embed_fn
    if _embed_fn is None:
        _embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
    return _embed_fn


def get_client() -> "chromadb.api.ClientAPI":
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNKS_FILE.name} not found — run `python src/ingest.py` first."
        )
    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


def build_index(reset: bool = True) -> "chromadb.api.models.Collection.Collection":
    """(Re)build the Chroma collection from chunks.json. Returns the collection."""
    chunks = _load_chunks()
    client = get_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:  # noqa: BLE001 — collection may not exist yet
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn(),
        metadata={"hnsw:space": "cosine"},  # cosine fits normalized text embeddings
    )

    # Chroma metadata values must be scalars, so flatten the chunk's nested dict.
    metadatas = [
        {
            "source_id": c["source_id"],
            "source_name": c["source_name"],
            "source_url": c["source_url"],
            "kind": c["metadata"].get("kind", ""),
            "description": c["metadata"].get("description", ""),
            "n_tokens": c["n_tokens"],
        }
        for c in chunks
    ]

    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=metadatas,
    )
    return collection


def get_collection() -> "chromadb.api.models.Collection.Collection":
    """Open the existing collection, building it on first use if absent/empty."""
    client = get_client()
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME, embedding_function=embedding_fn()
        )
        if collection.count() > 0:
            return collection
    except Exception:  # noqa: BLE001 — not created yet
        pass
    return build_index(reset=True)


if __name__ == "__main__":
    coll = build_index(reset=True)
    print(f"Built '{COLLECTION_NAME}' with {coll.count()} chunks "
          f"(model: {EMBED_MODEL}, space: cosine).")
    print(f"Persisted to {CHROMA_DIR}")
