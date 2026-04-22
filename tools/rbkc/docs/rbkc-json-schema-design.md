# RBKC JSON スキーマ設計

## 1. 目的

RBKC（RST/Markdown/Excel → JSON 知識ファイル変換）の出力 JSON スキーマを定義する。

### 設計原則

- **ソース忠実性**: ソースに実在しない文字列を JSON に混入させない
- **決定論性**: 同じソースからは常に同じ JSON が出力される
- **KC 形式互換**: 既存の v5 KC 形式（`tools/knowledge-creator/`）と互換を保ち、nabledge スキル側の既存 jq クエリが同じ契約で動作する

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

### 3-4. xlsx converter（本 Phase は最小対応）

- 現行の「全シート連結・単一セクション」方式を維持
- 全内容を top-level `content` に投入
- `title: ""`（xlsx ソースには h1 相当がなく、ファイル名由来の文字列はソースに実在しないため設定しない）
- `sections: []`
- **シート単位ファイル分割 + 行単位 section 化は Phase 21-C の責務**（title=シート名、file_id=base + sheet 識別子、検索インデックス影響なども 21-C で設計）

---

## 4. docs MD 生成

### 4-1. テンプレート

```markdown
# {title}

{content}

## {sections[0].title}

{sections[0].content}
```

### 4-2. ルール

- `# {title}` 直下に top-level `content` を出力（`content` が空ならスキップ）
- `sections == []` のとき `##` 見出しを一切出力しない（現行 `## \n` 空見出し問題の解消）
- `no_knowledge_content == true` のときは `# {title}` のみ
- hints は RBKC のスコープ外のため `<details><summary>keywords</summary>` ブロックは出力しない

---

## 5. nabledge スキル側への影響

既存 KC 形式との互換を保つため、**スキル側スクリプト・workflows に変更は最小限**:

- `.sections[]` array 前提の jq クエリ: 現行 v5/v1.x KC 形式と同じ → そのまま動作
- `.index[]` 経由の lookup: `__file__` エントリと sections の title がそのまま引ける（hints フィールドは無し）
- **`read-sections.sh` の修正が必要**: 現行 `jq '.sections[$sec]'` は array に object 構文でアクセスしており現状バグ。本 PR で 5 版（v6/v5/v1.4/v1.3/v1.2）同時に `jq '.sections[] | select(.id==$sec)'` 形式に修正する（`.claude/rules/nabledge-skill.md` cross-version ルール）

---

## 6. verify への影響

本スキーマ変更は verify の検証範囲・アルゴリズムに影響する。`.claude/rules/rbkc.md` の「Rules for changing verify」に従い、verify の変更は**別途ユーザー承認プロセス**で確定する。本設計書では verify 仕様を定めない。

影響が想定される観点（承認プロセスで具体化）:
- QC1–QC5 の検証対象に top-level `content` が追加される
- `index` / `official_doc_urls` フィールドの存在チェック追加

---

## 7. ロールアウト

`.claude/rules/nabledge-skill.md` の cross-version 原則に従い、全 5 版（v6, v5, v1.4, v1.3, v1.2）を同一 PR でロールアウト:

1. RBKC 側コード改修（TDD）
2. `read-sections.sh` 5 版同時修正
3. verify 側改修（別途承認後）
4. 全版で `rbkc create` + `rbkc verify` FAIL 0 件確認
5. 全版で `nabledge-test --baseline` 実行、劣化なし確認
