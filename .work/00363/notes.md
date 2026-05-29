# Notes

## 2026-05-29

### Issue #363 概要

Nablarch公式ドキュメントは詳細APIをJavadocに委ねているが、nabledge知識ファイルにJavadocが含まれていない。
jarツールを使ってNablarchソースからMarkdownを生成し、RBKCパイプラインに追加する。

### 調査結果: RBKCパイプライン構造

- `rbkc.sh` → `scripts/run.py` の薄いシム。`create|update|delete|verify <version>` をサポート
- ソース: `.lw/nab-official/v{N}/` 配下の RST/MD/xlsx を `scan_sources()` でスキャン
- コンバータ: `converters/rst.py`, `converters/md.py`, `converters/xlsx_*.py`（フォーマット別）
- 出力: `.claude/skills/nabledge-{N}/knowledge/{type}/{category}/{file_id}.json`
- 現在、`:javadoc_url:` ロールはURLを捨てて表示テキストのみ残す（`rst_ast_visitor.py` L781-786）

### 設計方針（暫定）

**絶対制約: 既存の RST/MD/xlsx パイプラインに一切触れない**

新フォーマット `javadoc` として追加のみ。変更対象は以下の追加のみ:
- `converters/javadoc.py` — 新規作成
- `mappings/v*.json` — 新エントリ追加のみ
- `scan_sources()` — 新分岐追加（既存分岐に触れない）
- `_converter_for()` — 新分岐追加（既存分岐に触れない）

→ jar の出力形式確認後（Task 0）に詳細設計を行う

### 未解決事項

- jar ファイルの入手方法（issue に「実装時に提供」と記載）
- 各バージョンで対象クラスの範囲（全 public クラス vs. `:javadoc_url:` 参照のみ）
