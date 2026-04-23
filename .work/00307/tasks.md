# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-23

## 現在地

- ベンチマークツールのリファクタリング完了 (should-be 構成へ全面書き直し、1572行 → 1130行)
- run.py / bench/ パッケージ / テスト / baseline 変換すべて完了、smoke test で動作確認済み (review-09 level=3)
- 次は answer.md 改訂版での 30件再計測 (ids + current)

## 構成

```
tools/benchmark/
├── README.md
├── run.py                CLI + orchestration (202行)
├── bench/
│   ├── types.py          dataclasses (69)
│   ├── claude.py         claude CLI + stream-json parse (123)
│   ├── search_ids.py     ids variant (145)
│   ├── search_current.py current variant (37)
│   ├── judge.py          judge 呼び出し (99)
│   └── io.py             scenario/path 解決 (177)
├── build_index.py
├── prompts/              search_ids.md / search_current.md / answer.md / judge.md
├── scenarios/            qa-v6.json + qa-v6-answers/
├── baseline/{ids,current}-sonnet/
└── tests/                test_build_index / test_claude_parse / test_io / test_search_ids (全19 GREEN)
```

**出力** `.results/{ts}-{variant}-{model}/`
- `run.json` / `summary.csv` / `summary.json`
- `{sid}/search.json`, `answer.md`, `judge.json`, `stream/*.jsonl`

**CLI**: `run.py --variant {ids|current}` / `run.py --rejudge --results-dir ...`

## 残タスク

### 次: answer.md 改訂版で 30件再計測

answer.md の「Use only what you need」改訂が入った状態で ids / current の 30件を測り直し、baseline を更新する。

**Steps:**
- [ ] `python3 tools/benchmark/run.py --variant ids` 実行 (30件、~33分)
- [ ] `python3 tools/benchmark/run.py --variant current` 実行 (30件、~40分) — **ids 完了後に逐次**
- [ ] 結果を `baseline/ids-sonnet/` `baseline/current-sonnet/` に反映 (手動コピーまたはスクリプト)
- [ ] baseline 比較表を notes.md or PR body に記載 (mean level / distribution / cost)

### その後

- [ ] PR 仕上げ (expert review + PR description 更新)
- [ ] ユーザーに採用可否判断を提示

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
- [x] `.claude/rules/benchmark.md` 新設 (並列実行禁止ルール) — commit `322f616fd`
- [x] 試行錯誤削除 (facet/stage2/v1判定系) — commit `af43acb20`
- [x] ベンチマークツール全面リファクタ (run.py → run.py + bench/ パッケージ、命名からバージョン痕跡撤去) — commit `7abb7f3e2`
- [x] notes.md を設計判断のみに整理 — commit `a7a016d27`
- [x] baseline を新レイアウトに変換 (search.json / answer.md / judge.json に統一)
- [x] 全テスト 19件 GREEN、smoke test OK
