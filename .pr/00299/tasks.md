# Tasks: RBKC Implementation

**PR**: (TBD)
**Issue**: #299
**Updated**: 2026-04-14

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認

## Not Started

### Phase 1: KC キャッシュからのヒントマッピング構築

`.cache/{version}/knowledge/` ファイルから RST見出し → hints の辞書を構築する。

**Files**: `scripts/hints.py`

**Steps:**
- [ ] `tools/knowledge-creator/.cache/{version}/knowledge/**/*.json` を全件ロード
- [ ] `{file_id: {section_title: hints[]}}` の辞書を構築して返す関数を実装
- [ ] Unit test: file_id + section_title でlookupすると正しい hints が返る
- [ ] Unit test: 存在しない file_id や title は空リストを返す（エラーなし）

**Key**: `index[].title` にRSTのh2/h3見出しテキストが格納されている → 直接マッチ、マッチ率実質100%

---

### Phase 2: RST converter

RSTをセクション分割し、各要素をMarkdownに変換する。

**Files**: `scripts/converters/rst.py`, `scripts/convert.py`

**Steps:**
- [ ] セクション検出: h1 → title、h2/h3 → セクション境界、overline（上下両記号）対応
- [ ] ディレクティブ変換:
  - `code-block` → ` ```lang ... ``` `
  - `list-table`, `csv-table` → Markdown table（`:class:` は無視）
  - `.. table::` → inner contentをgrid/simple tableとして変換
  - admonitions（note/warning/important/tip/caution/attention/danger/error/hint/seealso） → `> **{Type}:** ...`
  - `.. admonition:: {title}` → `> **{title}:** ...`
  - `image`, `figure` → `![caption](assets/{id}/filename)`
  - `deprecated`, `versionadded`, `versionchanged` → `> **...: ** ...`
  - `toctree` → no-knowledge-content検知、それ以外は除外
  - `contents` → 除外
  - `raw` → 空出力
  - `include` → 空出力
  - `function` → シグネチャをコードブロックとして変換
  - `literalinclude` → code-blockと同様
  - `class` → 空出力
  - `rubric` → 小見出しとして変換
- [ ] simple table（`==== ====`） → Markdown table
- [ ] grid table（`+----+----+`） → HTML `<table>` with rowspan（`docutils.core.publish_doctree`、`entry.get('morerows')`）
- [ ] no-knowledge-content検知（toctreeのみ/ラベルのみ/本文なし見出しのみ）
- [ ] 未知ディレクティブはエラーで停止
- [ ] E2E test: `universal_dao.rst` を変換 → セクション数・タイトル・コンテンツをアサート
- [ ] Unit test: overline検出、grid table rowspan、no-knowledge-contentエッジケース

---

### Phase 3: Hints extraction（Stage 1 + Stage 2マージ）

**Files**: `scripts/hints.py`

**Steps:**
- [ ] Stage 1: PascalCaseクラス名、`@Annotation`、パッケージ名、bold text、セクション見出しを正規表現で抽出
- [ ] Stage 2: Phase 1のキャッシュ辞書からセクション見出しで引いてhints取得
- [ ] Stage 1 + Stage 2をマージして重複排除、ソートして出力
- [ ] Unit test: 抽出パターン別の期待値テスト
- [ ] Unit test: dedup、Stage 2マージの境界値

---

### Phase 4: Cross-reference resolution + asset copying

**Files**: `scripts/resolver.py`

**Steps:**
- [ ] 全RSTファイルから `.. _label:` 定義を収集してラベルマップを構築
- [ ] `:ref:` → Markdownリンク（解決可能な場合）、解決不可（2.8%）→ プレインテキスト出力
- [ ] `:doc:` → Markdownリンク
- [ ] `:java:extdoc:` → `` `ClassName` ``
- [ ] `:download:` → `[text](assets/{id}/filename)` + ファイルコピー
- [ ] 参照画像を `assets/{id}/` にコピー
- [ ] Unit test: 解決成功・解決不可のフォールバック・アセットパス生成

---

### Phase 5: MD converter

**Files**: `scripts/converters/md.py`

**Steps:**
- [ ] `#` → title、`##` → セクション境界
- [ ] 相対パス画像 → アセットコピー
- [ ] Hints抽出はStage 1のみ（MDファイルにはKCキャッシュなし）
- [ ] E2E test: v6の3MDファイルのうち1件を変換してアサート

---

### Phase 6: Excel converters

**Files**: `scripts/converters/xlsx_releasenote.py`, `scripts/converters/xlsx_security.py`

**Steps:**
- [ ] リリースノート: Row 1-5スキップ → カテゴリ行（col A入力 + No.空）をスキップ → データ行を1行1セクションで変換
- [ ] セキュリティ対応表: col Aの脆弱性名でグループ化 → 1グループ1セクション
- [ ] E2E test: nablarch6-releasenote.xlsx → セクション数・フィールド抽出をアサート
- [ ] E2E test: Nablarch機能のセキュリティ対応表.xlsx → グループ化・セクション数をアサート

---

### Phase 7: Index + browsable docs generation

**Files**: `scripts/index.py`, `scripts/docs.py`

**Steps:**
- [ ] `index.toon` 生成: `no_knowledge_content: true` を除外、TOON形式で出力
- [ ] browsable MD生成: `# title`、`## section`、`<details><summary>keywords</summary>` 形式
- [ ] E2E test: index.toon のエントリ数・フォーマット検証

---

### Phase 8: CLI + create/update/delete/verify operations

**Files**: `rbkc.sh`, `scripts/run.py`, `scripts/scan.py`, `scripts/classify.py`, `scripts/differ.py`, `scripts/verify.py`

**Steps:**
- [ ] `rbkc create {version}`: scan → classify → convert → write
- [ ] `rbkc update {version}`: SHA-256スナップショット差分 → 変更分のみ再変換
- [ ] `rbkc delete {version}`: スナップショットにあって現在のソースにないファイルの出力を削除
- [ ] `rbkc verify {version}`: 生成済み知識ファイルJSONとソースファイルのコンテンツを突き合わせ、不一致を検出して報告
  - ソースのテキスト・見出し・コードブロック・テーブルセルがJSONに過不足なく含まれているか検証
  - リンクはURL・表示テキストが等価であることを確認（フォーマットの違いは許容）
  - 不一致があればファイルパスと差分を出力してexit 1
- [ ] スナップショット保存: `.state/{version}/snapshot.json`
- [ ] E2E test: create（全件）、update（1ファイル変更）、delete（1ファイル削除）
- [ ] E2E test: verify（正常系: 一致）、verify（異常系: 不一致検出 → exit 1）

---

### Phase 9: v1.x固有ディレクティブ対応

v6/v5には存在しないがv1.4/v1.3/v1.2で使われるディレクティブの追加。

**Files**: `scripts/converters/rst.py`

**Steps:**
- [ ] `.. admonition:: {title}` → `> **{title}:** ...`（Phase 2でカバー済みか確認）
- [ ] `.. function::` → シグネチャをコードブロックとして変換（Phase 2でカバー済みか確認）
- [ ] `.. literalinclude::` → code-blockと同様（Phase 2でカバー済みか確認）
- [ ] `.. attention::`, `.. hint::`, `.. class::`, `.. rubric::` がPhase 2で動作することを確認
- [ ] E2E test: v1.4 RSTファイルのうち `admonition` と `function` を含む1件を変換してアサート

---

## Done

(none yet)
