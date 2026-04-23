# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-23

## ゴール (この PR の本質)

ids flow の L1 以下を 0 にする。それが達成できて初めて current より「明確に良い」と言える。
L1 を残したまま speed 指標だけで ids 採用を提案しても Nabledge 品質基準 (1% リスク排除 / 品質は二値) に反する。

## 現在地

- judge を A 事前準備 / B,C は KB (reference + retrieved) で LLM 判定する方式に確定
- 30 scenario 全件に A-fact を手書き (review-01 は私が手書き、29件は Agent 草案→私がレビュー→17件修正)
- ids 30件 rejudge: mean=2.10, L3=16, L1=13, None=1 (req-09), cost=$16.48, 32.3min
- current 30件 rejudge: mean=2.17, L3=18, L1=11, L0=1, cost=$15.60, 51.3min

## ids L1 以下 14件の症状分類 (事実 = judge output ベース)

**A-only fail (9件)** — A-fact 欠け、C なし
- impact-01 (L1): A1/A2 PARTIAL/MISSING (TransactionManagementHandler, 往路/復路)
- impact-04 (L1): A3 MISSING (RetryHandler 配置順)
- impact-06 (L1): A3 PARTIAL (手動 nonce 付与 / JS 外出しの選択肢)
- impact-07 (L1): A2 PARTIAL, A4/A5 MISSING (内部フォワード認可の設定群)
- impact-10 (L1): A3 MISSING (PermissionCheckHandler 参照)
- req-04 (L1): A2/A3 MISSING (useToken / @UseToken)
- req-05 (L1): A3 MISSING (コード名称多言語化)
- review-03 (L1): A2 PARTIAL (リソースクラスとアノテーションの結びつけ)
- review-08 (L1): A5 PARTIAL (例外時の他スレッド終了描写)

**C-only fail (2件)** — A は全 COVERED だが C あり
- impact-03 (L1): CONTRADICTION (他スレッドが「ロールバック」、KB は「正常終了」)
- review-01 (L1): CONTRADICTION (data_bind 前提で ValidatableFileDataReader 推薦)

**A+C fail (2件)**
- impact-08 (L1): A3 MISSING (@AssertTrue) + C UNSUPPORTED (「標準機能として提供されていない」を勝手に断言)
- req-10 (L1): A3 PARTIAL + C CONTRADICTION ($url$ プレースホルダの誤用)

**None (1件)**
- req-09: AI-1 が selections=[] を返して answer 未生成 (ビルトインなし質問)

## 次にやること (決まっていない — 根拠ある改善案を作る)

これまでの改善案は事実確認なしの思いつきだった。まず各件で **retrieved / answer / judge の 3 者の実データ突き合わせ** をして、真の原因を確定する。

**Steps (これを順にやる):**
- [ ] impact-01 を 1 件詳細分析 (retrieved の中に A1/A2 の根拠が書かれているか → AI-3 の削り問題か AI-1 の検索漏れか)
- [ ] 同じ手順で残り 13 件を分析
- [ ] 失敗パターンを事実に基づき分類
- [ ] 原因ごとに具体的な改善レバーを設計
- [ ] 効果の見込める順に 1 件ずつ適用 → 関連 scenario だけ rejudge で効果測定
- [ ] L1 以下がゼロになるまで繰り返す

## やらないことにした (スコープ外)

- current variant の改善 (PR スコープ外、比較用のみ)
- 他バージョン (v1.2/1.3/1.4/5) 適用は別 PR
- 30件一括 rerun (改善は該当 scenario のみピンポイントで測る)
- speed / cost を根拠とした採用提案 (L1 があれば速度は無関係)

## ユーザー判断待ち / 方針確認済み

- 合格ライン = L2 以上。L1 は Nabledge 品質基準で失格 (確認済)
- 改善ターゲットは ids のみ (確認済)
- 改善案はこれから事実ベースで作る (思いつき提案をやめる)

## 既知の bug / 対処済

- judge tool_use 壊れた input → `_is_well_formed_tool_input` フィルタで除外
- max_turns 2 で A 長いと切れる → 4 に引き上げ
- `list(string)` で char-list 化する事故 → `_facts()` type ガード

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
- [x] answer.md 改訂で ids 30件再計測
- [x] current variant は旧 baseline 流用と判断 (answer.md 非依存を確認)
- [x] `.claude/rules/development.md` 追記 (実出力目視・レビューに実行ログ添付)
- [x] judge 方式確定: A 事前準備 / B,C は KB (ref∪retrieved) 基準
- [x] scenarios JSON に `a_facts` フィールド追加、io/types/judge.py 改修
- [x] 30 scenario に A-fact を書いた (手書き 1 + Agent 草案 29 → 17件は私がレビュー修正)
- [x] ids 30件 rejudge (新 judge): mean=2.10, L3=16, L1=13, None=1
- [x] current 30件 rejudge (新 judge): mean=2.17, L3=18, L1=11, L0=1
- [x] ids L1 14件の失敗パターン分類 (judge output ベース)
