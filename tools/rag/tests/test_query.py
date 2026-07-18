"""Unit tests for query.py — RAG query engine.

No Bedrock or Qdrant calls are made in these tests (all external calls are mocked).
"""
from __future__ import annotations

import json
import sys
import pathlib
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Allow importing without Bedrock/Qdrant installed
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.parent))

from tools.rag.scripts.query import (
    embed_query,
    search_qdrant,
    build_processing_type_filter,
    format_results,
    QueryResult,
    DEFAULT_EMBED_MODEL_ID,
    DEFAULT_TOP_K,
    _COLLECTION_NAME,
)

# Backward-compat aliases used in existing tests and new truncation tests
_DEFAULT_EMBED_MODEL_ID = DEFAULT_EMBED_MODEL_ID
_DEFAULT_TOP_K = DEFAULT_TOP_K


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_qdrant_hit(page_id: str, section_id: str, processing_type: str, score: float) -> MagicMock:
    """Build a mock Qdrant ScoredPoint."""
    hit = MagicMock()
    hit.score = score
    hit.payload = {
        "page_id": page_id,
        "section_id": section_id,
        "processing_type": processing_type,
        "category": "none",
        "title": f"{page_id} {section_id}",
        "level": 0,
        "class_names": [],
        "linked_pages": [],
    }
    return hit


# ---------------------------------------------------------------------------
# embed_query
# ---------------------------------------------------------------------------

class TestEmbedQuery:
    """Tests for embed_query() — calls Bedrock with input_type=search_query."""

    def test_returns_vector_from_bedrock(self) -> None:
        # Given: Bedrock returns a 1024-dim embedding
        fake_vector = [0.1] * 1024
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.__getitem__ = lambda self, key: {"body": MagicMock(read=lambda: b'{"embeddings":{"float":[[0.1]*1024]}}')}[key]  # noqa: E501

        body_bytes = json.dumps({"embeddings": {"float": [fake_vector]}}).encode()
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        mock_client.invoke_model.return_value = {"body": mock_body}

        with patch("boto3.client", return_value=mock_client):
            # When: embed_query is called
            result = embed_query("test query", model_id=_DEFAULT_EMBED_MODEL_ID)

        # Then: returns the first embedding vector
        assert result == fake_vector

    def test_uses_search_query_input_type(self) -> None:
        # Given: Bedrock mock that captures the request body
        fake_vector = [0.0] * 1024
        body_bytes = json.dumps({"embeddings": {"float": [fake_vector]}}).encode()
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = {"body": mock_body}

        with patch("boto3.client", return_value=mock_client):
            # When
            embed_query("my question", model_id=_DEFAULT_EMBED_MODEL_ID)

        # Then: invoke_model was called with input_type=search_query in the body
        call_args = mock_client.invoke_model.call_args
        sent_body = json.loads(call_args.kwargs.get("body") or call_args.args[0] if call_args.args else call_args.kwargs["body"])
        assert sent_body["input_type"] == "search_query"

    def test_passes_text_in_texts_array(self) -> None:
        # Given
        fake_vector = [0.0] * 1024
        body_bytes = json.dumps({"embeddings": {"float": [fake_vector]}}).encode()
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = {"body": mock_body}

        with patch("boto3.client", return_value=mock_client):
            # When
            embed_query("hello world", model_id=_DEFAULT_EMBED_MODEL_ID)

        # Then
        call_args = mock_client.invoke_model.call_args
        body_arg = call_args.kwargs["body"]
        sent_body = json.loads(body_arg)
        assert "hello world" in sent_body["texts"]


# ---------------------------------------------------------------------------
# build_processing_type_filter
# ---------------------------------------------------------------------------

class TestBuildProcessingTypeFilter:
    """Tests for build_processing_type_filter() — metadata filter construction."""

    def test_no_filter_when_none(self) -> None:
        # Given / When
        result = build_processing_type_filter(None)
        # Then: no filter
        assert result is None

    def test_filter_includes_given_type_and_none(self) -> None:
        # When
        result = build_processing_type_filter("nablarch-batch")

        # Then: result is a Qdrant Filter that matches the type OR "none"
        assert result is not None
        values = _extract_match_any_values(result)
        assert "nablarch-batch" in values
        assert "none" in values

    def test_filter_structure_allows_none_type(self) -> None:
        # Given: slug "nablarch-batch"
        # When
        filt = build_processing_type_filter("nablarch-batch")

        # Then: the filter accepts both "nablarch-batch" and "none"
        # We verify by checking the MatchAny values list
        assert filt is not None
        # Traverse filter to find the MatchAny values
        values = _extract_match_any_values(filt)
        assert "nablarch-batch" in values
        assert "none" in values

    def test_filter_structure_web_application(self) -> None:
        # Given
        filt = build_processing_type_filter("web-application")
        # Then
        values = _extract_match_any_values(filt)
        assert "web-application" in values
        assert "none" in values


def _extract_match_any_values(filt: Any) -> list[str]:
    """Recursively extract values from MatchAny conditions in a Qdrant Filter."""
    if filt is None:
        return []
    values: list[str] = []
    # Filter may have .should (list of conditions) or .must
    for attr in ("should", "must", "must_not"):
        conditions = getattr(filt, attr, None) or []
        for cond in conditions:
            # FieldCondition has .match with MatchAny
            match = getattr(cond, "match", None)
            if match is not None:
                # MatchAny has .any; MatchValue has .value
                if hasattr(match, "any"):
                    values.extend(match.any)
                elif hasattr(match, "value"):
                    values.append(match.value)
            # Nested Filter
            if hasattr(cond, "should") or hasattr(cond, "must"):
                values.extend(_extract_match_any_values(cond))
    return values


# ---------------------------------------------------------------------------
# search_qdrant
# ---------------------------------------------------------------------------

class TestSearchQdrant:
    """Tests for search_qdrant() — Qdrant top-k retrieval via query_points."""

    def _make_mock_response(self, hits: list) -> MagicMock:
        """Build a mock QueryResponse with .points."""
        mock_response = MagicMock()
        mock_response.points = hits
        return mock_response

    def test_returns_top_k_hits(self) -> None:
        # Given: mock Qdrant client returning 10 hits
        mock_client = MagicMock()
        hits = [_make_qdrant_hit(f"page-{i}", "s1", "nablarch-batch", 0.9 - i * 0.05) for i in range(10)]
        mock_client.query_points.return_value = self._make_mock_response(hits)

        vector = [0.1] * 1024

        # When
        results = search_qdrant(mock_client, vector, k=10, processing_type_filter=None)

        # Then
        assert len(results) == 10
        mock_client.query_points.assert_called_once()

    def test_passes_filter_to_qdrant(self) -> None:
        # Given
        mock_client = MagicMock()
        mock_client.query_points.return_value = self._make_mock_response([])
        vector = [0.0] * 1024
        from qdrant_client.models import Filter
        fake_filter = MagicMock(spec=Filter)

        # When
        search_qdrant(mock_client, vector, k=10, processing_type_filter=fake_filter)

        # Then: query_filter is passed to client.query_points
        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs.get("query_filter") is fake_filter

    def test_uses_correct_collection_name(self) -> None:
        # Given
        mock_client = MagicMock()
        mock_client.query_points.return_value = self._make_mock_response([])
        vector = [0.0] * 1024

        # When
        search_qdrant(mock_client, vector, k=5, processing_type_filter=None)

        # Then
        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs.get("collection_name") == _COLLECTION_NAME

    def test_k_controls_limit(self) -> None:
        # Given
        mock_client = MagicMock()
        mock_client.query_points.return_value = self._make_mock_response([])
        vector = [0.0] * 1024

        # When
        search_qdrant(mock_client, vector, k=20, processing_type_filter=None)

        # Then: limit=20 passed to Qdrant (all args are keyword args)
        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs.get("limit") == 20


# ---------------------------------------------------------------------------
# format_results
# ---------------------------------------------------------------------------

class TestFormatResults:
    """Tests for format_results() — converts Qdrant hits to QueryResult."""

    def test_returns_query_result_list(self) -> None:
        # Given: two Qdrant hits
        hits = [
            _make_qdrant_hit("processing-pattern/nablarch-batch/arch", "s1", "nablarch-batch", 0.95),
            _make_qdrant_hit("processing-pattern/nablarch-batch/arch", "s2", "nablarch-batch", 0.80),
        ]
        knowledge_dir = pathlib.Path("/fake/knowledge")

        # When
        results = format_results(hits, knowledge_dir)

        # Then
        assert len(results) == 2
        assert all(isinstance(r, QueryResult) for r in results)

    def test_section_ref_format(self) -> None:
        # Given: hit with page_id="processing-pattern/nablarch-batch/arch" and section_id="s1"
        # The file path should be derived from page_id
        hits = [
            _make_qdrant_hit("processing-pattern/nablarch-batch/arch", "s1", "nablarch-batch", 0.9),
        ]
        knowledge_dir = pathlib.Path("/knowledge")

        # When
        results = format_results(hits, knowledge_dir)

        # Then: section_ref is in "path.json:sN" format
        assert results[0].section_ref == "processing-pattern/nablarch-batch/arch.json:s1"

    def test_scores_preserved(self) -> None:
        # Given
        hits = [
            _make_qdrant_hit("page-a", "s1", "none", 0.88),
            _make_qdrant_hit("page-b", "s2", "none", 0.75),
        ]

        # When
        results = format_results(hits, pathlib.Path("/knowledge"))

        # Then
        assert results[0].score == pytest.approx(0.88)
        assert results[1].score == pytest.approx(0.75)

    def test_selected_sections_structure(self) -> None:
        # Given: a hit whose page_id contains a subdirectory path
        hits = [
            _make_qdrant_hit("processing-pattern/nablarch-batch/nablarch-batch-architecture", "s1", "nablarch-batch", 0.9),
        ]

        # When
        results = format_results(hits, pathlib.Path("/knowledge"))

        # Then: selected_section has file and section_id fields
        ss = results[0].as_selected_section()
        assert "file" in ss
        assert "section_id" in ss
        assert ss["section_id"] == "s1"
        assert ss["file"] == "processing-pattern/nablarch-batch/nablarch-batch-architecture.json"

    def test_read_sections_format(self) -> None:
        # Given
        hits = [
            _make_qdrant_hit("processing-pattern/nablarch-batch/nablarch-batch-architecture", "s2", "nablarch-batch", 0.9),
        ]

        # When
        results = format_results(hits, pathlib.Path("/knowledge"))

        # Then: section_ref is "path/to/file.json:s2"
        ref = results[0].section_ref
        assert ref == "processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2"

    def test_empty_hits_returns_empty_list(self) -> None:
        # Given / When / Then
        assert format_results([], pathlib.Path("/knowledge")) == []

    def test_empty_page_id_hit_is_skipped(self) -> None:
        # Given: a hit with no page_id in payload
        bad_hit = MagicMock()
        bad_hit.score = 0.5
        bad_hit.payload = {"page_id": "", "section_id": "s1", "processing_type": "none",
                           "category": "none", "title": "", "level": 0, "class_names": [], "linked_pages": []}

        # When
        results = format_results([bad_hit], pathlib.Path("/knowledge"))

        # Then: skipped — no invalid QueryResult produced
        assert len(results) == 0


# ---------------------------------------------------------------------------
# embed_query truncation tests
# ---------------------------------------------------------------------------

class TestEmbedQueryTruncation:
    """Tests for embed_query() text truncation at model max chars boundary."""

    def test_truncates_long_text_to_model_max_chars(self) -> None:
        # Given: text longer than 2048 chars (model max for v3)
        long_text = "あ" * 3000
        captured_body: dict = {}

        def mock_invoke(**kwargs):  # type: ignore[no-untyped-def]
            captured_body.update(json.loads(kwargs["body"]))
            body_bytes = json.dumps({"embeddings": {"float": [[0.0] * 1024]}}).encode()
            mock_body = MagicMock()
            mock_body.read.return_value = body_bytes
            return {"body": mock_body}

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = mock_invoke

        with patch("boto3.client", return_value=mock_client):
            # When
            embed_query(long_text, model_id=_DEFAULT_EMBED_MODEL_ID)

        # Then: text was truncated to 2048 chars
        assert len(captured_body["texts"][0]) == 2048

    def test_does_not_truncate_short_text(self) -> None:
        # Given: text shorter than 2048 chars
        short_text = "短い質問"
        captured_body: dict = {}

        def mock_invoke(**kwargs):  # type: ignore[no-untyped-def]
            captured_body.update(json.loads(kwargs["body"]))
            body_bytes = json.dumps({"embeddings": {"float": [[0.0] * 1024]}}).encode()
            mock_body = MagicMock()
            mock_body.read.return_value = body_bytes
            return {"body": mock_body}

        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = mock_invoke

        with patch("boto3.client", return_value=mock_client):
            # When
            embed_query(short_text, model_id=_DEFAULT_EMBED_MODEL_ID)

        # Then: text is unchanged
        assert captured_body["texts"][0] == short_text


# ---------------------------------------------------------------------------
# query() orchestration tests
# ---------------------------------------------------------------------------

class TestQuery:
    """Integration test for query() — verifies wiring between embed, filter, search, format."""

    def test_returns_results_for_question_with_filter(self) -> None:
        # Given: mocked embed, Qdrant client, and a processed hit
        fake_vector = [0.1] * 1024
        fake_hit = _make_qdrant_hit("processing-pattern/nablarch-batch/arch", "s1", "nablarch-batch", 0.9)
        mock_qdrant_client = MagicMock()
        mock_response = MagicMock()
        mock_response.points = [fake_hit]
        mock_qdrant_client.query_points.return_value = mock_response

        body_bytes = json.dumps({"embeddings": {"float": [fake_vector]}}).encode()
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = {"body": mock_body}

        from tools.rag.scripts.query import query as rag_query

        with patch("boto3.client", return_value=mock_bedrock):
            # When: query() is called with filter
            results = rag_query(
                "Nablarchバッチの起動方法は？",
                k=10,
                processing_type="nablarch-batch",
                qdrant_client=mock_qdrant_client,
            )

        # Then: returns QueryResult list with correct section_ref
        assert len(results) == 1
        assert results[0].section_ref.endswith(".json:s1")
        assert results[0].processing_type == "nablarch-batch"
