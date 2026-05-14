# RBKC JSON スキーマ設計

## 0. この文書を読む前に

### 全体像

RBKC は Nablarch 公式ドキュメント（RST / Markdown / Excel）を **nabledge スキルが検索・回答に使える JSON 形式**に変換するパイプラインである。

```
[ソース: RST / MD / Excel]
        ↓ RBKC create
[知識ファイル (JSON)]  ← AI がキーワード検索で引く索引
[閲覧用 MD (docs MD)]  ← GitHub 上でそのまま読めるレンダリング
[検索インデックス (index.toon)] ← 検索対象ファイルの一覧
```

- **知識ファイル (JSON)**: nabledge スキルが `jq` クエリ等で読み込む。`id` / `title` / `content` / `sections[]` を持つ構造体。本書で定義するスキーマに従う。
- **閲覧用 MD (docs MD)**: JSON と 1:1 対応する Markdown ファイル。GitHub 上で人間が直接読める。内容は JSON の人間可読レンダリングであり、JSON と完全一致が要件（verify QO2 で検証）。
- **検索インデックス (index.toon)**: 全 JSON ファイルの相対パスを列挙したテキストファイル。nabledge スキルはここを起点に知識ファイルを探す。verify QO4 で網羅性を検証。

### 用語

- **KC 形式**: `tools/knowledge-creator/` が v5 時代に定義した knowledge-creator 形式。本書では既存の nabledge スキル側 `jq` クエリとの互換を保つために参照する。
- **nabledge スキル**: Claude Code に読み込まれる AI アシスタント（`.claude/skills/nabledge-6/` 等）。知識ファイルを参照して Nablarch に関する質問に答える。
- **jq クエリ**: JSON を操作するコマンドラインツール `jq` のクエリ。nabledge スキル側のスクリプトが知識ファイルから情報を取り出すために使う。
- **h1 / h2 / h3**: Markdown の見出し記法（`#` / `##` / `###`）に対応する見出し深度。RST では `=` / `-` 等のアンダーライン記法で相当する。本書では RST / MD を問わず h1〜hN の記法で統一する。

---

## 1. 目的

RBKC（RST/Markdown/Excel → JSON 知識ファイル変換）の出力 JSON スキーマを定義する。

### 設計原則

- **ソース忠実性**: ソースに実在しない文字列を JSON に混入させない
- **決定論性**: 同じソースからは常に同じ JSON が出力される
- **KC 形式互換**: 既存の v5 KC 形式（`tools/knowledge-creator/`）と互換を保ち、nabledge スキル側の既存 jq クエリが同じ契約で動作する（用語は §0 参照）

---

## 2. JSON スキーマ

### 2-1. 構造

```json
{
  "id": "file-id",
  "title": "h1 タイトル",
  "content": "h1 直下〜最初の h2 直前までの本文（Markdown）",
  "sections": [
    {
      "id": "s1",
      "title": "h2 タイトル",
      "level": 2,
      "content": "セクション本文（Markdown）"
    }
  ],
  "index": [
    {"id": "__file__", "title": "h1 タイトル"},
    {"id": "s1", "title": "h2 タイトル"}
  ],
  "no_knowledge_content": false,
  "official_doc_urls": ["https://..."]
}
```

> **hints フィールドについて**: RBKC は content（タイトル + 本文）のみを生成する。`hints`（キーワード索引）は RBKC のスコープ外で、別 Issue の AI 駆動フローが扱う。したがって本スキーマには `hints` フィールドを含めない。

### 2-2. フィールド定義

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | string | ファイル識別子 |
| `title` | string | ソースの h1 タイトル |
| `content` | string | h1 直下〜最初の h2 直前の本文（Markdown）。preamble が空なら空文字 |
| `sections` | array | h2 セクション（KC の文量ルールで h3 分割されたものも含む。詳細は §3-1） |
| `sections[].id` | string | `s1`, `s2`, ... の連番（`sections[]` 内の位置ポインタ） |
| `sections[].title` | string | セクションのタイトル（ソース由来の h2/h3 そのもの） |
| `sections[].level` | int | セクションの heading 深度。RST h2 / MD `##` = 2、h3 / `###` = 3、h4 / `####` = 4。docs MD 出力時の `#` 数を決定する (Phase 22-B-16 追加)。h3 分割後の section も「元の RST 上の heading 深度」を保持する必要があるため、`sections[]` の配列位置から再計算することはできない（h3 section が 1 番目に来ることもある）。このため level を明示フィールドとして持つ。 |
| `sections[].content` | string | セクション本文（Markdown）。h4 以降は `####`/`#####`/`######` と深度を保持して埋め込む |
| `index` | array | 検索エントリ一覧。`{id:"__file__", title}` を先頭に、続いて `sections[]` と 1:1 対応の `{id, title}` を並べる。`sections[]` から決定論的に生成（独立ソースではない） |
| `no_knowledge_content` | bool | `true` のとき `content == ""` かつ `sections == []`（toctree 専用ページ等） |
| `official_doc_urls` | array | 公式ドキュメント URL |

### 2-3. 不変条件

- `index[]` は `sections[]` から機械的に生成される。先頭に `{id:"__file__", title:top-level title}`、続いて `sections[]` と順序・要素数・内容が 1:1 対応するエントリが並ぶ
- `sections[].id` は `sections[]` 配列内の位置を指すポインタ（`s1` = 先頭）。ソース変更で h2 が増減すると id は再採番される
- h2/h3 が無いファイルでも `sections[]` に疑似エントリを作らない（KC の `s1=h1_title` workaround は踏襲しない。ソース忠実の原則）

### 2-4. 現行 RBKC v6 出力との差分

現行 RBKC v6 出力は以下の点で既存 v5 KC 形式から逸脱している:

- **`content` フィールドなし** → 新設
- **`_PREAMBLE_TITLE = "概要"` 固定値で preamble を擬似 section 化** → 廃止、`content` に移す
- **`index` フィールドなし** → KC 仕様通りに追加（ただし `__file__` エントリは RBKC 独自）
- **`official_doc_urls` フィールドなし** → KC 仕様通りに追加

### 2-5. KC 形式からの意図的な逸脱

KC (`tools/knowledge-creator/`) は h2/h3 が無いファイルに対して `sections: {"s1": {title: h1_title, ...}}` の疑似 section を生成する。RBKC はこれを踏襲せず、`content` に格納する:

- **理由**: ソースに実在しない `s{n}` section を捏造しない（ソース忠実原則 §1）
- **影響**: nabledge スキル側の jq クエリは `index[]` を主入口とすれば両形式を差分なく扱える（`__file__` id も section id も同じ index エントリから引ける）

KC は `hints` フィールドを持つが、RBKC は hints をスコープ外とするため出力しない（AI 駆動 hints は別 Issue 管轄）。

---

## 3. converter 挙動

### 3-1. section 分割ルール

`tools/knowledge-creator/prompts/generate.md` の分割方針を踏襲する:

- **分割単位は h2**
- h2 の plain text が 2000 文字未満 → h3 は親 h2 に merge（独立 section にしない）
- h2 の plain text が 2000 文字以上かつ h3 が存在 → h3 ごとに section 分割
- h2 の plain text が 2000 文字以上で h3 なし → 1 section のまま

> **2000 文字の根拠**: `tools/knowledge-creator/prompts/generate.md` の分割方針に由来する。AI の検索・回答精度を高めるために、1 section が長すぎる場合は h3 単位で分割する閾値として定められた値。RBKC はこの既存の KC 形式仕様をそのまま踏襲する。
- h4 以降 → 所属 section の `content` 内に `####`/`#####`/`######` 見出しとして深度を保持して埋め込み（`#`・`##` は section content 内に出力しない）

### 3-2. 共通ルール

- h1 → top-level `title`
- h1 直下〜最初の h2 直前の本文 → top-level `content`
- h2/h3 → `sections[]`（§3-1 の分割ルール適用後）
- h2/h3 が 1 つも無いファイル → `sections: []`（`content` にファイル全文が入る）
- h1 すら無いファイル → `title: ""`, `content: ""`, `sections: []`, `no_knowledge_content: true`

### 3-3. RST / MD converter

- `_PREAMBLE_TITLE = "概要"` 固定値を廃止
- preamble は top-level `content` に格納

### 3-4. xlsx converter (Phase 22-B、sheet-level 分割 + P1/P2)

`rbkc-converter-design.md` §8 で詳細定義。本書は JSON スキーマ側の差分のみ記載する。

**P1 (データ表)**:
- `title`: `■…` タイトル行の値 (なければシート名)
- `content`: **preamble** (タイトル行とヘッダ行の間の非空セル群) を行優先・列順に `\n` 区切りで join した文字列 (Phase 22-B-12)
- `sections`: 1 データ行 = 1 section。`section.content` は `{列名}: {値}\n` の縦列挙形式
- `sheet_type: "P1"`
- `columns[]` / `data_rows[][]`: docs MD の table reconstruction 用

**P2 (段落主体)**:
- `title`: `■…` (なければシート名)
- `content`: シート全体のテキスト
- `sections: []`
- `sheet_type: "P2"`

**semantic 不変**: `content` は全 converter (RST/MD/Excel) で「title 直下の free-form preamble text」という同一 semantic を持つ。format 依存の分岐はしない。

---

## 4. docs MD 生成

### 4-1. テンプレート

```markdown
# {title}

{content}

## {sections[0].title}

{sections[0].content}

### {sections[1].title}

{sections[1].content}
```

### 4-2. ルール

- `# {title}` 直下に top-level `content` を出力（`content` が空ならスキップ）
- 各 section の heading は `sections[].level` に従って `##`/`###`/`####` を出力する (Phase 22-B-16 追加)
  - `level: 2` → `##`
  - `level: 3` → `###`
  - `level: 4` → `####`
  - 以降も同じ規則で `#` を level 個出力
- `sections == []` のとき `##` 見出しを一切出力しない（現行 `## \n` 空見出し問題の解消）
- `no_knowledge_content == true` のときは `# {title}` のみ
- hints は RBKC のスコープ外のため `<details><summary>keywords</summary>` ブロックは出力しない
- リンク rewrite: JSON content の `assets/` 先頭パスのみを docs MD の位置からの相対 (`../../knowledge/assets/...`) に rewrite する。MD リンク (`[text](../category/file_id.md)` 形式) は JSON / docs MD 双方で同一文字列を出力するため rewrite しない

---

## 5. nabledge スキル側への影響

既存 KC 形式との互換を保つため、**スキル側スクリプト・workflows に変更は最小限**:

- `.sections[]` array 前提の jq クエリ: 現行 v5/v1.x KC 形式と同じ → そのまま動作
- `.index[]` 経由の lookup: `__file__` エントリと sections の title がそのまま引ける（hints フィールドは無し）
- **`read-sections.sh` の修正が必要**: `read-sections.sh` は nabledge スキル側のスクリプトで、知識 JSON から特定セクションを取り出すシェルスクリプト。現行は `jq '.sections[$sec]'`（`$sec` を integer index として array に直接アクセス）を使っているが、RBKC JSON の `sections[]` は配列なので `jq '.sections[] | select(.id==$sec)'`（id フィールドで検索）形式に直す必要がある。現状のコードは integer index と string key を混同しており、section が正しく取り出せないバグ。本 PR で 5 版（v6/v5/v1.4/v1.3/v1.2）同時に修正する（`.claude/rules/nabledge-skill.md` cross-version ルール）。

---

## 6. verify への影響

本スキーマ変更は verify の検証範囲・アルゴリズムに影響する。`.claude/rules/rbkc.md` の「Rules for changing verify」に従い、verify の変更は**別途ユーザー承認プロセス**で確定する。本設計書では verify 仕様を定めない。

影響が想定される観点（承認プロセスで具体化）:
- QC1–QC5 の検証対象に top-level `content` が追加される
- `index` / `official_doc_urls` フィールドの存在チェック追加
- **`sections[].level` の存在と docs MD heading level 一致検証** (QO1 level、Phase 22-B-16)
- **`:ref:` / `:doc:` / `:numref:` / `:download:` / image / figure のリンク形式検証** (QL1 強化、Phase 22-B-16 — `rbkc-verify-quality-design.md` §3-2 参照)

---

## 7. ロールアウト

`.claude/rules/nabledge-skill.md` の cross-version 原則に従い、全 5 版（v6, v5, v1.4, v1.3, v1.2）を同一 PR でロールアウト:

1. RBKC 側コード改修（TDD）
2. `read-sections.sh` 5 版同時修正
3. verify 側改修（別途承認後）
4. 全版で `rbkc create` + `rbkc verify` FAIL 0 件確認
5. 全版で `nabledge-test --baseline` 実行、劣化なし確認
