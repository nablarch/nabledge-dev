# RBKC JSON スキーマ設計

## 1. 目的

RBKC（RST/Markdown/Excel → JSON 知識ファイル変換）の出力 JSON スキーマを定義する。RBKC の根本目的は**ソースに忠実な決定論的変換**であり、本スキーマはその原則を構造で保証する。

### 設計原則

- **ソース忠実性**: ソースに実在しない文字列・構造を JSON に混入させない
- **決定論性**: 同じソースからは常に同じ JSON が出力される
- **消費側アクセス性**: nabledge スキル（検索・取得スクリプト）が統一的にアクセスできる

---

## 2. JSON スキーマ

### 2-1. トップレベル構造

```json
{
  "id": "file-id",
  "title": "h1 タイトル（ソースに実在する）",
  "content": "h1 直下〜最初の h2 直前までの本文（Markdown）",
  "sections": [
    {
      "id": "s1",
      "title": "h2 または h3 のタイトル（ソースに実在する）",
      "content": "セクション本文（Markdown）",
      "hints": ["keyword1", "keyword2"]
    }
  ],
  "index": [
    {"id": "top", "title": "h1 タイトル", "hints": ["keyword"]},
    {"id": "s1",  "title": "h2 タイトル", "hints": ["keyword"]}
  ],
  "no_knowledge_content": false,
  "official_doc_urls": ["https://..."]
}
```

### 2-2. フィールド定義

| フィールド | 型 | 説明 | 必須 |
| --- | --- | --- | --- |
| `id` | string | ファイル識別子（ハイフン区切り、`_` なし） | ✅ |
| `title` | string | ソースの h1 タイトル | ✅ |
| `content` | string | h1 直下〜最初の h2 直前の本文（Markdown）。preamble が空なら空文字 | ✅ |
| `sections` | array | h2/h3 セクション。**存在しないファイルは `[]`** | ✅ |
| `sections[].id` | string | `s1`, `s2`, ... の連番 | ✅ |
| `sections[].title` | string | ソースの h2 または h3 タイトル | ✅ |
| `sections[].content` | string | セクション本文（Markdown） | ✅ |
| `sections[].hints` | array | セクションのキーワード | ✅（空配列可） |
| `index` | array | トップレベル + 各セクションの `{id, title, hints}` 一覧 | ✅ |
| `no_knowledge_content` | bool | `true` のとき `content`・`sections` はコンテンツを持たない目次/toctree 専用ページ | ✅ |
| `official_doc_urls` | array | 公式ドキュメント URL | ✅（空配列可） |

### 2-3. `index` フィールドの構造

nabledge スキル側が section メタ情報（id/title/hints）を取得する単一の窓口。

- **トップレベル content** は必ず `{"id": "top", "title": <h1 title>, "hints": [...]}` として含まれる（content が空でも hints がある場合があるため常に含む）
- 以降 `sections[]` と 1:1 対応で `{"id": "s1", ...}`, `{"id": "s2", ...}` と続く
- 順序はトップ→`s1`→`s2`→...

### 2-4. section id の付与規則

- h2/h3 実在順に `s1`, `s2`, `s3`, ... を付与
- h1 直下 preamble は `sections` に入らず、`content` トップレベルフィールドに入る（擬似セクションを作らない）
- **固定値セクションタイトル（"概要" 等）を作らない**

---

## 3. converter の挙動

### 3-1. 共通ルール

- h1 → top-level `title`
- h1 直下〜最初の h2 直前の本文 → top-level `content`
- h2/h3 → `sections[].title` / `sections[].content`（ソース出現順）
- h4 以降 → 所属 h2/h3 の `content` に `#` 記号付きで埋め込み（現行仕様踏襲）
- h2/h3 が 1 つも無いファイル → `sections: []`
- h1 すら無い（目次 toctree 専用など） → `title: ""`, `content: ""`, `sections: []`, `no_knowledge_content: true`

### 3-2. RST converter

- underline 文字の出現順で h1/h2/h3 を決定（最初が h1、2・3 番目が h2/h3）
- **廃止**: `_PREAMBLE_TITLE = "概要"` 固定値と、その固定値を用いた preamble 擬似 section 生成
- preamble は top-level `content` に格納

### 3-3. MD converter

- ATX 見出し（`#`）の `level == 1` → `title`、`level >= 2` → sections
- preamble は top-level `content` に格納（現行「`title=""` の擬似 section」を廃止）

### 3-4. xlsx converter（releasenote / security）

- Excel は構造化テキストではなく、全セル値をフラットに取り込む
- 新スキーマでの扱い: **`sections: []`** + 全内容を top-level `content` に投入
- `title` はファイル識別子由来の人間可読タイトル（現行仕様踏襲）
- 行単位 section 化は **Phase 21-C で別途対応**（本設計のスコープ外）

---

## 4. docs MD 生成仕様

### 4-1. テンプレート

```markdown
# {title}

{content}

<details><summary>keywords</summary>

keyword1, keyword2, ...

</details>

## {sections[0].title}

{sections[0].content}

<details><summary>keywords</summary>

...

</details>

## {sections[1].title}

...
```

### 4-2. 生成ルール

- `# {title}` 直下に top-level `content` をそのまま出力
  - `content` が空文字ならスキップ
- top-level hints が存在する場合のみ、`content` 直後に `<details>` ブロックを出力
- sections が空配列のときは `##` 見出しを一切出さない（重要: 現行の `## \n` 空見出し問題の解消）
- sections があればループで `## {title}` + content + hints の `<details>` を出力
- `no_knowledge_content == true` のときは `# {title}` のみで終了

### 4-3. README.md

`tools/rbkc/scripts/create/docs.py` の `_generate_readme` は index.toon 等経由で type/category/title の目次を生成（section 非依存、変更なし）。

---

## 5. hints ファイル仕様

### 5-1. フォーマット（`tools/rbkc/hints/v{version}.json`）

```json
{
  "version": "6",
  "hints": {
    "file-id": {
      "top": ["keyword1", "keyword2"],
      "s1": ["keyword"],
      "s2": ["keyword"]
    }
  }
}
```

### 5-2. key 定義

- トップレベル section 用 hints の key は `"top"`
- 以降 `sections[].id`（`s1`, `s2`, ...）
- **section title を key にしない**（title はソースの自然言語で変動しやすく、RBKC 再生成時に不安定）

### 5-3. 初期生成

`extract_hints.py`（`.pr/00299/extract_hints.py`）は KC キャッシュから初期 hints を生成する one-time スクリプト。section title ベースから section id ベースへのマッピング変更を伴う。詳細は Phase 21-D の実装タスクで確定する。

---

## 6. nabledge スキル側のアクセス API

本スキーマ変更に合わせ、全 5 版（nabledge-6/5/1.4/1.3/1.2）のスキルスクリプトを以下の契約で統一する。

### 6-1. `scripts/read-sections.sh`

- 入力: `$file` (knowledge file), `$section` (id: `top` または `s1`, `s2`, ...)
- 処理:
  - `section == "top"` → `jq -r '.content' $file`
  - それ以外 → `jq -r --arg sec "$section" '.sections[] | select(.id==$sec) | .content' $file`
- `SECTION_NOT_FOUND` を返す条件は現行踏襲

### 6-2. `scripts/full-text-search.sh`

- 検索単位: `[{id:"top", title:.title, content:.content, hints: (.index[] | select(.id=="top") | .hints)}] + .sections`
- 出力フォーマット: `<score>\t<file>|<id>` は現行踏襲

### 6-3. `workflows/_knowledge-search/_section-search.md`

- `jq '.index[]'` で id/title/hints を引く（現行 jq クエリ踏襲）
- `.index[]` は `top` を含むため、トップレベル content も検索候補に上がる

### 6-4. `workflows/_knowledge-search/_section-judgement.md`

- hints-based pre-filter は `.index[]` 経由（現行踏襲）
- Step A の section content 取得は `read-sections.sh` を利用（6-1 のルールで `top` 対応）

---

## 7. verify 仕様の更新（概要）

詳細は `rbkc-verify-quality-design.md` の更新で管理するが、本スキーマ変更に伴う verify 側の対応観点を記す。

- QC1–QC6: 検証テキストの連結範囲に top-level `content` を含める（`_json_text` / `_build_json_text` / `search_units` 構築に追加）
- QO1: `index` フィールドの整合性（`top` + sections[].id との一致）を検証
- QO5: docs MD 本文整合性は「top-level content → sections」の順序で検証
- `check_hints_file_consistency`: key が section title から id (`top`, `s*`) に変わる対応

---

## 8. 影響範囲サマリ

### RBKC 側
- `scripts/create/converters/rst.py` — `_PREAMBLE_TITLE` 削除、`_split_sections` 戻り値変更
- `scripts/create/converters/md.py` — preamble を top-level content に
- `scripts/create/converters/xlsx_releasenote.py` / `xlsx_security.py` — `sections=[]` + top-level content
- `scripts/run.py` — `_convert_and_write` にトップレベル `content` / `index` 書き出し追加
- `scripts/create/docs.py` — 新テンプレートに対応
- `scripts/create/hints.py` — section id ベースの hints 引きに対応
- `scripts/create/index.py` — `index` フィールド生成に top-level を含める
- `scripts/verify/verify.py` — 各チェックで top-level content を走査
- `hints/v6.json` — 全面再生成（section title key → section id key）

### nabledge スキル側（全 5 版同一改修）
- `scripts/read-sections.sh` — `top` 対応、array sections 対応
- `scripts/full-text-search.sh` — top + sections の検索単位化、array 対応
- `workflows/_knowledge-search/_section-search.md` — 変更なし（`.index[]` 経由）
- `workflows/_knowledge-search/_section-judgement.md` — 変更なし（`.index[]` 経由）

### 影響なし
- 全版の `SKILL.md` / `plugin/` / `assets/` / `docs/` の参照
- nabledge-test の scoring（keyword detection ベース）
