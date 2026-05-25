# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-25 (session 8)

## Rules

- タスクリスト通りに作業する（順序を勝手に変えない）
- ユーザー確認タスク（`[BLOCKED:]`）は飛ばさない
- 各ステップ完了・中断のたびにタスクリストを更新してコミット・プッシュする（いつでも中断・再開できる状態を保つ）

## In Progress

## Not Started

### ~~C-3. 他バージョン展開・差分チェック＋動作確認~~

C-2完了・承認済み。v6が正解、他バージョンはv6に合わせる（バージョン固有差分を除く）。

**チェック方針**:
1. `git diff main...HEAD --name-only | grep "^\.claude/"` で PR変更ファイルを全列挙
2. v6に関するファイルを洗い出し、他バージョンに対応するファイルを特定
3. v6ファイルをベースに `sed "s/nabledge-6/$v/g"` で期待値を生成し、実ファイルと diff
4. バージョン依存差分（許容）とそれ以外（要修正）を区別してチェックをつける

**許容差分（バージョン依存）**:
- ファイルパス・バージョン名の置換: `nabledge-6` → `nabledge-5` / `nabledge-1.4` 等
- `workflows/qa.md` 処理タイプリスト: バージョンごとに処理方式が異なる（`.claude/rules/nabledge-skill.md` で明文化）
- `workflows/semantic-search.md` カテゴリリスト: 各バージョンのknowledgeに存在するカテゴリのみ（例: `about/migration` は v6 のみ、`component/adapters` は v5/v6 のみ）
- `v5/template-guide.md` のURL: `LATEST`（v6）vs `5-LATEST`（v5）— mainから既存の差分
- `v1.4/v1.3/v1.2/template-guide.md`: official_docs説明変更＋サンプル削除（公式ドキュメント非公開のため）— バージョン依存差分

**ステップ1: 差分チェック＋展開（session 4で実施）**

`.claude/commands/` の変更ファイル:
- [x] `n6.md` が正解 — keyword-search/semantic-search examples追加済み
- [ ] `n5.md` / `n1.4.md` / `n1.3.md` / `n1.2.md` — keyword-search/semantic-search examples 未追加 → 修正必要

`.claude/skills/nabledge-6/` の変更ファイル vs 他バージョン:
- [x] `SKILL.md` — バージョン名差分のみ ✅
- [x] `knowledge/index.md` — バージョンごとのコンテンツ差分（許容）✅
- [x] `knowledge/index.toon` — v6固有ファイル（v5にも存在するが今回スコープ外）✅
- [x] `scripts/full-text-search.sh` — 全バージョンで削除済み ✅
- [x] `scripts/keyword-search.sh` — 全バージョン一致 ✅
- [x] `scripts/prefill-template.sh` — 修正済み（session 4: テンプレートパス `assets/` → `workflows/code-analysis/`）✅
- [x] `scripts/read-sections.sh` — 修正済み（session 4: jqフィルタをv6版に更新）✅
- [x] `workflows/_knowledge-search.md` 他4ファイル — 全バージョンで削除済み ✅
- [ ] `workflows/code-analysis.md` — v5/v1.4/v1.3/v1.2 が未更新（full-text-search+_section-judgement → keyword-search workflow に変更が未展開）→ 修正必要
- [x] `workflows/code-analysis/template.md` → `assets/code-analysis-template.md` — バージョン名差分のみ ✅
- [x] `workflows/code-analysis/template-guide.md` → `assets/code-analysis-template-guide.md` — URL差分は既存（許容）✅
- [x] `workflows/code-analysis/template-examples.md` → `assets/code-analysis-template-examples.md` — バージョン名・URL差分は既存（許容）✅
- [x] `workflows/keyword-search.md` — 全バージョン一致 ✅
- [x] `workflows/qa.md` — 処理タイプリストのみ差分（許容）、「その他」の番号はリスト数に対応 ✅
- [x] `workflows/semantic-search.md` — カテゴリ差分は各バージョンのknowledge構成による（許容）✅

**残作業（未チェック項目の修正）**:
- [x] `workflows/code-analysis.md` を v5/v1.4/v1.3/v1.2 に展開 — `f1c511976`
- [x] `.claude/commands/n5.md` / `n1.4.md` / `n1.3.md` / `n1.2.md` に keyword-search/semantic-search examples を追加 — `f1c511976`
- [x] `scripts/read-sections.sh` / `scripts/prefill-template.sh` を v5/v1.4/v1.3/v1.2 に展開 — `5ad00ee24`
- [x] 修正後、diff で全チェック項目が ✅ になることを確認 — `62aec4f90`〜`f89c2eed8`（session 6で追加修正）
- [x] コミット・プッシュ

**ステップ2追加バグ修正（session 7: v1.4動作確認で発見）**:
- [x] `prefill-template.sh` 出力先ディレクトリがcwd依存だった → `$PROJECT_ROOT` 使用に修正 — `01e3c69f1`（全バージョン）
- [x] `prefill-template.sh` find結果に絶対パスが混入 → `$PROJECT_ROOT` プレフィックス除去に修正 — `d3cd0438e`（全バージョン）

**ステップ2: 動作確認（C-2b と同じ5フロー × 4バージョン）**
- [x] v5: QA（ヒアリングなし）/ QA（ヒアリングあり）/ keyword-search / semantic-search / code-analysis
- [x] v1.4: 同上（code-analysisはImportZipCodeFileActionで確認済み — `d3cd0438e`後、全出力正常）
- [x] v1.3: 同上
- [x] v1.2: 同上
  - 各フローの受入条件は C-2b と同じ（ヒアリング発生・回答・ナレッジ引用等）
  - ヒアリングが発生した場合は適切なデフォルト回答を使用してよい

- [x] ユーザーに差分チェック結果（全差分が許容範囲）を報告し承認を得る — 承認済み（session 8）

### ~~B-7. nabledge-test削除~~

B-6完了後。新ベンチマーク基盤に完全移行。

- [x] `test-setup.sh` の `_scenario_field` 削除、質問・キーワードをハードコード — `157d1ee01`
- [x] `.claude/skills/nabledge-test/` / `.claude/agents/nabledge-test-runner.md` 削除 — `157d1ee01`
- [x] `.claude/settings.json` から `Skill(nabledge-test)` 行を削除 — `f9d0dfef6`
- [x] `.claude/rules/` からnabledge-test固有記述を削除 — `f9d0dfef6`
- [x] `python3 -m pytest tools/ -x` で全テストPASS — rbkc: 587 PASS, benchmark: 159 PASS, metrics: 8 PASS

### ~~B-8-pre. マージ前静的確認~~

B-7完了後、PRマージ前に実施。「マージしたら壊れる」を事前に潰す。

**確認1: GHA sync manifest**
- [x] `.github/workflows/sync-to-nabledge/sync-manifest.txt` を読み、今回追加・変更したスキルファイルが含まれているか確認
  - SKILL.md/workflows/scripts/knowledge/commands/prompts — 全てmanifestに含まれている ✅

**確認2: セットアップスクリプト**
- [x] `tools/setup/setup-cc.sh` / `tools/setup/setup-ghc.sh` を読み、今回削除・移動したファイルへの参照がないか確認
  - 削除・移動ファイルへの参照ゼロ ✅

**確認3: test-setup.sh**
- [x] B-7で削除したファイルへの参照がtest-setup.shに残っていないか確認
  - `grep -n "nabledge-test" tools/tests/test-setup.sh` → OUTPUT_DIR/.tmp参照のみ（スキル参照ゼロ）✅

### B-8. test-setup.sh 動作確認

B-7完了後、mainマージ → nablarch/nabledge:develop自動sync後に実施。
**前提**: mainマージ済みであること（test-setup.sh は nablarch/nabledge:develop からスキルを取得するため）

**確認対象**:
- `test-setup.sh` は GUIDE-CC.md / GUIDE-GHC.md からsetupスクリプトURLを取得
- setupスクリプトでスキルをインストール（静的チェック: SKILL.md / knowledge/ / docs/ / コマンドファイル）
- 動的チェック: `claude -p` でSKILL.mdが読まれるか（B-7で `_scenario_field` を削除してハードコードに変更済み）
- 全バージョン（v6/v5/v1.4/v1.3/v1.2/upgrade）× CC/GHC

**ステップ**:
- [ ] v6のみ先行確認:
  ```bash
  cd .tmp/nabledge-test-b8 && bash /path/to/tools/tests/test-setup.sh v6
  ```
  - 受入条件: 終了コード0、静的チェックOK、動的チェックOK（SKILL.md read）
- [ ] 問題があればB-7の修正内容を確認・修正してコミット
- [ ] 全バージョン確認:
  ```bash
  bash tools/tests/test-setup.sh
  ```
  - 受入条件: 終了コード0、全環境 `[OK]` のみ

## Done

- [x] B-8-pre. マージ前静的確認 — 全3確認PASS（session 8）
- [x] B-7. nabledge-test削除 — `157d1ee01`, `f9d0dfef6`（全テストPASS確認済み）
- [x] C-3. 他バージョン展開・差分チェック＋動作確認 — 全差分許容範囲、全バージョン全5フロー動作確認済み・ユーザー承認済み（2026-05-25 session 8）
- [x] C-2b. v6 動作確認（4フロー全PASS）— 全フローPASS確認・ユーザー承認済み（2026-05-25）
  - QA（ヒアリングなし）✅ / QA（ヒアリングあり）✅ / keyword-search ✅ / semantic-search ✅ / code-analysis ✅
- [x] GHC prompt英語化（n6/n5/n1.4/n1.3/n1.2）— `5622e3c79`
- [x] C-2. 設計書再作成（実装ベース）— `413728c22`〜`f39aa2947`、ユーザー承認済み（2026-05-25）
- [x] サブエージェント廃止・AskUserQuestion削除（n6/n5/n1.4/n1.3/n1.2 CC+GHC、code-analysis.md 全バージョン）— `4695a69f9`, `e6d0a1a13`

- [x] B-6. バージョン展開（v5/v1.4/v1.3/v1.2 keyword+semantic search 展開）— `c0dd1657f`
- [x] B-5. 改善サイクル — スキップ（v1-new-search 精度95.6%/幻覚88.9%、qa-05は揺らぎ扱い、ユーザー承認済み）
- [x] B-X. terms.json廃止 → 全文スキャン（impact-09: recall 0→1、26テストGREEN、QO5削除）— `99f8f3bfb`〜`feabbeb22`
- [x] ベンチマーク ステップ3〜6（妥当性評価・集計・根本原因調査・qa-05揺らぎ判定）— `8d1252b39`, qa-05対処不要ユーザー承認
- [x] B-4. 新スキルE2Eベンチマーク（run-1/2/3 実行完了） — run-1: `1e44a77d7`, run-2/3: `6f8dd0872`
- [x] B-4-1-fix. read-sections.sh sections:[] 対応（9テスト追加・全バージョン修正）— `11c9160ec`
- [x] B-4-1. run-1 再測定（B-4-1-fix後）— Claims 96.7%, Hal 93.3%, $27.56 — `1e44a77d7`, `66f936c6e`
- [x] B-4-pre. ユーザープロンプトレビュー — qa.md 大幅改修（Step 1-2-5）、PEレビュー 0 Findings — `86b319939`〜`2d2cfe3fa`
- [x] B-4-1-B. purpose ヒアリング追加（goal廃止・purpose7択追加・PEレビュー0 Findings）— `dbad4cf64`
- [x] B-4-1-C. evaluate.py 幻覚検証ロジック修正（search_sections を sections_text に追加、TDD 5テスト追加）— `563d8b4aa`
- [x] B-4-1. run-1 安定化（エラーゼロまで）— --allowedTools パターン誤りによりread-sections.sh未実行と判明。結果削除。
- [x] B-0-4. 設計書適合確認・SEエキスパートレビュー・PRレビュー — OK `2026-05-19`
- [x] ワークフローMDリファクタリング（B-0-4-H）— `76268a9d3`, `a3b523638`, `cf026e442`, `119ff53ce`, `189b51402`
- [x] B-0-4-A〜G 実装修正 — `890683762`〜`031b830c7`
- [x] B-0-3. code-analysis から semantic-search 削除 + keyword-search設計書整合 + PEレビュー3 Findings修正 — `c40433348`, `3362515ea`
- [x] B-0-2. keyword-search.md を設計書通りに修正（PEレビュー 0 Findings）— `6b3a9134a`
- [x] B-0-1. 設計書・SKILL.md・n6.md 最新化（PEレビュー 0 Findings）— `2ba8abd93`, `1a4b9902e`（qa.md keyword-search削除）
- [x] B-0-1（前半）. 設計書適合確認・assets廃止・index.toon削除 — `8d53739f6`, `0ebfb886b`, `2a96bb538`, `0c3605da7`, `b42ffd2d2`
- [x] PR #346 レビュー対応（BENCHMARKマーカー削除 `3f4b4d8d4`, QO4/QO5 ✅ `80c589c29`）
- [x] B-4-2. run_e2e.py エラー時診断情報の確実な保存（TDD, QAレビュー 0 Findings）— `5eab4f1dd`, `d9af9bd2c`
- [x] qa.md/hearing.md 修正（マーカー出力をStep 7に一元化、スキーマ不整合修正、PEレビュー5 Findings修正）— `a1570139a`
- [x] B-2. RBKC変更（index.md + terms.json生成）— `22566bc09`, `c05a3afac`, `84f2feb23`, `cc5d2c56b`, `38fe7aae9`, `b3f0c9dfe`
- [x] B-1. 現行検索E2Eベースライン取得 — 3 runs, 精度83.7%, 幻覚PASS14.4%, $59.34 — committed `7ea223ab3`
- [x] qa-current.json を results/baseline-current/ に移動 — `f3d8eeb15`
- [x] HOW-TO-RUN.md を新スキル向けに更新（qa-current.json参照除去） — `b6f7d092f`
- [x] B-3. スキルデプロイ（スモークテスト完了） — `a07583fc4`, `549df22d2`, `000fc91db`, `71a0c16e3`, `10a7aaf82`
- [x] B-4-1-inv-read-sections-qa. Step 4 省略不可を確認（選定 vs テキスト抽出で役割が異なる）— notes.md 記録済み
- [x] B-4-1-inv-allowedTools. --allowedTools パターン修正（`bash scripts/...` プレフィックス追加、329テストGREEN）— `44076bcbc`
- [x] B-4-0. run_e2e.py エラーハンドリング修正 + 調査（TIMEOUT=360根拠確認、TimeoutExpired動作確認、マーカー欠損ケース確認、review-08/impact-01再実行確認）— `46877d7a4`
- [x] B-0. run_e2e.py 再設計（旧結果削除 `338c8c471`、TDD実装 `218a5e051`）— SEレビュー 0 Findings
- [x] B-1（旧）. 現行検索E2Eベースライン取得（不正データのためB-0でリセット） — `f57b78581`, `4de6fb47b`
- [x] A-1. RBKC変更のリバート — `5bf479e1c`, `f0249fea0`
- [x] A-2. 設計書の整合 — `b3819fb94`
- [x] A-3. 部品プロンプトの移動 — `eea31f065`, `426b9a0f4`
- [x] A-4. read-sections.sh テスト追加 — `b65064dce`
- [x] A-5. 部品スクリプトの移動 — `d2e6db620`, `0724b3faa`
- [x] A-6. マージ — `8d95af52e`
- [x] C-1. ゴミ確認・部品ベンチ削除 — `5614a04f5`（159テストPASS、E2E pre-01動作確認済み）

### ベンチマーク基盤（完了済み）

評価エンジン（`evaluate.py`, 54テストGREEN）、ランナー群（`simulate_*.py`, `run.py`）。QAシナリオ28件（`qa.json`）、キーワード検索シナリオ12件（`keyword-search.json`）。SE/QAレビュー済。

### 意味検索（完了済み）

2段階方式（Stage1: カテゴリ選定 → Stage2: セクション選定）。部品ベンチマーク: 97.4%（37/38 must）。ユーザー承認済。

### 回答生成（完了済み）

知識セクションから引用付き回答を生成。部品ベンチマーク: 18/26 Stable PASS, 1 Stable FAIL（既知）, 7 Unstable。PE/SEレビュー済。

### 根拠検証（完了済み）

ハルシネーション検出。部品ベンチマーク: FP率5%, FN率0%。PEレビュー済。

### ヒアリング（完了済み）

事実ベース分類。部品ベンチマーク: 分類100%, 処理方式100%×3回完全一致。PEレビュー済。

### キーワード検索（完了済み）

terms.jsonによるキーワードマッチ（20テストGREEN）。

### 設計書（完了済み）

`design/` に7本: benchmark-design.md（今回更新）, search-design.md, semantic-search-design.md, hearing-design.md, answer-verify-design.md, keyword-search-design.md。
