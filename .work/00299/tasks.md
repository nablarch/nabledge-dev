# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-24 (session 68 — skill v6 同期完了)

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

(なし — 次は Not Started から着手)

## Done — session 67 (C8: RBKC create/verify 再生成で発覚した 2 問題を修正)

知識ファイルを v6 と同じ構造に揃える前段として `rbkc.sh create/verify` を全 5 バージョン実行。
結果: v6/v5 は commit 済と完全一致、**v1.3/v1.2 は dict→list 形式で大量差分** (想定内)、
**v1.4 だけ 161 files と大幅減少** (前回 455)。JSON sections は全 5 バージョン `list` に統一済。

発覚した 2 問題とその決着:

**P1: v1.4 mapping の `document/` prefix 余剰**
- `rel_for_classify()` は v1.4 で `document/` marker を strip する仕様 (file_id.py:75-77)
- v1.4 mapping は `document/FAQ/` 等 prefix 付きで書かれていたためマッチ不能 (v1.3/v1.2 には prefix 無し)
- 対応: mapping から `document/` prefix 除去 + 空 pattern + sample/portal 重複除去 (65→58 entries) — commit `69a876c19`

**P2: ERROR/3 `system_message` の過剰停止**
- 当初: `tool/07_AuthGenerator/01_AuthGenerator.rst` の "Inconsistent title style" (overline+underline と underline-only 混在) で v1.4 全体停止
- 調査: docutils parse 自体は成功 (AST 13 section 保持)、Sphinx も HTML build 継続、ERROR/3 は convention 警告であり RST 文法違反ではない
- エキスパート 2 名 (SE / Prompt Engineer) 相談結果: Option B (policy inversion) 採用
  - spec §3-1b 原則 4 と §3-2-3 書き換え: level ≥ 4 (SEVERE) のみ QC1 FAIL、level ≤ 3 は warning 記録で render 継続
  - content 損失検出は独立機構 (UnknownNodeError / UnknownRoleError / UnresolvedReferenceError / verify QC1 残存チェック) が担う
  - corpus 実測で全 5 バージョン "Unknown directive type" 0 件。Sphinx が HTML に出さない内容は RBKC も出さないのが §3-2-3 正解
- spec 更新 `f1009f243`、visitor/normaliser 実装 + tests `dadfcea13`

**Steps:**
- [x] P1 mapping 修正 — commit `69a876c19`
- [x] P2 方針転換 (Option B 採用) — エキスパート相談済み
- [x] P2 spec 更新 — commit `f1009f243`
- [x] P2 実装 (visitor / normaliser) + tests 再構成 — commit `dadfcea13` (376 tests GREEN)
- [x] v1.4 create/verify: 489 files (161→489 回復)、verify OK
- [x] 全 5 バージョン horizontal check: v6=353 / v5=533 / v1.4=489 / v1.3=327 / v1.2=321、全て "All files verified OK" (FAIL 0)
- [x] 生成物 commit: v1.4 `ed8161f10`, v1.3 `3b7515ce3`, v1.2 `fb0cc138a`

## Not Started (次 session で着手)

### v5 / v1.4 / v1.3 / v1.2 nabledge-test baseline 取得 (qa-001 単独)

v6 baseline 完了。v5 以降はフル baseline は取らず、**qa-001 単独 1 試行** のみで横展開確認する方針
(v6 で RBKC の構造的劣化は無しと確定済。v5 以降は同じ RBKC コード経路を通るため、代表シナリオ 1 本で
retrieval が壊れていないことを確認すれば足りる。費用対効果)。

- 対象: v5, v1.4, v1.3, v1.2 × qa-001 × 1 trial
- 実行方式: `nabledge-test <v> qa-001` (baseline mode は使わない — qa-001 のみの実行結果を baseline として手動保存)
- 保存先: `.claude/skills/nabledge-test/baseline/<v>/<run_id>/qa-001/` + `meta.json` に `scenarios_count: 1, scope: "qa-001 only (smoke)"` を記録

**Steps:**
- [ ] v5 × qa-001 実行 → baseline 保存 + latest シンリンク更新
- [ ] v1.4 × qa-001 実行 → baseline 保存 + latest シンリンク更新
- [ ] v1.3 × qa-001 実行 → baseline 保存 + latest シンリンク更新
- [ ] v1.2 × qa-001 実行 → baseline 保存 + latest シンリンク更新
- [ ] 4 バージョン分の結果を main (kc) 比較し、retrieval 劣化が無いことを記録

### nabledge-5 / nabledge-1.4 / nabledge-1.3 / nabledge-1.2 skill 側の v6 同期 — 残: retrieval smoke のみ

当初の想定 (jq 式差分のみ) より広く、`.claude/rules/nabledge-skill.md` L5
"share identical structure for prompts, workflows, templates, and scripts (path substitution only)"
に反する同期漏れが複数あった。

**Done (未コミット):**
- [x] `scripts/full-text-search.sh` jq 式を v6 と揃える (v5/1.4/1.3/1.2) — `.sections[]` + `title+content` score
- [x] `scripts/get-hints.sh` 削除 (v6 で廃止済, 余剰残存)
- [x] `scripts/prefill-template.sh` の `nabledge-6` ハードコード修正 → 各バージョン参照 (重大バグ: ca-* が他バージョンで v6 dir を見ていた)
- [x] `workflows/_knowledge-search.md` を v6 同期 (Step 5 インライン jq 化 / section-search 廃止)
- [x] `workflows/_knowledge-search/_section-judgement.md` を v6 同期 (Step 0 hints pre-filter 削除)
- [x] `workflows/_knowledge-search/_index-based-search.md` を v6 同期 (Step 2 インライン jq 化)
- [x] `workflows/_knowledge-search/_section-search.md` 削除 (v6 で廃止済, 余剰残存)
- [x] sanity: 4 バージョンで full-text-search.sh が検索ヒット返すこと確認

**残存差分 (バージョン固有の正当差分 — 同期対象外):**
- `workflows/code-analysis.md` L103: Jakarta EE vs Java EE
- `assets/code-analysis-template*.md`: Knowledge Base 表示名 / nablarch.github.io LATEST vs 5-LATEST vs 1.x URL

**Steps:**
- [ ] commit & push (4 バージョン × 7 ファイル変更を 1 コミットで横展開)
- [ ] nabledge-test qa-001 smoke で retrieval が動くこと確認 (4 バージョン)

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

