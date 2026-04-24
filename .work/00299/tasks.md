# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-24 (session 66 — C7 v6 baseline done 20260424-172654)

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

v6 baseline 完了。次は順次。

## Done — session 66

### C7: v6 nabledge-test baseline 取得 (20260424-172654)

- Overall 94.5% (QA 90.0% / CA 96.2%)、前回 20260424-103200 (95.9%) から -1.4pp は LLM サンプリング分散
- v6 配信物は C6 で byte identical 確認済のため構造的劣化ではない
- qa-001 benchmark: [75, 75, 62.5]% → mean 70.8% ±7.2% (前回 75.0 ±21.6)、SD 収束方向
- ca-003 benchmark: [97.3, 97.3, 97.3]% 完全固定 (Overview の BusinessDateUtil 欠落、既知の skill 側課題)
- 各 trial の response.md は runner 出力をそのまま保存 (偽造なし)
- baseline: `.claude/skills/nabledge-test/baseline/v6/20260424-172654/`、latest symlink 更新済
- comparison-report.md: 分析セクション埋め込み済

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
