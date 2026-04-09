# Rule-based Knowledge Creator (RBKC)

Deterministic, rule-based converter that transforms Nablarch official documentation (RST/MD/Excel) into structured knowledge files. No AI involved — all transformations are mechanical and reproducible.

## Motivation

The existing Knowledge Creator (KC) uses AI to generate and improve knowledge files. While effective, this approach has scaling problems:

1. **Full human review required** — AI-generated content needs human verification for every file
2. **Cost compounds across versions** — 5 Nablarch versions x 400+ files = impractical review volume
3. **Human review fatigue** — Reviewers may miss errors in large review batches
4. **Non-deterministic** — Same input can produce different output across runs

RBKC solves this by using deterministic rules: same input always produces same output. Once the conversion rules are verified, all files converted by those rules are trustworthy without per-file review.

## Usage

### Setup

```bash
# From repository root — clones .lw/ and installs Python dependencies
./setup.sh
```

### Commands

```bash
# 全件作成（初回実行）
./tools/rbkc/rbkc.sh create 6

# 差分更新（ソース変更検知 → 変更分のみ再変換）
./tools/rbkc/rbkc.sh update 6

# 削除されたソースに対応するファイルを削除
./tools/rbkc/rbkc.sh delete 6

# 特定ファイルのみ処理
./tools/rbkc/rbkc.sh create 6 --target handlers-data_read_handler

# ドライラン（変更内容を表示するのみ）
./tools/rbkc/rbkc.sh update 6 --dry-run
```

| Command | Behavior |
|---------|----------|
| `create` | 全ソースファイルを変換、index生成 |
| `update` | 前回 create/update 時のスナップショットと比較し、変更分のみ再変換 |
| `delete` | 前回スナップショットに存在し、現在のソースに存在しないファイルを削除 |

### Output

| Output | Path | Purpose |
|--------|------|---------|
| Knowledge JSON | `.claude/skills/nabledge-6/knowledge/{type}/{category}/{id}.json` | AI agent が検索・取得に使う |
| Browsable MD | `.claude/skills/nabledge-6/docs/{type}/{category}/{id}.md` | 人間がブラウザで確認 |
| Index | `.claude/skills/nabledge-6/knowledge/index.toon` | 知識ファイル一覧 |

## Development

### Requirements

#### Functional Requirements

| ID | Requirement | Notes |
|----|-------------|-------|
| F1 | Convert RST files to knowledge JSON + browsable MD | Primary format (413 files in v6) |
| F2 | Convert MD files to knowledge JSON + browsable MD | 3 files in v6 |
| F3 | Convert Excel files to knowledge JSON + browsable MD | 5 files in v6 (record-level sections) |
| F4 | Three operations: create, update, delete | Mechanical only, no AI loop |
| F5 | Output JSON compatible with nabledge skill | Same schema as existing knowledge files |
| F6 | Generate index.toon | Knowledge file index for skill |
| F7 | Resolve RST cross-references | :ref:, :doc:, :java:extdoc:, :download: |
| F8 | Copy referenced assets (images, downloads) | Preserve relative paths |
| F9 | Detect no-knowledge-content files | toctree-only, navigation-only |
| F10 | Import hints from existing KC knowledge files | Reuse AI-generated hints via rule-based mapping |
| F11 | Start with v6 | Extensible to v5 and v1.x later |

#### Non-Functional Requirements

| ID | Requirement | Notes |
|----|-------------|-------|
| N1 | Deterministic | Same input = same output, always |
| N2 | Fast | All v6 files (421) in seconds, not minutes |
| N3 | No external API calls | No AI, no network |
| N4 | Zero dependency on KC | Own mappings, own code; reuse ideas not imports |
| N5 | Incremental updates | Re-convert only changed files |

### Testing

#### Test Policy

**最も避けるべきこと: 実際に動かしたらエラーになること。**

テストは「動かしたら正しく動く」保証を提供する。合格したテストスイートがそのまま本番品質を意味するレベルを目指す。

**E2E テスト:**

- **目的**: ユーザーと同じ条件で全変換パイプラインを検証する
- **入力**: `.lw/nab-official/v6/` の実際の公式ドキュメント（テスト用フィクスチャではなく本物）
- **出力**: テスト用一時ディレクトリに生成（本番出力パスには書き込まない）
- **アサーション**: 出力の全フィールドを検証する。構造だけでなく内容も含む
  - JSON structure (required fields, types)
  - title, id, official_doc_urls
  - Section count and section titles
  - Section content (converted markdown)
  - Hints (extracted identifiers)
  - no_knowledge_content detection
  - Cross-reference resolution
  - Asset copying
  - index.toon
- **カバレッジ**: ユーザーが使う全機能・全コマンドをテストする
  - create: RST / MD / Excel それぞれの変換
  - update: 変更検知と差分変換
  - delete: 削除されたソースの対応ファイル削除
- **原則**: E2E テストで全ロジックパスをカバーする。E2E で検証できるものはE2Eで検証する

**Unit テスト:**

- **目的**: E2E では検証しにくい複雑な内部ロジックを個別にテストする
- **対象**: E2E で十分にカバーできない境界値、エッジケース、エラーケース
  - RST heading detection の特殊パターン（overline, 3+ levels）
  - list-table の複雑なケース（空セル、複数行セル、ネスト）
  - hints extraction の境界値（短い識別子、誤検出防止）
  - no-knowledge-content の判定ロジック
- **原則**: E2E でカバー済みのハッピーパスは unit test で重複させない

**テスト実行の前提:**

- `.lw/nab-official/v6/` が setup.sh でセットアップ済みであること
- `.lw` が存在しない場合、E2E テストは**エラーで失敗**する（skip ではない）
- skip すると「テストが通った」と勘違いするため、明示的に失敗させる

#### How to Run Tests

```bash
# Prerequisites: setup.sh must be run first
./setup.sh

# Run all tests
cd tools/rbkc
pytest

# Run E2E tests only
pytest tests/e2e/

# Run unit tests only
pytest tests/ut/

# Run with verbose output
pytest -v
```

### Design

#### Architecture Overview

```
Source                          RBKC                          Output
──────                          ────                          ──────

.lw/nab-official/v6/            tools/rbkc/
  nablarch-document/ja/
    *.rst  ───────────────┐     rbkc.sh (CLI)
  nablarch-system-dev-     │       │
  guide/                   ├───▶ converters/               .claude/skills/nabledge-6/
    *.md   ───────────────┤       rst.py                     knowledge/
    *.xlsx ───────────────┘       md.py                        {type}/{category}/
                                  xlsx_releasenote.py            {id}.json    (AI-readable)
Existing KC knowledge  ───────▶   xlsx_security.py           docs/
  (hints import)               hints.py                       {type}/{category}/
                               resolver.py                       {id}.md     (Human-readable)
                               index.py                      knowledge/
                                                               index.toon
```

#### Source Discovery

走査対象ディレクトリと対象ファイル:

| Format | Scan Path | Notes |
|--------|-----------|-------|
| RST | `.lw/nab-official/v6/nablarch-document/ja/` 配下を再帰走査 | `_` 始まりディレクトリは除外 |
| MD | `.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns/` | 対象ファイルは mappings/v6.json の `md` セクションで列挙 |
| Excel | `.lw/nab-official/v6/nablarch-document/ja/releases/` + `.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/` | 対象ファイルは mappings/v6.json の `xlsx`/`xlsx_patterns` で定義 |

#### ID Generation

ファイル ID は `{category}-{filename_without_ext}` 形式。

| ケース | ルール | 例 |
|--------|--------|-----|
| 通常 | `{category}-{basename}` | `handlers-data_read_handler` |
| index.rst | パターン残余パスで識別 | `handlers/index.rst` → `handlers-handlers` |
| index.rst (トップ) | `{category}-top` | ルート `index.rst` → `about-nablarch-top` |
| ID 重複 | 祖先ディレクトリ名を付加して解決 | `libraries-index-validation` |

#### official_doc_urls Generation

ソースパスから公式ドキュメント URL を機械的に生成:

```
base_url = "https://nablarch.github.io/docs/LATEST/doc/"
source:  .lw/nab-official/v6/nablarch-document/ja/application_framework/.../data_read_handler.rst
url:     {base_url}application_framework/.../data_read_handler.html
```

- RST: `nablarch-document/ja/` 以降のパスで `.rst` → `.html` に置換
- MD/Excel: 対応する公式URLがない場合は空配列 `[]`

#### Output JSON Schema

```json
{
  "id": "handlers-data_read_handler",
  "title": "データリードハンドラ",
  "official_doc_urls": ["https://nablarch.github.io/docs/LATEST/doc/..."],
  "index": [
    {
      "id": "s1",
      "title": "機能概要",
      "hints": ["DataReadHandler", "データリード", "ページング"]
    }
  ],
  "sections": {
    "s1": "機能概要に関するMarkdownコンテンツ..."
  }
}
```

#### Browsable MD Generation

知識 JSON から human-readable な Markdown を生成:

```markdown
# {title}

**公式ドキュメント**: [{title}]({official_doc_urls[0]})

## {index[0].title}

{sections.s1}

<details><summary>keywords</summary>
{index[0].hints をカンマ区切り}
</details>

## {index[1].title}
...
```

#### index.toon Format

TOON（Tab-Outline Object Notation）形式の知識ファイル一覧:

```
# Nabledge-6 Knowledge Index

files[295,]{title,type,category,processing_patterns,path}:
  データリードハンドラ, component, handlers, , component/handlers/handlers-data_read_handler.json
  Bean Validation, component, libraries, , component/libraries/libraries-bean_validation.json
  ...
```

- `no_knowledge_content: true` のファイルは除外
- `title` は知識ファイルの `title` フィールドから取得

#### Conversion Rules

##### RST (413 files in v6)

主要ソース形式。Sphinx拡張を多用。

**ファイル構造:**
- 1ソースファイル = 1知識ファイル（分割なし）
- 見出しレベルは**出現順**で決定（RST仕様: 記号と階層の対応はファイルごとに異なる）
- h1 → `title` フィールド
- h2, h3 → セクション境界（`sections` の各エントリ）
- h4+ → 親セクション内に `####` として保持
- h1〜最初のh2間のコンテンツ（プリアンブル） → 独立セクション「概要」として分離
- h2 がないファイル → 全コンテンツを1セクション

根拠: [セクション粒度調査](docs/evaluation/section-granularity.md) — 全334ファイル分析の結果、h2のみでは200行超のセクションが50件発生するが、h2+h3で16件に減少（68%改善）。検索結果の差異も解消される。

**構造変換ルール:**

| RST | Markdown |
|-----|----------|
| `.. code-block:: java` | ` ```java ... ``` ` |
| `.. list-table::` | `\| col \| col \|` (Markdown table) |
| admonition (`.. note::`, `.. warning::`, `.. important::`, `.. tip::`, `.. caution::`, `.. attention::`, `.. danger::`, `.. error::`, `.. hint::`, `.. seealso::`) | `> **{Type}:** ...` |
| `.. image:: path` | `![](assets/{id}/filename)` |
| `.. figure:: path` | `![caption](assets/{id}/filename)` |
| `.. deprecated::` | `> **Deprecated:** ...` |
| `.. versionadded::` | `> **Version Added:** ...` |
| `.. versionchanged::` | `> **Version Changed:** ...` |
| `.. toctree::` | no-knowledge-content 検知; それ以外は除外 |
| `.. contents::` | 除外（自動生成目次） |
| `*emphasis*` | `*emphasis*` (同じ) |
| `**strong**` | `**strong**` (同じ) |
| `` ``code`` `` | `` `code` `` |
| RST grid/simple tables | Markdown tables |

**未知ディレクティブの方針:**

実ファイルに未対応のRSTディレクティブが出現した場合、**エラーで停止**する（サイレントに無視しない）。これにより：
- 変換漏れを確実に検知できる
- 新しいディレクティブの追加が必要なことが即座に分かる
- ルールベースの信頼性を維持できる

**クロスリファレンス解決:**

| RST | 解決後 |
|-----|--------|
| `:ref:\`label\`` | `[text](resolved-path.json#section)` |
| `:doc:\`path\`` | `[text](resolved-path.json)` |
| `:java:extdoc:\`class\`` | `` `ClassName` `` |
| `:download:\`text <path>\`` | `[text](assets/{id}/filename)` |
| `.. _label:` | リンク解決マップに登録 |

**No-Knowledge-Content 検知:**

以下のみで構成されるファイルは `no_knowledge_content: true`:
- `.. toctree::` ディレクティブ
- RST ラベル (`.. _label:`)
- 本文のない見出し

##### MD (3 files in v6)

ソースが既にMarkdown。最小限の変換。

- `#` → `title` フィールド
- `##` → セクション境界
- コンテンツはほぼそのまま保持
- ヒント抽出はRSTと同じルール

##### Excel (5 files in v6)

レコード単位でセクション化。検索時に必要なレコードだけを取得できる。

**Release Notes** (`nablarch6*-releasenote.xlsx`, 4 files):

| 項目 | ルール |
|------|--------|
| セクション | 各レコード（行）= 1セクション |
| タイトル | ファイル名からバージョン識別（`nablarch6u2-releasenote` → "Nablarch 6u2 リリースノート"） |
| セクションタイトル | モジュール名またはキーカラムの値 |
| コンテンツ | 各レコードのカラムをkey-value形式で記述 |
| ヒント | モジュール名、バージョン番号、変更種別 |

**Security Check Table** (`Nablarch機能のセキュリティ対応表.xlsx`, 1 file):

| 項目 | ルール |
|------|--------|
| セクション | 各レコード（行）= 1セクション（機能単位） |
| タイトル | "Nablarch機能のセキュリティ対応表" |
| セクションタイトル | 機能名（行の先頭カラム） |
| コンテンツ | その機能のセキュリティ対策をkey-value形式で記述 |
| ヒント | 機能名、セキュリティ対策名 |

#### Hints Strategy

2段階のルールベース戦略。AIは使わない。

**Stage 1: 機械的抽出（英数字パターン）**

ソースコンテンツから正規表現で抽出:
- Java クラス/インタフェース名（PascalCase: `DataReadHandler`）
- パッケージ名（`nablarch.core.validation.ee`）
- アノテーション名（`@Required`, `@Domain`）
- 設定プロパティ名（XML要素、属性名）
- セクション見出しテキスト
- 太字テキスト（`**keyword**`）

**Stage 2: 既存KC知識ファイルからのヒント移植**

既存のAI生成知識ファイル（`.claude/skills/nabledge-6/knowledge/`）からセマンティックヒントを抽出し、対応するセクションにマッピング:

1. 既存知識ファイルの `index[].hints` を読み込み
2. ファイルID + セクションタイトルで対応関係を特定
3. Stage 1 で抽出済みのヒントに、セマンティックヒント（日本語キーワード等）をマージ
4. 重複排除して出力

これにより、KCで既に投資したAIヒントをルールベースで再利用できる。

#### Incremental Update (differ)

`.lw` は gitignored のため `git diff` では変更検知できない。代わりにスナップショット方式を使用:

1. **create/update 実行時**: 全ソースファイルのパスとハッシュ（SHA-256）をスナップショットとして保存
   - 保存先: `tools/rbkc/.state/v6/snapshot.json`
2. **update 実行時**: 現在のソースファイルとスナップショットを比較
   - ハッシュ変更 → 再変換
   - 新規ファイル → 変換
   - 削除ファイル → 対応する knowledge/docs を削除候補としてリストアップ
3. **delete 実行時**: スナップショットに存在し、現在のソースに存在しないファイルの knowledge/docs を削除

#### Error Handling

ルールベースの原則: **未知の入力はエラーで停止**。サイレントに無視しない。

| エラー | 振る舞い |
|--------|----------|
| 未知のRSTディレクティブ | エラーで停止。変換ルール追加を促す |
| RST パースエラー | エラーで停止。該当ファイルとエラー箇所を表示 |
| Excel 読み取りエラー | エラーで停止 |
| マッピング未定義のファイル | エラーで停止。mappings/v6.json への追加を促す |
| .lw 未セットアップ | エラーで停止。setup.sh 実行を促す |

#### Directory Structure

```
tools/rbkc/
├── README.md                # This file
├── rbkc.sh                  # CLI entry point (shell)
├── scripts/
│   ├── run.py               # Main orchestrator
│   ├── scan.py              # Source file discovery (.lw scan)
│   ├── classify.py          # Type/Category classification
│   ├── convert.py           # Conversion dispatcher
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── rst.py           # RST → Markdown converter
│   │   ├── md.py            # MD → structured MD
│   │   ├── xlsx_releasenote.py   # Release note parser
│   │   └── xlsx_security.py      # Security table parser
│   ├── hints.py             # Hints extraction + KC hints import
│   ├── resolver.py          # Cross-reference resolution
│   ├── index.py             # index.toon generation
│   ├── docs.py              # Browsable MD generation
│   └── differ.py            # Snapshot-based change detection
├── mappings/
│   └── v6.json              # Type/Category classification rules (own copy)
├── .state/                  # Snapshot for incremental updates (gitignored)
│   └── v6/
│       └── snapshot.json
└── tests/
    ├── e2e/
    │   ├── test_create.py   # create command E2E (RST/MD/Excel)
    │   ├── test_update.py   # update command E2E
    │   └── test_delete.py   # delete command E2E
    └── ut/
        ├── test_rst_parser.py    # RST parsing edge cases
        ├── test_hints.py         # Hints extraction edge cases
        └── test_resolver.py      # Link resolution edge cases
```

#### Dependencies

- Python 3.10+
- `openpyxl` — Excel reading (setup.sh でインストール済み)

No AI/API dependencies.

#### Implementation Plan

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認

| Phase | Scope | Files |
|-------|-------|-------|
| 1 | 既存KC知識ファイルからのヒント抽出・保存 | hints.py |
| 2 | RST converter (section detection, structural conversion) | rst.py, convert.py |
| 3 | Hints extraction (Stage 1: mechanical) + Stage 2 マージ | hints.py |
| 4 | Cross-reference resolution + asset copying | resolver.py |
| 5 | MD converter | md.py |
| 6 | Excel converters (record-level sections) | xlsx_releasenote.py, xlsx_security.py |
| 7 | Index + browsable docs generation | index.py, docs.py |
| 8 | CLI + create/update/delete operations | rbkc.sh, run.py, scan.py, classify.py, differ.py |
