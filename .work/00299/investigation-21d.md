# Phase 21-D 調査結果: RBKC JSON スキーマと変換/検証ロジック

## 目的

RBKC の根本目的（ソース忠実な決定論的変換）に沿うよう、converter が独自ルールで作っている section title（`_PREAMBLE_TITLE = "概要"` 固定値など）を廃止し、ソースに実在する構造のみを JSON に反映する設計へゼロベース見直しするための事前調査。

---

## 1. 現状の JSON スキーマ

### スキーマの実体

**定義場所1 (docstring)**: `tools/rbkc/scripts/run.py:6-19`

```
{
  "id": "file-id",
  "title": "Document Title",
  "no_knowledge_content": false,
  "sections": [
    {
      "id": "s1",
      "title": "Section Title",
      "content": "Markdown content",
      "hints": ["keyword1", "keyword2"]
    }
  ]
}
```

**生成コード**: `tools/rbkc/scripts/run.py:212-235` (`_convert_and_write`)

**重要な現状**:
- トップレベルに **`content` フィールドは存在しない**
- h1 直下の本文は `sections[].title="概要"` という疑似セクションに押し込まれる
- JSON スキーマ定義ファイル (JSONSchema 等) は存在せず、形式は生成コード + dataclass のみで表現されている

### データクラス

`tools/rbkc/scripts/create/converters/rst.py:23-33`

```python
@dataclass
class Section:
    title: str
    content: str   # Markdown

@dataclass
class RSTResult:
    title: str
    no_knowledge_content: bool
    sections: list[Section] = field(default_factory=list)
```

MD / xlsx converter も同じ `RSTResult`/`Section` を再利用。

### 実サンプル

`.claude/skills/nabledge-6/knowledge/guide/biz-samples/biz-samples-13.json` には "概要" セクションが重複発生（s1, s2 とも `title=概要`）する不整合例あり。

---

## 2. 全 converter

### 2.1 RST converter (`tools/rbkc/scripts/create/converters/rst.py`)

**固定値**:
- L54: `_PREAMBLE_TITLE = "概要"` ← 問題の根源

**固定値使用箇所** (すべて `_split_sections` 関数内):
- L133: 見出しが 1 つもない RST → `return "", [(_PREAMBLE_TITLE, lines)]`
- L228: h2/h3 が見つからず trailing_lines のみある場合
- L233: h1 直下〜最初の h2 直前の preamble 非空

**h1/h2/h3 扱いロジック** (`_split_sections` L119-235):
- 最初に出現した underline 文字を h1 として扱う
- 2・3 番目の underline 文字を h2/h3
- h4+ は `#` 付き文字列で現在 section の content に埋め込み

### 2.2 MD converter (`tools/rbkc/scripts/create/converters/md.py`)

**固定値**: `_PREAMBLE_TITLE` は **存在しない**。
- L74: `current_title = ""` (preamble の初期タイトルは空文字)
- L131: `sections = [s for s in sections if s.title or s.content]` (空な preamble セクションは除去)

**h1/h2/h3 扱い** (`_split_sections` L60-98):
- `level == 1` → タイトル、section は作らない
- `level >= 2` → 全て section 境界

**RST と差異**: MD converter では preamble は `title=""` のまま流れ、content が非空なら L131 で残り、空なら除去される。**2 converter で preamble の扱いが不整合**。

### 2.3 xlsx_releasenote / xlsx_security

- いずれも単一セクション、`title=""` で全内容を投入する単純構造
- `xlsx_releasenote.py:64`, `xlsx_security.py:40`

### 2.4 Converter dispatch

`tools/rbkc/scripts/run.py:56-71` (`_converter_for`): rst/md/xlsx (releasenote vs security) の分岐のみ

---

## 3. docs MD 生成ロジック (`tools/rbkc/scripts/create/docs.py`)

**出力形式**:
```
# {title}
## {section_title}
{section_content}
<details><summary>keywords</summary>
keyword1, keyword2, ...
</details>
```

**`##` 見出しの生成条件** (`_render_full` L83-107):
- L92: `lines.append(f"## {title}")` ← **section.title の値がそのまま ## 見出しになる。空でも無条件に `## ` が出力される**

**no_knowledge_content 分岐** (`_render_no_knowledge` L77-80): `# {title}` だけで終わる

**README 生成**: `_generate_readme` L110-139 (type/category/title の目次のみ、section 非依存)

**スキーマ変更時の影響**: 現行ロジックは「セクション配列がある前提」で `## {title}` を無条件出力する。`title=""` の preamble section が docs MD に `## \n` という空の見出しを出してしまう。

---

## 4. hints ロジック

### 4.1 `tools/rbkc/scripts/create/hints.py`

**Step A マッピング** (`_map_step_a`):
- カタログ Expected Sections (RST h2 見出しリスト) を key としてマップを作成
- KC index の title を expected と照合

**Step B マッピング** (`_map_step_b`):
- RST source から見出しを抽出 (underline-only heading = h2)
- content overlap で KC entry を RST heading にマップ

**key の正体**:
- Step A: カタログ `section_range.sections` (RST h2 見出し)
- Step B: RST 内の underline-only 見出し
- fallback: KC title

→ **どのルートでも `"概要"` 固定値は hints.py 内では生成されない**。しかし「h2 が存在しない RST の場合 preamble は section_range.sections に無く、代わりに KC の最初のエントリの title (しばしば "概要") が使われる」結果として `hints/v6.json` に "概要" key が大量発生している。

### 4.2 run.py 側の lookup フロー

- L74-113: `load_existing_hints` — 既存 RBKC JSON から `{file_id: {section_title: hints}}` を復元
- L116-139: `lookup_hints_with_fallback` — hints_idx 優先 + 既存 hints fallback
- L215-218: 変換中に section.title を key として hints を引き当て

### 4.3 hints/v6.json フォーマット

```json
{
  "version": "6",
  "hints": {
    "biz-samples-05": {
      "概要": ["FileManagementUtil", ...],
      ...
    }
  }
}
```

- 全エントリが `{file_id: {section_title: hints_array}}` の形
- "概要" key が多数存在
- **スキーマを変えると、この key 体系全てを再マップする必要がある**

### 4.4 `.pr/00299/extract_hints.py`

One-time スクリプトとしてマークされ「手動編集した後は再生成するな」と docstring に明記。`build_hints_index` を使用。

---

## 5. verify チェック (`tools/rbkc/scripts/verify/verify.py`)

### 5.1 全チェック関数

| ID | 関数 | 行 | セクション構造依存 |
|----|------|----|-------------------|
| QO5 | `check_json_docs_md_consistency` | L32-61 | あり |
| QC5 | `check_format_purity` | L119-158 | あり |
| QC6 | `check_hints_completeness` | L165-194 | あり |
| QC1-4 | `check_content_completeness` | L264-380 | あり |
| QL2 | `check_external_urls` | L421-450 | あり |
| QC1/QC2/QC3 (xlsx) | `verify_file` | L516-606 | あり |
| QL1 | `check_source_links` | L785-920 | あり |
| - | `check_hints_file_consistency` | L690-745 | あり (docs MD の `## title` を parse) |
| - | `check_docs_coverage` | L622-641 | なし |
| - | `_parse_docs_md_hints` | L650-687 | あり (docs MD の `##` 見出しを section 識別子として使う) |
| - | `_json_text` | L762-768 | あり |

### 5.2 run.py の verify パイプライン配線

**ファイル**: `tools/rbkc/scripts/run.py:416-505`

- L444-488 per-file ループ:
  - `verify_file` (xlsx QC1/2/3)
  - `check_source_links` (QL1)
  - `check_json_docs_md_consistency` (QO5)
- L491-503 global checks:
  - `check_docs_coverage`
  - `check_hints_file_consistency`

**重要な呼び出し漏れ**: `check_format_purity` (QC5), `check_hints_completeness` (QC6), `check_content_completeness` (QC1-4), `check_external_urls` (QL2) は定義されているが **run.py から呼び出されていない** — **Phase 21-G で対応予定**。

### 5.3 設計書

`tools/rbkc/docs/rbkc-verify-quality-design.md` (20 KB) — 品質ゲートの設計書。スキーマ変更時に整合性を取る必要あり。

---

## 6. index.py / index.toon

**ファイル**: `tools/rbkc/scripts/create/index.py`

- `_collect_hints`: sections を走査、hints を集約
- `title = data.get("title", ...)` — トップレベル title のみ使用

**section 依存度**: hints 集約のためにのみ sections を走査。**section.title には依存せず hints 配列のみ見るため、スキーマ変更時の影響は小**。トップレベル content に紐付く hints をどこから引くかの調整が必要になる可能性あり。

---

## 7. nabledge-test 側のセクション検索

### 7.1 scenarios.json

`.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json`: expectations はキーワード・コンポーネント単位。**知識 JSON の section.title には依存しない**。

### 7.2 SKILL.md の section 検索

`.claude/skills/nabledge-test/SKILL.md` の `## Overview` / `### Component Summary` 等の検索指示は、**sub-agent が出力する code-analysis レポートの MD 構造** を指しており、RBKC 知識 JSON のセクション構造ではない。

### 7.3 報告生成スクリプト

`generate_reports.py` / `generate_comparison_report.py`: `## ` 文字列は全てレポート作成側の見出しで、RBKC JSON parse には無関係。

### 7.4 nabledge-N skills

`.claude/skills/nabledge-6/SKILL.md` の Knowledge Structure は `index.toon` ベースで、JSON 内部の section 構造への言及なし。

**結論**: nabledge-test 側にスキーマ変更の直接影響はない。scoring は keyword detection ベース。

---

## 変更が必要な箇所サマリ

### 削除/修正（converter）

| ファイル | 行 | 内容 | 対応 |
|---------|-----|------|------|
| `tools/rbkc/scripts/create/converters/rst.py` | L54 | `_PREAMBLE_TITLE = "概要"` 定数 | 削除 |
| 同上 | L119-235 `_split_sections` | preamble を `("概要", ...)` セクションとして返すロジック | 戻り値を `(title, preamble_lines, sections)` の 3-tuple に変更 |
| 同上 | L1213-1216 `convert` | sections リスト構築 | preamble を content フィールドに回す構造化 |
| 同上 | L23-33 dataclass | `RSTResult` に `content` 追加 | |
| `tools/rbkc/scripts/create/converters/md.py` | L60-98, L124-131 | preamble を `title=""` のセクションとして扱う | content フィールドに移す |
| `tools/rbkc/scripts/create/converters/xlsx_releasenote.py` | L64 | `sections = [Section(title="", ...)]` 単一セクション | `content` に移し、sections=[] とする選択肢 |
| `tools/rbkc/scripts/create/converters/xlsx_security.py` | L40 | 同上 | 同上 |

### スキーマを使う側

| ファイル | 行 | 対応 |
|---------|-----|------|
| `tools/rbkc/scripts/run.py` | L212-235 | トップレベル `content` を書く |
| 同上 | L74-113 `load_existing_hints` | content 層の hints lookup 設計 |
| `tools/rbkc/scripts/create/docs.py` | L83-107 | トップレベル content を最初に出し、sections が無ければ `##` を出さない |
| `tools/rbkc/scripts/create/hints.py` | — | 新スキーマで content 層は hints 対象外 or top-level hints を導入するか決定が必要 |
| `tools/rbkc/hints/v6.json` | 多数 | 全面再生成 |
| `tools/rbkc/scripts/verify/verify.py` | 多数 | トップレベル content も走査対象に追加 |
| `tools/rbkc/scripts/create/index.py` | L46-59 | トップレベル hints 導入時は更新 |
| `tools/rbkc/docs/rbkc-verify-quality-design.md` | — | スキーマ記述更新 |

### 影響が無い/小さい場所

- `labels.py`, `classify.py`, `scan.py`, `differ.py`, `resolver.py`: スキーマ非依存
- `.claude/skills/nabledge-test/`: scoring は keyword detection、スキーマ非依存
- `.claude/skills/nabledge-N/SKILL.md`: index.toon 経由、JSON 内部構造非依存

### テストへの影響

- `tools/rbkc/tests/ut/test_verify.py`: `title: "概要"` を使うフィクスチャが多数 — 書き換え
- `tools/rbkc/tests/ut/test_run.py`: fixture 変更
- `tools/rbkc/tests/ut/test_hints.py`: KC cache fixture — スキーマ変更と独立に維持可能

### 既存 RBKC 出力 JSON の再生成

全 `.claude/skills/nabledge-*/knowledge/**/*.json` の再生成が必要。
