# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-24 (session 65 — tasks re-ordered after C2 revert)

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

## In Progress — create/verify 安定化 (baseline 取得前に完了必須)

### C3: "Unknown target name" filter が silent skip 化していないか確認

Finding C (`2e45cea4d`) で 2 箇所に filter 追加 (rst_normaliser / rst_ast_visitor)。WARN は `warnings_out` 経由で stderr に出るが件数を集計していない。

**Fix**:
- 5 バージョンで create + verify を走らせ、stderr の "Unknown target name" を含む WARN を grep して件数記録
- 想定: 07_BasicRules.rst (v1.3/v1.2 各 1 件) + 他に同構文あれば数件
- 想定を大幅超過したら silent skip を疑い追加調査

### C4: ws3 resolver AST 書き換えの挙動差分を確認

旧 regex `:download:`label <path>`` は `<>` 必須、新 AST は `<>` なし `:download:`path`` も拾う。verify FAIL 0 は「コピー漏れなし」は保証するが「余分コピーなし」は保証しない。

**Fix**:
- 22-B-12 前後で 5 バージョンの `knowledge/assets/` ツリーを `diff -r` で比較
- 差分を吟味し、妥当でなければ resolver を regex 時代と同じ条件に絞る

### C6: v6 生成物 byte-level diff 未確認

22-B-12 の fix は v1.x ターゲットだが resolver AST 化は全版に効く。v6 knowledge/docs の byte diff は未確認。

**Fix**:
- 22-B-12 前 (1 commit 戻した状態) と 後 (`3dd3d483f`) で v6 `knowledge/` と `docs/` を `diff -r` で比較
- 差分があれば内容を吟味 (ある・ないどちらも事実として記録)
- C3/C4 と連動する可能性あり

### C1, C2 — Done

- C1: Finding B 事後承認 (commit `9b3d5d032` keep) — session 65 user approval
- C2: Option F 方針断念・revert (`8315683cb`)。main baseline で運用されてきた並列方式 (race は known limitation) に戻す。偽造部分は C7 再取得でクリア

## Not Started

### C7: v6 nabledge-test baseline 再取得

C3/C4/C6 完了後に実施。runner は Sonnet 固定 (`nabledge-test-runner.md` frontmatter)。trial の response.md をコピー偽造しない、各 runner 応答をそのまま保存すること (今回偽造の反省)。

### v5 / v1.4 / v1.3 / v1.2 nabledge-test baseline 取得

v6 baseline 成功後に順次。

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
