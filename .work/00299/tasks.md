# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-24 (session 66 — C7 v6 baseline 20260424-172654 main 比較追記)

---

## 現状

- 22-B-12 code changes は commit 済 (`4b6d598f1`, `9b3d5d032`, `2e45cea4d`, `3dd3d483f`)
- **全 5 バージョン verify FAIL 0** 確認済 (`baseline-22-B-12-final/SUMMARY.md`)
- 377 tests GREEN
- Option F (NABLEDGE_OUTPUT_ROOT env override) は revert 済 (`8315683cb`) — 実測時の LLM compliance 33% でゼロトレランス非達成。並列 trial 独立性の深追いはやめて、main baseline 方式に戻す
- ワーキングツリー clean、`.tmp/` / `.nabledge/` 掃除済
- nabledge-test runner は model: sonnet 固定 (`nabledge-test-runner.md` frontmatter)

---

## 作業方針 (見直し後)

baseline 取得は create/verify の生成物が安定してから。C3/C4/C6 で生成物の品質が動く可能性があるため、それらを全部潰してから baseline を取る (そうしないと C7 で取った v6 baseline も後から取り直しになる)。

## In Progress

### v5 / v1.4 / v1.3 / v1.2 nabledge-test baseline 取得

v6 baseline 完了。v5 以降はベンチマーク 3 試行は実施せず、**coverage 1 試行** のみで baseline 取得する方針 (v6 で LLM ゆらぎが -2.8pp 以内で安定、構造的劣化の検出には 1 試行で十分、費用対効果)。scenarios.json の `benchmark: true` フラグは尊重しつつ `--baseline` 運用上は 1 試行扱いにする。

進捗: v5 は coverage batch 実行済・response/metrics 保存の途中で中断。v5 継続 → v1.4 → v1.3 → v1.2 の順に進める。

## Done — session 66

### C7: v6 nabledge-test baseline 取得 (20260424-172654)

本当の比較元は main 系 20260331-152005 (commit e55c25c3、kc + AI hints 時代)。299 ブランチ中途 20260424-103200 との比較は「中間状態比較」であり合否判定用には不適切。

**main (kc) baseline との差分**:
- 総検出: 142/146 (97.3%) → 138/146 (94.5%) = -2.8pp (4 項目)
- 合計実行時間: 1182 秒 → 944 秒 = **-238 秒 (-20%)**
- 出力トークン合計 (response_chars/4 推定): 18,382 → 10,356 = **-8,026 (-44%)**

**欠落 4 項目の事実確認** (retrieval vs 生成):
- qa-001 `listName` / `element*Property`: 対象 file は RBKC でも citation あり、hints にも含まれていた。しかし他キーワード経由で retrieval は成功している → 生成選択の揺らぎ (codeSelect 偏重)
- qa-002 `pageNumber`: 対象 file は citation あり、**kc hints に `pageNumber` は含まれていなかった** (前回通ったのは生成が偶然 Form 定義例を書いたため)。grader case sensitivity (`getPageNumber()` vs `pageNumber`) が主因
- ca-001 Overview `SessionUtil` / class-diagram `ProjectDto`: ソース解析タスクで hints 無関係、本文には言及あるが Overview / class-diagram の要約層で落ちた → workflow テンプレート側の粒度問題

**結論**:
- 時間 -20% / 出力 -44% は hints 2 段ゲート廃止による過剰読み込み削減の効果。明確な改善
- 精度 -2.8pp は retrieval 失敗ではなく生成選択の揺らぎ + grader 厳密性 + workflow テンプレート粒度
- **AI 生成ゆらぎを含めた厳密判定は原理的に不可能**。3 試行ベンチマークは前回と CI 重複、統計的に有意な劣化なし
- 本 baseline を合格とみなし、以降の比較の固定点として採用

改善提案 (別 issue 化候補): (1) grader の case-insensitive 化、(2) qa-001 シナリオ分割、(3) code-analysis workflow の Overview/class-diagram 粒度強化。詳細は `comparison-report.md` と `report-202604241726.md` 参照。

### 処理フロー差分 (事実確認)
kc 検索 → RBKC 検索で構造変更は 3 箇所: (1) Step 5 section search サブワークフロー廃止、(2) Section judgement Step 0 hints 事前フィルタ削除、(3) full-text-search.sh の jq 式変更 (sections dict → array、hints 含まず title+content のみ)。index.toon 列構造と keyword-only retrieval の方針は共通。

## Done — Stabilization (session 66)

### C3 / C4 / C6 — create/verify 安定化 (see `c3-c4-c6-results.md`)

- **C3**: "Unknown target name" filter は silent skip でない。v6/v5/v1.4 = 0 件、v1.3/v1.2 = 2 件 (同一箇所 07_BasicRules.rst:6 を 2 経路から再 parse しているため)。想定通り。
- **C4**: ws3 resolver の差分は v1.3/v1.2 で 64-65 asset dir 追加のみ、byte 差分 / 削除 = 0。追加は全て docs MD が `![…](…)` で参照する asset (include 先 RST の `image::` をようやく拾った)。余分コピーではない。
- **C6**: v6 は 22-B-12 前後で完全一致 (knowledge 677 / docs 354, added=removed=differ=0)。副作用ゼロ確認。

### C1, C2 — Done (session 65)

- C1: Finding B 事後承認 (commit `9b3d5d032` keep) — session 65 user approval
- C2: Option F 方針断念・revert (`8315683cb`)。main baseline で運用されてきた並列方式 (race は known limitation) に戻す。偽造部分は C7 再取得でクリア

## Not Started

### 配信物クリーン化 + ドキュメント整備

全バージョン baseline 取得後:
- setup スクリプト (`tools/setup/setup-cc.sh` / `setup-ghc.sh`): vup 時に旧 `.claude/skills/nabledge-${v}/` を完全削除してから `cp -r`
- 各バージョン CHANGELOG `[Unreleased]` への「ルールベース化」追記
- `tools/rbkc/README.md` を現状構成に書き直し
- `.work/00299/notes.md` を Phase 21-Y〜22 要約に圧縮

---

## 本 PR 対象外 (別 issue)

### C5: Finding A guard (`len(parents) >= 2`) の将来リスク

corpus 95/95 で該当なしのため現時点 risk=0。spec `rbkc-converter-design.md` §8-3 に「parent row ≥ 2 non-empty cells 必須」を明文化する作業は別 issue で。
