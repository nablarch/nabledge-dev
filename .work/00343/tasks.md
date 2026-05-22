# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-22 (session 15)

## Rules

- タスクリスト通りに作業する（順序を勝手に変えない）
- ユーザー確認タスク（`[BLOCKED:]`）は飛ばさない
- 各ステップ完了・中断のたびにタスクリストを更新してコミット・プッシュする（いつでも中断・再開できる状態を保つ）

## In Progress

### ベンチマーク ステップ3: run-1〜3の妥当性評価

HOW-TO-RUN.md ステップ3に従い、run-1〜3を1runずつ妥当性評価 → ユーザー承認 → FAILを確定させる。

- [x] HOW-TO-RUN.md ステップ3以降をゼロベース書き直し（3a/3b/3c → ステップ3/4/5/6の構造に変更） — `8f2ac2155`
- [x] HOW-TO-RUN.md ステップ3bに妥当性評価観点を追記（mustの充足確認、RST誤記の遡及確認） — `3a4625b71`
- [x] run-1 妥当性評価完了・レポート更新 — 確定FAIL 0件 — `0099e7026`
- [x] [DECISION: run-1 妥当性評価を承認（確定FAIL 0件）]
- [x] run-2 妥当性評価完了 — 確定FAIL 0件（4件すべて問題なし）— `1243f2471`
- [x] run-3 妥当性評価完了 — 確定FAIL 1件（qa-05: JaxbBodyConverter誤説明）— `1243f2471`
- [x] run-2/run-3 レポートとtasks.mdをコミット・プッシュ — `1243f2471`
- [x] qa.md / semantic-search.md: 「実装パターン・サンプルを参考にしたい」を「実装したい」に統合（v6のみ）— `acbf0d217`
- [x] qa.json: シナリオ修正（qa-05/qa-13 purpose変更、qa-05 must追加、qa-12a移動）— `acbf0d217`
- [x] semantic-search.md: 「実装したい」優先カテゴリに component/adapters 追加 — `02eedcccd`
- [x] qa-05 3回再実行（+4回追加）→ adapters-jaxrs-adaptor.json が選ばれない構造的問題を確認。現状の限界として受け入れ（ユーザー承認）
- [x] ステップ4: 3 run集計レポート作成 → `v1-new-search/report.md` に保存
- [x] ステップ5: 確定FAILの根本原因調査・提案（qa-05: 揺らぎ候補/要改善） → ユーザーが対応要否を判定
- [BLOCKED: qa-05対応要否をユーザーが判定してからコミット] ステップ6: コミット・プッシュ


## Not Started

### B-4-re. 現行検索ベースライン再取得（正当な比較のため）

新スキルのベンチマーク（v1-new-search）ではワークフロー詳細出力（Step 8: Workflow Details）が追加されており、旧ベンチマーク（baseline-current）と計測条件が異なる。正当なコスト・実行時間比較のために、現行検索スキルも同じ計測条件（新 run_e2e.py + 新 qa.json）で再取得する。

**背景**: output_tokens が1.5倍増えた主因は Step 8 の Workflow Details JSON 出力。input_tokens が13.5倍増えた主因は qa.md がプロンプトに埋め込まれるようになったため。旧 baseline-current はこれらが存在しない条件で取得されており、比較が不公平。

**ステップ:**
- [ ] `qa-baseline.json` を作成する（`hearing_answer` フィールドを除いたシナリオファイル）
  - 旧スキルにはヒアリングステップがなく、`hearing_answer` を埋め込むと旧スキルに不当なアドバンテージを与える
  - 全30シナリオの `when.hearing_answer` を削除したファイル `tools/benchmark/scenarios/qa-baseline.json` を生成
  - 受入条件: `python3 -c "import json; d=json.load(open('tools/benchmark/scenarios/qa-baseline.json')); assert all(s['when'].get('hearing_answer') is None for s in d['scenarios'])"` が通ること
- [ ] 現行検索スキル（mainブランチの `.claude/skills/nabledge-6`）を用意する
  - このブランチから別ブランチを作り、別ワークツリーで実行すれば本ブランチの作業と並行可能
  - `git branch 343-baseline-rerun main` で mainベースのブランチを作成
  - `git worktree add .tmp/baseline-rerun 343-baseline-rerun`
  - 受入条件: `.tmp/baseline-rerun/.claude/skills/nabledge-6/workflows/qa.md` が存在すること（旧スキル: `_knowledge-search.md` がある、`semantic-search.md` がない）
- [ ] 3 run 実行 → `tools/benchmark/results/baseline-current-v2/` に保存
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa-baseline.json \
    --skill-dir .tmp/baseline-rerun/.claude/skills/nabledge-6
  ```
- [ ] report.md を作成（3 run 集計、v1-new-search との比較）
- [ ] v1-new-search/report.md の比較表を `baseline-current-v2` ベースに更新
- [ ] worktree 削除: `git worktree remove .tmp/baseline-rerun`

**前提:** B-4（v1-new-search）完了後に実施。ステップ6コミット前でもよい。

### B-X. terms.json抽出ルールの見直し検討

keyword-search-design.md のterm抽出ルールについて、以下の点を検討・必要に応じて修正する。

**検討項目:**
- 設定値・機能名が拾えるか？（現行7カテゴリで十分か）
- ドット区切り3セグメント以上という閾値は妥当か？（2セグメントも有効では？）
- 高頻度term除外の7%閾値は妥当か？（緩めてよい？）
- 「ログ」で検索して機能横断のログ関連セクションを列挙できるか？（ユースケース確認）
- 絞り込みはページレベルANDで担保されるので、抽出は1〜7をもっと緩くして良いのでは？

**ステップ:**
- [ ] 実際のterms.jsonを使って「ログ」「設定」等で試し検索し、過不足を確認
- [ ] ドット区切り2セグメント、高頻度閾値10〜15%等の代替案をベンチマークシナリオで評価
- [ ] 設計書（keyword-search-design.md）と実装（terms.py / keyword-search.sh）を更新
- [ ] 20テストがGREENであること確認

**前提:** B-5（改善サイクル）完了後、B-6（バージョン展開）前に実施。v6で確定してから展開。

### B-5. 改善サイクル

B-4で現行未満の項目がある場合に実施。

- [ ] QAエキスパートの評価から劣化シナリオを特定
- [ ] 劣化原因を部品ベンチマークで特定（`simulate_*.py --scenario-ids <id>`）
- [ ] PE（プロンプト変更）またはSE（スクリプト変更）に改善案を相談してから実装
- [ ] E2Eベンチマーク再実行（`results/v2-new-search/` に保存）
- [ ] QAエキスパートによる再評価
- [ ] 全シナリオで baseline-current 以上になるまで繰り返し

### B-6. バージョン展開

B-5完了後。v6で確定した検索をv5/v1.xに展開。

- [ ] v5: ワークフロー・アセット・スクリプトをコピー（パス置換のみ）
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa.json \
    --skill-dir .claude/skills/nabledge-5 \
    --scenario-ids pre-01
  ```
- [ ] v1.4, v1.3, v1.2: 同上

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
