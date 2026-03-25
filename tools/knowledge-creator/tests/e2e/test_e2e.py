"""E2E tests for kc commands (gen / gen --resume / regen --target / fix / fix --target).

Tests call run.py facade functions (kc_gen, kc_fix, etc.) with mocked CC.
CCの出力は決定的なので、最終出力の完全一致・ファイル数・CC呼び出し回数でアサートする。
Expected values are computed by generate_expected.py independently from kc source code.
"""
import json
import os
import shutil
import subprocess
import sys
import uuid

import pytest

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from run import Context, kc_gen, kc_regen_target, kc_fix, kc_fix_target, _run_pipeline, _make_args


# ============================================================
# IsolatedContext: redirects all permanent outputs to log_dir
# ============================================================

class IsolatedContext(Context):
    """Context that redirects all permanent outputs to log_dir.

    Prevents E2E tests from modifying production files.
    All paths are rooted under {repo}/tools/knowledge-creator/.logs/v{version}/{run_id}/
    which is gitignored.
    """

    @property
    def classified_list_path(self) -> str:
        return f"{self.log_dir}/catalog.json"

    @property
    def knowledge_cache_dir(self) -> str:
        return f"{self.log_dir}/knowledge-cache"

    @property
    def knowledge_dir(self) -> str:
        return f"{self.log_dir}/knowledge"

    @property
    def docs_dir(self) -> str:
        return f"{self.log_dir}/docs"

    @property
    def reports_dir(self) -> str:
        return f"{self.log_dir}/reports"


def _make_ctx(version="6", run_id=None, max_rounds=2):
    if run_id is None:
        run_id = f"e2e-{uuid.uuid4().hex[:8]}"
    ctx = IsolatedContext(version=version, repo=REPO, concurrency=4, run_id=run_id)
    ctx.max_rounds = max_rounds
    return ctx


def _run_with_mock(facade_fn, ctx, mock_fn, **kwargs):
    """ファサード関数をCCモック付きで呼ぶ。"""
    from unittest.mock import patch
    with patch("phase_b_generate._default_run_claude", mock_fn), \
         patch("phase_d_content_check._default_run_claude", mock_fn), \
         patch("phase_e_fix._default_run_claude", mock_fn), \
         patch("phase_v_evaluate._default_run_claude", mock_fn):
        facade_fn(ctx, **kwargs)


def _run_phase_a_only(ctx, mock_fn):
    """テストセットアップ用: Phase Aのみ実行。"""
    args = _make_args(ctx, phase="A")
    from unittest.mock import patch
    with patch("phase_b_generate._default_run_claude", mock_fn), \
         patch("phase_d_content_check._default_run_claude", mock_fn), \
         patch("phase_e_fix._default_run_claude", mock_fn), \
         patch("phase_v_evaluate._default_run_claude", mock_fn):
        _run_pipeline(ctx, args)


def _copy_state(src_ctx, dst_ctx):
    """Copy state directories from src_ctx to dst_ctx."""
    # catalog.json
    os.makedirs(os.path.dirname(dst_ctx.classified_list_path), exist_ok=True)
    shutil.copy2(src_ctx.classified_list_path, dst_ctx.classified_list_path)

    # knowledge_cache_dir
    if os.path.exists(src_ctx.knowledge_cache_dir):
        shutil.copytree(src_ctx.knowledge_cache_dir, dst_ctx.knowledge_cache_dir)

    # knowledge_dir
    if os.path.exists(src_ctx.knowledge_dir):
        shutil.copytree(src_ctx.knowledge_dir, dst_ctx.knowledge_dir)

    # docs_dir
    if os.path.exists(src_ctx.docs_dir):
        shutil.copytree(src_ctx.docs_dir, dst_ctx.docs_dir)


def _count_json_files(directory):
    """Count all .json files recursively in a directory, excluding assets/ subdirectories."""
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "assets"]
        count += sum(1 for f in files if f.endswith(".json"))
    return count


def _count_all_files(directory, ext=None):
    """Count all files (optionally with extension) recursively."""
    count = 0
    for root, _, files in os.walk(directory):
        if ext:
            count += sum(1 for f in files if f.endswith(ext))
        else:
            count += len(files)
    return count


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _assert_full_output(ctx, expected, catalog_entries, U, M,
                        expected_findings_count=0):
    """全kcコマンド共通の出力検証。

    Phase Mまで実行した後の全出力を検証する。
    CC呼び出し回数は各テストで個別にアサートするため含まない。

    expected_findings_count: Phase D が保存したラウンド番号付き findings ファイルの
        期待数。Phase D/E ループはラウンドごとに findings を保持する設計のため、
        findings_dir には processed_files × max_rounds 個のファイルが残る。
    """
    # catalog.json entries
    catalog = _load_json(ctx.classified_list_path)
    catalog_ids = {f["id"] for f in catalog["files"]}
    expected_ids = {e["id"] for e in catalog_entries}
    assert catalog_ids == expected_ids, (
        f"Catalog IDs mismatch: extra={catalog_ids - expected_ids}, "
        f"missing={expected_ids - catalog_ids}"
    )
    assert len(catalog["files"]) == U

    # knowledge_cache_dir
    assert _count_json_files(ctx.knowledge_cache_dir) == U, (
        f"Expected {U} files in knowledge_cache_dir, "
        f"got {_count_json_files(ctx.knowledge_cache_dir)}"
    )
    for entry in catalog_entries:
        cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
        assert os.path.exists(cache_path), f"Missing cache file: {cache_path}"

    # findings_dir: round-numbered findings files are preserved
    if os.path.isdir(ctx.findings_dir):
        actual_findings = _count_all_files(ctx.findings_dir, ".json")
        assert actual_findings == expected_findings_count, (
            f"findings_dir should have {expected_findings_count} round-numbered files, "
            f"got {actual_findings}"
        )
        # Verify all findings files follow _r{N}.json naming convention
        for root, _, files in os.walk(ctx.findings_dir):
            for f in files:
                if f.endswith(".json"):
                    assert "_r" in f, (
                        f"Findings file {f} missing round number suffix (_rN.json)"
                    )

    # cache content matches expected_fixed_cache
    for entry in catalog_entries:
        cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
        actual = _load_json(cache_path)
        assert actual == expected["expected_fixed_cache"][entry["id"]], (
            f"fixed_cache mismatch for {entry['id']}"
        )

    # knowledge_dir
    assert _count_json_files(ctx.knowledge_dir) == M, (
        f"Expected {M} files in knowledge_dir, "
        f"got {_count_json_files(ctx.knowledge_dir)}"
    )

    # merged file content
    expected_merged = expected["expected_merged_fixed"]
    for merged_id, expected_content in expected_merged.items():
        entry = None
        for e in catalog_entries:
            if e.get("base_name") == merged_id or e["id"] == merged_id:
                entry = e
                break
            if "split_info" in e and e["split_info"]["original_id"] == merged_id:
                entry = e
                break
        assert entry is not None, f"No catalog entry for merged_id {merged_id}"
        knowledge_path = (
            f"{ctx.knowledge_dir}/{entry['type']}/{entry['category']}/{merged_id}.json"
        )
        assert os.path.exists(knowledge_path), (
            f"Missing merged file: {knowledge_path}"
        )
        actual = _load_json(knowledge_path)
        assert actual == expected_content, (
            f"Merged file mismatch for {merged_id}"
        )

    # index.toon
    index_toon = f"{ctx.knowledge_dir}/index.toon"
    assert os.path.exists(index_toon), "Missing index.toon"
    content = open(index_toon, encoding="utf-8").read()
    assert content.startswith(expected["expected_index_toon_header"]), (
        f"index.toon header mismatch:\n"
        f"expected: {expected['expected_index_toon_header']!r}\n"
        f"got: {content[:100]!r}"
    )
    entry_count = sum(
        1 for line in content.splitlines() if line.startswith("  ")
    )
    assert entry_count == expected["expected_index_toon_entry_count"], (
        f"index.toon entry count: expected {expected['expected_index_toon_entry_count']}, "
        f"got {entry_count}"
    )

    # docs (M knowledge .md files + 1 README.md generated by Phase M)
    docs_count = _count_all_files(ctx.docs_dir)
    assert docs_count == M + 1, (
        f"Expected {M + 1} doc files (M={M} knowledge docs + 1 README.md), got {docs_count}"
    )

    # final catalog: split state
    final_catalog = _load_json(ctx.classified_list_path)
    final_ids = {f["id"] for f in final_catalog["files"]}
    assert final_ids == {e["id"] for e in catalog_entries}, (
        "catalog.json should be in split state after Phase M"
    )
    assert len(final_catalog["files"]) == U
    for f in final_catalog["files"]:
        entry = next(e for e in catalog_entries if e["id"] == f["id"])
        # Exclude section_map (added by production classify but not in test fixtures)
        f_cmp = {k: v for k, v in f.items() if k != "section_map"}
        assert f_cmp == entry, (
            f"Split catalog entry mismatch for {f['id']}"
        )
        assert "processing_patterns" not in f, (
            f"processing_patterns should not be in catalog for {f['id']}"
        )


# ============================================================
# CC Mock factory
# ============================================================

def _make_cc_mock(expected_knowledge_cache, expected_fixed_cache, counter):
    """Create CC mock for E2E tests.

    Phase B ("phase-b" in log_dir): returns expected_knowledge_cache[file_id]
    Phase D ("findings" in schema): always returns has_issues
    Phase V ("phase-v" in log_dir): returns minimal valid evaluate/integrate response
    Phase E (fallback): returns expected_fixed_cache[file_id]
    """
    def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
        schema_str = json.dumps(json_schema) if json_schema else ""
        log_dir_str = log_dir or ""

        if "phase-b" in log_dir_str:
            # Phase B: generate knowledge (direct JSON output, no trace wrapper)
            counter["B"].append(file_id)
            knowledge = expected_knowledge_cache[file_id]
            return subprocess.CompletedProcess(
                args=["claude"],
                returncode=0,
                stdout=json.dumps(knowledge),
                stderr="",
            )

        elif "phase-v" in log_dir_str:
            # Phase V: evaluate or integrate - return minimal valid responses
            # Must be checked before "findings" schema check since EVALUATE_SCHEMA
            # contains "findings_assessment" which matches "findings" in schema_str.
            if file_id == "integration":
                return subprocess.CompletedProcess(
                    args=["claude"],
                    returncode=0,
                    stdout=json.dumps({"proposals": []}),
                    stderr="",
                )
            else:
                return subprocess.CompletedProcess(
                    args=["claude"],
                    returncode=0,
                    stdout=json.dumps({
                        "file_id": file_id,
                        "user_impact": "low",
                        "needs_improvement": False,
                        "reason": "mock",
                        "findings_assessment": [],
                    }),
                    stderr="",
                )

        elif "findings" in schema_str:
            # Phase D: always has_issues
            counter["D"].append(file_id)
            return subprocess.CompletedProcess(
                args=["claude"],
                returncode=0,
                stdout=json.dumps({
                    "file_id": file_id,
                    "status": "has_issues",
                    "findings": [{
                        "category": "omission",
                        "severity": "minor",
                        "location": "s1",
                        "description": "Missing detail",
                    }],
                }),
                stderr="",
            )

        else:
            # Phase E: fix
            counter["E"].append(file_id)
            fixed = expected_fixed_cache[file_id]
            return subprocess.CompletedProcess(
                args=["claude"],
                returncode=0,
                stdout=json.dumps(fixed),
                stderr="",
            )

    return mock_fn


# ============================================================
# Session fixtures
# ============================================================

def _build_expected(repo, version):
    """Build expected values for a given version."""
    from generate_expected import (
        list_sources,
        classify_all,
        mock_phase_b_knowledge,
        mock_phase_e_knowledge,
        compute_merged_files,
    )
    import generate_expected as ge

    sources = list_sources(repo, version)
    catalog_entries = classify_all(sources, repo, version)

    ids = [e["id"] for e in catalog_entries]
    N = len(catalog_entries)
    U = len(set(ids))
    assert N == U, f"Duplicate IDs found: {N} entries, {U} unique"

    split_entries = [e for e in catalog_entries if "split_info" in e]
    non_split_entries = [e for e in catalog_entries if "split_info" not in e]
    split_groups = {}
    for e in split_entries:
        oid = e["split_info"]["original_id"]
        split_groups.setdefault(oid, []).append(e)

    expected_merged_b = compute_merged_files(catalog_entries)
    M = len(expected_merged_b)
    expected_merged_fixed = compute_merged_files(catalog_entries, knowledge_fn=ge.mock_phase_e_knowledge)

    pp_type_merged = set()
    for e in catalog_entries:
        if e["type"] == "processing-pattern":
            if "split_info" in e:
                pp_type_merged.add(e["split_info"]["original_id"])
            else:
                pp_type_merged.add(e["id"])

    F_TARGET = M - len(pp_type_merged)

    all_base_names = sorted(set(e.get('base_name', e['id']) for e in catalog_entries))
    target_base_names = all_base_names[:len(all_base_names) // 3]
    target_split_ids = []
    for bn in target_base_names:
        matched = [e["id"] for e in catalog_entries if e.get("base_name") == bn]
        target_split_ids.extend(matched)

    expected_knowledge_cache = {
        e["id"]: mock_phase_b_knowledge(e["id"], e) for e in catalog_entries
    }
    expected_fixed_cache = {
        e["id"]: mock_phase_e_knowledge(e["id"], e) for e in catalog_entries
    }

    expected_index_toon_header = (
        f"# Nabledge-{version} Knowledge Index\n\n"
        f"files[{M},]{{title,type,category,processing_patterns,path}}:"
    )

    return {
        "params": {
            "N": N,
            "U": U,
            "M": M,
            "F_TARGET": F_TARGET,
            "split_entries": len(split_entries),
            "non_split_entries": len(non_split_entries),
            "split_groups": len(split_groups),
            "pp_type_merged": len(pp_type_merged),
            "target_base_names": target_base_names,
            "target_split_ids": target_split_ids,
            "target_split_ids_count": len(target_split_ids),
        },
        "catalog_entries": catalog_entries,
        "expected_knowledge_cache": expected_knowledge_cache,
        "expected_fixed_cache": expected_fixed_cache,
        "expected_merged_knowledge": expected_merged_b,
        "expected_merged_fixed": expected_merged_fixed,
        "expected_index_toon_header": expected_index_toon_header,
        "expected_index_toon_entry_count": M,
    }


@pytest.fixture(scope="session")
def expected():
    """Generate all expected values for v6."""
    return _build_expected(REPO, "6")


@pytest.fixture(scope="session")
def expected_v5():
    """Generate all expected values for v5."""
    return _build_expected(REPO, "5")


@pytest.fixture(scope="session")
def gen_state(expected):
    ctx = _make_ctx(version="6", run_id=f"gen-state-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected["expected_knowledge_cache"],
        expected["expected_fixed_cache"],
        counter,
    )

    _run_with_mock(kc_gen, ctx, mock)

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


@pytest.fixture(scope="session")
def gen_state_v5(expected_v5):
    ctx = _make_ctx(version="5", run_id=f"gen-state-v5-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected_v5["expected_knowledge_cache"],
        expected_v5["expected_fixed_cache"],
        counter,
    )

    _run_with_mock(kc_gen, ctx, mock)

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


@pytest.fixture(scope="session")
def expected_v1_4():
    """Generate all expected values for v1.4."""
    return _build_expected(REPO, "1.4")


@pytest.fixture(scope="session")
def gen_state_v1_4(expected_v1_4):
    ctx = _make_ctx(version="1.4", run_id=f"gen-state-v1-4-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected_v1_4["expected_knowledge_cache"],
        expected_v1_4["expected_fixed_cache"],
        counter,
    )

    _run_with_mock(kc_gen, ctx, mock)

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


@pytest.fixture(scope="session")
def expected_v1_3():
    """Generate all expected values for v1.3."""
    return _build_expected(REPO, "1.3")


@pytest.fixture(scope="session")
def gen_state_v1_3(expected_v1_3):
    ctx = _make_ctx(version="1.3", run_id=f"gen-state-v1-3-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected_v1_3["expected_knowledge_cache"],
        expected_v1_3["expected_fixed_cache"],
        counter,
    )

    _run_with_mock(kc_gen, ctx, mock)

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


@pytest.fixture(scope="session")
def expected_v1_2():
    """Generate all expected values for v1.2."""
    return _build_expected(REPO, "1.2")


@pytest.fixture(scope="session")
def gen_state_v1_2(expected_v1_2):
    ctx = _make_ctx(version="1.2", run_id=f"gen-state-v1-2-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected_v1_2["expected_knowledge_cache"],
        expected_v1_2["expected_fixed_cache"],
        counter,
    )

    _run_with_mock(kc_gen, ctx, mock)

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


@pytest.fixture(scope="session", params=["6", "5", "1.4", "1.3", "1.2"])
def version_fixture(request):
    """Parametrized fixture providing version, expected values, and gen_state for v6, v5, and v1.x."""
    version = request.param
    if version == "6":
        return {"version": "6", "expected": request.getfixturevalue("expected"), "gen_state": request.getfixturevalue("gen_state")}
    elif version == "5":
        return {"version": "5", "expected": request.getfixturevalue("expected_v5"), "gen_state": request.getfixturevalue("gen_state_v5")}
    elif version == "1.4":
        return {"version": "1.4", "expected": request.getfixturevalue("expected_v1_4"), "gen_state": request.getfixturevalue("gen_state_v1_4")}
    elif version == "1.3":
        return {"version": "1.3", "expected": request.getfixturevalue("expected_v1_3"), "gen_state": request.getfixturevalue("gen_state_v1_3")}
    elif version == "1.2":
        return {"version": "1.2", "expected": request.getfixturevalue("expected_v1_2"), "gen_state": request.getfixturevalue("gen_state_v1_2")}


# ============================================================
# TestGen: full pipeline ABCDEM
# ============================================================

class TestGen:
    """test_gen: kc gen — Phase ABCDEM with clean state, verify all outputs."""

    def test_gen(self, version_fixture):
        version = version_fixture["version"]
        expected = version_fixture["expected"]
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        catalog_entries = expected["catalog_entries"]

        ctx = _make_ctx(version=version, max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            _run_with_mock(kc_gen, ctx, mock)

            _assert_full_output(ctx, expected, catalog_entries, U, M,
                                expected_findings_count=U * (ctx.max_rounds + 1))

            # CC call counts
            assert len(counter["B"]) == U, (
                f"counter['B'] expected {U}, got {len(counter['B'])}"
            )
            assert len(counter["D"]) == U * (ctx.max_rounds + 1), (
                f"counter['D'] expected {U * (ctx.max_rounds + 1)}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * ctx.max_rounds, (
                f"counter['E'] expected {U * ctx.max_rounds}, got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestGenPreserveSources: pre-existing sources are preserved
# ============================================================

class TestGenPreserveSources:
    """kc gen with pre-existing sources in catalog.json: sources must be preserved."""

    def test_gen_preserves_sources(self, version_fixture):
        version = version_fixture["version"]
        expected = version_fixture["expected"]

        ctx = _make_ctx(version=version, max_rounds=1)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        pre_sources = [
            {"repo": "https://github.com/nablarch/nablarch-document",
             "branch": "main", "revision": "abc123"},
            {"repo": "https://github.com/Fintan-contents/nablarch-system-development-guide",
             "branch": "main", "revision": "def456"},
        ]
        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        with open(ctx.classified_list_path, 'w', encoding='utf-8') as f:
            json.dump({"version": version, "sources": pre_sources, "files": []}, f)

        try:
            _run_with_mock(kc_gen, ctx, mock)

            catalog = _load_json(ctx.classified_list_path)

            # Verify catalog was populated with files by Phase A
            assert len(catalog.get("files", [])) > 0, (
                "catalog.json files should be populated by Phase A after kc_gen"
            )

            actual_sources = catalog.get("sources", [])
            assert len(actual_sources) == len(pre_sources), (
                f"sources count should be {len(pre_sources)}, got {len(actual_sources)}"
            )
            for i, (actual, pre) in enumerate(zip(actual_sources, pre_sources)):
                assert actual["repo"] == pre["repo"], (
                    f"sources[{i}].repo should be preserved: "
                    f"expected {pre['repo']!r}, got {actual['repo']!r}"
                )
                assert actual["branch"] == pre["branch"], (
                    f"sources[{i}].branch should be preserved: "
                    f"expected {pre['branch']!r}, got {actual['branch']!r}"
                )
                # commit may be updated by update_knowledge_meta (to HEAD of local repo,
                # or "" if repo not found); assert it is not silently cleared to None
                assert actual.get("revision") is not None, (
                    f"sources[{i}].commit should not be None after kc_gen"
                )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestGenResume: pre-place 1 file, Phase B skips it
# ============================================================

class TestGenResume:
    """test_gen_resume: kc gen --resume — 1 pre-placed file, Phase B skips it."""

    def test_gen_resume(self, version_fixture):
        version = version_fixture["version"]
        expected = version_fixture["expected"]
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        catalog_entries = expected["catalog_entries"]
        preplace_entry = catalog_entries[0]

        ctx = _make_ctx(version=version, max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Phase A only (to create catalog)
            _run_phase_a_only(ctx, mock)

            # Pre-place one knowledge file before Phase B
            pre_path = f"{ctx.knowledge_cache_dir}/{preplace_entry['output_path']}"
            os.makedirs(os.path.dirname(pre_path), exist_ok=True)
            pre_knowledge = expected["expected_knowledge_cache"][preplace_entry["id"]]
            with open(pre_path, "w", encoding="utf-8") as f:
                json.dump(pre_knowledge, f)

            # ABCDEM (Phase B should skip the pre-placed file)
            _run_with_mock(kc_gen, ctx, mock)

            _assert_full_output(ctx, expected, catalog_entries, U, M,
                                expected_findings_count=U * (ctx.max_rounds + 1))

            # CC call counts
            assert len(counter["B"]) == U - 1, (
                f"counter['B'] expected {U - 1}, got {len(counter['B'])}"
            )
            assert preplace_entry["id"] not in counter["B"], (
                f"Pre-placed file {preplace_entry['id']} should not be regenerated"
            )
            assert len(counter["D"]) == U * (ctx.max_rounds + 1), (
                f"counter['D'] expected {U * (ctx.max_rounds + 1)}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * ctx.max_rounds, (
                f"counter['E'] expected {U * ctx.max_rounds}, got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestRegenTarget: regenerate specific target files
# ============================================================

class TestRegenTarget:
    """test_regen_target: kc regen --target — Phase ABCDEM on 1/3 of base_names."""

    def test_regen_target(self, version_fixture):
        version = version_fixture["version"]
        expected = version_fixture["expected"]
        gen_state = version_fixture["gen_state"]
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        target_split_ids = params["target_split_ids"]
        target_count = params["target_split_ids_count"]
        catalog_entries = expected["catalog_entries"]

        target_base_names = params["target_base_names"]

        src_ctx = gen_state["ctx"]
        ctx = _make_ctx(version=version, max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Copy gen_state to new ctx
            _copy_state(src_ctx, ctx)

            _run_with_mock(kc_regen_target, ctx, mock, targets=target_base_names)

            _assert_full_output(ctx, expected, catalog_entries, U, M,
                                expected_findings_count=target_count * ctx.max_rounds + U)

            # CC call counts
            assert len(counter["B"]) == target_count, (
                f"counter['B'] expected {target_count}, got {len(counter['B'])}"
            )
            assert len(counter["D"]) == target_count * ctx.max_rounds + U, (
                f"counter['D'] expected {target_count * ctx.max_rounds + U}, "
                f"got {len(counter['D'])}"
            )
            assert len(counter["E"]) == target_count * ctx.max_rounds, (
                f"counter['E'] expected {target_count * ctx.max_rounds}, "
                f"got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestFix: full quality improvement + stale file deletion
# ============================================================

class TestFix:
    """test_fix: kc fix — Phase ACDEM (no B), stale file deleted after Phase M."""

    def test_fix(self, version_fixture):
        version = version_fixture["version"]
        expected = version_fixture["expected"]
        gen_state = version_fixture["gen_state"]
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        catalog_entries = expected["catalog_entries"]

        src_ctx = gen_state["ctx"]
        ctx = _make_ctx(version=version, max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Copy gen_state to new ctx
            _copy_state(src_ctx, ctx)

            # Place a stale file in knowledge_dir
            stale_dir = f"{ctx.knowledge_dir}/stale"
            os.makedirs(stale_dir, exist_ok=True)
            stale_path = f"{stale_dir}/stale-file.json"
            with open(stale_path, "w", encoding="utf-8") as f:
                json.dump({"id": "stale-file", "title": "Stale"}, f)

            _run_with_mock(kc_fix, ctx, mock)

            # TestFix-specific: stale file deleted (delete-insert)
            assert not os.path.exists(stale_path), (
                "Stale file should be deleted by Phase M (delete-insert)"
            )

            _assert_full_output(ctx, expected, catalog_entries, U, M,
                                expected_findings_count=U * (ctx.max_rounds + 1))

            # CC call counts
            assert len(counter["B"]) == 0, (
                f"counter['B'] expected 0 (no Phase B in fix), got {len(counter['B'])}"
            )
            assert len(counter["D"]) == U * (ctx.max_rounds + 1), (
                f"counter['D'] expected {U * (ctx.max_rounds + 1)}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * ctx.max_rounds, (
                f"counter['E'] expected {U * ctx.max_rounds}, got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestFixTarget: targeted quality improvement
# ============================================================

class TestFixTarget:
    """test_fix_target: kc fix --target — Phase ACDEM with target 1/3 of base_names."""

    def test_fix_target(self, version_fixture):
        version = version_fixture["version"]
        expected = version_fixture["expected"]
        gen_state = version_fixture["gen_state"]
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        target_split_ids = params["target_split_ids"]
        target_count = params["target_split_ids_count"]
        catalog_entries = expected["catalog_entries"]

        target_base_names = params["target_base_names"]

        src_ctx = gen_state["ctx"]
        ctx = _make_ctx(version=version, max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Copy gen_state to new ctx
            _copy_state(src_ctx, ctx)

            _run_with_mock(kc_fix_target, ctx, mock, targets=target_base_names)

            _assert_full_output(ctx, expected, catalog_entries, U, M,
                                expected_findings_count=target_count * ctx.max_rounds + U)

            # CC call counts
            assert len(counter["B"]) == 0, (
                f"counter['B'] expected 0 (no Phase B in fix), got {len(counter['B'])}"
            )
            assert len(counter["D"]) == target_count * ctx.max_rounds + U, (
                f"counter['D'] expected {target_count * ctx.max_rounds + U}, "
                f"got {len(counter['D'])}"
            )
            assert len(counter["E"]) == target_count * ctx.max_rounds, (
                f"counter['E'] expected {target_count * ctx.max_rounds}, "
                f"got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)
