# セクション単位分割への切り替え実装タスク

## 背景

前回のタスク（Task 0-7, commit 6bb71f9..1bf0787）で「グループ化パート分割」方式を実装した。
しかし、GROUP_LINE_LIMIT/GROUP_SECTION_LIMIT/LARGE_SECTION_LINE_THRESHOLDの3閾値チューニングが不安定なため、**「1 h2セクション = 1分割ファイル」のセクション単位方式**に切り替える。

### 変更の本質

- **Before**: 「h2セクションをグループ化して800行以内のパートにまとめる」
- **After**: 「h2セクションが2個以上あれば、各h2セクションを1ファイルに分割する。h2が500行を超える場合はh3で再分割する」

### 変更しないもの

- Phase B/D/E: `section_range`を使った処理は既にTask 2で実装済み。セクション単位でもそのまま動作する
- merge.py: `split_info.original_id`による集約ロジックは変更不要（パート数が増えるだけ）
- run.py: フェーズ制御（ABCDEM）は変更不要
- phase_m_finalize.py: 変更不要

### IDの命名規則変更

```
Before: {original_id}-{part_num}   例: libraries-tag-1, libraries-tag-2
After:  {original_id}--{section_id} 例: libraries-tag--overview, libraries-tag--sec-a3b2c1d4
```

ダブルハイフン `--` で区切る。section_idはタイトルから生成する（詳細はTask Aに記載）。

---

## Task A: step2_classify.pyの分割ロジック変更

### 変更箇所1: 閾値定数（103-106行目）

```python
# Before (103-106行目)
    FILE_LINE_THRESHOLD = 800
    GROUP_LINE_LIMIT = 800
    GROUP_SECTION_LIMIT = 15
    LARGE_SECTION_LINE_THRESHOLD = 800

# After
    SPLIT_SECTION_THRESHOLD = 2  # h2セクションがこの数以上あれば分割
    H3_FALLBACK_THRESHOLD = 500  # h2セクションがこの行数を超えたらh3で再分割
```

### 変更箇所2: should_split_file（237-260行目）

```python
# Before (237-260行目)
    def should_split_file(self, file_path: str, format: str) -> tuple:
        ...
        file_exceeds = total_lines > self.FILE_LINE_THRESHOLD
        has_large_section = any(s['line_count'] > self.LARGE_SECTION_LINE_THRESHOLD for s in sections)
        has_many_sections = len(sections) > self.GROUP_SECTION_LIMIT
        should_split = file_exceeds or has_large_section or has_many_sections
        return should_split, sections, total_lines

# After: 全体を以下に置き換え
    def should_split_file(self, file_path: str, format: str) -> tuple:
        """Check if file should be split into per-section files.

        Returns:
            (should_split: bool, sections: list, total_lines: int)
        """
        if format != "rst":
            return False, [], 0

        full_path = os.path.join(self.ctx.repo, file_path)
        if not os.path.exists(full_path):
            return False, [], 0

        content = read_file(full_path)
        lines = content.splitlines()
        total_lines = len(lines)
        sections = self.analyze_rst_sections(content)

        # h2セクションが2個以上あれば分割
        should_split = len(sections) >= self.SPLIT_SECTION_THRESHOLD
        return should_split, sections, total_lines
```

### 変更箇所3: split_file_entry（270-360行目）

現行のメソッド全体（h3展開 + グループ化ループ）を以下に置き換える:

```python
    def split_file_entry(self, base_entry: dict, sections: list, content: str) -> list:
        """Split a file entry into one entry per h2 section.

        h2セクションが H3_FALLBACK_THRESHOLD を超える場合、h3サブセクションで再分割する。

        Args:
            base_entry: Original classified entry
            sections: List of h2 section info from analyze_rst_sections
            content: Full source file content

        Returns:
            List of split entries, one per section (h2 or h3)
        """
        # Step 1: h2セクションをh3で展開（必要な場合のみ）
        expanded_sections = []
        for section in sections:
            if section['line_count'] > self.H3_FALLBACK_THRESHOLD:
                h3_subs = self.analyze_rst_h3_subsections(
                    content, section['start_line'], section['end_line']
                )
                if h3_subs:
                    # h2セクションのh3より前の部分（プリアンブル）を最初のh3に含める
                    if h3_subs[0]['start_line'] > section['start_line']:
                        h3_subs[0]['start_line'] = section['start_line']
                        h3_subs[0]['line_count'] = h3_subs[0]['end_line'] - h3_subs[0]['start_line']
                    expanded_sections.extend(h3_subs)
                    print(f"    h3 fallback: '{section['title']}' ({section['line_count']} lines) → {len(h3_subs)} h3 subsections")
                else:
                    # h3がない巨大h2 → そのまま（警告付き）
                    expanded_sections.append(section)
                    print(f"    WARNING: '{section['title']}' has {section['line_count']} lines but no h3 subsections")
            else:
                expanded_sections.append(section)

        # Step 2: 各セクションから1エントリを生成
        result = []
        base_id = base_entry['id']
        type_ = base_entry['type']
        category = base_entry['category']
        total_parts = len(expanded_sections)
        used_ids = set()  # 同一ファイル内のID重複を回避

        for part_num, section in enumerate(expanded_sections, 1):
            section_id = self._title_to_section_id(section['title'])
            # 重複回避: 同じsection_idが既出なら連番を付与
            original_section_id = section_id
            counter = 2
            while section_id in used_ids:
                section_id = f"{original_section_id}-{counter}"
                counter += 1
            used_ids.add(section_id)
            split_id = f"{base_id}--{section_id}"

            result.append({
                **base_entry,
                'id': split_id,
                'output_path': f"{type_}/{category}/{split_id}.json",
                'assets_dir': f"{type_}/{category}/assets/{split_id}/",
                'section_range': {
                    'start_line': section['start_line'],
                    'end_line': section['end_line'],
                    'sections': [section['title']]
                },
                'split_info': {
                    'is_split': True,
                    'part': part_num,
                    'total_parts': total_parts,
                    'original_id': base_id
                }
            })

        return result

    @staticmethod
    def _title_to_section_id(title: str) -> str:
        """Convert section title to a safe, deterministic ID string.

        ASCII英数字部分を抽出。十分な長さがなければmd5ハッシュを使う。

        Examples:
            "HTMLエスケープ漏れを防げる" -> "html"
            "module-list" -> "module-list"
            "モジュール一覧" -> "sec-xxxxxxxx" (md5ハッシュ)
            "DefaultMeterBinderListProvider" -> "defaultmeterbinderlistprovider"
        """
        import hashlib
        # ASCII英数字とハイフンのみ残す
        ascii_id = re.sub(r'[^a-zA-Z0-9-]', '', title.replace(' ', '-')).lower().strip('-')
        # 連続ハイフンを1つに
        ascii_id = re.sub(r'-+', '-', ascii_id)
        if ascii_id and len(ascii_id) >= 3:
            return ascii_id[:50]
        # 日本語タイトル等: md5ハッシュの先頭8文字
        h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        return f"sec-{h}"
```

### 変更箇所4: analyze_rst_h3_subsectionsメソッドを保持（190-225行目）

h3フォールバックで使用するため、`analyze_rst_h3_subsections`メソッドは**そのまま保持**する。変更不要。

### テスト: test_split_criteria.pyを全面書き直し

現行のtest_split_criteria.py (273行) は全てグループ化方式のテスト（閾値、行数制限、セクション数制限、h3展開）のため、**ファイル全体を以下に置き換える**:

```python
"""Tests for section-unit split criteria."""
import os
import re
import pytest
from steps.step2_classify import Step2Classify


class TestSectionSplit:
    """Test section-unit splitting."""

    def _make_rst(self, section_count, lines_per_section=20):
        """Helper: create RST content with N h2 sections."""
        parts = ["Main Title\n==========\n\nPreamble content.\n"]
        for i in range(1, section_count + 1):
            body = "\n".join([f"Line {j} of section {i}" for j in range(1, lines_per_section + 1)])
            parts.append(f"Section {i}\n----------\n{body}\n")
        return "\n".join(parts)

    def test_single_section_not_split(self, ctx):
        """h2セクション1個 → 分割しない。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(1)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert not should_split
        assert len(sections) == 1

    def test_two_sections_split(self, ctx):
        """h2セクション2個 → 分割する。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(2)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert should_split
        assert len(sections) == 2

    def test_split_produces_one_entry_per_section(self, ctx):
        """5セクション → 5エントリ、各1セクション。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(5)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'test-file', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test-file.json',
            'assets_dir': 'component/test/assets/test-file/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        assert len(entries) == 5
        for entry in entries:
            assert len(entry['section_range']['sections']) == 1
            assert entry['split_info']['total_parts'] == 5
            assert entry['split_info']['original_id'] == 'test-file'

    def test_split_id_format(self, ctx):
        """分割IDが {original}--{section_id} 形式であること。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(3)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'libraries-tag', 'type': 'component', 'category': 'libraries',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/libraries/libraries-tag.json',
            'assets_dir': 'component/libraries/assets/libraries-tag/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        for entry in entries:
            assert '--' in entry['id'], f"ID should contain '--': {entry['id']}"
            assert entry['id'].startswith('libraries-tag--')

    def test_title_to_section_id_ascii(self):
        """英字タイトル → ASCII部分を使用。"""
        result = Step2Classify._title_to_section_id("module-list")
        assert result == "module-list"

    def test_title_to_section_id_mixed(self):
        """英字+日本語タイトル → ASCII部分が3文字以上ならそれを使用。"""
        result = Step2Classify._title_to_section_id("HTMLエスケープ")
        assert result == "html"

    def test_title_to_section_id_japanese_only(self):
        """日本語のみタイトル → ハッシュ。"""
        result = Step2Classify._title_to_section_id("モジュール一覧")
        assert result.startswith("sec-")
        assert len(result) == 12  # "sec-" + 8 hex chars

    def test_title_to_section_id_deterministic(self):
        """同じタイトル → 同じID（決定的）。"""
        id1 = Step2Classify._title_to_section_id("可変条件を持つSQL")
        id2 = Step2Classify._title_to_section_id("可変条件を持つSQL")
        assert id1 == id2

    def test_preamble_in_first_section(self, ctx):
        """最初のh2の前のプリアンブルが最初のセクションに含まれること。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(3)
        sections = classifier.analyze_rst_sections(content)

        # 現行のanalyze_rst_sectionsは最初のセクションのstart_lineを0にする
        assert sections[0]['start_line'] == 0

    def test_non_rst_not_split(self, ctx):
        """format="md" → 分割しない。"""
        classifier = Step2Classify(ctx, dry_run=True)
        should_split, _, _ = classifier.should_split_file("test.md", "md")
        assert not should_split

    def test_section_range_covers_all_lines(self, ctx):
        """全エントリのsection_rangeが全行をカバーすること。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(3, lines_per_section=10)
        sections = classifier.analyze_rst_sections(content)
        lines = content.splitlines()

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        all_lines = set()
        for entry in entries:
            sr = entry['section_range']
            for i in range(sr['start_line'], sr['end_line']):
                all_lines.add(i)

        assert all_lines == set(range(len(lines)))

    def test_duplicate_titles_get_unique_ids(self, ctx):
        """同じタイトルのh2セクションが重複しないIDを取得すること。"""
        classifier = Step2Classify(ctx, dry_run=True)

        # 同じタイトルのh2セクションを3つ作る
        parts = ["Main Title\n==========\n\nPreamble.\n"]
        for i in range(3):
            body = "\n".join([f"Line {j}" for j in range(1, 11)])
            parts.append(f"Same Title\n----------\n{body}\n")
        content = "\n".join(parts)

        sections = classifier.analyze_rst_sections(content)
        assert len(sections) == 3

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        ids = [e['id'] for e in entries]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"
        # 期待: test--same-title, test--same-title-2, test--same-title-3
        assert ids[0] == "test--same-title"
        assert ids[1] == "test--same-title-2"
        assert ids[2] == "test--same-title-3"

    def test_h3_fallback_for_large_h2(self, ctx):
        """500行超のh2セクションがh3で再分割されること。"""
        classifier = Step2Classify(ctx, dry_run=True)

        # h2が2つ。1つ目は小さい、2つ目は600行超でh3が3つ
        small_body = "\n".join([f"Line {j}" for j in range(1, 21)])
        # 大きいh2の中にh3を3つ（各200行）
        large_body_parts = ["Large section intro.\n"]
        for i in range(1, 4):
            h3_body = "\n".join([f"Line {j} of h3-{i}" for j in range(1, 201)])
            large_body_parts.append(f"Subsection {i}\n^^^^^^^^^^^^^^^^^^^^^^\n{h3_body}\n")
        large_body = "\n".join(large_body_parts)

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Small Section\n----------\n{small_body}\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        sections = classifier.analyze_rst_sections(content)
        assert len(sections) == 2

        # 2つ目のh2が500行超であることを確認
        assert sections[1]['line_count'] > 500

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # 1つ目のh2(1エントリ) + 2つ目のh2がh3展開(3エントリ) = 4エントリ
        assert len(entries) == 4
        # 全エントリの section_range.sections は長さ1
        for entry in entries:
            assert len(entry['section_range']['sections']) == 1

    def test_h3_fallback_no_h3_keeps_large_h2(self, ctx, capsys):
        """500行超のh2にh3がない場合、そのままh2を1エントリとして扱うこと。"""
        classifier = Step2Classify(ctx, dry_run=True)

        # h2が2つ。2つ目は600行だがh3がない
        small_body = "\n".join([f"Line {j}" for j in range(1, 21)])
        large_body = "\n".join([f"Line {j}" for j in range(1, 601)])

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Small Section\n----------\n{small_body}\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # h3がないのでh2がそのまま → 2エントリ
        assert len(entries) == 2

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
```

### 完了条件

```bash
cd tools/knowledge-creator && python -m pytest tests/test_split_criteria.py -v
```

全テストがパス。

---

## Task B: テスト全体のID形式を新方式に統一

### 背景

既存テストのmock内で`file_id.split("-")[-1]`によりパート番号を取得しているパターンがある（test_e2e_split.py 25行目, 230行目, 354行目, 411行目）。新ID形式（`test--section-1`）ではこのパターンが壊れる。

### 方針

テストのclassified.jsonフィクスチャとmockを新ID形式に変更する。**mockのパート番号取得を`split_info.part`から取得する方式**に変更することで、IDの命名規則への依存をなくす。

### 変更ファイルと変更内容

#### test_e2e_split.py

**変更パターン1: classified.jsonフィクスチャのID変更**

全3テストメソッド（test_full_pipeline_split_to_final, test_full_pipeline_split_with_fix_cycle, test_mixed_split_and_nonsplit）で、フィクスチャ内のIDを変更:

```python
# Before (全箇所共通パターン)
"id": "test-1",
"output_path": "component/test/test-1.json",
"assets_dir": "component/test/assets/test-1/",

# After
"id": "test--section-1",
"output_path": "component/test/test--section-1.json",
"assets_dir": "component/test/assets/test--section-1/",
```

同様に `test-2` → `test--section-2`, `split-1` → `split--section-1`, `split-2` → `split--section-2`。

**変更パターン2: mock内のパート番号取得**

mockがfile_idからpart番号を取得するパターンを、classified.jsonのsplit_info.partを使う方式に変更するのが理想だが、mock関数のシグネチャを変えると大幅な改修になる。代わりに、IDからダブルハイフン以降のサフィックスを取得する:

```python
# Before (25, 230, 354, 411行目)
part_num = file_id.split("-")[-1]  # test-1 -> 1, test-2 -> 2

# After
part_num = file_id.split("--")[-1].split("-")[-1]  # test--section-1 -> section-1 -> 1
```

**変更パターン3: パートファイル存在確認のアサーション**

```python
# Before
assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test-1.json")
assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test-2.json")
assert "test-1" not in ids
assert "test-2" not in ids

# After
assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-1.json")
assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-2.json")
assert "test--section-1" not in ids
assert "test--section-2" not in ids
```

同様に`split-1` → `split--section-1`, `split-2` → `split--section-2`。

#### test_merge.py

フィクスチャ内のIDを変更。全テストメソッドで以下のパターンを適用:

```python
# Before
"id": "libraries-tag-1",
"output_path": "component/libraries/libraries-tag-1.json",
"assets_dir": "component/libraries/assets/libraries-tag-1/",

# After
"id": "libraries-tag--overview",
"output_path": "component/libraries/libraries-tag--overview.json",
"assets_dir": "component/libraries/assets/libraries-tag--overview/",
```

`libraries-tag-2` → `libraries-tag--usage`。3パートのテストがあれば`libraries-tag-3` → `libraries-tag--rules`。

ファイルパスの参照も全て一致させる:
```python
# Before
write_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag-1.json", part1)
os.makedirs(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-1", exist_ok=True)

# After
write_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag--overview.json", part1)
os.makedirs(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag--overview", exist_ok=True)
```

knowledge JSONの中身のassets参照:
```python
# Before
"overview": "タグライブラリの概要。\n\n画像: assets/libraries-tag-1/image.png"

# After
"overview": "タグライブラリの概要。\n\n画像: assets/libraries-tag--overview/image.png"
```

traceファイルのパスも同様に更新。

#### test_split_validation.py

test_merge.pyと同じパターンでフィクスチャのID変更:
- `libraries-tag-1` → `libraries-tag--overview`
- ファイルパス、アサーション内のID参照も全て変更

#### test_phase_m.py, test_run_flow.py, test_run_phases.py

split関連のフィクスチャがある場合は同じパターンで変更。

### 一括置換コマンド

以下のsedコマンドで大部分の置換を一括実行できる。テスト対象は5ファイル、計76箇所:

```bash
cd tools/knowledge-creator

# ===== Step 1: IDの置換 =====

# test-1 → test--section-1, test-2 → test--section-2
# 対象: test_e2e_split.py(6箇所), test_phase_m.py(14箇所), test_run_flow.py(13箇所)
for f in tests/test_e2e_split.py tests/test_phase_m.py tests/test_run_flow.py; do
  sed -i 's/"test-1"/"test--section-1"/g' "$f"
  sed -i 's/"test-2"/"test--section-2"/g' "$f"
  sed -i 's/test-1\.json/test--section-1.json/g' "$f"
  sed -i 's/test-2\.json/test--section-2.json/g' "$f"
  sed -i 's|assets/test-1/|assets/test--section-1/|g' "$f"
  sed -i 's|assets/test-2/|assets/test--section-2/|g' "$f"
done

# split-1 → split--section-1, split-2 → split--section-2
# 対象: test_e2e_split.py(4箇所)
sed -i 's/"split-1"/"split--section-1"/g' tests/test_e2e_split.py
sed -i 's/"split-2"/"split--section-2"/g' tests/test_e2e_split.py
sed -i 's/split-1\.json/split--section-1.json/g' tests/test_e2e_split.py
sed -i 's/split-2\.json/split--section-2.json/g' tests/test_e2e_split.py
sed -i 's|assets/split-1/|assets/split--section-1/|g' tests/test_e2e_split.py
sed -i 's|assets/split-2/|assets/split--section-2/|g' tests/test_e2e_split.py

# libraries-tag-1 → libraries-tag--overview, libraries-tag-2 → libraries-tag--usage
# 対象: test_merge.py(6箇所), test_split_validation.py(3箇所)
for f in tests/test_merge.py tests/test_split_validation.py; do
  sed -i 's/"libraries-tag-1"/"libraries-tag--overview"/g' "$f"
  sed -i 's/"libraries-tag-2"/"libraries-tag--usage"/g' "$f"
  sed -i 's/"libraries-tag-3"/"libraries-tag--rules"/g' "$f"
  sed -i 's/libraries-tag-1\.json/libraries-tag--overview.json/g' "$f"
  sed -i 's/libraries-tag-2\.json/libraries-tag--usage.json/g' "$f"
  sed -i 's/libraries-tag-3\.json/libraries-tag--rules.json/g' "$f"
  sed -i 's|assets/libraries-tag-1/|assets/libraries-tag--overview/|g' "$f"
  sed -i 's|assets/libraries-tag-2/|assets/libraries-tag--usage/|g' "$f"
  sed -i 's|assets/libraries-tag-3/|assets/libraries-tag--rules/|g' "$f"
done

# split-1/split-2 in test_merge.py (split files used in mixed tests)
sed -i 's/"split-1"/"split--section-1"/g' tests/test_merge.py
sed -i 's/"split-2"/"split--section-2"/g' tests/test_merge.py
sed -i 's/split-1\.json/split--section-1.json/g' tests/test_merge.py
sed -i 's/split-2\.json/split--section-2.json/g' tests/test_merge.py
sed -i 's|assets/split-1/|assets/split--section-1/|g' tests/test_merge.py
sed -i 's|assets/split-2/|assets/split--section-2/|g' tests/test_merge.py

# ===== Step 2: mock内のパート番号取得を修正 =====
# test_e2e_split.py の4箇所
sed -i 's/file_id\.split("-")\[-1\]/file_id.split("--")[-1].split("-")[-1]/g' tests/test_e2e_split.py
```

### Step 1実行後の手動確認が必要な箇所

sed置換ではカバーできない可能性がある箇所:

1. **traceファイルのfile_id値** — `"file_id": "test-1"` が `"file_id": "test--section-1"` に変わるか確認
2. **test_merge.pyのknowledge JSON内のassets参照文字列** — `assets/libraries-tag-1/image.png` が正しく置換されたか確認
3. **test_phase_m.pyのtraceファイルパス** — `write_json(f"{ctx.trace_dir}/test-1.json", ...)` が正しく置換されたか確認

### 確認方法

```bash
# 旧ID形式（単一ハイフン+数字の分割ID）がテストに残っていないことを確認
grep -rn '"test-[12]"' tools/knowledge-creator/tests/
grep -rn '"split-[12]"' tools/knowledge-creator/tests/
grep -rn '"libraries-tag-[0-9]"' tools/knowledge-creator/tests/
# → 各コマンドの出力が0行であること（test_split_criteria.pyは全面書き直し済みのため対象外）
```

### 完了条件

```bash
cd tools/knowledge-creator && python -m pytest tests/ -v
```

全テストがパス。かつ、上記のgrep確認で旧ID形式が残っていないこと。

---

## Task C: テストモードでの動作確認

### 目的

実データ（nablarch-document）でStep2Classifyの新しい分割ロジックが正しく動作することを確認する。

### 実行

```bash
cd tools/knowledge-creator
python run.py --version v6 --phases A --test test_batch.txt --dry-run
```

### 確認項目

1. libraries-tag がh2セクション数分のエントリに分割されること（現行4パート → h2の数だけ）。ただし「使用方法」(2630行)はh3で再分割されるので、h2数+h3数-1のエントリになる
2. adapters-micrometer_adaptor がh2セクション数分のエントリに分割されること（現行2パート → h2の数だけ）
3. libraries-tag_reference がh2セクション数分のエントリに分割されること（現行3パート → h2の数だけ）
4. 各エントリのIDが`--`区切りであること
5. h2セクション1個のファイルは分割されていないこと
6. h3フォールバック: tag.rstの「使用方法」がh3で35個のサブセクションに分割されていること（ログに `h3 fallback:` が表示される）

### 完了条件

上記の確認項目が全て満たされていること。

---

## 実行順序

```
Task A → Task B → Task C
```

Task Aでstep2_classify.pyの分割ロジックを変更し、test_split_criteria.pyで単体テスト。
Task Bで全テストのフィクスチャを新ID形式に統一し、全テストパス。
Task Cでテストモード再実行により実データでの動作確認。

## 補足: 小さいセクションの結合は行わない

「モジュール一覧」のような数行のセクションも1ファイルとして生成する。小セクション結合ルールを入れると分割ロジックの複雑さが戻るため、シンプルさを優先する。APIコールのオーバーヘッドは並列実行で吸収する。

## 補足: _title_to_section_idの決定性

日本語タイトルからIDを生成する際、翻訳は行わずmd5ハッシュを使う。理由:
- 翻訳は非決定的でLLM依存 → 再実行で異なるIDが生成されるリスク
- ハッシュはタイトル文字列から決定的に生成される
- IDは内部的な識別子であり、人間が読む必要は低い（マージ後は消える）
- `split_info.original_id`で元ファイルとの対応は常に追跡可能
