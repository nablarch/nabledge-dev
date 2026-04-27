# nablarch-document RST全件対象化 + 知識不要ファイルの判定・検証

## 結論

nablarch-documentのRSTファイルは全件を生成対象にする。ブラックリストもホワイトリストも使わない。RST_MAPPINGにマッチしないファイルはエラー停止で気づかせる。知識として残す内容がないファイルは、生成時に `no_knowledge_content: true` マークをつけ、検証で妥当性を確認する。

## 変更一覧

| # | 対象ファイル | 変更 |
|---|---|---|
| 1 | `steps/step1_list_sources.py` | `f != "index.rst"` 削除 |
| 2 | `steps/step2_classify.py` | RST_MAPPING追加 + トップレベルindex.rst個別処理 |
| 3 | `steps/step2_classify.py` | unmatchedをエラー停止に変更 |
| 4 | `steps/step2_classify.py` | `classify_rst` 戻り値を3値に拡張 |
| 5 | `steps/step2_classify.py` | `generate_id` でindex.rstのID衝突解決 |
| 6 | `prompts/generate.md` | `no_knowledge_content` 判定 + スキーマ変更 |
| 7 | `steps/phase_c_structure_check.py` | `no_knowledge_content` 対応（S2, S16） |
| 8 | `prompts/content_check.md` | V5: `no_knowledge_content` 妥当性検証追加 |
| 9 | `steps/phase_d_content_check.py` | FINDINGS_SCHEMA enum追加 |
| 10 | `prompts/fix.md` | `no_knowledge_content_invalid` 修正指示追加 |
| 11 | `steps/phase_e_fix.py` | KNOWLEDGE_SCHEMA に `no_knowledge_content` 追加 |
| 12 | `steps/phase_f_finalize.py` | `no_knowledge_content: true` をindex.toon・docsから除外 |
| 13 | テスト | 新規4件 + 既存修正 |

---

## 1. `steps/step1_list_sources.py` L27

### Before

```python
                    if f.endswith(".rst") and f != "index.rst":
```

### After

```python
                    if f.endswith(".rst"):
```

---

## 2. `steps/step2_classify.py` — RST_MAPPING追加 + トップレベル対応

### 2a. RST_MAPPING追加 (L57の `("biz_samples/", ...)` の後に追加)

```python
    # messaging intermediate page
    ("application_framework/application_framework/messaging/", "processing-pattern", "db-messaging"),

    # Standalone content pages
    ("examples/", "about", "about-nablarch"),
    ("external_contents/", "about", "about-nablarch"),
    ("inquiry/", "about", "about-nablarch"),
    ("jakarta_ee/", "about", "about-nablarch"),
    ("nablarch_api/", "about", "about-nablarch"),
    ("releases/", "about", "release-notes"),
    ("terms_of_use/", "about", "about-nablarch"),

    # Intermediate toctree pages (will be no_knowledge_content in Phase B)
    ("application_framework/application_framework/", "about", "about-nablarch"),
    ("application_framework/", "about", "about-nablarch"),
    ("development_tools/", "development-tools", "testing-framework"),
```

> 注: これらはRST_MAPPINGの末尾に追加すること。first-match-winsなので、より具体的なパターンが先にマッチする。

### 2b. `classify_rst` にトップレベル `index.rst` 個別処理を追加 (L167-172)

#### Before

```python
        rel_path = path[idx + len(marker):]

        # Try to match against RST_MAPPING
        for pattern, type_, category in RST_MAPPING:
            if pattern in rel_path:
                return type_, category

        return None, None
```

#### After

```python
        rel_path = path[idx + len(marker):]

        # Top-level index.rst: no RST_MAPPING pattern can match "index.rst" alone
        # because "" would match everything. Handle explicitly.
        if rel_path == "index.rst":
            return "about", "about-nablarch", ""

        # Try to match against RST_MAPPING
        for pattern, type_, category in RST_MAPPING:
            if pattern in rel_path:
                return type_, category, pattern

        return None, None, None
```

> 注: 戻り値3値化（#4）と同時に修正。

---

## 3. `steps/step2_classify.py` — unmatchedエラー停止

### Before (L615-620)

```python
        if unmatched:
            self.logger.warning(f"\n   ⚠️WARNING: {len(unmatched)} files could not be classified:")
            for item in unmatched[:10]:  # Show first 10
                self.logger.warning(f"      {item['path']}")
            if len(unmatched) > 10:
                self.logger.warning(f"      ... and {len(unmatched) - 10} more")
```

### After

```python
        if unmatched:
            self.logger.error(f"\n   ❌ ERROR: {len(unmatched)} RST files have no RST_MAPPING entry.")
            self.logger.error(f"   Add a mapping for each file to RST_MAPPING in:")
            self.logger.error(f"   tools/knowledge-creator/steps/step2_classify.py")
            self.logger.error(f"")
            self.logger.error(f"   Unmapped files:")
            for item in unmatched:
                self.logger.error(f"     {item['path']}")
            self.logger.error(f"")
            self.logger.error(f"   Example: (\"examples/\", \"about\", \"about-nablarch\"),")
            self.logger.error(f"   If no existing type/category fits, add a new one.")
            raise SystemExit(1)
```

---

## 4. `steps/step2_classify.py` — classify_rst 戻り値3値化

#2bに含む。加えて以下の呼び出し元を修正。

### Before (L466-467)

```python
            if format == "rst":
                type_, category = self.classify_rst(path)
```

### After

```python
            matched_pattern = None
            if format == "rst":
                type_, category, matched_pattern = self.classify_rst(path)
```

---

## 5. `steps/step2_classify.py` — generate_id パターン残余パス方式

### Before (L129-157)

```python
    def generate_id(self, filename: str, format: str, category: str = None) -> str:
        """Generate knowledge file ID from filename and category

        Args:
            filename: Source filename
            format: File format (rst/md/xlsx)
            category: Category from classification (optional)

        Returns:
            Unique file ID (category-filename format for rst/md)
        """
        # For Excel files in XLSX_MAPPING, use category as ID (fixed mapping)
        if format == "xlsx" and filename in XLSX_MAPPING:
            return category

        base_name = None
        if format == "rst":
            base_name = filename.replace(".rst", "")
        elif format == "md":
            base_name = filename.replace(".md", "")
        elif format == "xlsx":
            base_name = filename.replace(".xlsx", "")
        else:
            base_name = filename

        # Include category to ensure uniqueness
        if category:
            return f"{category}-{base_name}"
        return base_name
```

### After

```python
    def generate_id(self, filename: str, format: str, category: str = None,
                    source_path: str = None, matched_pattern: str = None) -> str:
        """Generate knowledge file ID from filename and category

        Args:
            filename: Source filename
            format: File format (rst/md/xlsx)
            category: Category from classification (optional)
            source_path: Source file path for index.rst disambiguation (optional)
            matched_pattern: RST_MAPPING pattern that matched (optional, for index.rst)

        Returns:
            Unique file ID (category-filename format for rst/md)
        """
        # For Excel files in XLSX_MAPPING, use category as ID (fixed mapping)
        if format == "xlsx" and filename in XLSX_MAPPING:
            return category

        base_name = None
        if format == "rst":
            base_name = filename.replace(".rst", "")
        elif format == "md":
            base_name = filename.replace(".md", "")
        elif format == "xlsx":
            base_name = filename.replace(".xlsx", "")
        else:
            base_name = filename

        # index.rst: use pattern-remainder path to avoid ID collisions.
        # Multiple index.rst files can map to the same category, so filename alone
        # ("index") is insufficient. Use the path after the matched pattern as context.
        #
        # Examples:
        #   handlers/batch/index.rst matched by "handlers/" -> remainder "batch/index.rst" -> "batch"
        #   handlers/index.rst matched by "handlers/" -> remainder "index.rst" -> pattern basename "handlers"
        #   top-level index.rst matched by "" -> "top"
        if base_name == "index" and source_path is not None and matched_pattern is not None:
            marker = "nablarch-document/ja/"
            marker_idx = source_path.find(marker)
            if marker_idx >= 0:
                rst_rel = source_path[marker_idx + len(marker):]
                pattern_clean = matched_pattern.rstrip("/")
                if not pattern_clean:
                    # Top-level index.rst (matched by "")
                    base_name = "top"
                else:
                    pat_idx = rst_rel.find(pattern_clean)
                    if pat_idx >= 0:
                        remainder = rst_rel[pat_idx + len(pattern_clean):].strip("/")
                        if remainder == "index.rst":
                            base_name = os.path.basename(pattern_clean)
                        else:
                            dir_part = os.path.dirname(remainder)
                            base_name = dir_part.replace("/", "-")

        # Include category to ensure uniqueness
        if category:
            return f"{category}-{base_name}"
        return base_name
```

### 呼び出し元 (L488)

#### Before

```python
            file_id = self.generate_id(filename, format, category)
```

#### After

```python
            file_id = self.generate_id(filename, format, category,
                                       source_path=path, matched_pattern=matched_pattern)
```

---

## 6. `prompts/generate.md` — no_knowledge_content

### 6a. Work Step 1の後（L44 `---` の前）に追加

```markdown
## Work Step 1.5: Check for no-knowledge-content source

Evaluate whether this source file contains any Layer A or Layer B content (see Step 3 for layer definitions).

If the source consists entirely of:
- toctree directives and their entries
- Title and heading underlines
- RST labels (.. _label:)
- Blank lines
- Navigation links only (no explanatory text)

Then set `no_knowledge_content: true`. In this case:
- Set `index` to empty array `[]`
- Set `sections` to empty object `{}`
- Still set `id`, `title`, `official_doc_urls` normally
- Skip Work Steps 2–6
- In trace, set `sections` to `[]` and add `"no_knowledge_content_reason": "..."` explaining why

If ANY Layer A or Layer B content exists, set `no_knowledge_content: false` and proceed normally.
```

### 6b. JSON Schema変更 (L430)

#### Before

```json
      "required": ["id", "title", "official_doc_urls", "index", "sections"],
```

#### After

```json
      "required": ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"],
```

`properties` 内に追加:

```json
        "no_knowledge_content": {
          "type": "boolean",
          "description": "true if source has no Layer A/B content (toctree-only, navigation-only)"
        },
```

### 6c. trace スキーマに追加

`trace.properties` 内に追加:

```json
        "no_knowledge_content_reason": {
          "type": "string",
          "description": "Reason for no_knowledge_content=true (required when true)"
        }
```

### 6d. Final self-checksに追加

```markdown
- [ ] `no_knowledge_content` is set to `true` or `false`
- [ ] If `no_knowledge_content: true`, `index` is `[]` and `sections` is `{}`
- [ ] If `no_knowledge_content: true`, trace has `no_knowledge_content_reason`
- [ ] If `no_knowledge_content: false`, `index` and `sections` are non-empty
```

---

## 7. `steps/phase_c_structure_check.py` — no_knowledge_content対応

### 7a. S2チェックの修正 (L52)

#### Before

```python
        for field in ["id", "title", "official_doc_urls", "index", "sections"]:
```

#### After

```python
        for field in ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"]:
```

### 7b. S2チェックの直後（L57の `return errors` の後）に追加

```python
        # S16: no_knowledge_content validation
        if knowledge.get("no_knowledge_content") is True:
            if knowledge.get("index"):
                errors.append("S16: no_knowledge_content=true but index is not empty")
            if knowledge.get("sections"):
                errors.append("S16: no_knowledge_content=true but sections is not empty")
            return errors
```

> 注: `return errors` で早期リターンすることで、S3-S15チェック（index/sectionsが存在する前提）をスキップする。

---

## 8. `prompts/content_check.md` — V5追加

### Validation Checklistの末尾（V4の後）に追加

```markdown
### V5: no_knowledge_content Validation (severity: critical)

If the knowledge file has `no_knowledge_content: true`:
- Read the entire source file
- Confirm there is NO Layer A or Layer B content (see generate.md Step 3 for definitions)
- If any decision-necessary information, configuration properties, API specs, code examples,
  warnings, or constraints exist in the source → report as critical finding:
  category: "no_knowledge_content_invalid", description: "no_knowledge_content=true but source contains Layer A/B content: {description}"

If `no_knowledge_content: false`:
- Skip this check (V1/V2 handle normal content validation)
```

---

## 9. `steps/phase_d_content_check.py` — FINDINGS_SCHEMA

### Before (L27)

```python
                    "enum": ["omission", "fabrication", "hints_missing", "section_issue"]
```

### After

```python
                    "enum": ["omission", "fabrication", "hints_missing", "section_issue", "no_knowledge_content_invalid"]
```

---

## 10. `prompts/fix.md` — no_knowledge_content_invalid修正指示

### Instructions セクション（L27の `- **section_issue**:` の後）に追加

```markdown
- **no_knowledge_content_invalid**: The file was incorrectly marked as `no_knowledge_content: true` but the source has Layer A/B content. Set `no_knowledge_content: false`, then extract all Layer A/B content from the source into proper sections following the same rules as generate.md Steps 2-6. Build index[] and sections{} normally.
```

---

## 11. `steps/phase_e_fix.py` — KNOWLEDGE_SCHEMA

### Before (L14)

```python
    "required": ["id", "title", "official_doc_urls", "index", "sections"],
```

### After

```python
    "required": ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"],
```

`properties` 内に追加:

```python
        "no_knowledge_content": {"type": "boolean"},
```

---

## 12. `steps/phase_f_finalize.py` — no_knowledge_content除外

### 12a. `_build_index_toon` (L118の `knowledge = load_json(json_path)` の後)

#### Before

```python
            knowledge = load_json(json_path)
            title = knowledge.get("title", fi["id"])
```

#### After

```python
            knowledge = load_json(json_path)
            if knowledge.get("no_knowledge_content") is True:
                continue
            title = knowledge.get("title", fi["id"])
```

### 12b. `_generate_docs` (L232の `knowledge = load_json(json_path)` の後)

#### Before

```python
            knowledge = load_json(json_path)
            md_lines = [f"# {knowledge['title']}", ""]
```

#### After

```python
            knowledge = load_json(json_path)
            if knowledge.get("no_knowledge_content") is True:
                continue
            md_lines = [f"# {knowledge['title']}", ""]
```

---

## 13. テスト

### 影響分析

| テストファイル | 影響 | 理由 |
|---|---|---|
| `test_excel_classification.py` | **なし** | `generate_id` をxlsx用に呼び。新パラメータはデフォルトNone |
| `test_split_criteria.py` | **なし** | split系メソッドのみ。`classify_rst`/`generate_id` 不使用 |
| `test_run_phases.py` | **なし** | Phase呼び出し有無のモック確認のみ |
| `test_phase_c.py` | **要修正** | S2のrequiredフィールド追加。既存テストの `sample_knowledge.json` に `no_knowledge_content: false` 追加が必要 |
| `test_test_mode.py` | **要確認** | 実リポジトリ依存。ファイル数増加で件数アサーション変更の可能性。RST_MAPPING追加後にdry-runで確認 |
| `test_target_filter.py` | **なし** | classified.jsonを直接構築 |
| `test_e2e_split.py` | **なし** | classified.jsonを直接構築 |
| `test_pipeline.py` | **なし** | classified.jsonを直接構築 |
| `test_verification_loop.py` | **なし** | classified.jsonを直接構築 |
| `test_merge.py` | **なし** | classified.jsonを直接構築 |
| `test_phase_g.py` | **なし** | classified.jsonを直接構築 |
| `test_phase_m.py` | **なし** | classified.jsonを直接構築 |
| その他 | **なし** | |

### 既存フィクスチャ修正

`tests/fixtures/sample_knowledge.json` に `no_knowledge_content: false` を追加:

```json
{
  "id": "handlers-sample-handler",
  "title": "サンプルハンドラ",
  "no_knowledge_content": false,
  ...
}
```

`conftest.py` の `make_mock_run_claude` が返すデフォルト生成出力（`_generate`）のknowledgeにも `no_knowledge_content: false` が含まれるようにする。`sample_knowledge.json` を修正すれば `load_fixture` 経由で自動反映。

### 新規テスト

#### `tests/test_rst_all_inclusive.py`

Step1が全RSTを列挙することの検証。

```python
"""Tests: Step1 lists all RST files including index.rst."""
import os
import pytest
from run import Context
from steps.step1_list_sources import Step1ListSources


@pytest.fixture
def ctx_with_rst(tmp_path):
    repo = tmp_path / "repo"
    rst_base = repo / ".lw/nab-official/v6/nablarch-document/ja"
    for dir_path, files in {
        "application_framework/application_framework/libraries": ["tag.rst", "index.rst"],
        "about_nablarch": ["index.rst", "concept.rst"],
        "examples": ["index.rst"],
        "": ["index.rst"],
        "_static": ["excluded.rst"],
    }.items():
        d = rst_base / dir_path if dir_path else rst_base
        d.mkdir(parents=True, exist_ok=True)
        for f in files:
            (d / f).write_text(f"content of {f}")
    ctx = Context(version="6", repo=str(repo), concurrency=1)
    os.makedirs(ctx.log_dir, exist_ok=True)
    return ctx


class TestAllInclusive:
    def test_index_rst_included(self, ctx_with_rst):
        result = Step1ListSources(ctx_with_rst, dry_run=True).run()
        filenames = [s["filename"] for s in result["sources"]]
        assert filenames.count("index.rst") == 4

    def test_underscore_dirs_excluded(self, ctx_with_rst):
        result = Step1ListSources(ctx_with_rst, dry_run=True).run()
        assert not any("_static" in s["path"] for s in result["sources"])

    def test_total_count(self, ctx_with_rst):
        result = Step1ListSources(ctx_with_rst, dry_run=True).run()
        assert len([s for s in result["sources"] if s["format"] == "rst"]) == 6
```

#### `tests/test_unmatched_error.py`

Step2がunmatchedでエラー停止することの検証。

```python
"""Tests: Step2 raises SystemExit on unmatched RST files."""
import os
import pytest
from run import Context
from steps.step1_list_sources import Step1ListSources
from steps.step2_classify import Step2Classify


@pytest.fixture
def ctx_with_unmatched(tmp_path):
    repo = tmp_path / "repo"
    rst_base = repo / ".lw/nab-official/v6/nablarch-document/ja"
    # Unmatched file
    d = rst_base / "unknown_new_feature"
    d.mkdir(parents=True, exist_ok=True)
    (d / "guide.rst").write_text("New Feature\n=====\n\nContent")
    # Matched file (for contrast)
    d2 = rst_base / "about_nablarch"
    d2.mkdir(parents=True, exist_ok=True)
    (d2 / "concept.rst").write_text("Concept\n=====\n\nContent")
    ctx = Context(version="6", repo=str(repo), concurrency=1)
    os.makedirs(ctx.log_dir, exist_ok=True)
    return ctx


class TestUnmatchedError:
    def test_unmatched_raises_system_exit(self, ctx_with_unmatched):
        sources = Step1ListSources(ctx_with_unmatched, dry_run=True).run()
        with pytest.raises(SystemExit):
            Step2Classify(ctx_with_unmatched, dry_run=True, sources_data=sources).run()

    def test_all_matched_succeeds(self, tmp_path):
        repo = tmp_path / "repo"
        rst_base = repo / ".lw/nab-official/v6/nablarch-document/ja/about_nablarch"
        rst_base.mkdir(parents=True, exist_ok=True)
        (rst_base / "concept.rst").write_text("Concept\n=====\n\nContent")
        ctx = Context(version="6", repo=str(repo), concurrency=1)
        os.makedirs(ctx.log_dir, exist_ok=True)
        sources = Step1ListSources(ctx, dry_run=True).run()
        result = Step2Classify(ctx, dry_run=True, sources_data=sources).run()
        assert len(result["files"]) == 1
```

#### `tests/test_index_rst_id.py`

index.rstのID生成の検証。

```python
"""Tests: index.rst ID generation (pattern-remainder approach)."""
import pytest
from steps.step2_classify import Step2Classify


class TestIndexRstId:
    @pytest.fixture
    def c(self, ctx):
        return Step2Classify(ctx, dry_run=True)

    def test_at_pattern_root(self, c):
        assert c.generate_id(
            "index.rst", "rst", "handlers",
            source_path=".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/index.rst",
            matched_pattern="application_framework/application_framework/handlers/"
        ) == "handlers-handlers"

    def test_in_subdirectory(self, c):
        assert c.generate_id(
            "index.rst", "rst", "handlers",
            source_path=".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/batch/index.rst",
            matched_pattern="application_framework/application_framework/handlers/"
        ) == "handlers-batch"

    def test_deep_subdirectory(self, c):
        assert c.generate_id(
            "index.rst", "rst", "nablarch-batch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.rst",
            matched_pattern="application_framework/application_framework/batch/nablarch_batch"
        ) == "nablarch-batch-getting_started-nablarch_batch"

    def test_same_category_unique(self, c):
        id1 = c.generate_id("index.rst", "rst", "about-nablarch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/about_nablarch/index.rst",
            matched_pattern="about_nablarch/")
        id2 = c.generate_id("index.rst", "rst", "about-nablarch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/biz_samples/index.rst",
            matched_pattern="biz_samples/")
        assert id1 != id2

    def test_top_level(self, c):
        assert c.generate_id(
            "index.rst", "rst", "about-nablarch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/index.rst",
            matched_pattern=""
        ) == "about-nablarch-top"

    def test_non_index_unchanged(self, c):
        assert c.generate_id("tag.rst", "rst", "libraries") == "libraries-tag"

    def test_backward_compat_no_new_params(self, c):
        assert c.generate_id("tag.rst", "rst", "libraries") == "libraries-tag"
```

#### `tests/test_no_knowledge_content.py`

Phase C/F の `no_knowledge_content` 対応の検証。

```python
"""Tests: no_knowledge_content handling in Phase C and Phase F."""
import os
import json
import pytest
from conftest import load_fixture


def _write_knowledge(ctx, knowledge, file_id="handlers-sample-handler"):
    path = os.path.join(ctx.knowledge_dir, f"component/handlers/{file_id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    return path


class TestPhaseCNoContent:
    def test_no_content_true_with_empty_passes(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "no_knowledge_content": True,
            "official_doc_urls": [], "index": [], "sections": {}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert errors == []

    def test_no_content_true_with_non_empty_index_fails_s16(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "no_knowledge_content": True,
            "official_doc_urls": [],
            "index": [{"id": "x", "title": "X", "hints": ["h"]}],
            "sections": {}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert any("S16" in e for e in errors)

    def test_no_content_true_with_non_empty_sections_fails_s16(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "no_knowledge_content": True,
            "official_doc_urls": [],
            "index": [], "sections": {"x": "content"}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert any("S16" in e for e in errors)

    def test_no_content_missing_fails_s2(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "official_doc_urls": [], "index": [], "sections": {}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert any("S2" in e and "no_knowledge_content" in e for e in errors)

    def test_existing_valid_knowledge_still_passes(self, ctx):
        """Regression: existing knowledge files with no_knowledge_content: false still pass."""
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        # After fixture update, k has no_knowledge_content: false
        jp = _write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert errors == []
```

---

## 実装手順

1. `tests/fixtures/sample_knowledge.json` に `"no_knowledge_content": false` を追加
2. `step1_list_sources.py` L27修正
3. `step2_classify.py`: RST_MAPPING追加、`classify_rst` 3値化+トップレベル処理、`generate_id` パターン残余パス方式、unmatched エラー停止、呼び出し元修正
4. `prompts/generate.md`: Work Step 1.5追加、スキーマ変更、self-checks追加
5. `phase_c_structure_check.py`: S2修正、S16追加
6. `prompts/content_check.md`: V5追加
7. `phase_d_content_check.py`: FINDINGS_SCHEMA enum追加
8. `prompts/fix.md`: no_knowledge_content_invalid指示追加
9. `phase_e_fix.py`: KNOWLEDGE_SCHEMA修正
10. `phase_f_finalize.py`: no_knowledge_content除外
11. テスト追加（4件）+ `test_phase_c.py` の既存テスト確認（sample_knowledge.jsonの変更で自動対応）
12. 全テスト実行: `cd tools/knowledge-creator && python -m pytest tests/ -v`
13. 実リポジトリでPhase A dry-run: `python run.py --version 6 --phase A --dry-run` → unmatchedゼロ確認
