# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-21 (session 36)

全フェーズ TDD（verify が質問ゲートのため順序に注意）:
- **verify 追加時**: verify テスト作成 → RED確認 → verify チェック実装 → GREEN確認 → RBKC 実装 → verify GREEN確認 → サブエージェント品質チェック
- **CLI 追加時**: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする

---

## In Progress

### Phase 21-A: docs/README.md 未生成 ✅

- [x] verify に README.md 存在チェック追加 → verify FAIL 確認（RED）
- [x] `generate_docs()` に README 生成追加 → verify GREEN 確認
- [x] サブエージェント品質チェック（SE expert review 実施、指摘修正済み）
- [x] rbkc create 6 → verify 6 FAIL 0件確認
- [x] コミット — `c238dc8f`

---

### Phase 21-B: hints の永続化と完全一致チェック

**設計確定（ユーザー承認済み）**:
- `tools/rbkc/hints/v{version}.json` はソースファイル（git 管理、手動更新）
- `rbkc hints {version}` = 一回だけ実行して KC キャッシュから生成、以後は手動更新
- `rbkc create` は `hints/v{version}.json` を入力として使う（KC キャッシュ不要）
- verify チェック: JSON hints == hints/vN.json hints == docs MD hints（三者一致）
- KC キャッシュとの整合は hints 生成時のみ。verify には入らない

**問題2（解決済み）**: KC file_id（`_` あり）と RBKC file_id（ハイフンのみ）の不一致
→ `build_hints_index` で out_id = base_id.replace("_", "-") に修正済み（196 ファイル修正）

**Status**: 190 hints FAIL remaining. Hints file generated, JSON hints written, but ~140 docs MD lack hints blocks + ~50 hints file sections not in JSON (section title mismatch due to catalog Step A imperfect mapping).

**Root cause of remaining FAILs**:
1. `md=[]` (140件): docs MD 内の `<details><summary>keywords</summary>` ブロックがない — hints が hints ファイルにあるが docs MD には書かれていない
2. `json=[]` (0件): 解消済み
3. value mismatch (50件): JSON/docs MD の hints 値 ≠ hints ファイル — catalog Step A でマップされた section が RBKC JSON の section title と不一致（e.g. hints ファイルは KC title 'タグライブラリのネームスペース...' に hints を持つが JSON はその section なし）

**決定**:
- `lookup_hints_with_fallback` の優先順位を hints_idx 優先に修正済み（kc_result がある場合は hints_idx を使う）
- `catalog_index` の last-wins バグ修正済み（part-1 entry を保持）
- `extract_hints.py` を `.pr/00299/` に作成済み（standalone one-time script）
- `rbkc hints` コマンドを run.py から削除済み
- `tests/ut/test_hints.py` を追加済み（5テスト）
- `check_hints_file_consistency()` を verify.py に追加済み
- `check_docs_coverage()` を verify.py に追加済み

**Steps:**
- [x] 全容把握: file_id 不一致の全パターン調査（117直接一致、196正規化待ち、28はKC未収録）
- [x] file_id 正規化ロジック追加: `hints.py` の `build_hints_index` で `_` → `-` 正規化
- [x] 設計: hints 永続化ファイルのフォーマット決定、ユーザー承認
- [x] `catalog_index` last-wins バグ修正（part-1 entry 保持）+ TestBuildHintsIndexCatalogSplitHandling test 追加
- [x] verify チェック追加: `check_hints_file_consistency()` + `check_docs_coverage()` 実装 + テスト
- [x] `.pr/00299/extract_hints.py` 作成（standalone, build_hints_index 使用）
- [x] `rbkc hints` コマンドを run.py から削除
- [x] `tools/rbkc/hints/v6.json` 生成（339 file_ids, 1179 sections, 12595 hints）
- [x] `lookup_hints_with_fallback` 優先順位修正（hints_idx 優先）
- [x] rbkc create 6 実行（341 files）
- [x] verify FAIL 190件を分析 — 根本原因 = Phase 21-D / 21-E / 21-F に分割（下記）
- [ ] Phase 21-D / 21-E / 21-F 完了後に本 Phase の GREEN を再確認
- [ ] サブエージェント品質チェック
- [ ] コミット（Phase 21-B）

**Phase 21-B verify FAIL 190件 分析結果（事実）**:

1. **md=[] 140件**: RBKC converter の `_PREAMBLE_TITLE = "概要"` 固定値が RST h1 title と不一致
   - 例: RST h1 `全体像` → hints ファイル key `全体像` / RBKC JSON section title `概要`
   - h2/h3 が無い RST では RBKC は固定値 `概要` を使うが、hints ファイル側は h1 title を key にしている
   - 影響範囲: v6=119/413(28%), v5=181/515(35%), v1.4=198/553(35%), v1.3=260/387(67%), v1.2=246/372(66%)
   - → Phase 21-D で解消

2. **file=[] 46件**: RBKC JSON の section title が hints ファイルに存在しない
   - 主に migration 系。catalog Step A の Expected Sections マッピング精度問題
   - → Phase 21-E で解消

3. **値のみ不一致 4件**: 同一 section title で hints 値が異なる
   - 例: adapters-doma-adaptor 他
   - → Phase 21-F で解消

**Phase 21-B で判明した既存 verify の重大問題（Phase 21-G で対応）**:
- QC1/QC2/QC3/QC4 (`check_content_completeness`) は実装済みだが、`run.py` verify パイプラインに配線されていない
- `verify_file` は `fmt != "xlsx"` で即 return — RST/MD では何もしない
- 設計書マトリクスの QC2=❌ が "現状 verify は QC2 を検証していない" を意味していた（「未実装」ではなく「未検証」）
- 本来 `概要` 固定値問題は QC2 (fabricated title) として直接検知されるべきだったが、配線漏れのため hints FAIL 経由で間接的に見えていた
- → Phase 21-G で解消

---

### Phase 21-D: JSON スキーマゼロベース見直し — ソース忠実な section 構造

**目的**: RBKC の根本目的（ソースに忠実な決定論的変換）に沿うよう、converter が独自ルールで作っている section title（`_PREAMBLE_TITLE = "概要"` 固定値など）を廃止し、ソースに実在する構造のみを JSON に反映する。

**問題（事実）**:
- `scripts/create/converters/rst.py:54` の `_PREAMBLE_TITLE = "概要"` が、ソースに存在しない文字列を JSON に混入させている
- h2/h3 が無い RST でも強制的に section を作り、`概要` 固定値を section title にしている
- hints ファイル（h1 title を key）と RBKC JSON（`概要` を key）の食い違いで md=[] 140件の verify FAIL が発生
- 固定値 `概要` に置き換えるのも h1 title に置き換えるのも「独自ルール」であり、RBKC の目的に反する

**あるべき JSON スキーマ**:

```json
{
  "id": "...",
  "title": "全体像",          // h1 = ファイル全体のタイトル
  "content": "本文...",        // h1 直下〜最初の h2 直前 の本文
  "sections": [                // h2/h3 が存在するときのみ要素を持つ
    {"title": "...", "content": "..."},
    ...
  ]
}
```

**原則**:
- ソースに存在しない文字列を JSON に入れない
- h1 → top-level `title` / h1 直下の本文 → top-level `content`
- h2/h3 → `sections[]` の title/content
- h2/h3 が無いファイルは `sections=[]`
- 独自の固定値 section title (`概要` 等) を作らない

**docs MD の姿**:
- `# {title}` の直下に top-level `content` をそのまま出力
- h2/h3 があれば `## {section.title}` を続けて出力
- h2/h3 が無いファイルは `##` が出ない（ダブらない、直感通り）

**hints ファイル**:
- ファイルレベル hints（h1 直下 content 用）と section レベル hints を持つ構造に変更
- h2/h3 なしファイルはファイルレベル hints のみ

**影響範囲**:
- JSON スキーマ変更（top-level `content` 追加、section 生成ロジック変更）
- converter 全 3 種（rst/md/xlsx）
- docs.py（docs MD 生成）
- hints.py / extract_hints.py / hints ファイル v6.json
- verify 全チェック（QC1–QC6, QO1, QO5, check_hints_file_consistency）
- index.py（index.toon 生成）
- nabledge-test のスコアリングロジック影響確認

**Steps:**
- [x] 調査: 現状の JSON スキーマと全 converter / verify / docs / hints ロジックの一覧化 — `.pr/00299/investigation-21d.md` 参照
- [x] 調査: nabledge-test のセクション検索ロジックへの影響確認 — 影響なし（scoring は keyword detection）
- [x] 調査: nabledge スキル本体（nabledge-6/5/1.4/1.3/1.2）のスキーマ依存確認 — scripts/workflows に影響あり。本 Phase で同時改修
- [x] 設計書作成: `tools/rbkc/docs/rbkc-json-schema-design.md` 新規作成
- [x] Plan C 確定（flat 維持 + top-level content 追加 + `概要` 固定値廃止 + v5 KC 欠損フィールド復元）— `16cfbc0d`
- [x] SE サブエージェントレビュー実施、指摘反映 — `e3450c84`
  - H1: h4 以降 `####` 深度保持 / H2: hints key は title ベース維持 / M1: xlsx `title: ""`
  - M3: `read-sections.sh` の jq バグを本 PR で 5 版同時修正（cross-version 必須）
  - L1: `index[]` は `sections[]` から決定論的生成（不変条件として明記）
  - L2: top-level content に hints 付与しない
  - xlsx のシート単位ファイル分割 + 行単位 section 化は Phase 21-C へスコープ明示
- [x] ユーザー最終承認（Plan C 設計確定版）— 2026-04-21 session 31
- [ ] verify 変更提案: top-level content を QC スコープに追加等、別途ユーザー承認プロセスで確定（rbkc.md ルール）
- [ ] TDD: rst converter — `_PREAMBLE_TITLE` 廃止、preamble を top-level content に移す（RED → 実装 → GREEN）
- [ ] TDD: md converter — 同様（title="" preamble を top-level content に）
- [ ] TDD: xlsx converter — `title: ""`、全内容を top-level content へ、`sections: []`
- [ ] TDD: docs.py — 新テンプレート（top-level content 出力、sections==[] なら `##` 出さない）
- [ ] TDD: hints.py / extract_hints.py — title ベース key 維持、`概要` 廃止対応
- [x] `read-sections.sh` 修正（5 版: v6/v5/v1.4/v1.3/v1.2）— committed `8d559b52`
- [x] TDD: verify（スキーマ変更分のみ: QC1–QC5 / QO2 に top-level content 追加）— committed `7c9e4fc0`
- [x] hints ファイル v6.json 再生成: diff 無し（既存 15 件の `概要` キーは全てソース RST に実在する h2 見出し由来で source-faithful だった）
- [ ] rbkc create 6 → verify 6 FAIL 0件確認
- [ ] サブエージェント品質チェック (Software Engineer + QA Engineer)
- [ ] コミット（スキーマ変更は破壊的変更のため複数コミットに分割）

---

### Phase 21-H: hints file 生成ロジックの再設計（セッション 33 で着手）

**背景**: Phase 21-B で生成した `tools/rbkc/hints/v6.json` は「KC の file_id から出発して section を引き当てる」ロジックで作ったが、セクションタイトル側が KC キャッシュの AI 生成タイトル（ソース非忠実）に引きずられており、Phase 21-D のソース忠実スキーマと噛み合わない。hints file 生成を**ゼロベースで見直し**、ソース RST を真実ソースとしてマッピングし直す。

**設計書**: `tools/rbkc/docs/rbkc-hints-file-design.md`（セッション 33 で新規作成・追記中）
- §1〜§9: 基本設計（R1〜R9 フォールバック）
- **付録 A: KC パイプライン全体調査結果**（catalog/cache/knowledge 3 者の対応関係、実装ソース読んで確定）
- **付録 B: 5 バージョン裏取り結果**（P1〜P4 集計、真の不整合 255 件の正体）

**裏取り結果サマリー（付録 B）**:
- 決定論的に解決: v6/v5 93%, v1.x 97% → P1+P2+P3
- 残り P4 (sid 不整合) 合計 1082 件: cache.title の source 実見出しマッチで 70-86% 救える見込み
- **真の不整合 255 件**（5 版合計）: `—` 連結 / AI 創作 / 括弧注釈 の 3 パターン

**未決事項（ユーザー判断要）**:
1. hints 保存率目標: 100% 固執か、95% 許容か
2. AI 創作 section（getting_started 系）の扱い: h1 集約 or 捨てる
3. `—` 連結分解ロジックを機械処理するか手動補正にするか

**Steps:**
- [x] KC の catalog 作成ロジック調査（step2_classify.py: h2 は `-----`, h3 は `^~+*.=`, 400行超で展開）
- [x] KC の全パイプライン調査（Phase A→B→M の流れ、catalog/cache/knowledge の対応）
- [x] 設計書付録 A（KC パイプライン調査）追記
- [x] 5 バージョン全量マッピング可能性検証（P1〜P4 集計）
- [x] P4 現物調査（cache.title の source 実見出しマッチ率計測）
- [x] 設計書付録 B（5 バージョン裏取り結果）追記
- [x] P4 分類（全 5 版）: `.pr/00299/classify_p4.py` で集計 → 設計書 §B-8 に結果追記（2026-04-21 session 34）
  - **heading match (全レベル) = 813件 (72%)** — 全レベル見出し抽出で決定論的に救える
  - dash split = 22件、paren strip = 16件
  - **fabricated = 285件 (hints loss 3241件)** — h1-only 155件 / non-h1-only 130件
- [x] R8/R9 計測（xlsx 除く）: `.pr/00299/measure_r8_r9.py` → R8 救済率は 24% (31/130 件) と低く、R9 fallback size は中央値 1K字 / p90 5〜14K字 と妥当
- [x] 設計方針ユーザー承認（2026-04-21 session 34）: 保存率 100% / h1-only + 非 h1-only ともに R9 (h1 集約) / R8 は不採用 / xlsx は Phase 21-C まで `__file__` key
- [x] §4-2 簡略化: R1〜R6 に整理（R3 全レベル照合 / R8 削除 / R9 → R6 に改番）
- [x] §5/§6 更新（受容範囲・未解決リスク）
- [x] xlsx の全バージョン hints 集計（Phase 21-C 対応の参考値）— `.pr/00299/measure_xlsx_hints.py` 実行、設計書 §B-11 に追記。v6=221, v5=1158, v1.x=0 hints
- [x] 設計書最終承認（見直し完了版）— session 35 承認 `f7a4db40`
- [x] TDD: `.pr/00299/generate_hints.py` 実装
  - [x] 全レベル見出し抽出（RST h1/h2/h3/h4、MD `#`〜`####`）
  - [x] R1〜R6 + R2' 各ルールの単体テスト（58 tests, all GREEN）
  - [x] 正規化関数の境界値テスト（NFKC、空白、括弧、NFKC+paren combo）
  - [x] smoke test: 全 5 版 ERR 0件、hints 保存率 100%
  - [x] R2' ルール追加（catalog に sid なしを R6 から分離）
  - [x] SE/QA 指摘反映（1回目）: V1/V2/V4 post-check、ever_empty 伝播、orphan/R2 ERR
  - [x] 同名見出し対応: hints file スキーマを配列 `[{title,hints}]` に変更（§6 問題 5 解決）
  - [x] SE/QA 指摘反映（2回目）: round-robin overflow→h1 reclassify as R6、_normalized_match empty 対策、RST underline 長さ strict、R1 dead-code 除去、rule priority tests、NFKC combo tests
  - [x] R6% 目標値削除（数字遊びを排除）、unmapped-v{V}.json に全 R6/R2/R2' entry を出力
- [x] 全 5 版 hints/v{V}.json 再生成（v6=296files, v5=406, v1.4=402, v1.3=263, v1.2=255）
- [x] unmapped-v{6,5,1.4,1.3,1.2}.json 出力（後から個別監査用、コミット対象）
- [ ] verify で hints FAIL 0 件確認（Phase 21-D 完了後・スキーマ対応済み後）
- [ ] コミット

---

### Phase 21-E: （旧 file=[] 46件）— Phase 21-D で同時解消される見込み

Phase 21-D で section 構造を見直すため、現状の file=[] 46件の大半（catalog Step A マッピング精度問題）は自然に解消される可能性が高い。

**Steps:**
- [ ] Phase 21-D 完了後に verify 再実行し、残存 file=[] FAIL を再調査
- [ ] 残存があれば個別対応、無ければ Phase クローズ

---

### Phase 21-F: （旧 値不一致 4件）— Phase 21-D 完了後に再調査

**Steps:**
- [ ] Phase 21-D 完了後に verify 再実行し、残存値不一致 FAIL を再調査
- [ ] 残存があれば個別対応、無ければ Phase クローズ

---

### Phase 21-G: verify パイプラインの配線漏れを解消（QC1/QC2/QC3/QC4 等）

**問題（事実）**:
- `scripts/verify/verify.py` に実装された RST/MD 用チェック (`check_content_completeness`, `check_format_purity`, `check_hints_completeness`, `check_external_urls`) が、`scripts/run.py` の verify オーケストレーションから一切呼ばれていない
- `verify_file()` は `fmt != "xlsx"` で即 return — RST/MD では完全に noop
- そのため、本来 QC2 (fabricated title) として直接検知されるべき問題（例: `概要` 固定値）が hints FAIL 経由でしか見えていなかった
- 設計書マトリクス 4章 の ❌ は「verify が検証していない」状態を正しく示していた

**このフェーズの前提**:
- Phase 21-D / 21-E / 21-F を先に完了させ、現在検知されている FAIL を全て解消してから配線する
- そうしないと、配線直後に 21-D/21-E/21-F 由来の FAIL が大量に QC2 として顕在化して切り分け困難になる

**Steps:**
- [ ] 調査: verify.py 内の各 check_* 関数と設計書マトリクスとの対応を整理（どの関数がどの QC/QL/QO に対応するか）
- [ ] 調査: run.py から呼ばれていない check_* 関数を列挙
- [ ] 配線計画をユーザーに提示・承認（どの check を RST/MD/Excel それぞれで実行するか）
- [ ] TDD: 配線後に特定の既知不正ケース（テスト fixture）で RED を確認
- [ ] run.py に check_* 関数群を配線
- [ ] サブエージェント品質チェック
- [ ] rbkc create 6 → verify 6 FAIL 0件を確認（新たに顕在化する FAIL があれば個別 Phase 化）
- [ ] 設計書 rbkc-verify-quality-design.md のマトリクスを ❌→✅ に更新（配線済みの項目のみ）
- [ ] コミット

---

### Phase 21-C: リリースノート・セキュリティ対応表の粒度が粗い

**問題**: 現状は全シート×全行を1セクションに連結 → 毎回全行ロード、検索で使えない。
行単位（変更1件=1セクション）にすれば個別レコードとして検索可能になる。

**Steps:**
- [ ] 全容把握: v6リリースノート・セキュリティExcelのシート構造・行構造を調査しセクション分割設計を確定
- [ ] ユーザーに設計案提示・承認
- [ ] xlsx_releasenote TDD: 行単位セクション分割テスト（RED → GREEN）
- [ ] xlsx_security TDD: 行単位セクション分割テスト（RED → GREEN）
- [ ] verify 更新: 新粒度に対応したチェック
- [ ] rbkc create 6 → verify 6 FAIL 0件確認
- [ ] コミット

---

### Phase 18: 統合検証 — v6 完了

**前提**: Phase V4 完了 ✅

**Steps:**
- [ ] nabledge-test v6 実行 — ベースライン比で劣化なし確認
- [ ] 問題があればユーザー報告

---

### Phase 19: 統合検証 — v5

**前提**: Phase 18 完了後

**Steps:**
- [ ] `bash rbkc.sh create 5` → `bash rbkc.sh verify 5` — FAIL 0件
  - FAIL が出た場合: 分析 → ユーザー報告 → 承認後修正 → 再 verify
- [ ] nabledge-test v5 — 劣化なし確認
- [ ] コミット

---

### Phase 20: 統合検証 — v1.4 / v1.3 / v1.2

**前提**: Phase 19 完了後

**Steps:**
- [ ] `bash rbkc.sh create 1.4` → `bash rbkc.sh verify 1.4` — FAIL 0件
- [ ] `bash rbkc.sh create 1.3` → `bash rbkc.sh verify 1.3` — FAIL 0件
- [ ] `bash rbkc.sh create 1.2` → `bash rbkc.sh verify 1.2` — FAIL 0件
  - 各バージョンで FAIL が出た場合: 分析 → 報告 → 承認 → 修正 → 再 verify
- [ ] nabledge-test v1.4 / v1.3 / v1.2 — 劣化なし確認
- [ ] コミット（全3バージョン）

---

## Done

- [x] Phase V-skip: verify() FAIL on missing JSON/docs MD — committed `86dd660e`
  - run.py: 2 silent skip violations fixed (JSON missing, docs MD missing)
  - tests/ut/test_run.py: 4 unit tests added (TDD)
- [x] Phase V-hints: KC-format files deleted from nabledge-6 — committed `c92accc4`
  - 339 KC-format knowledge JSON + 339 KC docs MD deleted
- [x] Phase V2-4-post: converter fixes (QC1, QL1) + tests — committed `6ce09683`
  - xlsx_releasenote: all cells from all sheets, row-major (QC1 fix)
  - xlsx_security: all cells from all sheets, single flat section (QC2 fix)
  - rst: pre-resolve :ref:`label` via label_map (QL1 fix)
  - run.py: label_map built and passed to _convert_and_write
  - labels.py: overline-style RST headings support in build_label_map
  - tests: e2e restructured (QC1/QC2 verify), overline unit tests
  - image fix: _read_options() added, image directive uses it (QL1 fix) — `21ca2783`
- [x] Phase V4: rbkc create 6 + verify 6 FAIL 0件 — committed `dbfc0582`
  - 341 knowledge JSON files, 341 docs MD files generated
  - rbkc verify 6: All files verified OK

- [x] Phase V0: hints carry-over 実装 — committed `d155c92e`
  - `load_existing_hints(output_dir)` + `lookup_hints_with_fallback()` を run.py に追加
  - `create()` が rmtree する前に既存 RBKC 形式ファイルから hints を保存し新規生成時に引き継ぐ
  - `update()` も同様に carry-over 対応
  - テスト: 17件追加（TestLoadExistingHints）

- [x] Phase V1: 旧 verify 削除・スタブ化 — committed `2727facc`
  - `verify.py` を空スタブに置き換え（run.py の import は維持）
  - `test_verify.py` 削除
  - `test_cli.py` の verify テスト2件を skip マーク
  - pytest: 254 passed, 23 skipped

- [x] Phase V2-1/V2-2/V2-3: QO5 / QC5 / QC6 verify 実装 — committed `a0c7abf1`
  - QO5: docs MD content 完全一致（assets/ リンク含むセクションはスキップ）
  - QC5: RST/MD 形式純粋性（Java ジェネリクス false positive 排除済み）
  - QC6: hints 完全性（前回生成 hints の欠落検出）
  - テスト 34 本追加（計 288 passed, 23 skipped）

- [x] Phase V2: verify 実装計画確定
  - サブフェーズ V2-1〜V2-9 を設計（QA/SE エキスパートレビュー実施）
  - delete algorithm の方針確定: 先頭から順に削除するだけ→重複文字列問題なし
  - 計画は In Progress の Phase V3 に記載済み

- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー完了（旧 Phase 17-B/17-C/17-A の verify コードは新設計で作り直し）
  - `tools/rbkc/docs/rbkc-verify-quality-design.md` を新規作成（旧 requirement-and-approach.md を全面リファクタリング）
  - QA エキスパートレビュー2回実施、指摘事項をすべて反映
  - 最終状態: QC1–QC6 / QL1–QL2 / QO1–QO5 の全観点定義済み
  - committed `d020efd2` 〜 `2464a55c`

- [x] Phase 1: KC cache → hints mapping (`scripts/hints.py`) — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — committed `5913ff6e`, `1b62c4c4`, `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
- [x] Gap fill: Phase 2 test修正 + Phase 1/3 E2Eテスト追加 — committed `010d0c2f`
- [x] Phase 4: Cross-reference resolution + asset copying — committed `9336f900`, `87654126`
- [x] Phase 5: MD converter — committed `232df686`
- [x] Phase 6: Excel converters — committed `edce71eb`
- [x] Phase 7: Index + browsable docs generation — committed `dc019759`
- [x] Phase 8: CLI + create/update/delete/verify operations — committed `5baf7a6d`
- [x] Phase 9: v1.x固有ディレクティブ対応 — committed `bc632d0f`
- [x] Phase 10: コンバータ修正 (10-1〜10-6) — committed `54fe3ef8`, `d5a6961d`, `cd856500`, `d2303716`, `7eac70f6`, `10b239b1`
- [x] Phase 11: verify 完全チェック化 — committed `6c664a59` ※Phase 12で書き直し済み
- [x] Phase 12: verify 完全書き直し (B1/B2/B3修正) — committed `1eff2740`
- [x] Phase 13: create pipeline 完全修正 (B4修正) — committed `e85488cb`
- [x] Phase 14: classify 出力パス衝突修正 (B5修正) — committed `b6a4a630`
- [x] Phase 15: converter/verify URL バグ修正 (B6/B7修正) — committed `63ac0ec9`
- [x] Phase 16: toctree-only index.rst token coverage 修正 (B8修正) — committed `37d6e547`
- [x] docs.py: assets/ リンクを docs MD の位置から相対解決 — committed `008e8420`
  - → verify FAIL: 351件 → 50件（docs MD assets link 301件解消）
- [x] Rules整理: development.md追加、work-log/rbkc/pr.md更新 — committed `aa08f489`
- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー完了（旧 Phase 17-B/17-C/17-A の verify コードは新設計で作り直し）
  - `tools/rbkc/docs/rbkc-verify-quality-design.md` を新規作成（旧 requirement-and-approach.md を全面リファクタリング）
  - QA エキスパートレビュー2回実施、指摘事項をすべて反映
  - 最終状態: QC1–QC6 / QL1–QL2 / QO1–QO5 の全観点定義済み
  - **既存 verify.py（Phase 11〜17-A で実装済み）は Phase V1 で削除・作り直しへ**
  - committed `d020efd2` 〜 `2464a55c`
