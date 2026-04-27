# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-27 (final)

---

## 現状

- 22-B-12 code changes は commit 済 (`4b6d598f1`, `9b3d5d032`, `2e45cea4d`, `3dd3d483f`)
- **全 5 バージョン verify FAIL 0** 確認済
- 377 tests GREEN
- nabledge-test runner は model: sonnet 固定 (`nabledge-test-runner.md` frontmatter)
- PR #304 push 済 — **全バージョン knowledge/docs 再生成済み**

---

## In Progress

(なし)

## Not Started

(なし)

## Done

- [x] knowledge/docs 再生成 (全5バージョン) — `93fa83ea2`, `0d013db6e`, `88fb69aa2`, `7ece2e5a6`, `df0055f55`
- [x] 22-B-12 実装 (Finding A/B/C + ws3) — `4b6d598f1`, `9b3d5d032`, `2e45cea4d`, `3dd3d483f`
- [x] v1.4 mapping `document/` prefix 修正 — `69a876c19`
- [x] Sphinx-follow policy (ERROR/3 → warning) spec + 実装 — `f1009f243`, `dadfcea13`
- [x] v1.4/v1.3/v1.2 知識ファイル再生成 — `ed8161f10`, `3b7515ce3`, `fb0cc138a`
- [x] nabledge-5/1.4/1.3/1.2 skill 構造を v6 に同期 — `b06d8cf23`
- [x] v6 nabledge-test baseline 取得 (20260424-172654)
- [x] v5/1.4/1.3/1.2 qa-001 smoke baseline 取得 (20260424-201710)
- [x] setup スクリプト: 旧 skill dir 削除してから cp — `d496683bf`
- [x] RBKC README 現状構成に書き直し — `66a23db94`
- [x] CHANGELOG `[Unreleased]` ルールベース化追記 — `fac51b221`
- [x] `work-log.md` に `.work/` は常に git 対象である旨追記
- [x] kc 削除 + metrics kc→rbkc 置換 — `dae508c7f`, `0b7485008`
