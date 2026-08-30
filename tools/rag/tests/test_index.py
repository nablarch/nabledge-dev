"""Unit tests for index.py chunking and metadata derivation.

No Bedrock or Qdrant calls are made in these tests.
"""
from __future__ import annotations

import json
import pathlib
import textwrap
import tempfile
import os
import sys
from unittest.mock import MagicMock, patch
import pytest

# Allow importing index module without Bedrock/Qdrant being available
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.parent))

from tools.rag.scripts.index import (
    derive_metadata_from_path,
    build_chunks,
    parse_classes_md,
    extract_linked_pages,
    embed_texts,
    _MODEL_VECTOR_SIZES,
    _VECTOR_SIZE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_page() -> dict:
    return {
        "id": "nablarch-batch-architecture",
        "title": "アーキテクチャ概要",
        "content": "intro text",
        "no_knowledge_content": False,
        "sections": [
            {
                "id": "s1",
                "title": "Nablarchバッチの構成",
                "level": 2,
                "content": "Content referencing ../../component/handlers/handlers-main.json#anchor",
            },
            {
                "id": "s2",
                "title": "処理の流れ",
                "level": 2,
                "content": "No references here.",
            },
        ],
    }


@pytest.fixture()
def classes_md_text() -> str:
    return textwrap.dedent("""\
        # Class Index

        ## component

        ### Domaアダプタ
        path: component/adapters/adapters-doma-adaptor.json
        - Transactional
        - DomaDaoRepository

        ### バッチアーキテクチャ
        path: processing-pattern/nablarch-batch/nablarch-batch-architecture.json
        - BatchActionBase
        - RequestHandlerEntry
    """)


# ---------------------------------------------------------------------------
# derive_metadata_from_path
# ---------------------------------------------------------------------------

class TestDeriveMetadataFromPath:
    def test_processing_pattern_returns_processing_type(self):
        path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        meta = derive_metadata_from_path(path)
        assert meta["processing_type"] == "nablarch-batch"
        assert meta["category"] == "none"

    def test_component_returns_category(self):
        path = pathlib.Path("component/handlers/handlers-main.json")
        meta = derive_metadata_from_path(path)
        assert meta["processing_type"] == "none"
        assert meta["category"] == "handlers"

    def test_other_path_returns_none_for_both(self):
        path = pathlib.Path("about/about-nablarch/about-nablarch-concept.json")
        meta = derive_metadata_from_path(path)
        assert meta["processing_type"] == "none"
        assert meta["category"] == "none"

    def test_all_processing_type_values(self):
        valid_types = [
            "nablarch-batch",
            "mom-messaging",
            "http-messaging",
            "web-application",
            "db-messaging",
            "restful-web-service",
            "jakarta-batch",
        ]
        for pt in valid_types:
            path = pathlib.Path(f"processing-pattern/{pt}/some-file.json")
            meta = derive_metadata_from_path(path)
            assert meta["processing_type"] == pt

    def test_all_category_values(self):
        valid_categories = ["adapters", "handlers", "libraries"]
        for cat in valid_categories:
            path = pathlib.Path(f"component/{cat}/some-file.json")
            meta = derive_metadata_from_path(path)
            assert meta["category"] == cat


# ---------------------------------------------------------------------------
# extract_linked_pages
# ---------------------------------------------------------------------------

class TestExtractLinkedPages:
    def test_extracts_json_references(self):
        content = "See ../../component/handlers/handlers-main.json#anchor for details."
        result = extract_linked_pages(content)
        assert "handlers-main" in result

    def test_extracts_multiple_references(self):
        content = (
            "See foo.json and bar.json also baz-qux.json."
        )
        result = extract_linked_pages(content)
        assert "foo" in result
        assert "bar" in result
        assert "baz-qux" in result

    def test_no_references_returns_empty(self):
        content = "No references here at all."
        result = extract_linked_pages(content)
        assert result == []

    def test_deduplicates_repeated_references(self):
        content = "See foo.json and foo.json again."
        result = extract_linked_pages(content)
        assert result.count("foo") == 1

    def test_extracts_basename_without_extension(self):
        content = "some/path/to/my-page.json#section"
        result = extract_linked_pages(content)
        assert "my-page" in result
        # Should not include path prefix
        for item in result:
            assert "/" not in item


# ---------------------------------------------------------------------------
# parse_classes_md
# ---------------------------------------------------------------------------

class TestParseClassesMd:
    def test_parses_class_names_for_page(self, classes_md_text, tmp_path):
        md_path = tmp_path / "classes.md"
        md_path.write_text(classes_md_text, encoding="utf-8")
        mapping = parse_classes_md(md_path)
        # page id = basename without .json
        assert "processing-pattern/nablarch-batch/nablarch-batch-architecture" in mapping
        assert "BatchActionBase" in mapping["processing-pattern/nablarch-batch/nablarch-batch-architecture"]
        assert "RequestHandlerEntry" in mapping["processing-pattern/nablarch-batch/nablarch-batch-architecture"]

    def test_parses_component_page_classes(self, classes_md_text, tmp_path):
        md_path = tmp_path / "classes.md"
        md_path.write_text(classes_md_text, encoding="utf-8")
        mapping = parse_classes_md(md_path)
        assert "component/adapters/adapters-doma-adaptor" in mapping
        assert "Transactional" in mapping["component/adapters/adapters-doma-adaptor"]
        assert "DomaDaoRepository" in mapping["component/adapters/adapters-doma-adaptor"]

    def test_returns_empty_dict_if_file_missing(self, tmp_path):
        md_path = tmp_path / "nonexistent.md"
        mapping = parse_classes_md(md_path)
        assert mapping == {}


# ---------------------------------------------------------------------------
# build_chunks
# ---------------------------------------------------------------------------

class TestBuildChunks:
    def test_chunk_count_equals_section_count(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert len(chunks) == 2

    def test_chunk_text_includes_page_and_section_title(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        text = chunks[0]["text"]
        assert "アーキテクチャ概要" in text  # page title
        assert "Nablarchバッチの構成" in text  # section title

    def test_chunk_text_includes_section_content(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        text = chunks[0]["text"]
        assert "Content referencing" in text

    def test_metadata_processing_type(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["processing_type"] == "nablarch-batch"

    def test_metadata_category_none_for_processing_pattern(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["category"] == "none"

    def test_metadata_page_id(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["page_id"] == "processing-pattern/nablarch-batch/nablarch-batch-architecture"

    def test_metadata_section_id(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["section_id"] == "s1"
        assert chunks[1]["metadata"]["section_id"] == "s2"

    def test_metadata_title_is_section_title(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["title"] == "Nablarchバッチの構成"

    def test_metadata_level(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["level"] == 2

    def test_metadata_linked_pages(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        # s1 references handlers-main.json
        assert "handlers-main" in chunks[0]["metadata"]["linked_pages"]
        # s2 has no references
        assert chunks[1]["metadata"]["linked_pages"] == []

    def test_metadata_class_names_from_map(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        class_map = {"processing-pattern/nablarch-batch/nablarch-batch-architecture": ["BatchActionBase", "RequestHandlerEntry"]}
        chunks = build_chunks(sample_page, rel_path, class_map=class_map)
        # Both sections of the same page get the same class_names
        assert "BatchActionBase" in chunks[0]["metadata"]["class_names"]
        assert "RequestHandlerEntry" in chunks[0]["metadata"]["class_names"]

    def test_metadata_class_names_empty_when_not_in_map(self, sample_page):
        rel_path = pathlib.Path("processing-pattern/nablarch-batch/nablarch-batch-architecture.json")
        chunks = build_chunks(sample_page, rel_path, class_map={})
        assert chunks[0]["metadata"]["class_names"] == []

    def test_empty_sections_returns_empty_list(self):
        page = {
            "id": "empty-page",
            "title": "Empty",
            "content": "intro",
            "no_knowledge_content": False,
            "sections": [],
        }
        rel_path = pathlib.Path("about/empty-page.json")
        chunks = build_chunks(page, rel_path, class_map={})
        assert chunks == []

    def test_chunk_for_component_category(self):
        page = {
            "id": "handlers-main",
            "title": "共通起動ランチャ",
            "content": "intro",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "level": 2, "content": "details"},
            ],
        }
        rel_path = pathlib.Path("component/handlers/handlers-main.json")
        chunks = build_chunks(page, rel_path, class_map={})
        assert chunks[0]["metadata"]["category"] == "handlers"
        assert chunks[0]["metadata"]["processing_type"] == "none"


# ---------------------------------------------------------------------------
# _MODEL_VECTOR_SIZES
# ---------------------------------------------------------------------------

class TestModelVectorSizes:
    def test_v3_multilingual_size(self):
        assert _MODEL_VECTOR_SIZES["cohere.embed-multilingual-v3"] == 1024

    def test_v3_english_size(self):
        assert _MODEL_VECTOR_SIZES["cohere.embed-english-v3"] == 1024

    def test_v4_size(self):
        assert _MODEL_VECTOR_SIZES["cohere.embed-v4:0"] == 1536

    def test_unknown_model_fallback_equals_default_vector_size(self):
        assert _MODEL_VECTOR_SIZES.get("unknown-model", _VECTOR_SIZE) == _VECTOR_SIZE


# ---------------------------------------------------------------------------
# embed_texts truncation logic (Bedrock mocked)
# ---------------------------------------------------------------------------

def _make_mock_boto3_client(vectors: list[list[float]]):
    """Return a mock boto3 bedrock-runtime client that yields `vectors`."""
    mock_response = MagicMock()
    mock_response["body"].read.return_value = json.dumps(
        {"embeddings": {"float": vectors}}
    ).encode()
    mock_client = MagicMock()
    mock_client.invoke_model.return_value = mock_response
    return mock_client


class TestEmbedTextsModelMaxChars:
    """Verify that embed_texts truncates texts for v3 models and not for v4."""

    def _stub_vectors(self, n: int) -> list[list[float]]:
        return [[0.1] * 1024 for _ in range(n)]

    def test_v3_text_exceeding_limit_is_truncated(self):
        long_text = "a" * 2049
        captured: list[list[str]] = []

        def fake_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            captured.append(body["texts"])
            vectors = self._stub_vectors(len(body["texts"]))
            mock_resp = MagicMock()
            mock_resp["body"].read.return_value = json.dumps(
                {"embeddings": {"float": vectors}}
            ).encode()
            return mock_resp

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = fake_invoke_model

        with patch("boto3.client") as mock_boto3:
            mock_boto3.return_value = mock_client
            embed_texts([long_text], model_id="cohere.embed-multilingual-v3")

        assert len(captured[0][0]) == 2048

    def test_v3_text_at_exact_limit_is_not_modified(self):
        exact_text = "b" * 2048
        captured: list[list[str]] = []

        def fake_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            captured.append(body["texts"])
            vectors = self._stub_vectors(len(body["texts"]))
            mock_resp = MagicMock()
            mock_resp["body"].read.return_value = json.dumps(
                {"embeddings": {"float": vectors}}
            ).encode()
            return mock_resp

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = fake_invoke_model

        with patch("boto3.client") as mock_boto3:
            mock_boto3.return_value = mock_client
            embed_texts([exact_text], model_id="cohere.embed-multilingual-v3")

        assert len(captured[0][0]) == 2048

    def test_v3_text_below_limit_is_unchanged(self):
        short_text = "c" * 100
        captured: list[list[str]] = []

        def fake_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            captured.append(body["texts"])
            vectors = self._stub_vectors(len(body["texts"]))
            mock_resp = MagicMock()
            mock_resp["body"].read.return_value = json.dumps(
                {"embeddings": {"float": vectors}}
            ).encode()
            return mock_resp

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = fake_invoke_model

        with patch("boto3.client") as mock_boto3:
            mock_boto3.return_value = mock_client
            embed_texts([short_text], model_id="cohere.embed-multilingual-v3")

        assert len(captured[0][0]) == 100

    def test_v4_text_exceeding_v3_limit_is_not_truncated(self):
        long_text = "d" * 3000
        captured: list[list[str]] = []

        def fake_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            captured.append(body["texts"])
            vectors = [[0.1] * 1536 for _ in body["texts"]]
            mock_resp = MagicMock()
            mock_resp["body"].read.return_value = json.dumps(
                {"embeddings": {"float": vectors}}
            ).encode()
            return mock_resp

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = fake_invoke_model

        with patch("boto3.client") as mock_boto3:
            mock_boto3.return_value = mock_client
            embed_texts([long_text], model_id="cohere.embed-v4:0")

        assert len(captured[0][0]) == 3000

    def test_unknown_model_text_is_not_truncated(self):
        long_text = "e" * 3000
        captured: list[list[str]] = []

        def fake_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            captured.append(body["texts"])
            vectors = self._stub_vectors(len(body["texts"]))
            mock_resp = MagicMock()
            mock_resp["body"].read.return_value = json.dumps(
                {"embeddings": {"float": vectors}}
            ).encode()
            return mock_resp

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = fake_invoke_model

        with patch("boto3.client") as mock_boto3:
            mock_boto3.return_value = mock_client
            embed_texts([long_text], model_id="some-unknown-model")

        assert len(captured[0][0]) == 3000
