# Tasks: 検索改善

**Branch**: search
**Updated**: 2026-05-15

## Done

- [x] A-1. RBKC変更のリバート — committed `5bf479e1c`, `f0249fea0`
- [x] A-2. 設計書の整合（ディレクトリ構成） — committed `b3819fb94`
- [x] A-3. 部品プロンプトの移動 — committed `eea31f065`, `426b9a0f4`
- [x] A-4. read-sections.sh テスト追加 — committed `b65064dce` (jq bugfix included, all 5 versions)
- [x] A-5. 部品スクリプトの移動 — committed `d2e6db620`, `0724b3faa`
- [x] A-6. マージ準備完了 — 284 tests pass, diff clean (no skill/RBKC changes)

## Rules

- **数字を実際に読め**: ログや diff を目で確認する。サイズや形から推測しない。
- **答えを先に決めるな**: データが結論を導く。先入観・推測・仮説でバイアスをかけて調査してはいけない。観察した事実だけを報告し、原因不明なら「不明」と言う。
- **ベンチマークで調整するな**: シナリオを使って問題を探すのはOK。そのシナリオに合わせてスコアを調整するのはNG。
- **自己評価禁止**: ベンチマーク結果は必ず別エージェント（QA Expert）に評価させる。実装した本人が採点しない。
- **勝手に直すな**: バグや問題を見つけたら、専門家（SE / PE / QA）に相談してから実装する。
- **出来レース禁止**: シミュレーションは全シナリオ対象。特定シナリオ向けのチューニングは禁止。汎用性能のみ追求する。
- **シミュレーションは全件**: シミュレーション（トレース）は全シナリオで改善を繰り返す。コストゼロなので出し惜しみしない。
- **バイアス排除**: シミュレーション、エキスパートレビュー、改善はそれぞれ別コンテキスト（別エージェント）で実施。メインエージェントが最終判断。
- **調査は網羅的に**: 全バージョン（v6/v5/v1.4/v1.3/v1.2）、幅広いタイプの知識ファイルを対象。
- **設計書は常に最新状態**: （変更）（既存）（旧xxx）等の履歴注釈を入れない。gitが履歴を管理している。後から読むとノイズになる。
- **成果物はエキスパートレビュー後に使用**: プロンプト→PE、スクリプト・コード→SE。ベストプラクティスに従っているかを確認してから使用する。レビュー前の成果物は使わない。
- **バイアス排除（改善サイクル）**: シミュレーション結果の分析→QA（生データから独立分析）、改善提案→PE（QAの分析を受けて）。メインエージェントは生データを渡すだけで分析・結論を注入しない。
- **作業指示は迷わず実行できる粒度**: 各タスクのステップはルールに従った具体的な作業指示とする。曖昧なステップは作業開始前に具体化する。
- **やり直し時は旧成果物を削除**: 作業をやり直す場合、旧成果物（プロンプト、レビュー結果、中間ファイル等）を全て削除してプッシュしてから再開する。ノイズを残さない。
- **プロンプトは手順型で書く**: ルールベース（判断基準の羅列）ではなく、作業手順（明確な命令で実行順序を記述）で書く。LLMが何をどの順番でやるか迷わない形にする。
- **シナリオのmustは本文で検証**: mustセクションの妥当性はタイトルではなく本文を読んで判断する。タイトルだけで「必須」と設定しない。

## マージ前（フェーズA残タスク）

フェーズAの原則: 現行スキル・RBKCは一切変更しない。部品はすべて `tools/benchmark/` 内。

### A-6. マージ

- [x] 全テスト最終確認: 284 passed
- [x] searchブランチの成果物をフェーズBブランチにマージ — committed `8d95af52e`

## マージ後（フェーズB）

依存関係: B-1 → B-2 → B-3 → B-4 → B-5 → B-6。順序厳守。

### B-1. 現行検索E2Eベースライン取得

**RBKC変更・スキルデプロイの前に実施すること。** 変更後はベースラインが取れなくなる。

- [x] E2Eベンチマーク設計を確定（benchmark-design.md のE2Eセクション）
- [x] E2Eベンチマークランナー（`run_e2e.py`）のテストを書く（RED）
- [x] `run_e2e.py` を実装（GREEN）— committed `a4d4403f1`
- [ ] **出力データ品質を修正**（全件実行前に直す。壊れたデータでベースラインを取ると比較が無意味になる）
  - [ ] `model_usage` キー名を修正: `claude -p` のJSON出力は `modelUsage`（camelCase）で返すが、コードは `model_usage`（snake_case）で取得しているため常に `{}`。`claude_output.get("modelUsage", {})` に変更（テストも `modelUsage` キーで更新）
  - [ ] `usage.input_tokens` の実態を確認: pre-01は8ターンで `input_tokens: 9` — これがシングルターンのみなのか全ターン合算なのかを `claude -p --output-format json` のrawレスポンスで実測確認。全ターン合算でなければ設計書のパフォーマンスメトリクス比較（現行 vs 新）で正しい比較ができない。合算フィールドが別にあれば切り替える
  - [ ] `pytest tools/benchmark/tests/ -x` がグリーン
- [ ] **1シナリオ動作確認**（目的: E2Eランナーがワークフローを正しく実行し、設計書で定義した全メトリクスをキャプチャできていること）
  - `hearing.json` に `status` フィールドがある — ヒアリング診断が壊れていないこと
  - `search.json` の `section_ids` が1件以上 — 現行検索は必ずセクションを返すはず。0件は検索が動いていないサイン
  - `answer.md` が日本語の回答テキストを含む（`参照:` セクションがある） — 「空でない」ではなく、エラーメッセージではなく正常回答が入っていることの確認
  - `metrics.json` の `model_usage` にモデルキー（`claude-sonnet-4-6` 等）が入っている — コスト比較レポートにモデル別内訳が必要。`{}` だとコスト分析が死ぬ
  - `metrics.json` の `usage.input_tokens` が実態として全ターン合算値になっている — 現行 vs 新の検索コスト比較に使うため、1ターン分しか取れていないと比較が歪む
  - `benchmark-design.md` のパフォーマンスメトリクス一覧（duration_ms, duration_api_ms, num_turns, total_cost_usd, usage.input_tokens, usage.output_tokens, usage.cache_read_input_tokens, usage.cache_creation_input_tokens, model_usage）が全フィールド揃っていること
- [ ] **全QAシナリオ実行**（目的: 現行検索の品質・パフォーマンスをベースラインとして記録し、新検索との比較基準を確立する）
  - コマンド: `python3 -m tools.benchmark.scripts.run_e2e --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --output-dir tools/benchmark/results/baseline-current`
  - 終了コード0（途中エラーで中断したシナリオがないこと）
  - `summary.json` の `total_scenarios` = 28
  - 全シナリオの `metrics.json` に `model_usage` が `{}` でない（キー名修正が正しく効いていること）— `for d in tools/benchmark/results/baseline-current/*/metrics.json; do python3 -c "import json; d=json.load(open('$d')); assert d['model_usage'], f'empty: $d'"; done`
- [ ] 結果を `results/baseline-current/` にコミット
- [ ] **ベースラインレポートをユーザーに報告**（目的: 現行品質を数値で把握し、新検索デプロイ後の比較基準とする）
  - シナリオ別: `search_sections` 件数、`hearing_status`、コスト・ターン数
  - 集計: 平均コスト・ターン数・検索ヒット件数（設計書のパフォーマンスサマリー形式）

### B-2. RBKC変更

B-1完了後に実施。目的: 意味検索が使う `terms.json`（検索語辞書）と `index.md`（知識ファイル一覧）を生成できる状態にする。これがないと新検索のスキルが動かない。

- [ ] `git cherry-pick 46893d39f` — P1-group subtype再適用（xlsx_common.py, xlsx-sheet-mapping.md, test_xlsx_common.py）
  - `git diff HEAD~1 --stat` で3ファイルのみ変更されていること（他のファイルが混入していないこと）
- [ ] `pytest tools/rbkc/tests/ut/test_xlsx_common.py -x` がグリーン（cherry-pick が壊していないこと）
- [ ] P1-group subtype の変更内容をユーザーに提示し承認取得（承認なしで次に進まない）
- [ ] `git cherry-pick 03e20a535` — terms.py + test_terms.py + run.py terms統合を再適用
  - `git diff HEAD~1 --stat` で対象3ファイルのみ変更されていること
- [ ] `pytest tools/rbkc/tests/ut/test_terms.py -x` がグリーン
- [ ] index.md生成（index.py: index.toon → index.md変更）のテストを書く（RED）
  - 目的: 意味検索Stage1がカテゴリ一覧として参照するindex.mdをRBKCが生成できること。index.toonのままでは新検索ワークフローが読み込めない
  - `pytest tools/rbkc/tests/ut/test_index.py` が FAIL（実装前なのでFAILが正しい）
- [ ] index.py を実装（GREEN）: `pytest tools/rbkc/tests/ut/test_index.py` が PASS
- [ ] 全5バージョンで `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` を実行（v6/v5/v1.4/v1.3/v1.2）
  - 変更前のFAIL数を記録してから変更後と比較。想定外のFAIL増は横展開ミスのサイン

### B-3. スキルデプロイ

B-2完了後に実施。目的: ベンチマークで検証済みの部品プロンプト・スクリプトをスキルに組み込み、新検索ワークフローとして動く状態にする。ベンチマーク済みの部品をそのまま使うため、デプロイ≠新規実装（差分がないことが正しい）。

- [ ] `components/prompts/` → `.claude/skills/nabledge-6/assets/` にコピー
  - `diff tools/benchmark/components/prompts/ .claude/skills/nabledge-6/assets/` で差分なし（ベンチマーク済みと一致している）
- [ ] `components/scripts/` → `.claude/skills/nabledge-6/scripts/` にコピー
  - `diff tools/benchmark/components/scripts/ .claude/skills/nabledge-6/scripts/` で差分なし（既存ファイルとの競合がないこと）
- [ ] 各ワークフローを作成してPEレビュー後にコミット（目的: 部品をオーケストレートするワークフローが正しく部品を呼ぶこと）
  - `qa/hearing.md` — ヒアリングステップ（hearing-classify.md/hearing-extract.md を呼ぶ）
  - `semantic-search.md` — 意味検索（Stage1→Stage2 を呼ぶ）
  - `keyword-search.md` — キーワード検索（keyword-search.sh を呼ぶ）
  - `qa/answer.md` — 回答生成（answer.md を呼ぶ）
  - `qa/verify.md` — 根拠検証（verify.md を呼ぶ）
  - `qa.md` — QAオーケストレーション（hearing→search→answer→verify を順に呼ぶ）
  - `code-analysis.md` — コード解析
- [ ] 1シナリオでスモークテスト（目的: ワークフロー接続が正しく、エンドユーザー視点で回答が返ること）
  - `python3 -m tools.benchmark.scripts.run_e2e --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --output-dir .tmp/b3-smoke --scenario-ids pre-01` を実行し終了コード0
  - `.tmp/b3-smoke/pre-01/answer.md` に日本語テキストがあり、`参照:` セクションがある（知識ファイルから引用していることの証拠）
  - `.tmp/b3-smoke/pre-01/metrics.json` の `model_usage` が `{}` でない（スキルが新ワークフローで動いていること）

### B-4. 新検索E2Eベンチマーク

B-3完了後に実施。目的: 新検索が現行と比べて品質・パフォーマンスがどう変わったかを定量把握する。ここで「現行以上かどうか」の判断材料を作る。

- [ ] 新検索で1シナリオ動作確認（B-1の合格基準に加えて新検索固有の確認）
  - B-1と同じ: hearing.json/search.json/answer.md/metrics.json が揃い、answer.mdに`参照:`があり、model_usageが`{}`でない
  - 新検索固有: `search.json` の `section_ids` の内容が現行検索（baseline-current）と異なること — 同じなら新検索が使われていない
  - 新検索固有: `metrics.json` の `num_turns` を baseline-current の同シナリオと比較し、差が想定内であること（新ワークフローが余分なターンを消費していないこと）
- [ ] 全QAシナリオでE2Eベンチマーク実行
  - コマンド: `python3 -m tools.benchmark.scripts.run_e2e --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6 --output-dir tools/benchmark/results/v1-new-search`
  - `summary.json` の `total_scenarios` = 28（エラー中断なし）
- [ ] 結果を `results/v1-new-search/` にコミット
- [ ] 比較レポート生成（baseline-current vs v1-new-search）: `report.py` の比較機能で出力
- [ ] QAエキスパートに生データ（比較レポート）を渡して評価させる（実装者が自己採点しない。バイアス排除）
- [ ] ユーザーに報告（QAエキスパートの評価結果を添付）

### B-5. 改善サイクル

B-4の比較で現行未満の項目がある場合に実施。目的: 劣化した部分を部品レベルで修正し、E2Eで現行以上を確認する。E2Eから先に直そうとすると原因特定が困難なため部品→E2Eの順を守る。

- [ ] QAエキスパートの評価から劣化シナリオを特定（シナリオIDと劣化軸を列挙）
- [ ] 劣化原因を部品ベンチマークで特定（`simulate_*.py` で当該シナリオを個別実行）
  - 原因が特定できたら PE（プロンプト変更）または SE（スクリプト変更）に改善案を相談してから実装（勝手に直さない）
- [ ] 部品ベンチマーク再実行で改善確認（劣化していたシナリオのスコアが改善していること）
- [ ] E2Eベンチマーク再実行（`results/v{N}-new-search/`）
- [ ] QAエキスパートによる再評価（再評価もQAエキスパートがやる。実装者が採点しない）
- [ ] 全シナリオで baseline-current 以上になるまで繰り返し

### B-6. バージョン展開

B-5完了後、v6で確定した検索を展開。目的: v6で品質確認済みの検索をv5/v1.x にも提供する。パス置換以外の変更は原則不要。差分が大きい場合はv6との乖離を調査する。

- [ ] v5に展開
  - ワークフロー・アセット・スクリプトをv5スキルにコピー（パス置換のみ）
  - `python3 -m tools.benchmark.scripts.run_e2e --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-5 --output-dir tools/benchmark/results/v5-baseline` で1シナリオ動作確認（データが壊れていないこと）
- [ ] v1.4に展開（同上）
- [ ] v1.3に展開（同上）
- [ ] v1.2に展開（同上）

### B-7. nabledge-test削除

B-6完了後に実施。目的: 新ベンチマーク基盤（E2E + 部品ベンチマーク）に完全移行し、旧nabledge-testの重複メンテを解消する。削除後もCI（test-setup.sh + pytest）が通ることを確認する。

- [ ] `tools/tests/test-setup.sh` の `_scenario_field` 関数を削除し、質問・キーワードをハードコード（各バージョン1問ずつ）
  - 変更後: `bash tools/tests/test-setup.sh` が全バージョンでエラーなく完了（削除によって既存CIが壊れていないこと）
- [ ] `.claude/skills/nabledge-test/` ディレクトリ削除
- [ ] `.claude/agents/nabledge-test-runner.md` 削除
- [ ] `.claude/settings.json` から `Skill(nabledge-test)` 行を削除（`grep nabledge-test .claude/settings.json` が0件）
- [ ] `.claude/rules/temporary-files.md` と `nabledge-skill.md` からnabledge-test固有記述を削除
- [ ] `python3 -m pytest tools/ -x` で全テストパス（削除後もグリーン）

## Done

### ベンチマーク基盤

評価エンジン（`evaluate.py`, 54テストGREEN）とランナー群（`simulate_*.py`, `run.py`, 23テストGREEN）。QAシナリオ15件（`qa.json`）、キーワード検索シナリオ12件（`keyword-search.json`）。SE/QAレビュー済。

### 意味検索

2段階方式（Stage1: カテゴリ選定 → Stage2: セクション選定）。プロンプト: `semantic-search-stage1.md`, `semantic-search-stage2.md`。部品ベンチマーク: 97.4%（37/38 must）。ユーザー承認済。

### 回答生成

知識セクションから引用付き回答を生成。プロンプト: `answer.md`。部品ベンチマーク: 18/26 Stable PASS, 1 Stable FAIL（既知）, 7 Unstable。PE/SEレビュー済、ユーザー承認済。

### 根拠検証

回答のハルシネーションを検出。プロンプト: `verify.md`。部品ベンチマーク: FP率5%, FN率0%。PEレビュー済、ユーザー承認済。

### ヒアリング

事実ベース分類（明示キーワードリスト照合、推測禁止）。プロンプト: `hearing-classify.md`, `hearing-extract.md`。部品ベンチマーク: 分類100%, 処理方式100% × 3回完全一致。PEレビュー済、ユーザー承認済。

### キーワード検索

terms.jsonによるキーワードマッチ。case-insensitive部分一致、ページAND+セクションOR。スクリプト: `keyword-search.sh`（20テストGREEN）。

### 設計書

`design/` に6本整理: search-design.md, benchmark-design.md, semantic-search-design.md, hearing-design.md, answer-verify-design.md, keyword-search-design.md。
