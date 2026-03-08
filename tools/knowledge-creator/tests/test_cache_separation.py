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
    orig_fn = ge.mock_phase_b_knowledge
    ge.mock_phase_b_knowledge = ge.mock_phase_e_knowledge
    expected_merged_fixed = compute_merged_files(catalog_entries)
    ge.mock_phase_b_knowledge = orig_fn

    # Processing-pattern type files
    pp_type_merged = set()
    for e in catalog_entries:
        if e["type"] == "processing-pattern":
            if "split_info" in e:
                pp_type_merged.add(e["split_info"]["original_id"])
            else:
                pp_type_merged.add(e["id"])

    F_TARGET = M - len(pp_type_merged)

    # Persistent-error base_names → split IDs (24 base names, 57 IDs)
    persistent_error_base_names = [
        "adapters-doma_adaptor", "adapters-redisstore_lettuce_adaptor",
        "blank-project-CustomizeDB", "blank-project-setup_ContainerWeb",
        "cloud-native-aws_distributed_tracing", "db-messaging-multiple_process",
        "handlers-SessionStoreHandler", "handlers-csrf_token_verification_handler",
        "handlers-thread_context_handler", "java-static-analysis-java_static_analysis",
        "libraries-bean_validation", "libraries-database",
        "libraries-failure_log", "libraries-log",
        "libraries-service_availability", "libraries-tag",
        "libraries-tag_reference", "mom-messaging-feature_details",
        "nablarch-batch-architecture", "restful-web-service-architecture",
        "testing-framework-02_entityUnitTestWithNablarchValidation",
        "testing-framework-batch",
        "testing-framework-guide-development-guide-05-UnitTestGuide-02-RequestUnitTest",
        "toolbox-NablarchOpenApiGenerator",
    ]
    split_ids_24 = []
    for bn in persistent_error_base_names:
        matched = [e["id"] for e in catalog_entries if e.get("base_name") == bn]
        split_ids_24.extend(matched)

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
            "split_ids_24": split_ids_24,
            "split_ids_24_count": len(split_ids_24),
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
    """Run full ABCDEM pipeline once and return resulting (ctx, counter)."""
    from step1_list_sources import Step1ListSources
    from step2_classify import Step2Classify
    from phase_b_generate import PhaseBGenerate
    from phase_m_finalize import PhaseMFinalize

    ctx = _make_ctx(run_id=f"gen-state-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected["expected_knowledge_cache"],
        expected["expected_fixed_cache"],
        counter,
    )

    # Phase A
    sources = Step1ListSources(ctx).run()
    Step2Classify(ctx, sources_data=sources).run()

    # Phase B
    PhaseBGenerate(ctx, run_claude_fn=mock).run()

    # Phase C/D/E loop
    _run_cde_loop(ctx, expected, counter)

    # Phase M
    PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

    yield {"ctx": ctx, "counter": counter}

    # Cleanup after session
    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)


# ============================================================
# TestGen: full pipeline ABCDEM
# ============================================================

class TestGen:
    """test_gen: Phase ABCDEM with clean state, verify all outputs."""

    def test_gen(self, expected):
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_e_fix import PhaseEFix
        from phase_m_finalize import PhaseMFinalize

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
            # ---- Phase A ----
            sources = Step1ListSources(ctx).run()
            Step2Classify(ctx, sources_data=sources).run()

            # Assert: catalog.json entries match catalog_entries (full field match)
            catalog = _load_json(ctx.classified_list_path)
            catalog_ids = {f["id"] for f in catalog["files"]}
            expected_ids = {e["id"] for e in catalog_entries}
            assert catalog_ids == expected_ids, (
                f"Catalog IDs mismatch: extra={catalog_ids - expected_ids}, "
                f"missing={expected_ids - catalog_ids}"
            )
            assert len(catalog["files"]) == U
            for f in catalog["files"]:
                entry = next(e for e in catalog_entries if e["id"] == f["id"])
                assert f == entry, f"Catalog entry mismatch for {f['id']}"

            # ---- Phase B ----
            PhaseBGenerate(ctx, run_claude_fn=mock).run()

            # Assert: knowledge_cache_dir file count == U
            assert _count_json_files(ctx.knowledge_cache_dir) == U, (
                f"Expected {U} files in knowledge_cache_dir, "
                f"got {_count_json_files(ctx.knowledge_cache_dir)}"
            )

            # Assert: each cache file matches expected_knowledge_cache
            for entry in catalog_entries:
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                assert os.path.exists(cache_path), f"Missing cache file: {cache_path}"
                actual = _load_json(cache_path)
                assert actual == expected["expected_knowledge_cache"][entry["id"]], (
                    f"knowledge_cache mismatch for {entry['id']}"
                )

            # Assert: knowledge_dir has no JSON files (Phase B must not touch it)
            if os.path.exists(ctx.knowledge_dir):
                assert _count_json_files(ctx.knowledge_dir) == 0, (
                    "Phase B must not write to knowledge_dir"
                )

            # Assert: trace files match expected_traces (excluding generated_at)
            for entry in catalog_entries:
                trace_path = f"{ctx.trace_dir}/{entry['id']}.json"
                assert os.path.exists(trace_path), f"Missing trace file: {trace_path}"
                actual_trace = _load_json(trace_path)
                expected_trace = expected["expected_traces"][entry["id"]]
                actual_no_ts = {k: v for k, v in actual_trace.items() if k != "generated_at"}
                expected_no_ts = {k: v for k, v in expected_trace.items() if k != "generated_at"}
                assert actual_no_ts == expected_no_ts, (
                    f"Trace mismatch for {entry['id']}"
                )

            # ---- Phase C/D/E loop (max_rounds=2, always has_issues) ----
            phase_c = PhaseCStructureCheck(ctx)
            phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock)
            phase_e = PhaseEFix(ctx, run_claude_fn=mock)

            for round_num in range(1, ctx.max_rounds + 1):
                c_result = phase_c.run()
                d_result = phase_d.run(target_ids=c_result.get("pass_ids"))

                # Assert: findings_dir has U findings JSON files after Phase D
                assert os.path.isdir(ctx.findings_dir)
                findings_count = _count_all_files(ctx.findings_dir, ".json")
                assert findings_count == U, (
                    f"Round {round_num}: expected {U} findings, got {findings_count}"
                )

                phase_e.run(target_ids=d_result["issue_file_ids"])

                # Assert after Phase E round 1: sections have '-fixed' suffix
                if round_num == 1:
                    sample_entry = catalog_entries[0]
                    sample_cache = _load_json(
                        f"{ctx.knowledge_cache_dir}/{sample_entry['output_path']}"
                    )
                    for sid, content in sample_cache["sections"].items():
                        assert content.endswith("-fixed"), (
                            f"Round 1 E: section {sid} should end with -fixed"
                        )

                # Assert: findings_dir is empty after Phase E
                if os.path.isdir(ctx.findings_dir):
                    assert _count_all_files(ctx.findings_dir, ".json") == 0, (
                        f"Round {round_num}: findings_dir should be empty after Phase E"
                    )

            # Assert after all Phase E rounds: cache matches expected_fixed_cache
            for entry in catalog_entries:
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                actual = _load_json(cache_path)
                assert actual == expected["expected_fixed_cache"][entry["id"]], (
                    f"fixed_cache mismatch for {entry['id']}"
                )

            # ---- Phase M ----
            PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

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
            assert len(counter["F"]) == params["F_TARGET"], (
                f"counter['F'] expected {params['F_TARGET']}, got {len(counter['F'])}"
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
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify
        from phase_b_generate import PhaseBGenerate
        from phase_m_finalize import PhaseMFinalize

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
            # Phase A
            sources = Step1ListSources(ctx).run()
            Step2Classify(ctx, sources_data=sources).run()

            # Pre-place one knowledge file before Phase B
            pre_path = f"{ctx.knowledge_cache_dir}/{preplace_entry['output_path']}"
            os.makedirs(os.path.dirname(pre_path), exist_ok=True)
            pre_knowledge = expected["expected_knowledge_cache"][preplace_entry["id"]]
            with open(pre_path, "w", encoding="utf-8") as f:
                json.dump(pre_knowledge, f)

            # Phase B (should skip the pre-placed file)
            PhaseBGenerate(ctx, run_claude_fn=mock).run()

            # Assert: Phase B called U-1 times (skipped pre-placed file)
            assert len(counter["B"]) == U - 1, (
                f"counter['B'] expected {U - 1}, got {len(counter['B'])}"
            )
            assert preplace_entry["id"] not in counter["B"], (
                f"Pre-placed file {preplace_entry['id']} should not be regenerated"
            )

            # Phase C/D/E + Phase M
            _run_cde_loop(ctx, expected, counter)
            PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

            # Assert: D/E/F same as test_gen
            assert len(counter["D"]) == U * 2, (
                f"counter['D'] expected {U * 2}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * 2, (
                f"counter['E'] expected {U * 2}, got {len(counter['E'])}"
            )
            assert len(counter["F"]) == params["F_TARGET"], (
                f"counter['F'] expected {params['F_TARGET']}, got {len(counter['F'])}"
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
    """test_regen_target: Phase BCEM on split_ids_24 (57 files)."""

    def test_regen_target(self, gen_state, expected):
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_e_fix import PhaseEFix
        from phase_m_finalize import PhaseMFinalize
        from cleaner import clean_phase_artifacts

        params = expected["params"]
        M = params["M"]
        split_ids_24 = params["split_ids_24"]
        target_count = params["split_ids_24_count"]  # 57
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

            # Clean Phase B artifacts for target files (so Phase B re-generates them)
            clean_phase_artifacts(ctx, "B", target_ids=split_ids_24, yes=True)

            # Phase B (target_ids only)
            PhaseBGenerate(ctx, run_claude_fn=mock).run(target_ids=split_ids_24)

            # Assert: Phase B called exactly for target_ids
            assert set(counter["B"]) == set(split_ids_24), (
                f"counter['B'] should equal split_ids_24 (set):\n"
                f"  extra={set(counter['B']) - set(split_ids_24)}\n"
                f"  missing={set(split_ids_24) - set(counter['B'])}"
            )
            assert len(counter["B"]) == target_count, (
                f"counter['B'] expected {target_count}, got {len(counter['B'])}"
            )

            # Assert: knowledge_cache_dir has all U files
            all_entries = expected["catalog_entries"]
            for entry in all_entries:
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                assert os.path.exists(cache_path), (
                    f"Missing cache file after regen: {cache_path}"
                )

            # Phase C/D/E loop with target_ids
            phase_c = PhaseCStructureCheck(ctx)
            phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock)
            phase_e = PhaseEFix(ctx, run_claude_fn=mock)

            for _ in range(ctx.max_rounds):
                c_result = phase_c.run(target_ids=split_ids_24)
                d_ids = c_result.get("pass_ids", [])
                target_set = set(split_ids_24)
                d_ids = [fid for fid in d_ids if fid in target_set]
                d_result = phase_d.run(target_ids=d_ids)
                if not d_result.get("issue_file_ids"):
                    break
                phase_e.run(target_ids=d_result["issue_file_ids"])

            # Assert: D and E called target_count * max_rounds times
            assert len(counter["D"]) == target_count * ctx.max_rounds, (
                f"counter['D'] expected {target_count * ctx.max_rounds}, "
                f"got {len(counter['D'])}"
            )
            assert len(counter["E"]) == target_count * ctx.max_rounds, (
                f"counter['E'] expected {target_count * ctx.max_rounds}, "
                f"got {len(counter['E'])}"
            )

            # Phase M
            PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

            # Assert: knowledge_dir has all M files
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir, "
                f"got {_count_json_files(ctx.knowledge_dir)}"
            )

            # Assert: Phase F not called (processing_patterns already in catalog)
            assert len(counter["F"]) == 0, (
                f"counter['F'] should be 0 (processing_patterns preserved), "
                f"got {len(counter['F'])}"
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
        from phase_m_finalize import PhaseMFinalize

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

            # Phase C/D/E loop (no Phase A or B)
            _run_cde_loop(ctx, expected, counter)

            # Assert: B not called
            assert len(counter["B"]) == 0, (
                f"counter['B'] should be 0, got {len(counter['B'])}"
            )

            # Assert: D and E called U * max_rounds times
            assert len(counter["D"]) == U * ctx.max_rounds, (
                f"counter['D'] expected {U * ctx.max_rounds}, got {len(counter['D'])}"
            )
            assert len(counter["E"]) == U * ctx.max_rounds, (
                f"counter['E'] expected {U * ctx.max_rounds}, got {len(counter['E'])}"
            )

            # Assert: knowledge_cache_dir matches expected_fixed_cache
            for entry in catalog_entries:
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                actual = _load_json(cache_path)
                assert actual == expected["expected_fixed_cache"][entry["id"]], (
                    f"fixed_cache mismatch for {entry['id']}"
                )

            # Phase M
            PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

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

            # Assert: Phase F not called
            assert len(counter["F"]) == 0, (
                f"counter['F'] should be 0, got {len(counter['F'])}"
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
    """test_fix_target: Phase CDEM with --clean-phase D + target split_ids_24."""

    def test_fix_target(self, gen_state, expected):
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_e_fix import PhaseEFix
        from phase_m_finalize import PhaseMFinalize
        from cleaner import clean_phase_artifacts

        params = expected["params"]
        M = params["M"]
        split_ids_24 = params["split_ids_24"]
        target_count = params["split_ids_24_count"]  # 57
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

            # --clean-phase D for target files
            clean_phase_artifacts(ctx, "D", target_ids=split_ids_24, yes=True)

            # Phase C/D/E loop with target_ids (--clean-phase D + target)
            phase_c = PhaseCStructureCheck(ctx)
            phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock)
            phase_e = PhaseEFix(ctx, run_claude_fn=mock)

            for _ in range(ctx.max_rounds):
                c_result = phase_c.run(target_ids=split_ids_24)
                d_ids = c_result.get("pass_ids", [])
                target_set = set(split_ids_24)
                d_ids = [fid for fid in d_ids if fid in target_set]
                d_result = phase_d.run(target_ids=d_ids)
                if not d_result.get("issue_file_ids"):
                    break
                phase_e.run(target_ids=d_result["issue_file_ids"])

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
            for file_id in split_ids_24:
                entry = next(e for e in catalog_entries if e["id"] == file_id)
                cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
                actual = _load_json(cache_path)
                assert actual == expected["expected_fixed_cache"][file_id], (
                    f"Target file fixed_cache mismatch for {file_id}"
                )

            # Phase M
            PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

            # Assert: knowledge_dir has all M files
            assert _count_json_files(ctx.knowledge_dir) == M, (
                f"Expected {M} files in knowledge_dir, "
                f"got {_count_json_files(ctx.knowledge_dir)}"
            )

            # Assert: target merged files have -fixed in sections
            target_base_names = set()
            for fid in split_ids_24:
                entry = next(e for e in catalog_entries if e["id"] == fid)
                base = entry.get("base_name", fid)
                oid = entry.get("split_info", {}).get("original_id", base)
                target_base_names.add(oid)

            for merged_id in target_base_names:
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

            # Assert: Phase F not called
            assert len(counter["F"]) == 0, (
                f"counter['F'] should be 0, got {len(counter['F'])}"
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
