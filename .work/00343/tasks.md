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
- **問題なければ確認不要**: タスクリストに従って作業を進める。ユーザーへの確認はタスクに `[BLOCKED:]` または `[DECISION:]` マークがある場合のみ。それ以外は確認なしに次のステップを実行する。
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
- [x] **出力データ品質を修正** — committed `7e30bc862`
- [x] **1シナリオ動作確認** — pre-01: hearing/search/answer/metrics/evaluation 全OK、evaluate.py統合バグも修正 — committed `c46bb224b`
- [x] **全QAシナリオ実行** — 28シナリオ完了、終了コード0 — committed `e8b2da257`
- [x] 結果を `results/baseline-current/` にコミット — `e8b2da257`
- [x] **ベースラインレポート**: accuracy avg=0.96, hallucination PASS率=0.19(5/26), 総コスト$19.04, 平均7.1ターン, 平均6.4セクション
- [ ] **ベースライン結果の妥当性検証**（目的: accuracy=0.96が実態を正しく反映しているかを確認する。ヒアリングなしでこのスコアは高すぎる可能性があり、must/fact設計やLLM判定の問題を見逃すとベースライン自体が無意味になる）
  - [ ] 全28シナリオについて、回答・参照セクション内容・must fact・PRESENT判定理由を並べてユーザーに提示する
  - [ ] ユーザーが全件を目視確認する（判定基準: 「その回答を読んだ人間がfactを確認できるか」「参照セクションに根拠があるか」）
  - [ ] must factの設計自体に問題がないか確認する（キーワードが出れば通るだけの簡単すぎるfactになっていないか）
  - [ ] 問題があればQAエキスパートに評価させ、シナリオ修正または再測定の判断を行う
  - 合格基準: ユーザーが全28件を確認し、問題なしまたは修正方針が確定すること

### B-2. RBKC変更

B-1完了後に実施。目的: 意味検索が使う `terms.json`（検索語辞書）と `index.md`（知識ファイル一覧）を生成できる状態にする。これがないと新検索のスキルが動かない。

- [x] cherry-pickコミットが存在しないため、`index.md` と `terms.json` を新規実装する方針に変更
- [x] index.md生成: `generate_index_md()` を `index.py` に追加（Option A: index.toon維持、並行生成）— committed `0aefe7168`
  - SEエキスパート推奨: index.toonとQO4 verifyへの影響ゼロ
  - 12テスト追加、567テスト全GREEN、v6 create+verify FAIL=0確認
- [ ] 全5バージョンで `rbkc.sh create` を実行し `index.md` が生成されることを確認
  - v6: ✅ 確認済み（`.claude/skills/nabledge-6/knowledge/index.md` 生成）
  - v5: 実行中断（セッション終了のため）
  - v1.4/v1.3/v1.2: 未実行
  - コマンド: `for v in 5 1.4 1.3 1.2; do (cd tools/rbkc && bash rbkc.sh create $v); done`
  - 各バージョンで `.claude/skills/nabledge-$v/knowledge/index.md` が存在すること
- [ ] 全5バージョンで `bash rbkc.sh verify <v>` を実行し FAIL=0 確認（変更前FAIL=0）
- [ ] [DECISION: terms.jsonの実装が必要か確認] terms.py（terms.json生成）を新規実装する — 設計書: `keyword-search-design.md` §terms.json
  - TDD: test_terms.py を書く（RED）→ 実装（GREEN）
  - 全5バージョン create+verify FAIL=0 確認

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
