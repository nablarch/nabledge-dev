"""E2E tests verifying cache separation between knowledge_cache_dir and knowledge_dir.

Key invariants:
- Phase B writes to knowledge_cache_dir, NOT knowledge_dir
- Phase C/D/E read from knowledge_cache_dir
- Phase M reads from knowledge_cache_dir, writes to knowledge_dir (delete-insert)
- After Phase M, catalog.json is restored to split state
"""
import json
import os
import shutil
import subprocess
import sys
import uuid

import pytest

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from run import Context


# ============================================================
# TestContext: redirects all permanent outputs to log_dir
# ============================================================

class TestContext(Context):
    """Context that redirects all permanent outputs to log_dir.

    Prevents E2E tests from modifying production files.
    All paths are rooted under {repo}/tools/knowledge-creator/.logs/v{version}/{run_id}/
    which is gitignored.
    """

    @property
    def classified_list_path(self) -> str:
        return f"{self.log_dir}/catalog.json"

    @property
    def trace_dir(self) -> str:
        return f"{self.log_dir}/traces"

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


def _make_ctx(run_id=None, max_rounds=2):
    if run_id is None:
        run_id = f"e2e-{uuid.uuid4().hex[:8]}"
    ctx = TestContext(version="6", repo=REPO, concurrency=4, run_id=run_id)
    ctx.max_rounds = max_rounds
    return ctx


def _run_main(ctx, mock_fn, phases=None, target=None, clean_phase=None):
    """run.py main() を CC mock 付きで実行する。

    ctx は TestContext インスタンス。
    mock_fn は _make_cc_mock() の戻り値。
    """
    from unittest.mock import patch, MagicMock

    args = MagicMock()
    args.version = "6"
    args.phase = phases          # None = "ABCDEM"
    args.max_rounds = ctx.max_rounds
    args.concurrency = ctx.concurrency
    args.dry_run = False
    args.test = None
    args.run_id = ctx.run_id
    args.yes = True
    args.regen = False
    args.target = target         # list of base_names, or None
    args.clean_phase = clean_phase
    args.verbose = False

    original_abspath = os.path.abspath

    def patched_abspath(path):
        result = original_abspath(path)
        if result == original_abspath(os.path.join(TOOL_DIR, '..', '..')):
            return ctx.repo
        return result

    with patch("sys.argv", ["run.py", "--version", "6"]), \
         patch("argparse.ArgumentParser.parse_args", return_value=args), \
         patch("os.path.abspath", side_effect=patched_abspath), \
         patch("run.Context", lambda **kwargs: ctx), \
         patch("phase_b_generate._default_run_claude", mock_fn), \
         patch("phase_d_content_check._default_run_claude", mock_fn), \
         patch("phase_e_fix._default_run_claude", mock_fn), \
         patch("phase_f_finalize._default_run_claude", mock_fn):
        import run as run_module
        run_module.main()


def _copy_state(src_ctx, dst_ctx):
    """Copy state directories from src_ctx to dst_ctx."""
    # catalog.json
    os.makedirs(os.path.dirname(dst_ctx.classified_list_path), exist_ok=True)
    shutil.copy2(src_ctx.classified_list_path, dst_ctx.classified_list_path)

    # knowledge_cache_dir
    if os.path.exists(src_ctx.knowledge_cache_dir):
        shutil.copytree(src_ctx.knowledge_cache_dir, dst_ctx.knowledge_cache_dir)

    # trace_dir
    if os.path.exists(src_ctx.trace_dir):
        shutil.copytree(src_ctx.trace_dir, dst_ctx.trace_dir)

    # knowledge_dir
    if os.path.exists(src_ctx.knowledge_dir):
        shutil.copytree(src_ctx.knowledge_dir, dst_ctx.knowledge_dir)

    # docs_dir
    if os.path.exists(src_ctx.docs_dir):
        shutil.copytree(src_ctx.docs_dir, dst_ctx.docs_dir)


def _count_json_files(directory):
    """Count all .json files recursively in a directory."""
    count = 0
    for root, _, files in os.walk(directory):
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


# ============================================================
# CC Mock factory
# ============================================================

def _make_cc_mock(expected_knowledge_cache, expected_fixed_cache, counter):
    """Create CC mock for E2E tests.

    Phase B ("trace" in schema): returns expected_knowledge_cache[file_id]
    Phase D ("findings" in schema): always returns has_issues
    Phase F ("patterns" in schema): returns empty patterns
    Phase E (fallback): returns expected_fixed_cache[file_id]
    """
    def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
        schema_str = json.dumps(json_schema) if json_schema else ""

        if "trace" in schema_str:
            # Phase B: generate knowledge + trace
            counter["B"].append(file_id)
            knowledge = expected_knowledge_cache[file_id]
            trace = {
                "file_id": file_id,
                "generated_at": "2026-01-01T00:00:00Z",
                "sections": [
                    {
                        "section_id": e["id"],
                        "source_heading": e["title"],
                        "heading_level": "h2",
                        "h3_split": False,
                        "h3_split_reason": "mock",
                    }
                    for e in knowledge["index"]
                ],
            }
            return subprocess.CompletedProcess(
                args=["claude"],
                returncode=0,
                stdout=json.dumps({"knowledge": knowledge, "trace": trace}),
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
                        "location": "sec-0",
                        "description": "Missing detail",
                    }],
                }),
                stderr="",
            )

        elif "patterns" in schema_str:
            # Phase F: classify processing patterns
            counter["F"].append(file_id)
            return subprocess.CompletedProcess(
                args=["claude"],
                returncode=0,
                stdout=json.dumps({
                    "patterns": [],
                    "reasoning": [
                        {"pattern": "nablarch-batch", "matched": False, "evidence": "N/A"}
                    ],
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

@pytest.fixture(scope="session")
def expected():
    """Generate all expected values from generate_expected.py."""
    from generate_expected import (
        list_sources,
        classify_all,
        mock_phase_b_knowledge,
        mock_phase_b_trace,
        mock_phase_e_knowledge,
        compute_merged_files,
    )
    import generate_expected as ge

    sources = list_sources(REPO, "6")
    catalog_entries = classify_all(sources, REPO)

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

    # Merged files from Phase B output
    expected_merged_b = compute_merged_files(catalog_entries)
    M = len(expected_merged_b)

    # Merged files from Phase E output (used for Phase M assertions after Phase E runs)
    expected_merged_fixed = compute_merged_files(catalog_entries, knowledge_fn=ge.mock_phase_e_knowledge)

    # Processing-pattern type files
    pp_type_merged = set()
    for e in catalog_entries:
        if e["type"] == "processing-pattern":
            if "split_info" in e:
                pp_type_merged.add(e["split_info"]["original_id"])
            else:
                pp_type_merged.add(e["id"])

    F_TARGET = M - len(pp_type_merged)

    # 1/3 target: sorted base_names の先頭 1/3
    all_base_names = sorted(set(e.get('base_name', e['id']) for e in catalog_entries))
    target_base_names = all_base_names[:len(all_base_names) // 3]
    target_split_ids = []
    for bn in target_base_names:
        matched = [e["id"] for e in catalog_entries if e.get("base_name") == bn]
        target_split_ids.extend(matched)

    # Per-file expected outputs
    expected_knowledge_cache = {
        e["id"]: mock_phase_b_knowledge(e["id"], e) for e in catalog_entries
    }
    expected_traces = {
        e["id"]: mock_phase_b_trace(e["id"], e) for e in catalog_entries
    }
    expected_fixed_cache = {
        e["id"]: mock_phase_e_knowledge(e["id"], e) for e in catalog_entries
    }

    # index.toon expected header
    expected_index_toon_header = (
        f"# Nabledge-6 Knowledge Index\n\n"
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
        "expected_traces": expected_traces,
        "expected_fixed_cache": expected_fixed_cache,
        "expected_merged_knowledge": expected_merged_b,
        "expected_merged_fixed": expected_merged_fixed,
        "expected_index_toon_header": expected_index_toon_header,
        "expected_index_toon_entry_count": M,
    }


def _run_cde_loop(ctx, expected, counter, target_ids=None):
    """Run Phase C/D/E loop for max_rounds rounds."""
    from phase_c_structure_check import PhaseCStructureCheck
    from phase_d_content_check import PhaseDContentCheck
    from phase_e_fix import PhaseEFix

    mock = _make_cc_mock(
        expected["expected_knowledge_cache"],
        expected["expected_fixed_cache"],
        counter,
    )
    phase_c = PhaseCStructureCheck(ctx)
    phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock)
    phase_e = PhaseEFix(ctx, run_claude_fn=mock)

    for _ in range(ctx.max_rounds):
        c_result = phase_c.run(target_ids=target_ids)
        d_ids = c_result.get("pass_ids", [])
        if target_ids is not None:
            target_set = set(target_ids)
            d_ids = [fid for fid in d_ids if fid in target_set]
        d_result = phase_d.run(target_ids=d_ids)
        if not d_result.get("issue_file_ids"):
            break
        phase_e.run(target_ids=d_result["issue_file_ids"])

    return mock


@pytest.fixture(scope="session")
def gen_state(expected):
    ctx = _make_ctx(run_id=f"gen-state-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected["expected_knowledge_cache"],
        expected["expected_fixed_cache"],
        counter,
    )

    _run_main(ctx, mock)  # phases=None = ABCDEM

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


# ============================================================
# TestGen: full pipeline ABCDEM
# ============================================================

class TestGen:
    """test_gen: Phase ABCDEM with clean state, verify all outputs."""

    def test_gen(self, expected):
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        catalog_entries = expected["catalog_entries"]

        ctx = _make_ctx(max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            _run_main(ctx, mock)  # phases=None = ABCDEM

            # Assert: catalog.json entries match catalog_entries (full field match)
            catalog = _load_json(ctx.classified_list_path)
            catalog_ids = {f["id"] for f in catalog["files"]}
            expected_ids = {e["id"] for e in catalog_entries}
            assert catalog_ids == expected_ids, (
                f"Catalog IDs mismatch: extra={catalog_ids - expected_ids}, "
                f"missing={expected_ids - catalog_ids}"
            )
            assert len(catalog["files"]) == U

            # Assert: knowledge_cache_dir file count == U
            assert _count_json_files(ctx.knowledge_cache_dir) == U, (
                f"Expected {U} files in knowledge_cache_dir, "
                f"got {_count_json_files(ctx.knowledge_cache_dir)}"
            )

            # Assert: each cache file matches expected_fixed_cache (after Phase E)
            for entry in catalog_entries:
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                assert os.path.exists(cache_path), f"Missing cache file: {cache_path}"

            # Assert: findings_dir is empty after Phase E (Phase E clears it)
            if os.path.isdir(ctx.findings_dir):
                assert _count_all_files(ctx.findings_dir, ".json") == 0, (
                    "findings_dir should be empty after Phase E"
                )

            # Assert after all Phase E rounds: cache matches expected_fixed_cache
            for entry in catalog_entries:
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                actual = _load_json(cache_path)
                assert actual == expected["expected_fixed_cache"][entry["id"]], (
                    f"fixed_cache mismatch for {entry['id']}"
                )

            # Assert: knowledge_dir file count == M
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir, "
                f"got {_count_json_files(ctx.knowledge_dir)}"
            )

            # Assert: each merged file matches expected_merged_fixed
            expected_merged = expected["expected_merged_fixed"]
            for merged_id, expected_content in expected_merged.items():
                # Find type/category for this merged_id
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

            # Assert: trace_dir - split group merged traces exist, part traces deleted
            split_groups_by_oid = {}
            for e in catalog_entries:
                if "split_info" in e:
                    oid = e["split_info"]["original_id"]
                    split_groups_by_oid.setdefault(oid, []).append(e["id"])
            for oid, part_ids in split_groups_by_oid.items():
                # Merged trace should exist
                merged_trace = f"{ctx.trace_dir}/{oid}.json"
                assert os.path.exists(merged_trace), (
                    f"Missing merged trace for {oid}"
                )
                # Part traces should be deleted
                for part_id in part_ids:
                    part_trace = f"{ctx.trace_dir}/{part_id}.json"
                    assert not os.path.exists(part_trace), (
                        f"Part trace should be deleted after merge: {part_trace}"
                    )

            # Assert: knowledge_resolved_dir file count == M
            assert _count_json_files(ctx.knowledge_resolved_dir) == M, (
                f"Expected {M} resolved files, "
                f"got {_count_json_files(ctx.knowledge_resolved_dir)}"
            )

            # Assert: index.toon header and entry count
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

            # Assert: docs_dir file count == M
            docs_count = _count_all_files(ctx.docs_dir)
            assert docs_count == M, (
                f"Expected {M} doc files, got {docs_count}"
            )

            # Assert: catalog.json is in split state (catalog_entries + processing_patterns)
            final_catalog = _load_json(ctx.classified_list_path)
            final_ids = {f["id"] for f in final_catalog["files"]}
            assert final_ids == {e["id"] for e in catalog_entries}, (
                "catalog.json should be in split state after Phase M"
            )
            assert len(final_catalog["files"]) == U
            for f in final_catalog["files"]:
                entry = next(e for e in catalog_entries if e["id"] == f["id"])
                f_no_pp = {k: v for k, v in f.items() if k != "processing_patterns"}
                assert f_no_pp == entry, (
                    f"Split catalog entry mismatch for {f['id']} "
                    f"(excluding processing_patterns)"
                )
                assert "processing_patterns" in f, (
                    f"processing_patterns missing for {f['id']}"
                )

            # Assert: CC call counts
            assert len(counter["B"]) == U, (
                f"counter['B'] expected {U}, got {len(counter['B'])}"
            )
            assert len(counter["D"]) == U * 2, (
                f"counter['D'] expected {U * 2}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * 2, (
                f"counter['E'] expected {U * 2}, got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestGenResume: pre-place 1 file, Phase B skips it
# ============================================================

class TestGenResume:
    """test_gen_resume: 1 pre-placed file → Phase B called U-1 times."""

    def test_gen_resume(self, expected):
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        catalog_entries = expected["catalog_entries"]
        preplace_entry = catalog_entries[0]

        ctx = _make_ctx(max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Phase A only (to create catalog)
            _run_main(ctx, mock, phases="A")

            # Pre-place one knowledge file before Phase B
            pre_path = f"{ctx.knowledge_cache_dir}/{preplace_entry['output_path']}"
            os.makedirs(os.path.dirname(pre_path), exist_ok=True)
            pre_knowledge = expected["expected_knowledge_cache"][preplace_entry["id"]]
            with open(pre_path, "w", encoding="utf-8") as f:
                json.dump(pre_knowledge, f)

            # ABCDEM (Phase B should skip the pre-placed file)
            _run_main(ctx, mock)

            # Assert: Phase B called U-1 times (skipped pre-placed file)
            assert len(counter["B"]) == U - 1, (
                f"counter['B'] expected {U - 1}, got {len(counter['B'])}"
            )
            assert preplace_entry["id"] not in counter["B"], (
                f"Pre-placed file {preplace_entry['id']} should not be regenerated"
            )

            # Assert: D/E/F same as test_gen
            assert len(counter["D"]) == U * 2, (
                f"counter['D'] expected {U * 2}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * 2, (
                f"counter['E'] expected {U * 2}, got {len(counter['E'])}"
            )
            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

            # Assert: knowledge_dir has M files
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir"
            )

            # Assert: catalog is in split state
            final_catalog = _load_json(ctx.classified_list_path)
            final_ids = {f["id"] for f in final_catalog["files"]}
            assert final_ids == {e["id"] for e in catalog_entries}, (
                "catalog.json should be in split state"
            )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestRegenTarget: regenerate specific target files
# ============================================================

class TestRegenTarget:
    """test_regen_target: Phase BCEM on 1/3 of base_names."""

    def test_regen_target(self, gen_state, expected):
        params = expected["params"]
        M = params["M"]
        target_split_ids = params["target_split_ids"]
        target_count = params["target_split_ids_count"]
        catalog_entries = expected["catalog_entries"]

        target_base_names = params["target_base_names"]

        src_ctx = gen_state["ctx"]
        ctx = _make_ctx(max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Copy gen_state to new ctx
            _copy_state(src_ctx, ctx)

            _run_main(ctx, mock, phases="ABCDEM", target=target_base_names, clean_phase="BD")

            # Assert: knowledge_dir has all M files
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir, "
                f"got {_count_json_files(ctx.knowledge_dir)}"
            )

            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

            # Assert: catalog is in split state with processing_patterns
            final_catalog = _load_json(ctx.classified_list_path)
            final_ids = {f["id"] for f in final_catalog["files"]}
            assert final_ids == {e["id"] for e in catalog_entries}, (
                "catalog.json should be in split state after Phase M"
            )
            for f in final_catalog["files"]:
                assert "processing_patterns" in f, (
                    f"processing_patterns missing for {f['id']}"
                )

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestFix: full quality improvement + stale file deletion
# ============================================================

class TestFix:
    """test_fix: Phase CDEM (no A/B), stale file deleted after Phase M."""

    def test_fix(self, gen_state, expected):
        params = expected["params"]
        U = params["U"]
        M = params["M"]
        catalog_entries = expected["catalog_entries"]

        src_ctx = gen_state["ctx"]
        ctx = _make_ctx(max_rounds=2)
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

            _run_main(ctx, mock, phases="CDEM")

            # Assert: stale file deleted (delete-insert)
            assert not os.path.exists(stale_path), (
                "Stale file should be deleted by Phase M (delete-insert)"
            )

            # Assert: knowledge_dir has exactly M files
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir, "
                f"got {_count_json_files(ctx.knowledge_dir)}"
            )

            # Assert: each merged file has sections with -fixed suffix
            for merged_id, expected_content in expected["expected_merged_fixed"].items():
                entry = None
                for e in catalog_entries:
                    if e.get("base_name") == merged_id or e["id"] == merged_id:
                        entry = e
                        break
                    if "split_info" in e and e["split_info"]["original_id"] == merged_id:
                        entry = e
                        break
                assert entry is not None
                knowledge_path = (
                    f"{ctx.knowledge_dir}/{entry['type']}/{entry['category']}/{merged_id}.json"
                )
                actual = _load_json(knowledge_path)
                for sid, content in actual["sections"].items():
                    assert "-fixed" in content, (
                        f"sections should contain -fixed in {merged_id}.{sid}"
                    )

            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

            # Assert: catalog is in split state
            final_catalog = _load_json(ctx.classified_list_path)
            final_ids = {f["id"] for f in final_catalog["files"]}
            assert final_ids == {e["id"] for e in catalog_entries}
            for f in final_catalog["files"]:
                assert "processing_patterns" in f

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)


# ============================================================
# TestFixTarget: targeted quality improvement
# ============================================================

class TestFixTarget:
    """test_fix_target: Phase CDEM with --clean-phase D + target 1/3 of base_names."""

    def test_fix_target(self, gen_state, expected):
        params = expected["params"]
        M = params["M"]
        target_split_ids = params["target_split_ids"]
        target_count = params["target_split_ids_count"]
        catalog_entries = expected["catalog_entries"]

        target_base_names = params["target_base_names"]

        src_ctx = gen_state["ctx"]
        ctx = _make_ctx(max_rounds=2)
        counter = {"B": [], "D": [], "E": [], "F": []}
        mock = _make_cc_mock(
            expected["expected_knowledge_cache"],
            expected["expected_fixed_cache"],
            counter,
        )

        try:
            # Copy gen_state to new ctx
            _copy_state(src_ctx, ctx)

            _run_main(ctx, mock, phases="CDEM", target=target_base_names, clean_phase="D")

            # Assert: B not called
            assert len(counter["B"]) == 0, (
                f"counter['B'] should be 0, got {len(counter['B'])}"
            )

            # Assert: D and E called target_count * max_rounds times
            assert len(counter["D"]) == target_count * ctx.max_rounds, (
                f"counter['D'] expected {target_count * ctx.max_rounds}, "
                f"got {len(counter['D'])}"
            )
            assert len(counter["E"]) == target_count * ctx.max_rounds, (
                f"counter['E'] expected {target_count * ctx.max_rounds}, "
                f"got {len(counter['E'])}"
            )

            # Assert: target files in knowledge_cache_dir match expected_fixed_cache
            for file_id in target_split_ids:
                entry = next(e for e in catalog_entries if e["id"] == file_id)
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                actual = _load_json(cache_path)
                assert actual == expected["expected_fixed_cache"][file_id], (
                    f"Target file fixed_cache mismatch for {file_id}"
                )

            # Assert: knowledge_dir has all M files
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir, "
                f"got {_count_json_files(ctx.knowledge_dir)}"
            )

            # Assert: target merged files have -fixed in sections
            target_merged_ids = set()
            for fid in target_split_ids:
                entry = next(e for e in catalog_entries if e["id"] == fid)
                base = entry.get("base_name", fid)
                oid = entry.get("split_info", {}).get("original_id", base)
                target_merged_ids.add(oid)

            for merged_id in target_merged_ids:
                entry = None
                for e in catalog_entries:
                    if e.get("base_name") == merged_id or e["id"] == merged_id:
                        entry = e
                        break
                    if "split_info" in e and e["split_info"]["original_id"] == merged_id:
                        entry = e
                        break
                assert entry is not None
                knowledge_path = (
                    f"{ctx.knowledge_dir}/{entry['type']}/{entry['category']}/{merged_id}.json"
                )
                actual = _load_json(knowledge_path)
                for sid, content in actual["sections"].items():
                    assert "-fixed" in content, (
                        f"Target merged file {merged_id}.{sid} should have -fixed"
                    )

            assert len(counter["F"]) == 0, (
                f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
            )

            # Assert: catalog in split state with processing_patterns
            final_catalog = _load_json(ctx.classified_list_path)
            final_ids = {f["id"] for f in final_catalog["files"]}
            assert final_ids == {e["id"] for e in catalog_entries}
            for f in final_catalog["files"]:
                assert "processing_patterns" in f

        finally:
            if os.path.exists(ctx.log_dir):
                shutil.rmtree(ctx.log_dir)
