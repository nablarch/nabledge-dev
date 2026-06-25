"""Unit tests for query.py — RAG query engine.

No Bedrock or Qdrant calls are made in these tests (all external calls are mocked).
"""
from __future__ import annotations

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
    _DEFAULT_EMBED_MODEL_ID,
    _DEFAULT_TOP_K,
    _COLLECTION_NAME,
)


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

        import json
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
        import json
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
        import json
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
        body_arg = call_args.kwargs.get("body") or (call_args.args[1] if len(call_args.args) > 1 else None)
        if body_arg is None:
            # try positional
            body_arg = call_args[1].get("body", "")
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
        # Given
        from qdrant_client.models import Filter, FieldCondition, MatchAny

        # When
        result = build_processing_type_filter("nablarch-batch")

        # Then: result is a Qdrant Filter that matches the type OR "none"
        assert result is not None
        # The filter should be a Filter object (or equivalent structure)
        # We check structure by inspecting the type
        assert hasattr(result, "should") or hasattr(result, "must")

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
        assert results[0].section_ref.endswith(".json:s1")

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

    def test_read_sections_format(self) -> None:
        # Given
        hits = [
            _make_qdrant_hit("processing-pattern/nablarch-batch/nablarch-batch-architecture", "s2", "nablarch-batch", 0.9),
        ]

        # When
        results = format_results(hits, pathlib.Path("/knowledge"))

        # Then: section_ref is "path/to/file.json:s2"
        ref = results[0].section_ref
        assert ref.endswith(".json:s2"), f"Expected .json:sN format, got: {ref}"
        assert ":" in ref

    def test_empty_hits_returns_empty_list(self) -> None:
        # Given / When / Then
        assert format_results([], pathlib.Path("/knowledge")) == []
