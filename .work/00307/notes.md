# Notes: Issue #307 — benchmark + streamlined search flow

Design decisions only. For trial-and-error and implementation history, see git log.

## Scope

- PR は1本で運用（ディレクトリ分離＋変更ファイル少のため）
- 本 PR の対象は v6 のみ。他バージョン (v1.2/1.3/1.4/5) 適用は別 PR (ロールベース KC 側) で実施

## Benchmark framework

- ベンチマークは nabledge-6 skill 経由ではなく、`tools/benchmark/` 内の prompt を `claude -p` で直接起動する
  - Reason: skill 起動 overhead を避ける / フロー切り替えが容易 / ログを per-call 保存できる
  - Trade-off: 「本物の skill を叩く」計測ではなくなるが、本番相当の挙動は `current` variant が担う
- 30 シナリオ × 2 variant (`ids` / `current`) を比較する設計
- Sonnet 固定 (Haiku 比較で +0.80 mean level 差、採用)
- 並列実行禁止 (`.claude/rules/benchmark.md`)

## Search variants

- `ids` — AI-1 が `index-llm.md` (titles-only) を読んで `file_id|sid` を返す → 機械解決 → read-sections → AI-3 が回答
  - index-llm.md / index-script.json を `build_index.py` で生成
- `current` — 本番 skill 相当。単一エージェントが Bash (full-text-search / get-hints / read-sections) で検索し回答

`ids` の狙い: AI-1 に全 section title を見せ、BM25 より意味的にマッチする選択をさせる。本番 skill への反映は別 PR。

## Judge

- Fact-coverage 方式。模範回答 + 模範 citation の本文を入力とし、生成回答の required_facts / over_reach を判定して 0-3 で採点
- Judge は品質ゲート。flow が通らないからといって judge を緩めない (`.claude/rules/rbkc.md` に準じる)
- 模範回答 30件は `scenarios/qa-v6-answers/*.md` に配置、path:sid citation を含む

## AI-3 answer policy

- 「渡された section を全部使う」ことは要件ではない。質問に直接答えるものだけ使い、周辺的 section は skip する
  - Reason: AI-1 は recall 優先で広めに拾うため、AI-3 が全部引用すると範囲外事実で減点される
- 複数 section 合成は OK (on-scope 判定は範囲、self-sufficient 判定は粒度)
- 迷ったら include (MISSING 悪化を避けるための非対称 tiebreaker)

## Directory / file naming

- `v2` / `stage3` / `facet` などのバージョン痕跡は名前に残さない
- 出力は `search.json` / `answer.md` / `judge.json` に統一 (variant 内部構造はファイル名に出さず、JSON の `steps[]` に格納)
- 旧 baseline は `baseline/{variant}-sonnet/` に最新1件のみ保存
