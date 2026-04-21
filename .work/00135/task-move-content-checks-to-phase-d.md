# タスク: 内容チェック(S6/S7/S9/S13)をPhase CからPhase Dに移動

## 目的

Phase Cに混在している「内容品質」チェック4項目（S6, S7, S9, S13）をPhase Cから完全に削除し、Phase Dスクリプト内でPythonによる事前検証として実行する。検証結果はPhase Dのプロンプトに含めてAIに判断させる。

## 結論

Phase C不合格のファイルはPhase D/E（AI修正ループ）に進めない。S6/S7/S9/S13はAI修正が必要な内容品質の問題であり、Phase Cにあると修正機会を得られないままPhase Mでマージされ、品質の低い知識ファイルが出力される。

Phase Cは構造整合性チェックのゲートに徹し、内容品質チェックはPhase Dの責務とする。

## 変更対象ファイル（7ファイル）

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `scripts/common.py` | `import re`追加、`count_source_headings`関数を追加 |
| 2 | `scripts/phase_c_structure_check.py` | S6/S7/S9/S13チェックコード削除、`count_source_headings`メソッド削除、import変更 |
| 3 | `scripts/phase_d_content_check.py` | import追加、`_compute_content_warnings`メソッド追加、`_build_prompt`にwarnings引数追加、`check_one`でwarnings計算・注入 |
| 4 | `prompts/content_check.md` | content_warningsセクション追加 |
| 5 | `tests/ut/test_phase_c.py` | S6/S7テスト削除、S6/S7/S9/S13がerrorsに含まれないテスト追加 |
| 6 | `tests/ut/test_phase_d_content_warnings.py` | 新規作成。`_compute_content_warnings`のユニットテスト |
| 7 | `tests/ut/test_no_knowledge_content.py` | 変更なし（全テストpassを確認するのみ） |

## 変更詳細

### 1. `scripts/common.py`

#### 1-1. import reを追加

既存のimport群に`import re`を追加する。

**Before:**

```python
import json
import subprocess
import os
```

**After:**

```python
import json
import re
import subprocess
import os
```

#### 1-2. count_source_headings関数を追加

ファイル末尾（`aggregate_cc_metrics`関数の後）に以下を追加する。

```python
def count_source_headings(content: str, fmt: str) -> int:
    """Count split-level headings in source content.

    Args:
        content: Source file content
        fmt: Source format ('rst', 'md', 'xlsx')

    Returns:
        Number of headings found
    """
    if fmt == "rst":
        return len(re.findall(r'\n[^\n]+\n-{3,}\n', content))
    elif fmt == "md":
        return len(re.findall(r'^## (?!#)', content, re.MULTILINE))
    elif fmt == "xlsx":
        return 1
    return 0
```

### 2. `scripts/phase_c_structure_check.py`

#### 2-1. importを変更

**Before:**

```python
from common import load_json, write_json, read_file
```

**After:**

```python
from common import load_json, write_json
```

`read_file`はS9のソース読み込みでのみ使用されている。S9削除後は不要になる。

#### 2-2. count_source_headingsメソッドを削除

以下のメソッド全体を削除する:

```python
    def count_source_headings(self, content, fmt):
        if fmt == "rst":
            return len(re.findall(r'\n[^\n]+\n-{3,}\n', content))
        elif fmt == "md":
            return len(re.findall(r'^## (?!#)', content, re.MULTILINE))
        elif fmt == "xlsx":
            return 1
        return 0
```

#### 2-3. S6チェックを削除

以下のコードブロックを完全に削除する:

```python
        # S6: Non-empty hints
        for entry in knowledge.get("index", []):
            if not entry.get("hints"):
                errors.append(f"S6: Section '{entry['id']}' has empty hints")
```

#### 2-4. S7チェックを削除

以下のコードブロックを完全に削除する:

```python
        # S7: Non-empty sections
        for sid, content in knowledge.get("sections", {}).items():
            if not content.strip():
                errors.append(f"S7: Section '{sid}' has empty content")
```

#### 2-5. S9チェックを削除

以下のコードブロックを完全に削除する:

```python
        # S9: Section count
        if file_info and "section_range" in file_info:
            # For split files, use section_range as expected count
            expected = len(file_info["section_range"]["sections"])
        elif os.path.exists(source_path):
            # For non-split files, count headings in source
            source_content = read_file(source_path)
            expected = self.count_source_headings(source_content, source_format)
        else:
            expected = 0

        actual = len(knowledge.get("sections", {}))
        if expected > 0 and actual < expected:
            errors.append(f"S9: Section count {actual} < source headings {expected}")
```

#### 2-6. S13チェックを削除

以下のコードブロックを完全に削除する:

```python
        # S13: Minimum section length
        for sid, content in knowledge.get("sections", {}).items():
            stripped = content.strip()
            if len(stripped) < 20 and stripped not in ["なし。", "なし"]:
                errors.append(f"S13: Section '{sid}' too short ({len(stripped)} chars)")
```

### 3. `scripts/phase_d_content_check.py`

#### 3-1. importに`count_source_headings`を追加

**Before:**

```python
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
```

**After:**

```python
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics, count_source_headings
```

#### 3-2. _compute_content_warningsメソッドを追加

PhaseDContentCheckクラスに以下のメソッドを追加する。配置位置は`__init__`メソッドと`_build_prompt`メソッドの間。

```python
    def _compute_content_warnings(self, knowledge, source_content, source_format, file_info):
        """Run S6/S7/S9/S13 content quality checks. Returns list of warning strings."""
        warnings = []

        # S6: Non-empty hints
        for entry in knowledge.get("index", []):
            if not entry.get("hints"):
                warnings.append(f"S6: Section '{entry['id']}' has empty hints")

        # S7: Non-empty sections
        for sid, content in knowledge.get("sections", {}).items():
            if not content.strip():
                warnings.append(f"S7: Section '{sid}' has empty content")

        # S9: Section count vs source headings
        if file_info and "section_range" in file_info:
            expected = len(file_info["section_range"]["sections"])
        else:
            expected = count_source_headings(source_content, source_format)

        actual = len(knowledge.get("sections", {}))
        if expected > 0 and actual < expected:
            warnings.append(f"S9: Section count {actual} < source headings {expected}")

        # S13: Minimum section length
        for sid, content in knowledge.get("sections", {}).items():
            stripped = content.strip()
            if len(stripped) < 20 and stripped not in ["なし。", "なし"]:
                warnings.append(f"S13: Section '{sid}' too short ({len(stripped)} chars)")

        return warnings
```

#### 3-3. _build_promptにwarnings引数を追加

**Before:**

```python
    def _build_prompt(self, file_info, knowledge, source_content):
        prompt = self.prompt_template
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        return prompt
```

**After:**

```python
    def _build_prompt(self, file_info, knowledge, source_content, warnings=None):
        prompt = self.prompt_template
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        if warnings:
            prompt = prompt.replace("{CONTENT_WARNINGS}",
                                    "\n".join(f"- {w}" for w in warnings))
        else:
            prompt = prompt.replace("{CONTENT_WARNINGS}", "なし")
        return prompt
```

#### 3-4. check_one内でcontent_warningsを計算してプロンプトに渡す

check_one内の`_build_prompt`呼び出し直前にwarnings計算を追加する。

**Before:**

```python
        prompt = self._build_prompt(file_info, knowledge, source)
```

**After:**

```python
        warnings = self._compute_content_warnings(knowledge, source, file_info["format"], file_info)
        prompt = self._build_prompt(file_info, knowledge, source, warnings=warnings)
```

### 4. `prompts/content_check.md`

25行目の`---`（Knowledge Fileセクションの後の区切り線）の直後、27行目の`## Validation Checklist`の直前に以下を追加する。（注意: 113行目にも`---`があるがそちらではない）

```markdown
## Content Quality Warnings (automated pre-check)

The following content quality warnings were detected by automated checks before this AI review.
Evaluate each warning against the source file and include it as a finding if the issue is real.
If the source justifies the current state (e.g., the source section is genuinely short, or headings were intentionally merged), do NOT report it as a finding.

{CONTENT_WARNINGS}

```

### 5. `tests/ut/test_phase_c.py`

#### 5-1. 削除するテスト

以下の2テストメソッドを削除する:

- `test_s6_empty_hints`
- `test_s7_empty_section`

#### 5-2. 追加するテスト

`TestStructureValidation`クラス内に以下を追加する。S6/S7/S9/S13がPhase Cのerrorsに含まれないことを検証する。

```python
    def test_s6_not_checked_by_phase_c(self, ctx):
        """S6 (empty hints) must NOT be checked by Phase C."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert not any("S6" in e for e in errors)

    def test_s7_not_checked_by_phase_c(self, ctx):
        """S7 (empty section) must NOT be checked by Phase C."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = ""
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert not any("S7" in e for e in errors)

    def test_s9_not_checked_by_phase_c(self, ctx):
        """S9 (section count) must NOT be checked by Phase C."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        del k["sections"]["module-list"]
        k["index"] = [e for e in k["index"] if e["id"] != "module-list"]
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert not any("S9" in e for e in errors)

    def test_s13_not_checked_by_phase_c(self, ctx):
        """S13 (short section) must NOT be checked by Phase C."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "短い"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert not any("S13" in e for e in errors)
```

### 6. `tests/ut/test_phase_d_content_warnings.py`（新規作成）

Phase Dの`_compute_content_warnings`のユニットテスト。AIを使わないPythonチェックなので高速に実行できる。

```python
"""Phase D _compute_content_warnings unit tests. No AI, runs fast."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from conftest import load_fixture


@pytest.fixture
def checker(ctx):
    from phase_d_content_check import PhaseDContentCheck
    return PhaseDContentCheck(ctx, dry_run=True)


class TestComputeContentWarnings:

    def test_clean_knowledge_returns_no_warnings(self, checker):
        """Valid knowledge file produces no warnings."""
        k = load_fixture("sample_knowledge.json")
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert warnings == []

    def test_s6_empty_hints(self, checker):
        """S6: Empty hints array triggers warning."""
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S6" in w for w in warnings)

    def test_s7_empty_section_content(self, checker):
        """S7: Empty section content triggers warning."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = ""
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S7" in w for w in warnings)

    def test_s9_section_count_less_than_headings(self, checker):
        """S9: Fewer sections than source headings triggers warning."""
        k = load_fixture("sample_knowledge.json")
        del k["sections"]["module-list"]
        k["index"] = [e for e in k["index"] if e["id"] != "module-list"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S9" in w for w in warnings)

    def test_s9_with_split_file_info(self, checker):
        """S9: Uses section_range from file_info for split files."""
        k = load_fixture("sample_knowledge.json")
        # Only 2 sections, but file_info says 5 section headings
        file_info = {
            "section_range": {
                "sections": ["a", "b", "c", "d", "e"]
            }
        }
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", file_info)
        assert any("S9" in w for w in warnings)

    def test_s13_short_section(self, checker):
        """S13: Section shorter than 20 chars triggers warning."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "短い"
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S13" in w for w in warnings)

    def test_s13_nashi_excluded(self, checker):
        """S13: 'なし。' is allowed even though < 20 chars."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "なし。"
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert not any("S13" in w for w in warnings)

    def test_multiple_warnings(self, checker):
        """Multiple issues produce multiple warnings."""
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []      # S6
        k["sections"]["overview"] = ""   # S7
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S6" in w for w in warnings)
        assert any("S7" in w for w in warnings)
```

### 7. `tests/ut/test_no_knowledge_content.py`

変更なし。S6/S7/S9/S13に依存するテストがないため影響しない。全テストpassを確認するのみ。

## 実行手順

### Step 1: テストが通ることを確認（変更前のベースライン）

```bash
cd tools/knowledge-creator && python -m pytest tests/ut/test_phase_c.py tests/ut/test_no_knowledge_content.py -v
```

全テストがpassすることを確認する。

### Step 2: テストを先に変更（TDD）

以下を実行する:

- `tests/ut/test_phase_c.py`: `test_s6_empty_hints`と`test_s7_empty_section`を削除し、4つの新テスト（5-2）を追加
- `tests/ut/test_phase_d_content_warnings.py`: 新規作成（変更詳細6の全内容）

### Step 3: 新テストが期待通りに失敗することを確認

```bash
cd tools/knowledge-creator && python -m pytest tests/ut/test_phase_c.py -v -k "s6_not_checked or s7_not_checked or s9_not_checked or s13_not_checked"
```

Phase Cにまだ S6/S7/S9/S13があるのでerrorsに含まれてfailするはず。

```bash
cd tools/knowledge-creator && python -m pytest tests/ut/test_phase_d_content_warnings.py -v
```

Phase Dに`_compute_content_warnings`がまだないのでAttributeErrorでfailするはず。

両方のfailを確認できたら次へ。

### Step 4: common.pyを変更（変更詳細1-1, 1-2）

### Step 5: phase_c_structure_check.pyを変更（変更詳細2-1〜2-7）

変更詳細2-1（import変更）と2-2（メソッド削除）と2-3〜2-6（S6/S7/S9/S13削除）をすべて同時に適用する。部分的に適用するとAttributeErrorになるため、必ずまとめて変更する。

### Step 6: Phase Cテストが全パスすることを確認

```bash
cd tools/knowledge-creator && python -m pytest tests/ut/test_phase_c.py tests/ut/test_no_knowledge_content.py -v
```

### Step 7: phase_d_content_check.pyを変更（変更詳細3-1〜3-4）

### Step 8: Phase Dユニットテストがパスすることを確認

```bash
cd tools/knowledge-creator && python -m pytest tests/ut/test_phase_d_content_warnings.py -v
```

### Step 9: content_check.mdを変更（変更詳細4）

### Step 10: 全テスト実行

```bash
cd tools/knowledge-creator && python -m pytest tests/ -v
```

run.pyとPhase Dの`run()`シグネチャは変更なし（content_warningsはcheck_one内で完結する）のため、E2Eテストへの影響はない。全テストpassを確認する。

### Step 11: コミット前検証

```bash
cd tools/knowledge-creator && python -m pytest tests/ -v
```

全テストpassを確認してからコミットする。
