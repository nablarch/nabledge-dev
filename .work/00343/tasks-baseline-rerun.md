# Tasks: 現行検索ベースライン再取得

**Branch**: 343-baseline-rerun
**Updated**: 2026-05-22

## 概要

新スキル（v1-new-search）と公平に比較するため、現行検索スキル（mainベース）を新ベンチマーク基盤（run_e2e.py）で計測する。

完了後、`343-improve-search-quality` にマージする。

---

## 問題と解決策

現行検索スキルをそのまま run_e2e.py で計測するには3つの問題がある:

| 問題 | 原因 | 解決策 |
|---|---|---|
| knowledge searchがスキップされる | `e2e-prompt.md` に「Step 1/2 Skip」指示がある | 旧スキル用プロンプト `e2e-prompt-baseline.md` を作成 |
| MarkerErrorで落ちる | `parse_e2e_response()` が `### Workflow Details` を必須とする | `e2e-prompt-baseline.md` でもマーカー出力指示を残す |
| 旧スキルに不当アドバンテージ | `hearing_answer` を質問に埋め込むと処理方式・目的が渡される | `hearing_answer` なしの `qa-baseline.json` を使う |

---

## Not Started

### 1. run_e2e.py に `--prompt-template` オプションを追加（TDD）

`build_e2e_prompt()` はすでに `prompt_template` 引数を受け取れる設計。`main()` の argparse に追加するだけ。

- [ ] テスト追加: `tools/tests/` に `--prompt-template` オプションのテストを追加（RED）
  - 受入条件: テストが RED であること
- [ ] 実装: `main()` の argparse に `--prompt-template` を追加し、指定があれば読み込んで `run_e2e_all()` に渡す
  - 受入条件: `python3 -m pytest tools/tests/ -x` が GREEN

### 2. `e2e-prompt-baseline.md` を作成する

`e2e-prompt.md` をベースに、旧スキル（ヒアリングなし）向けに変更する。

- [ ] `tools/benchmark/prompts/e2e-prompt-baseline.md` を作成する
  - 変更点: 「Step 1 and Step 2: Skip both steps.」の段落を削除する（旧スキルはStep 1から実行する）
  - 残す点: Workflow Details 出力指示（parse_e2e_response() がマーカーを必要とするため）
  - 残す点: Step 3/4/8 の詳細記録指示
  - 受入条件:
    ```bash
    grep "Skip both steps" tools/benchmark/prompts/e2e-prompt-baseline.md && echo "NG" || echo "OK"
    ```
    → `OK` と出力されること

### 3. `qa-baseline.json` を作成する

`qa.json` の全30シナリオから `when.hearing_answer` キーを削除したファイル。

- [ ] `tools/benchmark/scenarios/qa-baseline.json` を作成する
  - 受入条件:
    ```bash
    python3 -c "
    import json
    d = json.load(open('tools/benchmark/scenarios/qa-baseline.json'))
    assert len(d['scenarios']) == 30
    assert all(s['when'].get('hearing_answer') is None for s in d['scenarios'])
    print('OK')
    "
    ```
    → `OK` と出力されること

### 4. ステップ1（動作確認）: pre-01 を1シナリオ実行

- [ ] pre-01 を実行して旧スキルが正常に動作することを確認する:
  ```bash
  python3 -m tools.benchmark.scripts.run_e2e \
    --scenarios tools/benchmark/scenarios/qa-baseline.json \
    --skill-dir .claude/skills/nabledge-6 \
    --prompt-template tools/benchmark/prompts/e2e-prompt-baseline.md \
    --scenario-ids pre-01
  ```
  - 受入条件: 終了コード0
  - 受入条件: `tools/benchmark/results/YYYYMMDD-HHMMSS/pre-01/workflow_details.json` が存在する
  - 受入条件: `tools/benchmark/results/YYYYMMDD-HHMMSS/pre-01/answer.md` が存在する
  - 動作確認ディレクトリを削除する: `rm -rf tools/benchmark/results/YYYYMMDD-HHMMSS`
- [ ] コミット・プッシュ（タスク1〜3の成果物）

### 5. 全30シナリオを3 run実行

HOW-TO-RUN.md ステップ2に従う。通常手順からの差分のみ記載:
- `--scenarios`: `tools/benchmark/scenarios/qa-baseline.json`
- `--skill-dir`: `.claude/skills/nabledge-6`（このブランチ自体が旧スキル）
- `--prompt-template`: `tools/benchmark/prompts/e2e-prompt-baseline.md`
- 結果保存ラベル: `baseline-current-v2`

- [ ] run-1 実行 → `tools/benchmark/results/baseline-current-v2/run-1/` にリネーム
  - エラーが出た場合: HOW-TO-RUN.md「エラー時の調査」に従い単体再実行で回収
  - 受入条件: `summary.json` の `total_scenarios` が 30、`status: error` のシナリオが 0
- [ ] run-2 実行 → `tools/benchmark/results/baseline-current-v2/run-2/` にリネーム
  - 受入条件: 同上
- [ ] run-3 実行 → `tools/benchmark/results/baseline-current-v2/run-3/` にリネーム
  - 受入条件: 同上
- [ ] コミット・プッシュ（3 run結果）

### 6. HOW-TO-RUN.md ステップ3: 各runの妥当性評価

HOW-TO-RUN.md ステップ3に従う。

- [ ] run-1 妥当性評価 → `baseline-current-v2/run-1/report.md` に保存、コミット・プッシュ
- [ ] run-2 妥当性評価 → `baseline-current-v2/run-2/report.md` に保存、コミット・プッシュ
- [ ] run-3 妥当性評価 → `baseline-current-v2/run-3/report.md` に保存、コミット・プッシュ

### 7. HOW-TO-RUN.md ステップ4: 3 run集計レポート作成

- [ ] `tools/benchmark/results/baseline-current-v2/report.md` を作成する
  - 内容: 精度 PASS率・幻覚 PASS率・コスト/run の3 run集計、確定FAIL一覧
- [ ] コミット・プッシュ

## Done
