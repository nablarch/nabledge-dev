# Tasks: 検索改善

**Branch**: 343-improve-search-quality
**Updated**: 2026-05-19

## In Progress

### B-0-1. 設計書との適合確認・修正（最優先）

設計書 `.work/00343/design/search-design.md` のアーキテクチャと現在の実装が一致しているか確認し、乖離があれば修正。ユーザーレビューでパスするまで繰り返す。

**ステップ:**
- [ ] 設計書（`search-design.md` のフェーズB構成）と現実装（`.claude/skills/nabledge-6/workflows/` 以下の全ファイル）の差異を列挙して報告
  - 受入条件: 乖離リストをユーザーに提示
- [ ] [DECISION: ユーザーがレビューして修正方針を承認]
- [ ] 承認された修正を実装してコミット
- [ ] 再度差異を確認して報告
- [ ] [DECISION: ユーザーがレビューしてパスを確認]


### B-4-1. エラー原因調査と修正（B-4-2完了後）

run-1結果 (tools/benchmark/results/20260519-113919/): 30シナリオ中13件エラー
- TIMEOUT (360s): pre-03, qa-01 — 2件
- `<<<BENCHMARK_HEARING>>>` マーカー欠損: review-06, review-08, impact-01, impact-06, qa-03, qa-08, qa-09, qa-12a — 8件
- `<<<END_BENCHMARK_ANSWER>>>` マーカー欠損: qa-06, qa-12b — 2件

**ステップ:**
- [ ] エラーシナリオを再実行して trace.json / raw_response.txt を取得
- [ ] trace.json / raw_response.txt を読んでエラー原因を特定し、ユーザーに報告
- [ ] 原因に応じてスキル（qa.md）またはスクリプトを修正
- [ ] エラーシナリオのみ再実行して全件成功を確認
- [ ] 全30シナリオ再実行して全件成功を確認
  - 受入条件: summary.json の全シナリオに `status: error` が存在しないこと

### B-4. 新スキルE2Eベンチマーク（B-4-1完了後）

- [ ] run-1 リネーム: `mv tools/benchmark/results/20260519-113919 tools/benchmark/results/v1-new-search/run-1`
  （または全件成功後の新しい実行結果をrun-1とする）
- [ ] run-2, run-3 実行（同上、run-2/run-3にリネーム）
- [ ] 結果をコミット
- [ ] QAエキスパート（別エージェント）に生データを渡して比較評価させる（実装者が自己採点しない）
- [ ] [BLOCKED: ユーザーがQAエキスパートの評価を確認し、B-5着手の承認を出す]

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

- [x] B-4-2. run_e2e.py エラー時診断情報の確実な保存（TDD, QAレビュー 0 Findings）— `5eab4f1dd`, `d9af9bd2c`
- [x] qa.md/hearing.md 修正（マーカー出力をStep 7に一元化、スキーマ不整合修正、PEレビュー5 Findings修正）— `a1570139a`
- [x] B-2. RBKC変更（index.md + terms.json生成）— `22566bc09`, `c05a3afac`, `84f2feb23`, `cc5d2c56b`, `38fe7aae9`, `b3f0c9dfe`
- [x] B-1. 現行検索E2Eベースライン取得 — 3 runs, 精度83.7%, 幻覚PASS14.4%, $59.34 — committed `7ea223ab3`
- [x] qa-current.json を results/baseline-current/ に移動 — `f3d8eeb15`
- [x] HOW-TO-RUN.md を新スキル向けに更新（qa-current.json参照除去） — `b6f7d092f`
- [x] B-3. スキルデプロイ（スモークテスト完了） — `a07583fc4`, `549df22d2`, `000fc91db`, `71a0c16e3`, `10a7aaf82`
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
