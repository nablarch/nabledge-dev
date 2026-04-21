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
      "content": "セクション本文（Markdown）",
      "hints": ["keyword1", "keyword2"]
    }
  ],
  "index": [
    {"id": "s1", "title": "h2 タイトル", "hints": ["keyword1"]}
  ],
  "no_knowledge_content": false,
  "official_doc_urls": ["https://..."]
}
```

### 2-2. フィールド定義

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | string | ファイル識別子 |
| `title` | string | ソースの h1 タイトル |
| `content` | string | **[本 Phase で新設]** h1 直下〜最初の h2 直前の本文（Markdown）。preamble が空なら空文字 |
| `sections` | array | h2 セクション（KC の文量ルールで h3 分割されたものも含む。詳細は §3-1） |
| `sections[].id` | string | `s1`, `s2`, ... の連番 |
| `sections[].title` | string | セクションのタイトル（ソース由来） |
| `sections[].content` | string | セクション本文（Markdown） |
| `sections[].hints` | array | セクションのキーワード |
| `index` | array | `sections[]` と 1:1 対応の `{id, title, hints}` 一覧（hints-based pre-filter 用） |
| `no_knowledge_content` | bool | `true` のとき `content == ""` かつ `sections == []`（toctree 専用ページ等） |
| `official_doc_urls` | array | 公式ドキュメント URL |

### 2-3. 現行 RBKC v6 出力との差分

現行 RBKC v6 出力は以下の点で既存 KC 形式から逸脱している:

- **`content` フィールドなし** → 新設
- **`_PREAMBLE_TITLE = "概要"` 固定値で preamble を擬似 section 化** → 廃止、`content` に移す
- **`index` フィールドなし** → KC 仕様通りに追加
- **`official_doc_urls` フィールドなし** → KC 仕様通りに追加

---

## 3. converter 挙動

### 3-1. section 分割ルール

`tools/knowledge-creator/prompts/generate.md` の分割方針を踏襲する:

- **分割単位は h2**
- h2 の plain text が 2000 文字未満 → h3 は親 h2 に merge（独立 section にしない）
- h2 の plain text が 2000 文字以上かつ h3 が存在 → h3 ごとに section 分割
- h2 の plain text が 2000 文字以上で h3 なし → 1 section のまま
- h4 以降 → 所属 section の `content` 内に `#` 記号付き見出しとして埋め込み

### 3-2. 共通ルール

- h1 → top-level `title`
- h1 直下〜最初の h2 直前の本文 → top-level `content`
- h2/h3 → `sections[]`（§3-1 の分割ルール適用後）
- h2/h3 が 1 つも無いファイル → `sections: []`
- h1 すら無いファイル → `title: ""`, `content: ""`, `sections: []`, `no_knowledge_content: true`

### 3-3. RST / MD converter

- `_PREAMBLE_TITLE = "概要"` 固定値を廃止
- preamble は top-level `content` に格納

### 3-4. xlsx converter

- heading 階層が存在しないため `sections: []` + 全内容を top-level `content` に投入
- `title` はファイル識別子由来の人間可読タイトル（現行踏襲）
- 行単位 section 化は Phase 21-C で別途対応

---

## 4. docs MD 生成

### 4-1. テンプレート

```markdown
# {title}

{content}

## {sections[0].title}

{sections[0].content}

<details><summary>keywords</summary>

keyword1, keyword2, ...

</details>
```

### 4-2. ルール

- `# {title}` 直下に top-level `content` を出力（`content` が空ならスキップ）
- `sections == []` のとき `##` 見出しを一切出力しない（現行 `## \n` 空見出し問題の解消）
- `no_knowledge_content == true` のときは `# {title}` のみ

---

## 5. hints ファイル

### 5-1. フォーマット

```json
{
  "version": "6",
  "hints": {
    "file-id": {
      "s1": ["keyword1", "keyword2"],
      "s2": ["keyword"]
    }
  }
}
```

key は `section.id`（`s1, s2, ...`）。**title ベースではなく id ベース**に変更することで、ソース変更時の title 揺れに影響されない安定したキーとなる。

---

## 6. nabledge スキル側への影響

既存 KC 形式との互換を保つため、**スキル側スクリプト・workflows に変更は不要**:

- `.sections[]` array 前提の jq クエリ: 現行 v5/v1.x KC 形式と同じ → そのまま動作
- `.index[]` 経由の hints 引き: 現行仕様踏襲
- `read-sections.sh` の `jq '.sections[$sec]'` は **object 前提の旧コード**。v5 KC の実際の形式も array であるため、このコード自体が現状バグ(詳細未確認)。本 Phase では対象外、別途修正。

---

## 7. verify への影響

本スキーマ変更は verify の検証範囲・アルゴリズムに影響する。`.claude/rules/rbkc.md` の「Rules for changing verify」に従い、verify の変更は**別途ユーザー承認プロセス**で確定する。本設計書では verify 仕様を定めない。

影響が想定される観点:
- QC1–QC6 の検証対象に top-level `content` が追加される
- `index` / `official_doc_urls` フィールドの存在チェック追加
- QC6 の照合 key が section title から section id に変わる（hints ファイル key 変更に伴う）

---

## 8. ロールアウト

`.claude/rules/nabledge-skill.md` の cross-version 原則に従い、全 5 版（v6, v5, v1.4, v1.3, v1.2）を同一 PR でロールアウト:

1. RBKC 側コード改修（TDD）
2. verify 側改修（別途承認後）
3. 全版の `hints/v{version}.json` 再生成（key を section id ベースに）
4. 全版で `rbkc create` + `rbkc verify` FAIL 0 件確認
5. 全版で `nabledge-test --baseline` 実行、劣化なし確認
