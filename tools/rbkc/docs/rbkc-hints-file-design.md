# hints file 生成設計

## 1. 目的

ソースファイル（RST / Markdown / Excel）の見出しごとに検索キーワードを紐付けた
`tools/rbkc/hints/v{version}.json` を生成する。

- hints file は **手動管理のソースファイル**（git 管理）。生成は一回限り。
- `rbkc create` は hints file を入力として使う。KC cache は create 時に参照しない。
- verify は「RBKC JSON ⇔ docs MD ⇔ hints file」の三者一致を検証する。

---

## 2. hints file の構造（ソース忠実版）

```json
{
  "version": "6",
  "hints": {
    "{file_id}": {
      "{ソースの h1 / h2 / h3 タイトル（実在文字列）}": ["keyword1", "keyword2", ...]
    }
  }
}
```

### 原則

- key は **ソースファイルに実在する** h1 / h2 / h3 タイトル（そのままの文字列）
- 値は **KC cache で蓄積された keywords のみ**（新規推測・生成は一切しない）
- 同じ見出しに複数の KC section が対応する場合は hints を union
- xlsx は見出し構造を持たないため **ファイル単位 1 key**（key = `"__file__"` 固定）

### 不変条件

- `hints[file_id]` のすべての key はソースファイルに実在する（検証対象）
- すべての KC cache の hints が損失なく埋め込まれている（**KC hints 保存率 100%**）
- 空 hints の key は hints file に書かない

---

## 3. 入力ソースの 3 者関係

| ソース | 役割 | 信頼度 |
|---|---|---|
| ソース RST/MD/xlsx | 見出し構造の真実ソース | 最高（hints file の key はここから生成） |
| KC catalog.json (`.cache/v{V}/catalog.json`) | s{n} → h2 heading の部分的マッピング | 中（h2 のみ、h3/preamble は記録されない、split で欠損あり） |
| KC cache knowledge JSON (`.cache/v{V}/knowledge/.../*.json`) | s{n} → (AI が付けた title, hints, 本文) | 低（title は AI が改変、AI 創作混入の可能性） |

**結論**: ソース RST を真実ソース、KC cache は hints の供給源、catalog は補助情報として扱う。

---

## 4. マッピングアルゴリズム

### 4-1. 全体フロー（per base_name）

```
1. ソース見出し抽出: RST/MD パーサで (h1, [h2/h3 titles with line numbers]) を得る
2. catalog 情報集約: 同じ base_name の全 split entry から section_map と section_range を union
3. cache 集約: 同じ base_name の全 split cache json から index[{sid, title, hints}] を union
4. 各 s{n} をソース見出しに解決（§4-2 参照）
5. 解決結果を hints file 形式に書き出し（同一見出しにマップされた複数 s{n} の hints を union）
```

### 4-2. s{n} → ソース見出しの解決（優先順位つき）

以下の順で試行し、最初に成功した規則を採用する。すべて失敗した場合は **ERROR** で停止（生成中断、ただし xlsx を除く）。

ソース見出しは **h1 / h2 / h3 / h4 の全レベル**を抽出して照合対象とする（実計測で 72% の P4 が全レベル照合で解決できることを確認済み、§B-8）。

| 順 | ルール | 適用条件 | 解決先 |
|---|---|---|---|
| R1 | catalog 直接マッチ | catalog.section_map[s{n}].heading が非空 かつ ソースに完全一致 | その見出し title |
| R2 | catalog heading 空 → h1 fallback | catalog に s{n} あり、heading="" | ソースの h1 title |
| R3 | cache.title 直接マッチ（全レベル） | cache.index[s{n}].title が h1〜h4 いずれかのソース見出しに完全一致 | そのソース見出し |
| R4 | 空白/括弧正規化マッチ | cache.title を NFKC・連続スペース畳み込み・全半角括弧統一 後にソース見出しと一致 | 一致したソース見出し（ソース側文字列） |
| R5 | `—` 連結分解 | cache.title が `"A — B"` 形式、分解した片側がソースに実在 | その実在側の見出し（両側実在なら後半＝より詳細な側） |
| R6 | h1 fallback（最終手段） | 上記すべて失敗、かつ source に h1 がある | h1 title（警告ログ、`rule=R6` で記録） |
| ERR | 失敗 | R6 も失敗（h1 なし） | **生成エラー**（ユーザー確認要） |

### 4-3. 各ルールの詳細

**R3: cache.title 直接マッチ（全レベル）**

- ソース RST を h1〜h4 全レベルでパースし、全見出しタイトルのリストを構築
- cache.index[s{n}].title と完全一致する見出しを採用
- 複数レベルに同名見出しがあった場合は **最深レベル**（h3 > h2 > h1）を優先

**R4: 空白/括弧正規化マッチ**

正規化ルール（ソース見出し・cache.title 双方に適用してから比較）:
- NFKC 正規化（全角英数 → 半角、など）
- 連続スペース → 1 個、前後 trim
- 全角括弧 `（）` ⇔ 半角括弧 `()`
- 末尾の `（...）` / `(...)` 注釈を除去した形でも一致を試行

解決先は **必ずソース側の実在文字列**を採用（key はソース忠実の原則）。

**R5: `—` 連結分解**

KC AI が `"A — B"` の形で cache.title を生成するケース（em-dash 等で連結）。

- 区切り候補: ` — `, ` – `, ` - `, `—`, `–`, `: `, `：`, `｜`, `|`
- 分解した各片を R3/R4 と同じ照合にかける
- 両方実在するなら、hints は後半（より具体的）側に貼る
- 片方のみ実在なら、その側に貼る

**R6: h1 fallback（最終手段）**

R1〜R5 すべて失敗した sid は、AI が作った fabricated title（ソース実在なし）。
- hints を捨てずに、ソース h1 に union する（hints 保存率 100% を担保）
- 警告ログに `sid`, `cache.title`, `base_name` を出力して可視化
- 計測上の想定件数: 5 版合計 179 件 / 1617 hints（§B-8, xlsx 除く）

### 4-4. xlsx 特例

- xlsx には見出し構造がない
- すべての s{n} の hints を **単一 key `"__file__"`** に集約（union）
- R1〜R6 / ERR は xlsx では発動しない
- Phase 21-C で行単位 section 化された後、この特例は廃止して再生成

---

## 5. 品質担保

### 5-1. 生成時の自動検証（fail-fast）

generate_hints.py 実行時に以下をすべて検証し、違反があれば ERROR で停止する:

| 検証項目 | 違反時の動作 |
|---|---|
| V1: すべての key はソースに実在する文字列（xlsx の `__file__` を除く） | ERROR（マッピングロジック不備） |
| V2: KC cache の hints 保存率 100%（ロスなし） | ERROR（R6 fallback を含めて 1 件も落とさない） |
| V3: ルール別の解決件数サマリ出力（R1〜R6 ごと） | 人間レビュー用、必須出力 |
| V4: ERR 停止件数（h1 も無い RST/MD） | 0 件であること |

### 5-2. 解決ルール使用頻度の受容範囲

生成完了後、解決ルール別統計を確認する。以下は §B-8 実計測に基づく期待値:

- R1 + R2（catalog 系）: 全 sid の **≥ 85%**
- R3（cache.title 直接・全レベル）: 残りの大部分（P4 の 72% 相当）
- R4 + R5（正規化・連結分解）: 各 2% 以下
- R6（h1 fallback、xlsx 除く）: **≤ 2%**（想定: 全 5 版合計 179 sid / 6000+ sid）

### 5-3. hints ファイル事後検証（別プロセス）

生成後、`rbkc verify` パイプラインに以下を追加:

| 検証 | 内容 |
|---|---|
| C1: hints file key のソース実在性 | hints/v{V}.json の全 key について、対応するソースファイルに実在する見出しか確認（xlsx の `__file__` を除く） |
| C2: hints file ⇔ RBKC JSON 整合性 | 各 key（ソース見出し）が RBKC JSON の「title or sections[].title」のいずれかに一致 |
| C3: hints 重複チェック | 同一 hints が複数 key にまたがらない（union 不正の検出） |

### 5-4. TDD 適用

- 各ルール R1〜R6 に対して単体テストを持つ（fixture として最小ケース）
- ルール優先度の統合テスト（R1 で解決するケースで R3 が走らないこと等）
- 正規化ロジック（NFKC、全半角スペース、括弧）は境界値テスト
- R6 fallback テスト: h1-only ソースと fabricated title の組み合わせ

---

## 6. 重要な問題と未解決リスク

### 問題 1: AI 創作 title を h1 に吸着する影響（R6 fallback）

R6 で h1 へ集約される 5 版合計 179 sid / 1617 hints（§B-8, xlsx 除く）は、
本来別の概念を指していた可能性がある hints を h1 レベルに集約する。
- 想定サイズ: h1 配下ページ size 中央値 1K字、p90 5〜14K字（xlsx 除く）→ ノイズ化リスクは低い
- 代替案（閾値 0.3 の n-gram 本文マッチ）を実計測した結果、救済率 24%(31/130) で複雑性に見合わないため不採用
- **R6 fallback 件数が 2% を超える版が出たら設計見直し**（§5-2）

### 問題 2: xlsx hints

xlsx は見出し構造を持たないため全 hints を `__file__` key に集約する（§4-4）。
- Phase 21-C（行単位 section 化）完了後に行単位 key へ再生成が必要
- Phase 21-C は本 PR の In Progress フェーズ、完了前の hints file は中間成果

### 問題 3: catalog の section_map 欠損（no_section_map_in_entry）

v5 で 256 件、v1.4 で 264 件が catalog.section_map 空。split されていないのに空というのは KC 側の構造的取りこぼし。
- 本設計では **ソース RST を自前パース**（generate_hints.py の parse_source_headings）することで catalog 欠損に依存しない
- catalog は R1/R2 での補助情報としてのみ使用

### 問題 4: 同一見出しへの複数 s{n} 集約時の hints 順序

R1〜R6 で同一見出しに複数 s{n} がマップされたとき hints を union する。
- 順序は「先に解決された s{n} の順」→ 決定論的
- 重複 hints は除去（順序保持 dedup）

### 問題 5: 同一ファイル内の同名見出し衝突

hints file は見出しタイトルを key に取るため、同一ファイル内に同名 h2 があると衝突する。
- **検出**: 生成時に同一 file_id 内で key 重複を検出したら ERROR
- **対策**: 実データで対象件数を確認してから判断（fail-fast で検出）

---

## 7. スクリプト構成

### 7-1. 新規スクリプト: `.pr/00299/generate_hints.py`

standalone、`tools/rbkc/scripts/` には置かない（rbkc のランタイム依存にはしない）。

```
generate_hints.py
  ├── load_catalog(version) → dict[base_name → entries]
  ├── load_cache(version, base_name) → list[(sid, title, hints, content)]
  ├── parse_source_headings(source_path, format) → list[(level, title, line)]  # h1〜h4 全レベル
  ├── resolve_sid_to_heading(sid, cache_entry, catalog_entry, source_headings) → (heading, rule_id)
  │   ├── R1〜R6 を順に試行
  │   └── 各ルールは専用関数に分離（TDD 容易化）
  ├── aggregate_hints(resolved) → dict[heading → list[keyword]]
  ├── emit_statistics(log) → 解決ルール別件数、R6 fallback 件数
  └── main(version) → 出力: tools/rbkc/hints/v{version}.json
```

### 7-2. テスト: `.pr/00299/test_generate_hints.py`

- R1〜R6 の単体テスト（fixture ベース）
- 正規化関数の境界値テスト（NFKC、空白、括弧）
- 全 5 版に対する smoke test: ERR 0 件、R6 ≤ 2%、hints 保存率 100%

### 7-3. 生成コマンド

```
python .pr/00299/generate_hints.py --version 6
python .pr/00299/generate_hints.py --version 5
python .pr/00299/generate_hints.py --version 1.4
python .pr/00299/generate_hints.py --version 1.3
python .pr/00299/generate_hints.py --version 1.2
```

出力: `tools/rbkc/hints/v{version}.json`
ログ: stdout に統計サマリ（R1〜R6 別件数、R6 fallback の sid 一覧）

---

## 8. 受け入れ基準

以下すべてを満たしたら設計完了:

- [ ] 全 5 版で ERR 0 件で完走（xlsx 除く RST/MD のみ）
- [ ] KC cache の hints 保存率 = 100%（V2 が PASS、R6 fallback を含めて hints を捨てない）
- [ ] hints file の全 key がソース実在（V1 が PASS、xlsx `__file__` を除く）
- [ ] R6（h1 fallback）が全 sid の 2% 以下
- [ ] `rbkc verify` で hints 関連 FAIL が 0 件（全 5 版）
- [ ] 設計書（本ファイル）に未解決リスク（§6）が残らない／残れば明示的に deferred 記録

---

## 9. スコープ外（明示）

- 新規 keywords の生成（AI にキーワードを作らせる機能は含まない）
- hints の内容評価（keywords の検索適合度の評価は nabledge-test の責務）
- xlsx の行単位 section 化（Phase 21-C）
- RBKC JSON スキーマへの影響（本設計で JSON スキーマを変更しない）

---

## 付録 A: KC パイプライン調査結果（事実）

hints file 設計の前提となる KC（knowledge-creator）の処理仕様を、実装を読んで確認した結果。

### A-1. 全体パイプライン

```
Phase A: Preparation
  step1_list_sources.py: ソースファイル一覧
  step2_classify.py    : 分類 + split 判定 + section_map 構築 → catalog.json
Phase B: Generate
  phase_b_generate.py  : AI で 1 entry ごとに knowledge JSON 生成
                         → .cache/v{V}/knowledge/<path>/<id>.json (分割された部分ファイル)
Phase C: Structure Check (構造検証のみ、cache は変えない)
Phase D: Content Check  (内容検証、findings を出すだけ)
Phase E: Fix            (AI で cache の部分ファイルを修正、上書き)
Phase M: Merge + Finalize
  merge.py             : split された部分 cache を original_id でマージ
                         → .claude/skills/nabledge-{V}/knowledge/<path>/<id>.json
  phase_f_finalize.py  : docs 生成 + link 解決 + 最終化
```

### A-2. catalog.json の構造と section_map の作成ロジック

**作成**: `step2_classify.py` がスクリプトで RST をパースして構築する。AI は介在しない。

**h2 / h3 判定基準** (`analyze_rst_sections` / `analyze_rst_h3_subsections`):
- h2: 下線が `-{5,}` （ハイフン 5 文字以上）
- h3: 下線が `[\^~+*.=]{5,}` （`^ ~ + * . =` のいずれか 5 文字以上）
- **階層ルール（RST 公式の最初に出た下線が h1 ...）は見ない。下線文字だけで判定。**

**h3 展開** (`_expand_large_sections`):
- h2 の行数 ≤ 400 → そのまま（h3 は展開されず h2 に吸収される）
- h2 の行数 > 400 → h3 で再分割（h3 が存在する場合のみ。なければ巨大 h2 のまま warning）
- **閾値 `LINE_GROUP_THRESHOLD = 400`**

**section_map のエントリ** (`split_file_entry` Step 6):
```json
{
  "section_id": "s{n}",       // 分割後の通し番号
  "heading": "見出しテキスト",  // ソース実在文字列（h2 または h3 タイトル）
  "rst_labels": [...]          // section 範囲内の :ref: ラベル
}
```

**h1 直下の preamble の扱い** (`analyze_rst_sections` line 221-223):
```python
if sections:
    sections[0]['start_line'] = 0   # 最初の h2 の start_line を 0 に拡張
```
→ s1 は **preamble + 最初の h2 全体** を含む。heading は最初の h2 タイトル。
→ preamble だけ単独では section にならない（最初の h2 と結合）。

**非 split の場合** (`step2_classify.py` line 574-):
- h2 ごとに `s1, s2, ...` を順に振る（`sections[0]['start_line'] = 0` により先頭 s1 は preamble 込み）
- h2 が 0 個 かつ RST ラベルあり → `s1 heading="" rst_labels=[...]` を 1 個だけ追加
- h2 が 0 個 かつラベルもなし → section_map は空配列

**empty section_map の正体**:
- `-----` が 1 つもない RST（例: h1 + toctree だけ、h1 + 表だけ、h1 + code-block だけ）
- ラベルもないと空のまま

### A-3. cache knowledge JSON（Phase B 出力）の構造

**パス**: `.cache/v{V}/knowledge/<type>/<category>/<output_path>.json`
- split 時: `...base_name--s{n}.json`（section group ごと）
- 非 split 時: `...base_name.json`（1 ファイル）

**スキーマ** (`prompts/generate.md` の Output JSON Schema):
```json
{
  "id": "<FILE_ID>",                  // catalog の id と一致
  "title": "<ドキュメントタイトル>",    // AI が source の h1 から抽出
  "no_knowledge_content": false,
  "official_doc_urls": [...],
  "index": [
    {
      "id": "s1",
      "title": "<section title>",     // AI 生成（source 見出しと一致するとは限らない）
      "hints": ["keyword1", ...]
    }
  ],
  "sections": {                        // Markdown 本文
    "s1": "## 見出し\n\n本文..."
  }
}
```

**AI が section title をどう決めるか** (`prompts/generate.md` Work Step 2):
- `{EXPECTED_SECTIONS}` プレースホルダに `section_range.sections`（catalog 由来）を流し込む
- AI には「Expected Sections があれば **全部生成必須**、なければ自前スキャン」と指示
- ただし AI は title を **自由に書き換える可能性がある**（promo、要約、分解、結合）

**AI が hints をどう決めるか** (Work Step 5):
- 5-1: クラス/インターフェース名（backtick + PascalCase / package 表記）
- 5-2: アノテーション `@XxxName`
- 5-3: Exception 名
- 5-4: property table の第一列
- 5-5: 機能的な日本語キーワード 2〜5 個（AI 生成）
- 5-6: toctree の項目名
- 5-7: 統合された h3 見出しのキーワード

### A-4. section ID の振り方と catalog ↔ cache の対応

**catalog の section_map** : section_id = split 後の通し番号（split 内では s1 から開始）
- 例: 3 split されたファイル
  - part 1 の section_ids: `["s1", "s2", "s3"]`
  - part 2 の section_ids: `["s4", "s5"]`
  - part 3 の section_ids: `["s6", "s7", "s8"]`

**cache knowledge JSON の index[].id**: 部分ファイル内では **s1 から振り直し**ではなく、catalog の section_id と**一致**する
- 確認: prompts に「Use sequential IDs starting from s1」とあるが、`section_range.section_ids` を渡している
- ただし、**AI が指示を無視して s1 から振り直すバグは起きうる**（実データで要確認）

**merge 時の振る舞い** (`merge.py`):
- part を `split_info.part` 順にソート
- index: 同じ `section_id` が複数 part に出たら hints を union（重複排除、順序保持）
- sections: 同じ `section_id` が複数 part に出たら content を `\n\n` で連結

### A-5. 知識ファイル（merge 後、最終出力）の構造

**パス**: `.claude/skills/nabledge-{version}/knowledge/<type>/<category>/<original_id>.json`

**スキーマ**: cache と同じ。ただし:
- split ファイルは `original_id` 単位に統合済み
- section_id はマージ後も保持（`s1, s2, ...` が split 境界を越えて連番）

**重要な観察**（現物確認済み）:
- 最終出力 `sections[]` は **flat**（ネストなし）
- 元 RST が h3 持ちでも、h3 は h2 に吸収されて同列に並ぶ（AI が Markdown 内で `###` として出す）
- → 知識ファイルの section 粒度は **基本 h2**、400 行超の h2 だけ h3 展開

### A-6. catalog ↔ cache ↔ 知識ファイル ↔ ソース の対応関係（まとめ）

```
ソース RST (.lw/...)
  │ h1: Document Title
  │ h2: Section A       ← KC が "-----" で判定
  │   h3: Sub A-1       ← h2<400行なら無視、>=400行なら分割キー
  │ h2: Section B
  │
  ▼ step2_classify.py (スクリプト・決定論的)
catalog.json
  files[].section_map[]:
    { section_id: s1, heading: "Section A", rst_labels: [...] }
    { section_id: s2, heading: "Section B", rst_labels: [...] }
  files[].section_range: split 時の範囲情報
  ★ h1 は記録されない
  ★ h3 は通常記録されない（大きい h2 の場合のみ）
  ★ heading はソース実在文字列（AI 改変なし）
  │
  ▼ phase_b_generate.py (AI)
.cache/v{V}/knowledge/.../base_name[--s{n}].json  (split 時は複数ファイル)
  index[]:
    { id: s1, title: "Section A", hints: [...] }  ← title は AI 改変の可能性
    { id: s2, title: "Section B", hints: [...] }
  sections:
    s1: "## Section A\n..."  ← Markdown 本文
    s2: "## Section B\n..."
  ★ title と heading は別物。AI が要約/書き換えする可能性あり
  ★ hints は AI が source から抽出（クラス名・アノテーション・キーワード等）
  │
  ▼ merge.py + phase_f_finalize.py
knowledge/<type>/<category>/<original_id>.json  (split を統合、1 ファイル)
  index[]: part-sequential 順、id 重複なら hints union
  sections: id 重複なら content を \n\n 連結
```

### A-7. 本設計（hints file 生成）への影響

この調査結果から、設計方針を以下に確定する:

1. **hints file の真実ソースはソース RST 本体**（catalog も cache も一次ソースではない）
2. **catalog.section_map は信頼できる補助情報**（heading はソース実在、ただし階層潰れあり）
3. **cache.index[].title は信頼できない**（AI 改変の可能性）
4. **cache.index[].hints は最大限活用する**（100% ロスなしが目標）
5. **AI が section_id を振り直すバグは実データ検査で確認する必要あり**

これにより §4-2 の R1〜R9 を見直し、以下に簡略化する:

| 順 | ルール | ソース |
|---|---|---|
| P1 | ソース RST を自前パース → h1/h2/h3 の実在タイトルリスト取得 | **必須（一次ソース）** |
| P2 | catalog.section_map で s{n} → h2/h3 ソース見出しにマップ（heading 非空のみ） | 確実 |
| P3 | catalog の heading="" / section_map 空 → ソース h1 にフォールバック | 決定論的 |
| P4 | cache.title は**使わない**（検証用途のみ） | 改変リスク |
| ERR | s{n} が catalog にも cache にもない / id 不整合 → 生成エラー | fail-fast |

→ 元の R5〜R8（cache.title 正規化/分解/本文マッチ）は**不要**。cache.title を使わないので。

---

## 付録 B: 5 バージョン裏取り結果（事実）

§A の方針で本当に全件マップできるかを 5 版のキャッシュに対して検証した結果。

### B-1. 検証方法

- `cache.index[].id` が `catalog.section_map[].section_id` にある → その heading を採用（P1/P2）
- heading="" / section_map 空 → ソース RST の h1 にフォールバック（P3）
- sid が catalog に存在しない → 不整合として抽出（P4）

### B-2. 全 5 版の集計

| ver | index 総数 | hints 総数 | P1 (heading 非空) | P2 (heading="") | P3 (sm 空) | **P4 (sid 不整合)** | xlsx hints |
|---|---|---|---|---|---|---|---|
| v6 | 1778 | 12805 | 1432 (80%) | 169 (9%) | 55 (3%) | **165** | 221 |
| v5 | 2101 | 14796 | 1552 (73%) | 205 (9%) | 196 (9%) | **281** | 1158 |
| v1.4 | 2199 | 16616 | 1171 (53%) | 696 (31%) | 270 (12%) | **332** | 0 |
| v1.3 | 1389 | 11125 | 747 (53%) | 485 (34%) | 113 (8%) | **157** | 0 |
| v1.2 | 1334 | 10643 | 720 (53%) | 467 (34%) | 106 (7%) | **147** | 0 |

**P1+P2+P3 = 決定論的に解決できる**: v6/v5 で 92-93%、v1.x で 96-97%
**P4 合計 1082 件** = `cache.index[].id` が `catalog.section_map` に存在しない（KC の bug またはスキーマ齟齬）

### B-3. P4 の正体（現物調査）

**例 v6 `web_thymeleaf_adaptor.rst`**:
```
ソース実構造:
  h1: ウェブアプリケーション Thymeleafアダプタ
  h2: モジュール一覧
  h2: ウェブアプリケーション Thymeleafアダプタを使用するための設定を行う
    h3: 処理対象判定について                       ← catalog は取り逃し
  h2: テンプレートエンジンを使用する

catalog.section_map: s1,s2,s3 (h2 のみ)
cache.index:         s1,s2,s3,s4 (AI が h3 を拾って s3 に入れ、h2 を s4 にずらした)
```

**例 v1.4 `01_userDeleteBatchSpec.rst`**:
```
ソース: h1 + h2 x 4（`=====` 下線=h1 と `-----` 下線=h2 が混在）
  実際は `=====` が複数あり、KC の -{5,} 判定で "障害通知仕様" (-----) の 1 個しか拾えてない
catalog.section_map: s1 だけ
cache.index:         s1:機能概要, s2:エンティティ情報, s3:ファイル情報 (AI が = 下線の h2 を拾った)
```

P4 は **KC の下線文字判定ロジックの取りこぼし**。AI が source を見て拾い直してるので cache.index[].title は **ソース実在文字列であることが多い**。

### B-4. P4 の解消見込み（cache.title → source 実見出しマッチ）

cache.index[].title をソース RST の全見出し（h1/h2/h3/h4 全レベル）と照合:

| ver | P4 total | exact match | normalized match | NO match |
|---|---|---|---|---|
| v6 | 165 | 142 (86%) | 2 | **21** |
| v5 | 281 | 220 (78%) | 0 | **61** |
| v1.4 | 332 | 260 (78%) | 0 | **72** |
| v1.3 | 157 | 105 (67%) | 1 | **51** |
| v1.2 | 147 | 96 (65%) | 1 | **50** |

**P4 の約 70-86% は cache.title の完全一致で救える**（ソース見出し抽出を全レベル対応にすれば）。
残り **合計 255 件（5 版）が真の不整合**。

### B-5. 真の不整合 255 件のパターン（現物）

1. **`—` 連結タイトル（AI が h2 — h3 を結合）**:
   - v5 `router_adaptor.rst`: `"JAX-RSのPathアノテーションでマッピングする — マッピングの実装方法"`
   - v1.4 `01_JspStaticAnalysis.rst`: `"使用方法 — 設定ファイルの準備"`
   - 分解（`—` で split）して h2 側 or h3 側にマッチ試行すれば救える

2. **AI が source にない section を創作**:
   - v6 `getting_started.rst` (h1 のみのソース) に cache が `前提条件` `概要` 等を勝手に作った
   - R4 (`概要` マーカー → h1 fallback) で救える可能性あり。それ以外は本物の創作で hints を捨てる判断要

3. **括弧で注釈追加**:
   - v1.4 `01_MasterDataSetupTool.rst`: cache `"ツールの特徴（設定ファイル不要）"` vs source `"ツールの特徴"`
   - 括弧部分を削れば一致

### B-6. 裏取り結論

**決定論的に解決できる hints 保存率の上限**:
- P1+P2+P3+P4(exact+normalized) で計算すると:
  - v6: (1432+169+55+144)/1778 = **~100%（ただし P5=h1 欠落 1 件）→ 1757/1778 = 99%**
  - v5: (1552+205+196+220)/2101 = 2173/2101 → index 側の総数超え（一部複数回カウント）になるため要精査
  - **正確な数字は実装して数え直す必要あり**

**未解決の未解決リスク（設計書 §6 に新規追加）**:
- 真の不整合 **255 件**（5 版合計）: `—` 分解・AI 創作・括弧注釈 の 3 パターン
- hints 保存率 100% を目指すなら、このうち最低でも `—` 分解と括弧注釈パターンは機械処理必須
- AI 創作分（getting_started 系）は hints を捨てるか h1 に集約するかユーザー判断要

### B-7. 今後必要な調査（実装前）

- [x] P4 真の不整合 255 件を `—` / 創作 / 括弧 の 3 パターンに分類して件数確認 → §B-8
- [x] `—` 分解で救える件数を全 5 版で集計 → §B-8
- [x] AI 創作パターン（h1 のみソースに複数 section 生成）を特定 → §B-8
- [ ] xlsx の全バージョン集計（v5 1158 件が最大、v1.x は 0）
- [ ] **目標 hints 保存率**を上記を踏まえて再設定（100% 固執か、95% 許容かユーザー判断）

### B-8. P4 分類結果（実計測、2026-04-21）

**計測スクリプト**: `.pr/00299/classify_p4.py`（RST 全レベル見出し抽出 + dash/paren 正規化試行）
**結果データ**: `.pr/00299/p4-classification.json`

| ver | P4 | heading match (全レベル) | dash split | paren strip | fabricated (h1-only/other) | fabricated hints loss |
|---|---|---|---|---|---|---|
| v6 | 169 | 137 | 0 | 1 | 31 (15 / 16) | 388 |
| v5 | 341 | 219 | 11 | 10 | 101 (19 / 82) | 1519 |
| v1.4 | 326 | 255 | 5 | 3 | 63 (42 / 21) | 592 |
| v1.3 | 155 | 106 | 3 | 1 | 45 (39 / 6) | 376 |
| v1.2 | 145 | 96 | 3 | 1 | 45 (40 / 5) | 366 |
| **合計** | **1136** | **813** | **22** | **16** | **285** (155 / 130) | **3241** |

**解釈**:

- **heading match（全レベル）= 813 件**: ソース RST を h1〜h4 全レベルでパースすれば cache.title と完全／正規化一致。**これが P4 の 72%**。`parse_source_headings` を全レベル対応にすれば決定論的に救える。
- **dash split = 22 件**: `h2 — h3` 連結を split して片側に完全一致。R5 ルールで救える。
- **paren strip = 16 件**: 末尾の `(...)` を除去すれば完全一致。R7 ルールで救える。
- **fabricated = 285 件**（旧 255 件推定から更新）: ソース見出しに対応なし。内訳:
  - **h1-only source = 155 件**: 元 RST が h1 しか持たないのに cache に複数 section が作られたケース（`前提条件` `概要` など AI 創作）
  - **h1 以外のソース = 130 件**: h2/h3 はあるが cache title が独自解釈（再構成した見出し等）

**fabricated hints 合計 3241 件**: これらを捨てる場合の最大ロス。5 版 total hints 66K に対し約 5%。

**非 h1-only fabricated の特徴**:
- **リリースノート系（v5/v6）**: `releases-nablarch6u2-releasenote` 等、AI がノート構造を再編成。section 見出しが AI 再生成。**hints 数が大きい**（v5 で 1 entry に 68 hints）。
- **validator 設定系（v1.x）**: `LengthValidator の設定値` 等、cache が独立 section に立てるが source では別構造。
- **sequence-/flow-like 系（v6 releases）**: `マルチパートリクエストのサポート対応（6u2からの移行手順）` など AI が括弧付きで補足。

### B-9. これを踏まえた設計方針（提案）

1. **§4-2 R3 の拡張**: cache.title ⇔ ソース見出し完全一致は、h1〜h4 全レベルでマッチを試行する（現行も既にそう書いているが、実装面で「全レベル」を明示）
2. **R5 `—` 分解** と **R7 括弧正規化** を維持。対象件数（22 + 16 = 38）は少ないが救える。
3. **R4 `概要` マーカー → h1 fallback** は h1-only source での救済策として維持。
4. **h1-only fabricated 155 件（合計 hints 1436 件）**:
   - R4 の「`概要`」以外のタイトル（`前提条件`・`Exampleの位置づけ` 等）も h1 fallback で救うか、捨てるか要ユーザー判断
5. **非 h1-only fabricated 130 件（合計 hints 1805 件）**:
   - ソースに存在しない見出しを作ると「hints file の key がソース実在」という V1 不変条件を破る
   - R8（本文最大一致）で救うか、捨てるか要ユーザー判断。リリースノート系は本文量が多く R8 が働きやすい見込み
6. **達成可能 hints 保存率（楽観シナリオ = h1-only を h1 に集約 + R8 稼働）**:
   - 5 版合計 hints ≈ 66000 中、最大ロスは AI 創作の 3241 件 (5%)
   - **95% は余裕で達成可能。100% は R8 の効果次第**

### B-10. ユーザー判断が必要な点

1. **目標 hints 保存率**: 95% 許容か、100% 固執か
2. **h1-only fabricated（155 件, 1436 hints）の扱い**: h1 に集約するか、捨てるか
3. **非 h1-only fabricated（130 件, 1805 hints）の扱い**:
   - 選択肢 A: R8（本文最大一致、閾値付き）を実装して救う
   - 選択肢 B: 完全にソース忠実として捨てる
   - 選択肢 C: cache.title をそのまま key として許可（V1 不変条件を緩和）

