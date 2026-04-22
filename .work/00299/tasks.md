# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-22 (session 39 — Step K-3 complete)

全フェーズ TDD（verify が質問ゲートのため順序に注意）:
- **verify 追加時**: verify テスト作成 → RED確認 → verify チェック実装 → GREEN確認 → RBKC 実装 → verify GREEN確認 → サブエージェント品質チェック
- **CLI 追加時**: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする

---

## 方針転換（session 38 合意）

**RBKC は "ルールベースで content のみ生成" に責務を限定する。**

**背景**:
- hints は機械抽出しても本文検索で同等にヒットするため価値が低い（本文にない別名・略語・類義語こそ価値、それは AI でしか取れない）
- KC catalog は h4 まで section 化、RBKC converter は h2/h3 のみ section 化 → 粒度不整合に起因する mismatch が Phase 21-D 以降ずっと続いている
- hints を RBKC から外すことで、粒度不整合問題は本 PR から消える

**本 PR で扱うこと**:
- RBKC は JSON / docs MD / 索引を content（タイトル + 本文）のみで生成
- JSON の `hints` フィールドは出力しない（空でも出さない）
- docs MD の `<details><summary>keywords</summary>` ブロックは出さない
- verify の hints 関連チェック（QC6 完全一致・`_parse_docs_md_hints` 等）は削除

**本 PR で扱わないこと（別 Issue 管轄）**:
- AI 生成 hints (`hints/v*.json`) の人間レビュー・マージ
- 別 Issue に以下を資産として渡す:
  - 現状の `hints/v6.json`（他バージョン含む）
  - `.work/00299/generate_hints.py` と周辺スクリプト
  - KC catalog との粒度差の背景

---

## 現状サマリー（session 38 方針転換時点）

`bash rbkc.sh verify 6` → **FAIL 合計 139件**（全て hints 関連、Phase 21-K 完了後に自動解消予定）

| カテゴリ | 件数 | 受け皿 Phase |
|---|---|---|
| hints `file entry not matched by any knowledge section` | 74 | Phase 21-K（削除で解消） |
| hints `docs MD hints differ from hints file` | 65 | Phase 21-K（削除で解消） |

---

## In Progress

### Phase 21-G-1: verify 配線漏れ解消（配線のみ・修正は 21-G-2 以降）

**目的**: verify_file() に RST/MD 用 check を配線。FAIL 修正は後続フェーズに分割。

**実行結果 (2026-04-22)**:
- 配線実装・unit tests 200 PASS
- `rbkc verify 6` で 23,989 FAIL / 299 ファイル表面化
- 根本原因別内訳（調査済み）:

| パターン | 件数 | 受け皿 Phase |
|---|---|---|
| RST grid-table 変換不整合 (`==== ==== ` / MD table 行残留) | ~3,854 + OTHER 大半 | 21-G-2 |
| RST `:role:` 未変換 | 2,277 | 21-G-3 |
| RST `` ``double backtick`` `` | 1,094 | 21-G-4 |
| RST `\\ ` backslash-space エスケープ | 593 | 21-G-5 |
| RST `.. directive::` 残留 | 124 | 21-G-6 |
| QC4 配置ミス | 1,640 | 21-G-7 |
| QL2 / QC3 | 124 | 21-G-8 |
| その他 OTHER (大部分は grid-table 巻き込み) | ~13,787 | 21-G-2 で大半解消見込み |

**Steps:**
- [x] TDD: 配線テスト追加 (test_verify.py TestVerifyFileExcelQC に新規2件)
- [x] `verify_file()` に RST/MD 分岐追加、check_content_completeness / check_format_purity / check_external_urls を呼び出し
- [x] unit tests 200 PASS
- [x] `rbkc verify 6` 実行、FAIL 件数把握、根本原因別に分類
- [ ] コミット・プッシュ（配線のみ）

---

### Phase 21-G-2: RST grid-table 変換修正

**仮説**: `====  ====` 形式の grid-table が converter で正しく MD table に変換されない、または本文と混在して取り込まれる。QC1 (RST 本文欠落) と QC2 (JSON に MD table 残留) の両方で多発。

**Steps:**
- [ ] 典型ファイル `tag.rst` / `tag_reference.rst` / grid-table 多用テスト framework 系で再現ケース抽出
- [ ] RST converter の grid-table ハンドラを調査、仕様（reStructuredText grid table）と突き合わせ
- [ ] TDD: 最小再現テスト追加（RED）
- [ ] converter 修正（GREEN）
- [ ] `rbkc verify 6` で FAIL 件数減少を確認
- [ ] サブエージェント品質チェック
- [ ] コミット・プッシュ

---

### Phase 21-G-3: RST role (`:ref:` `:doc:` 等) 未変換

**Steps:**
- [ ] role 種別ごとの出現パターンと期待変換形式を調査
- [ ] TDD: 各 role 型の再現テスト
- [ ] converter 修正
- [ ] verify 減少確認
- [ ] コミット

---

### Phase 21-G-4: RST double backtick (`` ``text`` ` 形式) 処理

**Steps:**
- [ ] `` ``...`` `` → MD `` `...` `` の変換が不完全な箇所を特定
- [ ] TDD → 修正 → verify 確認 → コミット

---

### Phase 21-G-5: RST `\\ ` backslash-space エスケープ処理

**Steps:**
- [ ] RST inline markup の `\\ ` 分離記法を content から剥がす
- [ ] TDD → 修正 → verify 確認 → コミット

---

### Phase 21-G-6: RST `.. directive::` 残留

**Steps:**
- [ ] 残留している directive 種別を列挙
- [ ] converter の directive 分岐を調査、未ハンドル分を追加または除外
- [ ] TDD → 修正 → verify 確認 → コミット

---

### Phase 21-G-7: QC4 配置ミス (1,640 件)

**Steps:**
- [ ] 配置逆行の典型ケース抽出
- [ ] 原因調査（多くは 21-G-2〜21-G-6 の副作用で解消する可能性あり）
- [ ] 残存分のみ別対応

---

### Phase 21-G-8: QL2 / QC3 残件

**Steps:**
- [ ] QL2 62件: ソース外部 URL が JSON に欠落している理由を調査
- [ ] QC3 62件: 重複の典型ケース抽出
- [ ] 修正 → verify 確認 → コミット

---

### Phase 21-G-9: 設計書マトリクス更新

**Steps:**
- [ ] 21-G-1〜21-G-8 完了後、`rbkc-verify-quality-design.md` 4章マトリクスの ❌→✅ 更新
- [ ] コミット

---

### Phase 21-K: hints スコープアウト — 設計書とコードを "content のみ" に整える (完了)

**目的**: 後続タスク（統合検証など）で「ここは hints あるんだっけ？」と判断に迷わないように、設計書とコードから hints 関連を削除して基盤を整える。hints 資産は別 Issue 用にブランチ外の形で保全する。

#### Step K-1: 別 Issue 用の資産棚卸し（削除前に固定）

- [x] `hints/v6.json` / `v5.json` / `v1.4.json` / `v1.3.json` / `v1.2.json` の現状を別 Issue 用資料として `.work/00299/handoff-hints/` にコピー
- [x] `.work/00299/generate_hints.py` / `extract_hints.py` も同ディレクトリに保全
- [x] 別 Issue 用の引き継ぎメモ `.work/00299/handoff-hints/README.md` 作成（背景・粒度差問題・AI hints の価値判断の要約）
- [x] コミット・プッシュ（「hints 別 Issue 引き継ぎ資産を保全」）— committed `28fdef842`

#### Step K-2: 設計書を "content のみ" に更新

- [x] `tools/rbkc/docs/rbkc-verify-quality-design.md` — QC6 / hints 関連検査項目を削除、マトリクスも hints 行削除
- [x] `tools/rbkc/docs/rbkc-json-schema-design.md` — `hints` フィールドの記述を削除（top-level / section 両方）
- [x] `.claude/rules/rbkc.md` — Hints files セクション（`rbkc hints` / `hints/v{V}.json` / 三者一致ルール）を削除。「RBKC は content のみ扱う、hints は別 Issue」と明記
- [x] コミット・プッシュ（「docs: scope RBKC to content-only」）— committed `b21197d73`

#### Step K-3: コードから hints を削除 + processing_patterns バグ修正

**session 39 で発覚した追加問題（必ず本 Step で同時修正）**:
- `tools/rbkc/scripts/create/index.py:91` が `_collect_hints(data)` を呼び、hints 語彙を `processing_patterns` 列に詰め込んでいる（本来の意味論違反）
- 監査結果（v6 index.toon 313 entries）:
  - `type=processing-pattern` 79件: `pp != category`（本来 `pp == category` が正、例: `pp=nablarch-batch`）
  - `type!=processing-pattern` 186件: `pp` に hints 語彙が詰まっている（本来空文字）
- v1.2〜v5 は KC 出力のまま正しい意味論。汚染されているのは v6 のみ
- KC の挙動 (`phase_f_finalize.py:303-308`): `type=processing-pattern` なら `category` を使う、それ以外は空
- RBKC の mapping (`tools/rbkc/mappings/v{V}.json`) は既に type/category を持つので RBKC 自己完結で機械生成可能（AI 不要、別ファイル不要）

**修正方針（ユーザー承認済み: 案 A）**:
- `processing_patterns` は mapping 由来の type/category から機械生成（KC と同じ意味論）
- 追加ファイル生成は不要。`index.py` のロジック差し替えだけで済む
- index.toon スキーマ `{title,type,category,processing_patterns,path}` は維持（skill 5 版の `_file-search.md` Axis 3 も維持）

**Steps:**
- [x] `tools/rbkc/scripts/create/index.py` — `_collect_hints(data)` 呼び出しを削除し、`file_infos` を受け取って `fi.type == "processing-pattern"` なら `fi.category`、それ以外は空文字を使うロジックに置換
- [x] `tools/rbkc/scripts/create/hints.py` — ファイル削除
- [x] `tools/rbkc/scripts/run.py` — hints 関連を全削除、generate_index() 呼び出しを新シグネチャに更新
- [x] `tools/rbkc/scripts/create/docs.py` — `<details>keywords</summary>` ブロック出力を削除（2箇所）
- [x] `tools/rbkc/scripts/verify/verify.py` — `check_hints_completeness` / `_parse_docs_md_hints` / `check_hints_file_consistency` / `_KEYWORDS_RE` / `FILE_SENTINEL` import を削除
- [x] `tools/rbkc/scripts/common/constants.py` — `FILE_SENTINEL` のみの定義だったためファイル削除
- [x] `tools/rbkc/hints/` ディレクトリ削除
- [x] converters は元々 hints 参照なしを確認済み
- [x] `tools/rbkc/rbkc.sh` は hints サブコマンドなしを確認済み
- [x] `test_hints.py` 削除、`test_run.py` / `test_verify.py` / `test_docs.py` の hints 関連テスト削除。`test_index.py` 新規作成（TestProcessingPatternsSemantics / TestNoKnowledgeContentExcluded / TestMissingJsonSkipped / TestTitleCommaEscape / TestGenerateIndexEdgeCases）
- [x] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` — "All files verified OK" (FAIL 0件)、index.toon 監査: pp 79件すべて `pp == category`、他 239件すべて `pp == ''`、違反 0件
- [x] サブエージェント品質チェック (SE 4.5/5 / QA 4.5/5) — 全指摘（Medium 2, Low 3）を同一コミットで修正済み
- [x] コミット・プッシュ — committed `f7cff23a1` (feat) + `983ae8301` (docs)

#### Step K-4: 別 Issue 起票

- [x] GitHub Issue #309 起票 — AI-curated hints のフォローアップ
- [x] `.work/00299/handoff-hints/` へのリンクと背景要約を記載

---

## Not Started

### Phase 21-G: verify パイプラインの配線漏れを解消（QC1/QC2/QC3/QC4 等）

**問題（事実）**:
- `scripts/verify/verify.py` に実装された RST/MD 用チェック (`check_content_completeness`, `check_format_purity`, `check_hints_completeness`, `check_external_urls`) が、`scripts/run.py` の verify オーケストレーションから一切呼ばれていない
- `verify_file()` は `fmt != "xlsx"` で即 return — RST/MD では完全に noop
- 設計書マトリクス 4章 の ❌ は「verify が検証していない」状態を正しく示していた

**このフェーズの前提**:
- Phase 21-K（hints スコープアウト）を先に完了させ、現在検知されている FAIL を全て解消してから配線する
- そうしないと、配線直後に既存 FAIL が大量に QC2 として顕在化して切り分け困難になる

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

**前提**: Phase 21-K / 21-G 完了後

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

- [x] Phase 21-A: docs/README.md 未生成 — committed `c238dc8f`
- [x] Phase 21-B: hints 永続化と完全一致チェック — verify check 実装 / `build_hints_index` file_id 正規化 / `catalog_index` last-wins バグ修正 / `extract_hints.py` 作成 / v6.json 初版生成。残 FAIL の分析は 21-D/21-I/21-J に分割
- [x] Phase 21-D: JSON スキーマゼロベース見直し（ソース忠実）— session 31〜37 で `_PREAMBLE_TITLE` 廃止、top-level content + hints 導入、converter/docs/index/verify 同時改修、read-sections.sh 5版同時修正 — commits `603c5ade` / `23bb7e5f` / `4b6531fe` / `49e467e2` / `3154264e`
- [x] Phase 21-E（旧 file=[] 46件）: Phase 21-D で大半解消。残存は Phase 21-J に統合してクローズ
- [x] Phase 21-F（旧値不一致 4件）: Phase 21-D で解消。Phase 21-J に統合してクローズ
- [x] Phase 21-H: hints file 生成ロジックの再設計（R1〜R6 ルールで 5 版 hints/v{V}.json を ゼロベース再生成、同名見出し対応の配列スキーマ化）— commits `9ffefa08` / `5adf4404` / `60b16f98` / `ca7a924f` / `f7a4db40` / `fbd2b52f` / `8ed9aa0c` / `c286de77` / `83031d95` / `d015c03e` / `80a3ed48`（verify GREEN 確認は 21-J にバトン）
- [x] Phase 21-I: QL1 回帰 314件解消 — `_json_text()` に top-level content 追加（設計書 `rbkc-verify-quality-design.md:170` 通りに修正、false-positive fix）。TDD: RED 3件 → GREEN、regression/MD top-level/`_json_text()` 直接テスト 5件追加（合計244 PASS）。SE 5/5 / QA 5/5（追試対応後）
- [x] Phase 21-J: hints mismatch 139件分析 — 根本原因は KC catalog（h4 まで section 化）と RBKC converter（h2/h3 のみ section）の粒度不整合。ユーザー判断により方針転換（session 38）し、hints は RBKC 本 PR から外して別 Issue 管轄に。受け皿は Phase 21-K

- [x] Phase V-skip: verify() FAIL on missing JSON/docs MD — committed `86dd660e`
- [x] Phase V-hints: KC-format files deleted from nabledge-6 — committed `c92accc4`
- [x] Phase V2-4-post: converter fixes (QC1, QL1) + tests — committed `6ce09683` / `21ca2783`
- [x] Phase V4: rbkc create 6 + verify 6 FAIL 0件 — committed `dbfc0582`
- [x] Phase V0: hints carry-over 実装 — committed `d155c92e`
- [x] Phase V1: 旧 verify 削除・スタブ化 — committed `2727facc`
- [x] Phase V2-1/V2-2/V2-3: QO5 / QC5 / QC6 verify 実装 — committed `a0c7abf1`
- [x] Phase V2: verify 実装計画確定
- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー — commits `d020efd2`〜`2464a55c`
- [x] Phase 1: KC cache → hints mapping — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — commits `5913ff6e` / `1b62c4c4` / `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
- [x] Gap fill: Phase 2 test修正 + Phase 1/3 E2Eテスト追加 — committed `010d0c2f`
- [x] Phase 4: Cross-reference resolution + asset copying — commits `9336f900` / `87654126`
- [x] Phase 5: MD converter — committed `232df686`
- [x] Phase 6: Excel converters — committed `edce71eb`
- [x] Phase 7: Index + browsable docs generation — committed `dc019759`
- [x] Phase 8: CLI + create/update/delete/verify operations — committed `5baf7a6d`
- [x] Phase 9: v1.x固有ディレクティブ対応 — committed `bc632d0f`
- [x] Phase 10: コンバータ修正 (10-1〜10-6) — commits `54fe3ef8` / `d5a6961d` / `cd856500` / `d2303716` / `7eac70f6` / `10b239b1`
- [x] Phase 11: verify 完全チェック化 — committed `6c664a59`（Phase 12 で書き直し済み）
- [x] Phase 12: verify 完全書き直し — committed `1eff2740`
- [x] Phase 13: create pipeline 完全修正 — committed `e85488cb`
- [x] Phase 14: classify 出力パス衝突修正 — committed `b6a4a630`
- [x] Phase 15: converter/verify URL バグ修正 — committed `63ac0ec9`
- [x] Phase 16: toctree-only index.rst token coverage 修正 — committed `37d6e547`
- [x] docs.py: assets/ リンクを docs MD の位置から相対解決 — committed `008e8420`
- [x] Rules整理: development.md追加、work-log/rbkc/pr.md更新 — committed `aa08f489`
