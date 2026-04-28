---
# Tasks: fix handler docs raw HTML in nabledge-1.x

**PR**: #315
**Issue**: #312
**Updated**: 2026-04-28

**Note**: rbkc.sh は `tools/rbkc/` から実行する（`cd tools/rbkc && bash rbkc.sh ...`）

## Not Started

### 4. PR
**Steps:**
- [ ] Expert review
- [ ] Create PR

## Done

- [x] Issue #312 fetched and branch `312-fix-handler-docs-raw-html` created
- [x] Task 1: Investigate and design — completed
- [x] Task 2: Prototype + Bug 1/2/3 fix + design extension — `224c2a669`, `496d6d6f2`, `52c1d59a1`
  - Bug 1: visit_image で height/width=0 不可視画像を抑制
  - Bug 2: visit_raw Block 3 検出をポジションベースに修正
  - Bug 3: docs.py で title 空時の先頭空行除去
  - 拡張: handler table にクラス名・入力型・結果型列追加
- [x] Task 3: Full implementation — verify FAIL 対応 — all 5 versions: 0 FAILs
  - v6/v5: 0 FAILs（変更前から）
  - v1.4/v1.3/v1.2: verify.py QL1 invisible image false positive 修正 → 0 FAILs
  - verify 変更: false positive 修正（acceptable change per rbkc.md）
  - コメント・docstring・設計書をRBKC独立性原則に準拠した記述に修正 — `6201761bd`
  - Horizontal check: :file: + raw::html は v1.x のみ（v5/v6 なし）
  - Post-mortem: `.work/00312/postmortem-handler-raw-html.md`
