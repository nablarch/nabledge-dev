# 作業指示: E2Eテスト アサート漏れ修正

## 対象ファイル

`tools/knowledge-creator/tests/e2e/test_e2e.py`

## 作業ルール

- 以下の「完成形コード」をそのまま使う。エージェントが独自にアサートを考えて書かない
- 変更後 `cd tools/knowledge-creator && python -m pytest tests/e2e/ -x -v` を実行し全件passを確認する
- failしたらcounterの実測値をprint出力して報告する。独自判断で期待値を変えない

## 変更1: _assert_full_output ヘルパー追加

`_load_json` 関数の直後、`# CC Mock factory` コメントの直前に以下の関数をそのまま追加する:

```python
def _assert_full_output(ctx, expected, catalog_entries, U, M):
    """全kcコマンド共通の出力検証。

    Phase Mまで実行した後の全出力を検証する。
    CC呼び出し回数は各テストで個別にアサートするため含まない。
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

    # findings_dir empty
    if os.path.isdir(ctx.findings_dir):
        assert _count_all_files(ctx.findings_dir, ".json") == 0, (
            "findings_dir should be empty after Phase E"
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

    # traces: merged exist, parts deleted
    split_groups_by_oid = {}
    for e in catalog_entries:
        if "split_info" in e:
            oid = e["split_info"]["original_id"]
            split_groups_by_oid.setdefault(oid, []).append(e["id"])
    for oid, part_ids in split_groups_by_oid.items():
        merged_trace = f"{ctx.trace_dir}/{oid}.json"
        assert os.path.exists(merged_trace), (
            f"Missing merged trace for {oid}"
        )
        for part_id in part_ids:
            part_trace = f"{ctx.trace_dir}/{part_id}.json"
            assert not os.path.exists(part_trace), (
                f"Part trace should be deleted after merge: {part_trace}"
            )

    # resolved
    assert _count_json_files(ctx.knowledge_resolved_dir) == M, (
        f"Expected {M} resolved files, "
        f"got {_count_json_files(ctx.knowledge_resolved_dir)}"
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

    # docs
    docs_count = _count_all_files(ctx.docs_dir)
    assert docs_count == M, (
        f"Expected {M} doc files, got {docs_count}"
    )

    # final catalog: split state + processing_patterns
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
```

## 変更2: TestGen 完成形

TestGenクラス全体を以下に置き換える:

```python
class TestGen:
    """test_gen: kc gen — Phase ABCDEM with clean state, verify all outputs."""

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
            _run_with_mock(kc_gen, ctx, mock)

            _assert_full_output(ctx, expected, catalog_entries, U, M)

            # CC call counts
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
```

## 変更3: TestGenResume 完成形

TestGenResumeクラス全体を以下に置き換える:

```python
class TestGenResume:
    """test_gen_resume: kc gen --resume — 1 pre-placed file, Phase B skips it."""

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
            _run_phase_a_only(ctx, mock)

            # Pre-place one knowledge file before Phase B
            pre_path = f"{ctx.knowledge_cache_dir}/{preplace_entry['output_path']}"
            os.makedirs(os.path.dirname(pre_path), exist_ok=True)
            pre_knowledge = expected["expected_knowledge_cache"][preplace_entry["id"]]
            with open(pre_path, "w", encoding="utf-8") as f:
                json.dump(pre_knowledge, f)

            # Pre-place trace for the same file (Phase B skips → trace not generated)
            pre_trace = expected["expected_traces"][preplace_entry["id"]]
            trace_path = f"{ctx.trace_dir}/{preplace_entry['id']}.json"
            os.makedirs(os.path.dirname(trace_path), exist_ok=True)
            with open(trace_path, "w", encoding="utf-8") as f:
                json.dump(pre_trace, f)

            # ABCDEM (Phase B should skip the pre-placed file)
            _run_with_mock(kc_gen, ctx, mock)

            _assert_full_output(ctx, expected, catalog_entries, U, M)

            # CC call counts
            assert len(counter["B"]) == U - 1, (
                f"counter['B'] expected {U - 1}, got {len(counter['B'])}"
            )
            assert preplace_entry["id"] not in counter["B"], (
                f"Pre-placed file {preplace_entry['id']} should not be regenerated"
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
```

## 変更4: TestRegenTarget 完成形

TestRegenTargetクラス全体を以下に置き換える:

```python
class TestRegenTarget:
    """test_regen_target: kc regen --target — Phase ABCDEM on 1/3 of base_names."""

    def test_regen_target(self, gen_state, expected):
        params = expected["params"]
        U = params["U"]
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

            _run_with_mock(kc_regen_target, ctx, mock, targets=target_base_names)

            _assert_full_output(ctx, expected, catalog_entries, U, M)

            # CC call counts
            assert len(counter["B"]) == target_count, (
                f"counter['B'] expected {target_count}, got {len(counter['B'])}"
            )
            assert len(counter["D"]) == target_count * ctx.max_rounds, (
                f"counter['D'] expected {target_count * ctx.max_rounds}, "
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
```

## 変更5: TestFix 完成形

TestFixクラス全体を以下に置き換える:

```python
class TestFix:
    """test_fix: kc fix — Phase ACDEM (no B), stale file deleted after Phase M."""

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

            _run_with_mock(kc_fix, ctx, mock)

            # TestFix-specific: stale file deleted (delete-insert)
            assert not os.path.exists(stale_path), (
                "Stale file should be deleted by Phase M (delete-insert)"
            )

            _assert_full_output(ctx, expected, catalog_entries, U, M)

            # CC call counts
            assert len(counter["B"]) == 0, (
                f"counter['B'] expected 0 (no Phase B in fix), got {len(counter['B'])}"
            )
            assert len(counter["D"]) == U * ctx.max_rounds, (
                f"counter['D'] expected {U * ctx.max_rounds}, got {len(counter['D'])}"
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
```

## 変更6: TestFixTarget 完成形

TestFixTargetクラス全体を以下に置き換える:

```python
class TestFixTarget:
    """test_fix_target: kc fix --target — Phase ACDEM with target 1/3 of base_names."""

    def test_fix_target(self, gen_state, expected):
        params = expected["params"]
        U = params["U"]
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

            _run_with_mock(kc_fix_target, ctx, mock, targets=target_base_names)

            _assert_full_output(ctx, expected, catalog_entries, U, M)

            # CC call counts
            assert len(counter["B"]) == 0, (
                f"counter['B'] expected 0 (no Phase B in fix), got {len(counter['B'])}"
            )
            assert len(counter["D"]) == target_count * ctx.max_rounds, (
                f"counter['D'] expected {target_count * ctx.max_rounds}, "
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
```

## 変更7: 不要コードの削除

`_run_cde_loop` 関数はどのテストからも呼ばれていないので削除する。

## テスト実行

```bash
cd tools/knowledge-creator && python -m pytest tests/e2e/ -x -v
```

## コミット

```bash
git add tools/knowledge-creator/tests/e2e/test_e2e.py
git commit -m "test: add _assert_full_output helper, fix assertion gaps in all E2E tests

- Extract common output assertions into _assert_full_output()
- All 5 tests now verify: catalog, cache, knowledge, traces, resolved,
  index.toon, docs, final catalog state, and CC call counts
- Remove _run_cde_loop (unused)
- Fix TestFix docstring: Phase ACDEM, not CDEM"
```
