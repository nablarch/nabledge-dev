# Task: knowledge-creator pipeline quality fixes

## Background

7 issues found from v6 knowledge gen/fix run results. This task fixes all issues with tests.

**Branch**: `106-nabledge-creator-tool` (PR #135)

## Approach

- TDD: write test first, confirm fail, then implement
- One commit per fix
- Before each commit: `cd tools/knowledge-creator && python3 -m pytest tests/ -x -q`
- Tests go in `tests/ut/` (edge cases not reproducible in E2E mock data)
- Follow `.claude/rules/language.md`: code/commits/tests in English

---

## Fix 1: Add S17 check to Phase C: Structure Check (empty knowledge guard)

### Problem

Files with `no_knowledge_content=False` + empty `index=[]` + empty `sections={}` pass Phase C: Structure Check. S3/S4 find zero mismatches when both are empty. 10 such files exist in production; 3 resulted in completely empty deployed knowledge.

### Test

File: `tests/ut/test_phase_c.py`, append to `TestStructureValidation` class:

```python
    def test_s17_empty_knowledge_rejected(self, ctx):
        """S17: no_knowledge_content=False with empty index+sections must fail."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = {
            "id": "handlers-sample-handler",
            "title": "サンプルハンドラ",
            "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [],
            "sections": {}
        }
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S17" in e for e in errors)

    def test_s17_no_knowledge_content_true_not_affected(self, ctx):
        """S17 must not trigger when no_knowledge_content=True."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = {
            "id": "handlers-sample-handler",
            "title": "サンプルハンドラ",
            "no_knowledge_content": True,
            "official_doc_urls": ["https://example.com"],
            "index": [],
            "sections": {}
        }
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert not any("S17" in e for e in errors)
```

Confirm fail: `python3 -m pytest tests/ut/test_phase_c.py::TestStructureValidation::test_s17_empty_knowledge_rejected -x -q`

### Implementation

File: `scripts/phase_c_structure_check.py`

Insert between S16's `return errors` (L65) and `index_ids = ...` (L67).

Before:

```python
            return errors

        index_ids = [entry["id"] for entry in knowledge.get("index", [])]
```

After:

```python
            return errors

        # S17: Empty knowledge guard
        if not knowledge.get("index") and not knowledge.get("sections"):
            errors.append("S17: no_knowledge_content=false but index and sections are both empty")
            return errors

        index_ids = [entry["id"] for entry in knowledge.get("index", [])]
```

Confirm pass: `python3 -m pytest tests/ut/test_phase_c.py -x -q` → 9 passed

### Commit

```
fix: add S17 empty knowledge guard to Phase C structure check
```

---

## Fix 2: Add `--disallowedTools` to `run_claude` to block CC file operations

### Problem

In Phase E: Fix, CC chooses `ToolSearch → Glob → Read → Edit` file editing instead of StructuredOutput, causing `error_max_turns`. CC also writes files to repo root.

### Test

Not needed (external process argument change, not testable in automated tests).

### Implementation

File: `scripts/common.py`

Change cmd construction in `run_claude()` (L79-92).

Before:

```python
    if verbose:
        cmd = [
            "claude", "-p",
            "--output-format", "stream-json",
            "--verbose",
            "--json-schema", json.dumps(json_schema),
            "--max-turns", "10"
        ]
    else:
        cmd = [
            "claude", "-p",
            "--output-format", "json",
            "--json-schema", json.dumps(json_schema),
            "--max-turns", "10"
        ]
```

After:

```python
    disallowed = "Read,Edit,Write,Glob,Grep,LS,ToolSearch"

    if verbose:
        cmd = [
            "claude", "-p",
            "--output-format", "stream-json",
            "--verbose",
            "--json-schema", json.dumps(json_schema),
            "--max-turns", "10",
            "--disallowedTools", disallowed
        ]
    else:
        cmd = [
            "claude", "-p",
            "--output-format", "json",
            "--json-schema", json.dumps(json_schema),
            "--max-turns", "10",
            "--disallowedTools", disallowed
        ]
```

Blocked tools rationale:
- `Read`, `Edit`, `Write`, `Glob`, `Grep`, `LS`: file operation tools
- `ToolSearch`: entry point for CC to discover file tools (confirmed in logs: ToolSearch → Glob → Read → Edit)
- StructuredOutput is implicitly enabled by `--json-schema`, so blocking ToolSearch has no side effect

### Also: remove stray JSON file from repo root

```bash
git rm adapters-redisstore_lettuce_adaptor--sec-88c3e343.json
```

Confirm pass: `python3 -m pytest tests/ -x -q`

### Commit

```
fix: add --disallowedTools to run_claude and remove stray JSON file
```

---

## Fix 3: Use list-based index merge for stable ordering

### Problem

`merge.py` uses `index_map = {}` (dict) for index merging. When Phase E: Fix moves sections between parts, dict insertion order changes, making merged index order unstable.

### Test

File: `tests/ut/test_merge.py`, append to `TestMergeSplitFiles` class:

```python
    def test_merge_index_order_is_part_sequential(self, ctx):
        """Merged index must follow part1 all sections -> part2 new sections order."""
        from merge import MergeSplitFiles

        part1 = {
            "id": "libraries-tag--p1",
            "title": "タグ",
            "official_doc_urls": ["https://example.com"],
            "processing_patterns": [],
            "index": [
                {"id": "section-a", "title": "A", "hints": ["a"]},
                {"id": "section-b", "title": "B", "hints": ["b"]}
            ],
            "sections": {"section-a": "content A", "section-b": "content B"}
        }
        part2 = {
            "id": "libraries-tag--p2",
            "title": "タグ",
            "official_doc_urls": ["https://example.com"],
            "processing_patterns": [],
            "index": [
                {"id": "section-b", "title": "B", "hints": ["b", "extra"]},
                {"id": "section-c", "title": "C", "hints": ["c"]},
                {"id": "section-d", "title": "D", "hints": ["d"]}
            ],
            "sections": {
                "section-b": "content B moved",
                "section-c": "content C",
                "section-d": "content D"
            }
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--p1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--p2.json", part2)

        catalog = load_json(ctx.classified_list_path)
        catalog["files"] = [
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libraries-tag--p1",
                "output_path": "component/libraries/libraries-tag--p1.json",
                "assets_dir": "component/libraries/assets/libraries-tag--p1/",
                "split_info": {"is_split": True, "original_id": "libraries-tag", "part": 1, "total": 2}
            },
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libraries-tag--p2",
                "output_path": "component/libraries/libraries-tag--p2.json",
                "assets_dir": "component/libraries/assets/libraries-tag--p2/",
                "split_info": {"is_split": True, "original_id": "libraries-tag", "part": 2, "total": 2}
            }
        ]
        write_json(ctx.classified_list_path, catalog)

        MergeSplitFiles(ctx).run()

        merged = load_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag.json")
        index_ids = [e["id"] for e in merged["index"]]
        assert index_ids == ["section-a", "section-b", "section-c", "section-d"]

        section_b_entry = [e for e in merged["index"] if e["id"] == "section-b"][0]
        assert "b" in section_b_entry["hints"]
        assert "extra" in section_b_entry["hints"]
```

Note: current dict-based implementation may also pass this test (Python 3.7+ dict preserves insertion order). Change to list-based regardless — makes the intent explicit in code.

### Implementation

**Two files must be changed.**

#### (a) `scripts/merge.py`

Replace `# Merge index` block (L141-157).

Before:

```python
            # Merge index
            index_map = {}
            for pj in part_jsons:
                for entry in pj.get("index", []):
                    sid = entry["id"]
                    if sid not in index_map:
                        index_map[sid] = {
                            "id": sid, "title": entry["title"],
                            "hints": list(entry.get("hints", []))
                        }
                    else:
                        existing = set(index_map[sid]["hints"])
                        for h in entry.get("hints", []):
                            if h not in existing:
                                index_map[sid]["hints"].append(h)
                                existing.add(h)
            merged["index"] = list(index_map.values())
```

After:

```python
            # Merge index: part-sequential order, dedup by id, merge hints
            merged_index = []
            seen_ids = {}  # id -> position in merged_index
            for pj in part_jsons:
                for entry in pj.get("index", []):
                    sid = entry["id"]
                    if sid not in seen_ids:
                        new_entry = {
                            "id": sid, "title": entry["title"],
                            "hints": list(entry.get("hints", []))
                        }
                        seen_ids[sid] = len(merged_index)
                        merged_index.append(new_entry)
                    else:
                        existing_entry = merged_index[seen_ids[sid]]
                        existing_hints = set(existing_entry["hints"])
                        for h in entry.get("hints", []):
                            if h not in existing_hints:
                                existing_entry["hints"].append(h)
                                existing_hints.add(h)
            merged["index"] = merged_index
```

#### (b) `tests/e2e/generate_expected.py`

Apply same change to `compute_merged_files()` index merge logic (L552-567). E2E tests compare merge.py output with expected values from this file — both must use identical logic.

Before:

```python
        # Merge index (dedup by id)
        index_map = {}
        for p in parts:
            pk = knowledge_fn(p['id'], p)
            for entry in pk.get("index", []):
                sid = entry["id"]
                if sid not in index_map:
                    index_map[sid] = {"id": sid, "title": entry["title"],
                                      "hints": list(entry.get("hints", []))}
                else:
                    existing = set(index_map[sid]["hints"])
                    for h in entry.get("hints", []):
                        if h not in existing:
                            index_map[sid]["hints"].append(h)
                            existing.add(h)
        merged_knowledge["index"] = list(index_map.values())
```

After:

```python
        # Merge index: part-sequential order, dedup by id, merge hints
        merged_index = []
        seen_ids = {}
        for p in parts:
            pk = knowledge_fn(p['id'], p)
            for entry in pk.get("index", []):
                sid = entry["id"]
                if sid not in seen_ids:
                    seen_ids[sid] = len(merged_index)
                    merged_index.append({"id": sid, "title": entry["title"],
                                         "hints": list(entry.get("hints", []))})
                else:
                    existing_entry = merged_index[seen_ids[sid]]
                    existing_hints = set(existing_entry["hints"])
                    for h in entry.get("hints", []):
                        if h not in existing_hints:
                            existing_entry["hints"].append(h)
                            existing_hints.add(h)
        merged_knowledge["index"] = merged_index
```

Confirm pass: `python3 -m pytest tests/ -x -q`

### Commit

```
fix: use list-based index merge for stable part-sequential ordering
```

---

## Fix 4: Add post-merge index-section consistency validation

### Problem

`libraries-data_bind` has cross-part ID mismatch (`extension` in index vs `section-extension` in sections). Phase C: Structure Check validates each part independently, so cross-part inconsistencies go undetected until after merge.

### Test

File: `tests/ut/test_merge.py`, append to `TestMergeSplitFiles` class:

```python
    def test_merge_warns_on_index_section_mismatch(self, ctx, caplog):
        """Merge must log warning when merged result has index-section mismatch."""
        import logging
        from merge import MergeSplitFiles

        part1 = {
            "id": "libs-bind--p1",
            "title": "Data Bind",
            "official_doc_urls": ["https://example.com"],
            "processing_patterns": [],
            "index": [
                {"id": "ext", "title": "拡張", "hints": ["extension"]}
            ],
            "sections": {"section-ext": "拡張の内容"}
        }
        part2 = {
            "id": "libs-bind--p2",
            "title": "Data Bind",
            "official_doc_urls": ["https://example.com"],
            "processing_patterns": [],
            "index": [
                {"id": "csv", "title": "CSV", "hints": ["csv"]}
            ],
            "sections": {"csv": "CSV content"}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libs-bind--p1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libs-bind--p2.json", part2)

        catalog = load_json(ctx.classified_list_path)
        catalog["files"] = [
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-bind--p1",
                "output_path": "component/libraries/libs-bind--p1.json",
                "assets_dir": "component/libraries/assets/libs-bind--p1/",
                "split_info": {"is_split": True, "original_id": "libs-bind", "part": 1, "total": 2}
            },
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-bind--p2",
                "output_path": "component/libraries/libs-bind--p2.json",
                "assets_dir": "component/libraries/assets/libs-bind--p2/",
                "split_info": {"is_split": True, "original_id": "libs-bind", "part": 2, "total": 2}
            }
        ]
        write_json(ctx.classified_list_path, catalog)

        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            MergeSplitFiles(ctx).run()

        warning_messages = [r.message for r in caplog.records if "index-section mismatch" in r.message]
        assert len(warning_messages) > 0, "No index-section mismatch warning logged"
        assert any("libs-bind" in msg for msg in warning_messages)
```

Confirm fail: `python3 -m pytest tests/ut/test_merge.py::TestMergeSplitFiles::test_merge_warns_on_index_section_mismatch -x -q`

### Implementation

File: `scripts/merge.py`

Insert after `write_json(merged_path, merged)` (L175), before `# Consolidate assets` comment (L177).

```python
                # Validate merged index-section consistency
                merged_idx_ids = set(e["id"] for e in merged["index"])
                merged_sec_ids = set(merged["sections"].keys())
                idx_only = merged_idx_ids - merged_sec_ids
                sec_only = merged_sec_ids - merged_idx_ids
                if idx_only or sec_only:
                    warn_parts = []
                    if idx_only:
                        warn_parts.append(f"index only: {sorted(idx_only)}")
                    if sec_only:
                        warn_parts.append(f"sections only: {sorted(sec_only)}")
                    self.logger.warning(
                        f"    ⚠️ {original_id}: index-section mismatch after merge: "
                        + ", ".join(warn_parts)
                    )
```

Confirm pass: `python3 -m pytest tests/ -x -q`

### Commit

```
fix: add post-merge index-section consistency validation
```

---

## Fix 5: Add test for merge skip when cache is missing

### Problem

When ID dedup splits old IDs into new IDs, Phase M: Finalization's delete-insert removes old files, but new IDs may not exist in cache yet, causing knowledge loss.

### Verification

Existing code handles this at `merge.py` L107-109:

```python
            if not all_exist:
                self.logger.info(f"  [SKIP] {original_id}: not all parts generated")
                continue
```

This test confirms the existing behavior as a regression guard.

### Test

File: `tests/ut/test_merge.py`, append to `TestMergeSplitFiles` class:

```python
    def test_merge_skips_group_when_cache_missing(self, ctx, caplog):
        """If any split part's cache file is missing, skip that group entirely."""
        import logging
        from merge import MergeSplitFiles

        part1 = {
            "id": "libs-comp--p1", "title": "Comparison",
            "official_doc_urls": [], "processing_patterns": [],
            "index": [{"id": "overview", "title": "概要", "hints": ["x"]}],
            "sections": {"overview": "content for overview section here"}
        }
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libs-comp--p1.json", part1)
        # Part 2 does NOT exist in cache

        catalog = load_json(ctx.classified_list_path)
        catalog["files"] = [
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-comp--p1",
                "output_path": "component/libraries/libs-comp--p1.json",
                "assets_dir": "component/libraries/assets/libs-comp--p1/",
                "split_info": {"is_split": True, "original_id": "libs-comp", "part": 1, "total": 2}
            },
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-comp--p2",
                "output_path": "component/libraries/libs-comp--p2.json",
                "assets_dir": "component/libraries/assets/libs-comp--p2/",
                "split_info": {"is_split": True, "original_id": "libs-comp", "part": 2, "total": 2}
            }
        ]
        write_json(ctx.classified_list_path, catalog)

        with caplog.at_level(logging.INFO, logger="knowledge_creator"):
            MergeSplitFiles(ctx).run()

        merged_path = f"{ctx.knowledge_dir}/component/libraries/libs-comp.json"
        assert not os.path.exists(merged_path), "Merged file must not exist when cache is incomplete"
        assert any("SKIP" in r.message and "libs-comp" in r.message for r in caplog.records)
```

Confirm pass: `python3 -m pytest tests/ut/test_merge.py -x -q`

### Commit

```
test: verify merge skips group when cache file is missing
```

---

## Commit order summary

| # | Commit message | Changed files |
|---|---|---|
| 1 | `fix: add S17 empty knowledge guard to Phase C structure check` | phase_c_structure_check.py, test_phase_c.py |
| 2 | `fix: add --disallowedTools to run_claude and remove stray JSON file` | common.py, adapters-...json (git rm) |
| 3 | `fix: use list-based index merge for stable part-sequential ordering` | merge.py, generate_expected.py, test_merge.py |
| 4 | `fix: add post-merge index-section consistency validation` | merge.py, test_merge.py |
| 5 | `test: verify merge skips group when cache file is missing` | test_merge.py |

## Final verification

After all commits:

```bash
cd tools/knowledge-creator && python3 -m pytest tests/ -x -q
```
