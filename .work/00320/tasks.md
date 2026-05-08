# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-08

## Not Started

### Task 15: 設計 — `scripts/common/labels.py` + verify リンク照合

**背景:**
前回の実装（Tasks 1–14）はリバート済み（commit `8673f77a5`）。
原因: verify の QL1 チェックが「リンク先が存在するか」しか見ておらず、
「RST が意図したページ・セクションを指しているか」を検証していなかった。
そのため RBKC が間違ったリンクを生成しても PASS してしまっていた。

**設計方針（エキスパートレビュー済み、ユーザー承認待ち）:**
- Option C: `scripts/common/labels.py` を新設し、create / verify 両方が使う
- `labels.py`: RST ファイルをスキャンして `label → (file_id, section_title)` マップを構築（RBKC ロジックを含まない）
- verify: labels.py のマップで「RST が意図した section_title」を取得 → 生成 MD のリンクを辿って target `.md` の実際のページタイトル・セクションタイトルと照合
- create: 同じ `labels.py` を使って解決

**Steps:**
- [ ] 設計書 §3-2-3 の QL1 照合ロジックを更新（labels.py の役割・インタフェース定義）
- [ ] `scripts/common/labels.py` のインタフェース設計（入出力・テスト fixtures）
- [ ] verify リンク照合ロジックの詳細設計
- [ ] ユーザーへ設計確認依頼 [DECISION: 設計方針の承認]

### Task 16: 実装

**Steps:**
- [ ] TDD: `TestLabels_*` テスト追加（RED）
- [ ] `scripts/common/labels.py` 実装（GREEN）
- [ ] TDD: verify QL1 リンク照合テスト追加（RED）
- [ ] verify QL1 リンク照合実装（GREEN）
- [ ] 全5バージョン verify 実行、FAIL diff 確認

## In Progress

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
  - リバート理由: verify が「リンク先存在チェック」のみで「意図したリンクか」を検証しておらず、
    RBKC の heading 修正が正しいリンクを壊しても FAIL しなかった
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
