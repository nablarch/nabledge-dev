# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-23

## 現在地

- 30件ベンチマーク基盤 (ids / current 2 flow) 完成
- judge は fact-coverage 方式 (模範回答を参照して採点)
- 試行錯誤の痕跡をクリーンアップ中。SE 推奨の should-be 構成に全面書き直し予定

## 構成（should-be）

```
tools/benchmark/
├── run.py                CLI + orchestration (~150行)
├── bench/
│   ├── types.py          dataclasses
│   ├── claude.py         claude CLI 呼び出し + stream-json parse
│   ├── search_ids.py     ids variant
│   ├── search_current.py current variant
│   ├── judge.py          judge 呼び出し + verdict parse
│   └── io.py             scenario 読込・path 解決
├── build_index.py
├── prompts/ (search_ids.md / search_current.md / answer.md / judge.md)
├── scenarios/qa-v6.json + qa-v6-answers/
├── baseline/{ids,current}-sonnet/
└── tests/ (test_build_index / test_io / test_claude_parse / test_judge_parse)
```

**出力** `.results/{ts}-{variant}-{model}/`
- `run.json` / `summary.csv`
- `{scenario_id}/search.json`, `answer.md`, `judge.json`, `stream/*.jsonl`

**CLI**: `run.py --variant {ids|current}` / `run.py --rejudge --results-dir ...`

## 進め方

1. [x] 試行錯誤の削除 (facet flow / stage2 / stage1_extract / v1 judge / sample5 / sanity6 / 過去 .results / 過去 baseline)
2. [x] baseline 保存 (ids-sonnet / current-sonnet 最新 30件のみ、軽量化済み)
3. [x] プロンプトリネーム (stage1_ids→search_ids, stage3_answer→answer, judge_stage3_v2→judge)
4. [ ] **run.py 全面書き直し** (1572行 → bench/ パッケージ 6ファイル + run.py ~150行)
5. [ ] テスト再構成 (test_reference_answer 削除、test_io / test_claude_parse / test_judge_parse 新設)
6. [ ] 全テスト GREEN 確認
7. [ ] answer.md の「Use only what you need」改訂版で 30件再計測 (ids + current)
8. [ ] baseline 更新・比較表作成
9. [ ] `.claude/rules/benchmark.md` のコマンド例を新 CLI に更新
10. [ ] notes.md を「設計判断のみ」に整理
11. [ ] PR 仕上げ (expert review + description 更新)

## ユーザー判断待ち

- 30件再計測結果を見た後: ids / current の採用可否、本番 skill 反映タイミング
- 他バージョン (v1.2/1.3/1.4/5) 適用は別 PR (ロールベース KC 側)

## Done

- [x] 30 シナリオ + 模範回答 30件作成
- [x] 2-flow 比較基盤 (ids / current)
- [x] judge 設計 (fact-coverage, 模範回答参照)
- [x] Haiku vs Sonnet 比較 → Sonnet 固定
- [x] 30件 × 2 flow 初回計測
- [x] AI-3 answer プロンプト改訂 (Use only what you need, PE レビュー反映済み)
- [x] `.claude/rules/benchmark.md` 新設 (並列実行禁止ルール)
- [x] 試行錯誤クリーンアップ (facet/stage2/v1判定系すべて削除)
