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
| `sections[].id` | string | `s1`, `s2`, ... の連番。**regex `^s[1-9][0-9]*$` に必ず一致。`top` は予約語で section id には使えない** | ✅ |
| `sections[].title` | string | ソースの h2 または h3 タイトル | ✅ |
| `sections[].content` | string | セクション本文（Markdown） | ✅ |
| `sections[].hints` | array | セクションのキーワード | ✅（空配列可） |
| `index` | array | トップレベル + 各セクションの `{id, title, hints}` 一覧。`no_knowledge_content == true` のときは `[]`（top 不在） | ✅ |
| `no_knowledge_content` | bool | `true` のとき `content`・`sections`・`index` はすべて空（目次/toctree 専用ページ） | ✅ |
| `official_doc_urls` | array | 公式ドキュメント URL | ✅（空配列可） |

### 2-2a. スキーマ不変条件

以下は verify で検証する（QO1 配下）:

- `sections[].id` は `^s[1-9][0-9]*$` に一致。`top` は section id として使えない
- `.index[]` に id の重複があってはならない（`top` 含む）
- `no_knowledge_content == true` ⇒ `content == ""` AND `sections == []` AND `index == []`
- `no_knowledge_content == false` ⇒ `.index[0].id == "top"`（トップレベル content が空でも `top` エントリは存在する）

### 2-3. `index` フィールドの構造

nabledge スキル側が section メタ情報（id/title/hints）を取得する単一の窓口。

- `no_knowledge_content == false` のとき:
  - 先頭は必ず `{"id": "top", "title": <h1 title>, "hints": [...]}`（top-level content が空でも `top` エントリは存在）
  - 以降 `sections[]` と 1:1 対応で `{"id": "s1", ...}`, `{"id": "s2", ...}` が順に続く
- `no_knowledge_content == true` のとき:
  - `index == []`（`top` エントリも含まれない。content / sections いずれも存在しないため）

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
- **h2 と h3 は同一階層（フラット）として `sections` に入る**。たとえば h2→h3→h2 の順であれば `sections[0]` = h2, `sections[1]` = h3, `sections[2]` = h2。`sections[].title` に heading level 情報は残さない
- h4 以降 → 所属 h2/h3 の `content` に `#` 記号付きで埋め込み（現行仕様踏襲）
- h2/h3 が 1 つも無いファイル → `sections: []`
- h1 すら無い（目次 toctree 専用など） → `title: ""`, `content: ""`, `sections: []`, `index: []`, `no_knowledge_content: true`

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

**原則 §1「ソース非存在文字列混入禁止」の例外としての位置付け**:

Excel には h1 相当のソース構造が存在しないため、`title` を「ファイル識別子由来の人間可読タイトル」に設定することは §1 に対する設計上の**例外**である。RST/MD は source-faithful を厳格に適用するが、xlsx だけは source-derived（ファイル識別子から決定論的に導出）の title を許容する。この例外は本 Phase 21-D の範囲で唯一許容され、他の固定値／独自ルールの導入は禁止する。Phase 21-C で行単位 section 化を行う際に、セル値ベースの title 導出（例: A1 セル値）への移行を検討する。

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

### 4-2a. 空行ルール（正規）

docs MD の空行規則は以下のとおり。QO1/QO2 の完全一致比較が決定論的に行えるよう、RBKC と verify の両方で本規則に従う。

1. 各出力ブロック（`# title` / `content` / `<details>` / `## section title` / section content / section `<details>`）の間には、**空行ちょうど 1 行** を挿入する
2. 出力しないブロックは、その分の空行も出さない（連続した空行を生じさせない）
3. ファイル末尾は改行ちょうど 1 つで終わる（trailing newline）
4. `<details>` ブロック内部の構造は以下で固定:
   ```
   <details><summary>keywords</summary>

   keyword1, keyword2, ...

   </details>
   ```

### 4-2b. 出力パターン例

以下に主要な 4 パターンを例示する。`◯` は実在、`×` は空/不在を表す。

**Pattern A**: title ◯ / content ◯ / top hints ◯ / sections ◯

```markdown
# タイトル

トップレベルの本文。

<details><summary>keywords</summary>

kw1, kw2

</details>

## セクション1

セクション本文。

<details><summary>keywords</summary>

kw3

</details>
```

**Pattern B**: title ◯ / content ◯ / top hints × / sections ×

```markdown
# タイトル

本文のみ。
```

**Pattern C**: title ◯ / content × / sections ◯（h1 直下に preamble なし、最初が h2）

```markdown
# タイトル

## セクション1

セクション本文。
```

**Pattern D**: `no_knowledge_content == true`（title も空、toctree 専用ページ）

```markdown
# 
```

（h1 のみの 1 行 + trailing newline。title が空のときは `# ` の後に空白も付けない実装選択が可能だが、一貫性のため `# \n` で統一する）

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

`extract_hints.py`（`.pr/00299/extract_hints.py`）は KC キャッシュから初期 hints を生成する one-time スクリプト。section title ベースから section id ベースへのマッピング変更を伴う。

### 5-3a. 旧 hints → 新 hints のマッピング契約

旧 `hints/v6.json`（section title を key）から新 `hints/v6.json`（section id を key）への変換は以下の契約に従う。実装は `extract_hints.py` を本契約に合わせて改修する。

**前提**: 新 RBKC 出力（新スキーマ適用後の `rbkc create` 結果）のソース h1 title と `sections[].title` の一覧が、マッピングの参照源となる。

**マッピング手順（ファイルごと）**:

1. 新 RBKC 出力 JSON を読み込み、`title`（h1）と `sections[].{id,title}` の一覧を取得する
2. 旧 hints entry のキー（セクション title 文字列）ごとに以下を判定:
   - 旧 key == 新 h1 title（`title` フィールド） → 新 key は `"top"`
   - 旧 key が `sections[].title` のいずれかと完全一致 → 新 key はその section の id（`s1`, `s2` ...）
   - 旧 key が `_PREAMBLE_TITLE = "概要"` 固定値由来で、かつ新 JSON に title が `"概要"` の section が存在しない → 新 key は `"top"`（旧 preamble 擬似 section の hints を top に移す）
   - 旧 key が `_PREAMBLE_TITLE = "概要"` 固定値由来で、かつ新 JSON に title が `"概要"` の section が実在する → **ambiguous**。警告出力し、当該 file の hints 手動確認を要求（自動マッピングしない）
   - 上記いずれにも該当しない（ソース変更で h2 が削除されたなど） → 警告出力し、該当 hints を drop（stale hints）
3. 生成された新 hints を書き出す前に、旧 hints との **dry-run diff** を出力（追加・削除・再マップされたキーの一覧）。ユーザーが diff を確認してから最終書き出しを行う

**生成後の検証ゲート**:

- `rbkc create 6` を実行して新スキーマ JSON を再生成
- `rbkc verify 6` を実行し、QC6（hints 完全性）が PASS することを確認
- QC1–QC5 / QO1–QO5 のすべてが PASS することで、hints が正しく新スキーマに移行したことを保証する

**ambiguous ケースの扱い**: 上記 2-d（旧 "概要" key かつ新 JSON に "概要" section 実在）に該当するファイルは、手動で split を判断する。自動処理で false PASS が出る可能性があるため、ゼロトレランス原則に従って自動処理を行わない。

---

## 6. nabledge スキル側のアクセス API

本スキーマ変更に合わせ、全 5 版（nabledge-6/5/1.4/1.3/1.2）のスキルスクリプトを以下の契約で統一する。

### 6-1. `scripts/read-sections.sh`

- 入力: `$file` (knowledge file), `$section` (id: `top` または `s1`, `s2`, ...)
- 処理:
  - `section == "top"` → `jq -r '.content' $file`。結果が空文字列でも正常終了（空の content を返す。SECTION_NOT_FOUND を返すのは `.content` フィールド自体が JSON に存在しない場合のみ = スキーマ違反）
  - それ以外 → `jq -r --arg sec "$section" '.sections[] | select(.id==$sec) | .content' $file`
  - section id にマッチするエントリが存在しない → `SECTION_NOT_FOUND` を返す
- スキーマ違反（`.content` フィールド不在など）は別種エラーとして報告する

### 6-2. `scripts/full-text-search.sh`

- 検索単位: トップレベル + sections を `id` 統一で扱う
  ```jq
  [{
    id: "top",
    title: .title,
    content: .content,
    hints: ([.index[] | select(.id=="top") | .hints][0] // [])
  }] + .sections
  ```
- `no_knowledge_content == true` の場合、トップレベル `top` エントリは `content=""` / `hints=[]` となり、検索スコアリングで自然に落ちる。実装は empty ガードを明示的に持つ必要はないが、jq の `// []` ガードで `.index[]` が空のときに null が紛れ込むのを防ぐ
- 出力フォーマット: `<score>\t<file>|<id>` は現行踏襲

### 6-3. `workflows/_knowledge-search/_section-search.md`

- `jq '.index[]'` で id/title/hints を引く（現行 jq クエリ踏襲）
- `.index[]` は `top` を含むため、トップレベル content も検索候補に上がる

### 6-4. `workflows/_knowledge-search/_section-judgement.md`

- hints-based pre-filter は `.index[]` 経由（現行踏襲）
- Step A の section content 取得は `read-sections.sh` を利用（6-1 のルールで `top` 対応）

---

## 7. verify への影響（別プロセスで管理）

本スキーマ変更は verify の検証範囲・アルゴリズムに影響する。`.claude/rules/rbkc.md` §「Rules for changing verify」に従い、verify の変更は**本スキーマ設計とは独立にユーザー承認が必要**である。以下は変更が必要になる観点の列挙（仕様の決定ではない）:

- QC1–QC6 の検証対象に top-level `content` が追加される
- QO1 で新スキーマ不変条件（§2-2a）の検証が必要になる
- QC6 の照合 key が section title から section id に変わる
- `check_hints_file_consistency` の key 体系が変わる

これらの verify 側の具体的な変更仕様は、本スキーマ設計書の承認後に別途 `rbkc-verify-quality-design.md` の更新プロセス（rules 記載の TDD + ユーザー承認）を経て確定する。

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

### 8a. 展開順序（cross-version rollout）

`.claude/rules/nabledge-skill.md` の "Apply cross-version changes in a single commit or PR" 原則に従い、全 5 版を同一 PR でロールアウトする。

1. RBKC 側コードと verify を新スキーマに対応（テスト含む TDD）
2. 全版の `hints/v{version}.json` を §5-3a の契約に従い再生成
3. 全版で `rbkc create {version}` を実行し、新スキーマ JSON を生成
4. 全版で `rbkc verify {version}` を実行、FAIL 0 件確認
5. 全版の nabledge スキルスクリプト（§6）を改修
6. 全版で `nabledge-test <version> --baseline` を実行し、ベースライン劣化がないこと確認
7. 単一 PR でコミット
