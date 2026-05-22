# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-22 (session 21)

## Rules

- タスクリスト通りに作業する（順序を勝手に変えない）
- ユーザー確認タスク（`[BLOCKED:]`）は飛ばさない
- 各ステップ完了・中断のたびにタスクリストを更新してコミット・プッシュする（いつでも中断・再開できる状態を保つ）

## In Progress

## Not Started

### C-1. ゴミ確認・部品ベンチ削除

- [x] `tools/benchmark/` 以下を確認し、部品ベンチマーク（`components/`, `simulate_*.py`）など不要ファイルを特定してリスト化
- [x] ユーザーに削除対象を確認してから削除（承認済み）
- [ ] 削除実施:
  - `git rm -r tools/benchmark/scripts/run.py tools/benchmark/scripts/simulate_*.py`
  - `git rm -r tools/benchmark/components/`
  - `git rm tools/benchmark/tests/test_run.py tools/benchmark/tests/test_simulate_*.py`
  - `rm -rf tools/benchmark/results/20260522-165151/ tools/benchmark/results/20260522-170658/`
- [ ] 動作確認: `python3 -m pytest tools/benchmark/ -x -q` が全 PASS（削除後に残ったテストが壊れていないことを確認）
  - 受入条件: 終了コード 0、test_run_qa / test_run_keyword_search / test_evaluate / test_report が全て PASS
- [x] 新検索スキル（v6）の実装ファイルを確認し、不要ファイルなし（確認済み）

### C-2. 設計書再作成（実装ベース）

- [ ] 既存設計書を削除（`git rm .work/00343/design/`）— 削除してから作業開始。既存設計書は参照しない
- [ ] v6の新検索実装（`workflows/`, `scripts/`）だけを読み、検索設計書を作成
  - 最新状態として記述（変更履歴・経緯は書かない）
  - 実装から分からない設計意図（なぜその方式か、なぜその閾値か等）を含める
- [ ] ベンチマーク実装（`tools/benchmark/`）だけを読み、ベンチマーク設計書を作成
  - 同上（最新状態・変更履歴なし・設計意図を含める）
- [BLOCKED: ユーザーに設計書を確認してもらう] 設計書レビュー承認後、次タスクへ

### C-3. 他バージョン展開・差分チェック

C-2完了後。v6設計書をチェックリストとして他バージョンを確認し品質担保。

- [ ] v6の正解状態からチェックリストを作成
- [ ] v5/v1.4/v1.3/v1.2 の各ファイルをチェックリストと照合（バージョン固有差分は許容）
- [BLOCKED: ユーザーにチェック結果を報告し承認を得る] NGがあれば修正案を提示してから実施

### B-7. nabledge-test削除

B-6完了後。新ベンチマーク基盤に完全移行。

- [ ] `test-setup.sh` の `_scenario_field` 削除、質問・キーワードをハードコード
  - `bash tools/tests/test-setup.sh` が全バージョンでエラーなく完了
- [ ] `.claude/skills/nabledge-test/` / `.claude/agents/nabledge-test-runner.md` 削除
- [ ] `.claude/settings.json` から `Skill(nabledge-test)` 行を削除
- [ ] `.claude/rules/` からnabledge-test固有記述を削除
- [ ] `python3 -m pytest tools/ -x` で全テストPASS

### B-8-pre. マージ前静的確認

B-7完了後、PRマージ前に実施。「マージしたら壊れる」を事前に潰す。

**確認1: GHA sync manifest**
- [ ] `.github/workflows/sync-to-nabledge/sync-manifest.txt` を読み、今回追加・変更したスキルファイルが含まれているか確認
  - 含まれるべきもの: `workflows/qa.md`, `workflows/qa/`, `workflows/_knowledge-search.md`, `workflows/_knowledge-search/`, `assets/answer.md` など今回の変更ファイル
  - 含まれないべきもの: `tools/`, `.work/`, `.claude/rules/` など開発専用ファイル
  - 受入条件: デプロイ対象ファイルがすべてmanifestに含まれること

**確認2: セットアップスクリプト**
- [ ] `tools/setup/setup-6-cc.sh` / `tools/setup/setup-6-ghc.sh` を読み、今回削除・移動したファイルへの参照がないか確認
  - 受入条件: 削除・移動したファイルへの参照がゼロであること

**確認3: test-setup.sh**
- [ ] B-7で削除するファイル（`.claude/skills/nabledge-test/scenarios/`）への参照がtest-setup.shに残っていないか確認
  - B-7の `_scenario_field` 削除ステップで対処済みであることを確認
  - 受入条件: `grep -n "nabledge-test" tools/tests/test-setup.sh` が0件であること

- [ ] 問題があればB-7の修正に追加してコミット

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
