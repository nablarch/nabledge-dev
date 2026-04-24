# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-24 (session 65)

---

## 現状

- **22-B-12 完了** (`3dd3d483f`): 全 5 バージョンで verify FAIL 0 (`.work/00299/baseline-22-B-12-final/SUMMARY.md`)
- 377 tests GREEN

## Done (session 65)

- [x] ws1: 5 バージョン post-fix ベースライン取得 — `ca1d880ce`
- [x] Finding A: v1.2 Excel preamble-as-parent — `4b6d598f1` (v1.2 8299 → 118)
- [x] Finding B: QO2 pipe-escape false-positive — `9b3d5d032` (v1.3/v1.2 QO2 -1 each)
- [x] Finding C: "Unknown target name" Sphinx 追従化 — `2e45cea4d` (v1.3/v1.2 QC1 -1 each)
- [x] ws3: resolver AST walk for include-follow — `3dd3d483f` (v1.3 118→0 / v1.2 116→0)

---

## Not Started

### nabledge-test ベースライン再取得 (v6 + 他バージョン)

22-B-12 完了後に実施。resolver 書き換え + Excel v1.2 大幅改善で出力が変わるため、
22-B-13b の v6 baseline (`20260424-103200`) を再取得し、v5 / v1.4 / v1.3 / v1.2 も
順次取得する。各バージョンで直近 baseline と比較して劣化なしを確認。

### 配信物クリーン化 + ドキュメント整備

全バージョン baseline 取得後:
- setup スクリプトのゴミ残り対策 (`tools/setup/setup-cc.sh` / `setup-ghc.sh`): vup 時に旧 `.claude/skills/nabledge-${v}/` を完全削除してから `cp -r`
- 各バージョン CHANGELOG `[Unreleased]` への「ルールベース化」追記
- `tools/rbkc/README.md` を現状構成に書き直し
- `.work/00299/notes.md` を Phase 21-Y〜22 要約に圧縮
