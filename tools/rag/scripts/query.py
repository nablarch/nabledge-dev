"""RAG Query Engine: embed a question and retrieve top-k sections from Qdrant.

Usage (as a library):
    from tools.rag.scripts.query import QueryEngine, QueryResult

Usage (CLI):
    python3 -m tools.rag.scripts.query \
        --question "Nablarchバッチの起動方法は？" \
        --processing-type nablarch-batch \
        --k 10
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_EMBED_MODEL_ID = "cohere.embed-multilingual-v3"
_EMBED_REGION = "ap-northeast-1"
DEFAULT_TOP_K = 10
_COLLECTION_NAME = "nabledge-6"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Max characters per text for Cohere v3 models
_MODEL_MAX_CHARS: dict[str, int] = {
    "cohere.embed-multilingual-v3": 2048,
    "cohere.embed-english-v3": 2048,
}


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_query(
    text: str,
    model_id: str = DEFAULT_EMBED_MODEL_ID,
    verify_ssl: bool = True,
) -> list[float]:
    """Embed a query text using Cohere Embed via AWS Bedrock (input_type=search_query).

    Args:
        text: The query text to embed.
        model_id: Bedrock model ID for the Cohere Embed model.
        verify_ssl: Whether to verify SSL certificates.

    Returns:
        Embedding vector as a list of floats.
    """
    import boto3  # noqa: PLC0415

    client = boto3.client(
        "bedrock-runtime",
        region_name=_EMBED_REGION,
        verify=verify_ssl,
    )

    max_chars = _MODEL_MAX_CHARS.get(model_id)
    if max_chars is not None:
        text = text[:max_chars]

    body = json.dumps(
        {
            "texts": [text],
            "input_type": "search_query",
            "embedding_types": ["float"],
        }
    )
    response = client.invoke_model(
        modelId=model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["embeddings"]["float"][0]


# ---------------------------------------------------------------------------
# Metadata filter
# ---------------------------------------------------------------------------

def build_processing_type_filter(processing_type: str | None) -> Any:
    """Build a Qdrant filter for processing_type.

    When processing_type is provided (e.g. "nablarch-batch"), the filter matches
    points where processing_type == provided_value OR processing_type == "none".
    "none" represents general pages always relevant regardless of processing type.

    Args:
        processing_type: Slug-format processing type (e.g. "nablarch-batch"), or None.

    Returns:
        A Qdrant Filter object, or None if no filtering is needed.
    """
    if processing_type is None:
        return None

    from qdrant_client.models import FieldCondition, Filter, MatchAny  # noqa: PLC0415

    return Filter(
        should=[
            FieldCondition(
                key="processing_type",
                match=MatchAny(any=[processing_type, "none"]),
            )
        ]
    )


# ---------------------------------------------------------------------------
# Qdrant search
# ---------------------------------------------------------------------------

def search_qdrant(
    client: Any,
    vector: list[float],
    k: int,
    processing_type_filter: Any,
) -> list[Any]:
    """Search Qdrant for top-k nearest sections.

    Uses the `query_points` API (Qdrant client >= 1.10).

    Args:
        client: QdrantClient instance.
        vector: Query embedding vector.
        k: Number of top results to return.
        processing_type_filter: Optional Qdrant Filter for metadata filtering.

    Returns:
        List of ScoredPoint-like results from Qdrant (each has .score and .payload).
    """
    response = client.query_points(
        collection_name=_COLLECTION_NAME,
        query=vector,
        limit=k,
        query_filter=processing_type_filter,
    )
    return response.points


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class QueryResult:
    """A single RAG retrieval result."""

    page_id: str
    section_id: str
    score: float
    processing_type: str
    category: str
    title: str
    # Relative path of the JSON file (e.g. "processing-pattern/nablarch-batch/arch.json")
    file_path: str
    # Full section reference: "path/to/file.json:sN"
    section_ref: str
    payload: dict[str, Any] = field(default_factory=dict)

    def as_selected_section(self) -> dict[str, Any]:
        """Return this result in the workflow_details step3.selected_sections format."""
        return {
            "file": self.file_path,
            "section_id": self.section_id,
            "relevance": "high",
            "reason": "RAG top-k result",
        }


# ---------------------------------------------------------------------------
# format_results
# ---------------------------------------------------------------------------

def _page_id_to_file_path(page_id: str) -> str:
    """Convert a page_id (Qdrant payload) to a relative JSON file path.

    The page_id is stored as a path without extension, e.g.:
      "processing-pattern/nablarch-batch/nablarch-batch-architecture"

    Returns the path with .json appended:
      "processing-pattern/nablarch-batch/nablarch-batch-architecture.json"
    """
    if page_id.endswith(".json"):
        return page_id
    return f"{page_id}.json"


def format_results(hits: list[Any], knowledge_dir: pathlib.Path) -> list[QueryResult]:
    """Convert Qdrant ScoredPoints to QueryResult objects.

    Args:
        hits: List of ScoredPoint objects from Qdrant.
        knowledge_dir: Path to the knowledge root directory (used for context, not I/O here).

    Returns:
        List of QueryResult objects.
    """
    results: list[QueryResult] = []
    for hit in hits:
        payload = hit.payload or {}
        page_id: str = payload.get("page_id", "")
        section_id: str = payload.get("section_id", "")

        if not page_id:
            print(f"Warning: hit with missing page_id skipped (section_id={section_id})", file=sys.stderr)
            continue

        file_path = _page_id_to_file_path(page_id)
        section_ref = f"{file_path}:{section_id}"

        results.append(
            QueryResult(
                page_id=page_id,
                section_id=section_id,
                score=float(hit.score),
                processing_type=payload.get("processing_type", "none"),
                category=payload.get("category", "none"),
                title=payload.get("title", ""),
                file_path=file_path,
                section_ref=section_ref,
                payload=payload,
            )
        )
    return results


# ---------------------------------------------------------------------------
# High-level query function
# ---------------------------------------------------------------------------

def query(
    question: str,
    *,
    k: int = DEFAULT_TOP_K,
    processing_type: str | None = None,
    model_id: str = DEFAULT_EMBED_MODEL_ID,
    qdrant_host: str = QDRANT_HOST,
    qdrant_port: int = QDRANT_PORT,
    qdrant_client: Any | None = None,
    knowledge_dir: pathlib.Path | None = None,
    verify_ssl: bool = True,
) -> list[QueryResult]:
    """Embed a question and retrieve top-k sections from Qdrant.

    Args:
        question: The user question to answer.
        k: Number of top results to retrieve (default: 10).
        processing_type: Optional processing-type slug for metadata filtering.
        model_id: Bedrock Cohere Embed model ID.
        qdrant_host: Qdrant host (ignored if qdrant_client is provided).
        qdrant_port: Qdrant port (ignored if qdrant_client is provided).
        qdrant_client: Optional pre-built QdrantClient to inject (for testing or reuse).
        knowledge_dir: Path to knowledge root (used only for result context).
        verify_ssl: Whether to verify SSL certificates.

    Returns:
        List of QueryResult ordered by descending relevance score.
    """
    from qdrant_client import QdrantClient  # noqa: PLC0415

    # Embed the question
    vector = embed_query(question, model_id=model_id, verify_ssl=verify_ssl)

    # Build optional filter
    filt = build_processing_type_filter(processing_type)

    # Search Qdrant (use injected client if provided)
    client = qdrant_client if qdrant_client is not None else QdrantClient(host=qdrant_host, port=qdrant_port)
    hits = search_qdrant(client, vector, k=k, processing_type_filter=filt)

    # Format results
    kd = knowledge_dir or pathlib.Path(".")
    return format_results(hits, kd)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="RAG query engine: embed question → Qdrant top-k")
    parser.add_argument("--question", required=True, help="Question to answer")
    parser.add_argument("--k", type=int, default=DEFAULT_TOP_K, help=f"Top-k results (default: {DEFAULT_TOP_K})")
    parser.add_argument("--processing-type", default=None, help="Filter by processing type slug (e.g. nablarch-batch)")
    parser.add_argument("--model", default=DEFAULT_EMBED_MODEL_ID, help="Cohere Embed model ID")
    parser.add_argument("--qdrant-host", default=QDRANT_HOST)
    parser.add_argument("--qdrant-port", type=int, default=QDRANT_PORT)
    parser.add_argument("--no-verify-ssl", action="store_true", default=False)
    args = parser.parse_args()

    results = query(
        args.question,
        k=args.k,
        processing_type=args.processing_type,
        model_id=args.model,
        qdrant_host=args.qdrant_host,
        qdrant_port=args.qdrant_port,
        verify_ssl=not args.no_verify_ssl,
    )

    for r in results:
        print(f"{r.score:.4f}  {r.section_ref}  {r.title}")


if __name__ == "__main__":
    main()
