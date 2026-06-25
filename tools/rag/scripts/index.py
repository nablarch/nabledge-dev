"""RAG Indexing pipeline: Knowledge JSON → Cohere Embed → Qdrant.

Usage:
    python3 -m tools.rag.scripts.index \
        --knowledge-dir .claude/skills/nabledge-6/knowledge \
        --limit 10 \
        --model cohere.embed-multilingual-v3
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import uuid
from typing import Any

try:
    import boto3 as _boto3_module
except ImportError:  # allow importing without boto3 installed (unit tests)
    _boto3_module = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Path-based metadata derivation
# ---------------------------------------------------------------------------

_PROCESSING_TYPES = {
    "nablarch-batch",
    "mom-messaging",
    "http-messaging",
    "web-application",
    "db-messaging",
    "restful-web-service",
    "jakarta-batch",
}

_CATEGORIES = {"adapters", "handlers", "libraries"}


def derive_metadata_from_path(rel_path: pathlib.Path) -> dict[str, str]:
    """Derive processing_type and category from the relative JSON path.

    Args:
        rel_path: Path relative to the knowledge root directory.

    Returns:
        Dict with keys "processing_type" and "category".
    """
    parts = rel_path.parts
    processing_type = "none"
    category = "none"

    if len(parts) >= 2 and parts[0] == "processing-pattern":
        subdir = parts[1]
        if subdir in _PROCESSING_TYPES:
            processing_type = subdir
    elif len(parts) >= 2 and parts[0] == "component":
        subdir = parts[1]
        if subdir in _CATEGORIES:
            category = subdir

    return {"processing_type": processing_type, "category": category}


# ---------------------------------------------------------------------------
# Linked-page extraction
# ---------------------------------------------------------------------------

_JSON_REF_RE = re.compile(r"[\w/.-]+\.json")


def extract_linked_pages(content: str) -> list[str]:
    """Extract unique page IDs (basename without .json extension) from content.

    Args:
        content: Section content text.

    Returns:
        Deduplicated list of page IDs referenced in content.
    """
    matches = _JSON_REF_RE.findall(content)
    seen: list[str] = []
    seen_set: set[str] = set()
    for m in matches:
        # Take basename and strip .json extension
        basename = pathlib.PurePosixPath(m).name
        page_id = basename[: -len(".json")]
        if page_id not in seen_set:
            seen_set.add(page_id)
            seen.append(page_id)
    return seen


# ---------------------------------------------------------------------------
# classes.md parsing
# ---------------------------------------------------------------------------

def parse_classes_md(md_path: pathlib.Path) -> dict[str, list[str]]:
    """Parse classes.md and return a mapping from page_id to class names.

    Args:
        md_path: Path to the classes.md file.

    Returns:
        Dict mapping page_id (basename without .json) to list of class names.
        Returns empty dict if the file does not exist or cannot be parsed.
    """
    if not md_path.exists():
        return {}

    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    mapping: dict[str, list[str]] = {}
    current_path: str | None = None
    current_classes: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()

        # Detect "path: <relative-path>" line
        if stripped.startswith("path:"):
            # Save previous entry
            if current_path is not None:
                page_id = str(pathlib.PurePosixPath(current_path).with_suffix(""))
                mapping[page_id] = current_classes
            raw_path = stripped[len("path:"):].strip()
            current_path = raw_path
            current_classes = []
        elif stripped.startswith("- ") and current_path is not None:
            class_name = stripped[2:].strip()
            if class_name:
                current_classes.append(class_name)

    # Save last entry
    if current_path is not None:
        page_id = str(pathlib.PurePosixPath(current_path).with_suffix(""))
        mapping[page_id] = current_classes

    return mapping


# ---------------------------------------------------------------------------
# Chunk building
# ---------------------------------------------------------------------------

def build_chunks(
    page: dict[str, Any],
    rel_path: pathlib.Path,
    class_map: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Build one chunk per section in the page.

    Each chunk has:
      - text: "<page_title>\n<section_title>\n<section_content>"
      - metadata: processing_type, category, page_id, section_id, title,
                  level, class_names, linked_pages

    Args:
        page: Parsed JSON page dict.
        rel_path: Path relative to the knowledge root.
        class_map: Mapping from page_id to class names (from classes.md).

    Returns:
        List of chunk dicts (one per section).
    """
    path_meta = derive_metadata_from_path(rel_path)
    page_id: str = str(rel_path.with_suffix(""))
    page_title: str = page.get("title", "")
    class_names: list[str] = class_map.get(page_id, [])

    chunks: list[dict[str, Any]] = []
    for section in page.get("sections", []):
        section_title: str = section.get("title", "")
        section_content: str = section.get("content", "")
        section_id: str = section.get("id", "")
        level: int = section.get("level", 0)

        text = f"{page_title}\n{section_title}\n{section_content}"
        linked_pages = extract_linked_pages(section_content)

        metadata: dict[str, Any] = {
            "processing_type": path_meta["processing_type"],
            "category": path_meta["category"],
            "page_id": page_id,
            "section_id": section_id,
            "title": section_title,
            "level": level,
            "class_names": class_names,
            "linked_pages": linked_pages,
        }

        chunks.append({"text": text, "metadata": metadata})

    return chunks


# ---------------------------------------------------------------------------
# Bedrock Cohere Embed
# ---------------------------------------------------------------------------

_DEFAULT_EMBED_MODEL_ID = "cohere.embed-multilingual-v3"
_EMBED_REGION = "ap-northeast-1"
_EMBED_BATCH_SIZE = 96  # Cohere max per call

# Vector sizes by model
_MODEL_VECTOR_SIZES: dict[str, int] = {
    "cohere.embed-multilingual-v3": 1024,
    "cohere.embed-english-v3": 1024,
    "cohere.embed-v4:0": 1536,
}

# Max characters per text imposed by Bedrock for each model family.
# v3 enforces a 2048-character limit per text; v4 has no such restriction.
_MODEL_MAX_CHARS: dict[str, int] = {
    "cohere.embed-multilingual-v3": 2048,
    "cohere.embed-english-v3": 2048,
}


def embed_texts(
    texts: list[str],
    model_id: str = _DEFAULT_EMBED_MODEL_ID,
    verify_ssl: bool = True,
) -> list[list[float]]:
    """Embed texts using a Cohere Embed model via AWS Bedrock.

    Args:
        texts: List of text strings to embed.
        model_id: Bedrock model ID for the Cohere Embed model.
        verify_ssl: Whether to verify SSL certificates (set False for corporate proxies
                    with self-signed certificates).

    Returns:
        List of embedding vectors (one per input text).
    """
    import boto3 as _boto3  # noqa: PLC0415

    client = _boto3.client(
        "bedrock-runtime",
        region_name=_EMBED_REGION,
        verify=verify_ssl,
    )

    # Truncate texts that exceed the model's character limit.
    max_chars = _MODEL_MAX_CHARS.get(model_id)
    if max_chars is not None:
        texts = [t[:max_chars] for t in texts]

    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), _EMBED_BATCH_SIZE):
        batch = texts[i : i + _EMBED_BATCH_SIZE]
        body = json.dumps(
            {
                "texts": batch,
                "input_type": "search_document",
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
        # Cohere Embed returns embeddings under result["embeddings"]["float"]
        batch_embeddings = result["embeddings"]["float"]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


# ---------------------------------------------------------------------------
# Qdrant upsert
# ---------------------------------------------------------------------------

_QDRANT_HOST = "localhost"
_QDRANT_PORT = 6333
_COLLECTION_NAME = "nabledge-6"
_VECTOR_SIZE = 1024  # Cohere Embed v3 default; v4 is 1536
_UPSERT_BATCH_SIZE = 500  # keep each upsert well under Qdrant's 33 MB payload limit


def ensure_collection(client: Any, vector_size: int) -> None:
    """Create the Qdrant collection if it does not exist."""
    from qdrant_client.models import Distance, VectorParams  # noqa: PLC0415

    existing = {c.name for c in client.get_collections().collections}
    if _COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=_COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def upsert_chunks(
    client: Any,
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
) -> None:
    """Upsert chunks with their embeddings into Qdrant in batches."""
    from qdrant_client.models import PointStruct  # noqa: PLC0415

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=emb,
            payload=chunk["metadata"],
        )
        for chunk, emb in zip(chunks, embeddings)
    ]
    for i in range(0, len(points), _UPSERT_BATCH_SIZE):
        client.upsert(collection_name=_COLLECTION_NAME, points=points[i : i + _UPSERT_BATCH_SIZE])


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def load_json_files(
    knowledge_dir: pathlib.Path, limit: int | None
) -> list[tuple[pathlib.Path, dict[str, Any]]]:
    """Collect JSON files from knowledge_dir, optionally capped at limit."""
    files = sorted(knowledge_dir.rglob("*.json"))
    if limit is not None:
        files = files[:limit]
    results: list[tuple[pathlib.Path, dict[str, Any]]] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append((f, data))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Skipping {f}: {exc}", file=sys.stderr)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Index knowledge JSON into Qdrant via Cohere Embed.")
    parser.add_argument(
        "--knowledge-dir",
        required=True,
        type=pathlib.Path,
        help="Path to the nabledge-6 knowledge directory.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N JSON files (smoke-test mode).",
    )
    parser.add_argument(
        "--model",
        default=_DEFAULT_EMBED_MODEL_ID,
        help=f"Bedrock model ID for Cohere Embed (default: {_DEFAULT_EMBED_MODEL_ID}).",
    )
    parser.add_argument(
        "--qdrant-host",
        default=_QDRANT_HOST,
        help="Qdrant host (default: localhost).",
    )
    parser.add_argument(
        "--qdrant-port",
        type=int,
        default=_QDRANT_PORT,
        help="Qdrant port (default: 6333).",
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        default=False,
        help="Disable SSL certificate verification (for corporate proxies with self-signed certs).",
    )
    args = parser.parse_args()

    knowledge_dir: pathlib.Path = args.knowledge_dir.resolve()
    classes_md = knowledge_dir / "classes.md"

    print(f"Parsing classes.md from {classes_md}...")
    class_map = parse_classes_md(classes_md)
    print(f"  → {len(class_map)} page entries loaded.")

    print(f"Loading JSON files from {knowledge_dir} (limit={args.limit})...")
    pages = load_json_files(knowledge_dir, limit=args.limit)
    print(f"  → {len(pages)} files loaded.")

    # Build chunks
    all_chunks: list[dict[str, Any]] = []
    for json_path, page in pages:
        rel_path = json_path.relative_to(knowledge_dir)
        chunks = build_chunks(page, rel_path, class_map)
        all_chunks.extend(chunks)
    print(f"  → {len(all_chunks)} chunks built.")

    if not all_chunks:
        print("No chunks to index. Done.")
        return

    # Embed
    verify_ssl = not args.no_verify_ssl
    print(f"Embedding {len(all_chunks)} chunks via Bedrock {args.model} (verify_ssl={verify_ssl})...")
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts, model_id=args.model, verify_ssl=verify_ssl)
    print(f"  → {len(embeddings)} embeddings received.")

    # Infer vector size from first embedding; fall back to model lookup or default
    vector_size = (
        len(embeddings[0])
        if embeddings
        else _MODEL_VECTOR_SIZES.get(args.model, _VECTOR_SIZE)
    )

    # Qdrant
    print(f"Connecting to Qdrant at {args.qdrant_host}:{args.qdrant_port}...")
    from qdrant_client import QdrantClient  # noqa: PLC0415

    client = QdrantClient(host=args.qdrant_host, port=args.qdrant_port)
    ensure_collection(client, vector_size)
    upsert_chunks(client, all_chunks, embeddings)

    count = client.count(collection_name=_COLLECTION_NAME).count
    print(f"Done. Collection '{_COLLECTION_NAME}' now has {count} points.")


if __name__ == "__main__":
    main()
