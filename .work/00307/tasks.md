# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-23

## 現在地

- answer.md 改訂版で ids 30件計測済 (mean level=1.59, $16.75, 41min)
- 30件 answer 内容は変わらず保持 → rejudge で採点だけ更新する方針
- judge を A/B/C 方式に書き換え中。**A を事前準備する仕様** に舵切り (進行中)
- 判定基準の議論・実測でボロ多数 → `.claude/rules/development.md` に「実出力目視」ルール追記済

## judge 設計の確定事項 (2026-04-23)

- **A**: scenario ごとに人手で事前準備 (件数は質問次第、縛りなし)
- **B**: 事前準備不可。judge LLM が模範引用 section を見て on-topic / 裏付けあり と判断したものを B
- **C**: 模範引用 section にない主張 = 捏造 / off-topic / contradiction
- retrieved sections は judge に渡さない（C は模範 section 基準で判定）
- 採点:
  - L3 = A 全 COVERED + B 何か COVERED + C なし
  - L2 = A 全 COVERED + C なし
  - L1 = A 欠け (MISSING/PARTIAL) or C あり
  - L0 = 非回答 / A 大半欠け

## 進行中: judge を A 事前準備方式に再設計

**Steps:**
- [DECISION: 上記「judge 設計の確定事項」と A 事前準備の理解が正しいか、ユーザー最終確認待ち]
- [ ] scenarios/qa-v6.json に各 scenario の `a_facts: []` フィールド追加（review-01 を手書きしてレビュー→合意後残り29件）
- [ ] judge.md を「A は入力から受け取る」形に修正（抽出 step 削除）
- [ ] bench/judge.py を修正: Scenario から a_facts を読み込んで prompt に埋め込む
- [ ] bench/types.py Scenario dataclass に `a_facts` 追加、io.py load_scenarios で読み込み
- [ ] retrieved_sections を prompt から削除（いらない）
- [ ] 1 シナリオで full output 目視 → 3件 smoke → OK なら 30件 rejudge
- [ ] 新判定での ids baseline 確定 → notes.md / PR body に結果反映

## やらないことにした (この PR スコープ外)

- current variant の再計測 (answer.md 改訂は ids 側のみ影響、旧 baseline 流用)
- 30件一括 rerun (答えは変わらず rejudge で足りる)
- PARTIAL を L2 許容する案 (A の見直しで解消予定)

## ユーザー判断待ち

- judge 設計の確定事項（上記）の最終合意
- A の粒度感（review-01 で 5〜8 個あたりが目安か）

## 既知の bug / 注意

- judge の tool_use が複数回出ると最後を取るため、途中が壊れると壊れた方を拾う → `_is_well_formed_tool_input` で array-as-string を除外 (対処済)
- max_turns=4 に引き上げ済（2 だと A 長いと途中で切れて structured_output=None になっていた）
- io.py `verdict_from_structured` で `list(x)` 使うと string が char list になる → `_facts()` で type ガード (対処済)

## Done

- [x] 30 シナリオ + 模範回答 30件作成
- [x] 2-flow 比較基盤 (ids / current)
- [x] Haiku vs Sonnet 比較 → Sonnet 固定
- [x] 30件 × 2 flow 初回計測
- [x] AI-3 answer プロンプト改訂 (Use only what you need, PE レビュー反映済み)
- [x] `.claude/rules/benchmark.md` 新設 (並列実行禁止ルール)
- [x] 試行錯誤削除 / ベンチマークツール全面リファクタ (1572 → 1130行)
- [x] notes.md を設計判断のみに整理
- [x] baseline を新レイアウトに変換 / 全テスト 19件 GREEN
- [x] answer.md 改訂で ids 30件再計測 (`.results/20260423-113626-ids-sonnet/`)
- [x] current variant は旧 baseline 流用と判断（answer.md 非依存と確認）
- [x] judge A/B/C 方式 v1 実装 → 3件 smoke → A 過剰抽出 (15件) 問題発覚
- [x] `.claude/rules/development.md` に「Observe Real Output Before Claiming Success」追記
- [x] `.claude/rules/development.md` の Expert Review 節に「実行ログを必ずレビュー入力に添付」追記
