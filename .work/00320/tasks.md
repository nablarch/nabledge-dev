# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-08

## In Progress

### Task 13: Fix RBKC create — cross-doc section_title missing from sections[]

verify FAIL 0件 は §4 マトリクス ✅ 成立条件 3。現在 v6:38, v5:48, v1.x:28-32 FAIL。

**⚠️ 不変ルール — このタスク全体を通じて厳守する:**
- **目的は「FAIL を消すこと」ではなく「設計書 `rbkc-verify-quality-design.md` の品質基準が RBKC 出力に対して検証済みであること」**
- verify は品質ゲート。verify が FAIL を報告した場合、原因は RBKC create 側にある。verify の判定ロジックを緩和することで FAIL を消してはならない
- RBKC の修正は「正しい出力を生成するように create を直す」こと。verify の基準に合わせるのではなく、仕様に合わせる
- 修正案を考えた時点でユーザーに提案し承認を得てから実装する。勝手に実装しない
- verify が FAIL するたびに「これは本当に RBKC の誤りか、それとも verify の誤検出か」を仕様書で確認してから対処する

**Root cause (確定):**
- h1 直前ラベルに `section_title=h1_title` / `anchor=github_slug(h1_title)` が設定されていた
- JSON スキーマ上 h1 は `title` のみ（`sections[]` に入らない）→ verify が誤って FAIL
- fix: `labels.py` `build_label_doc_map()` で `title == doc_title` なら `section_title=""` / `anchor=""`

**Steps:**
- [x] v6 FAIL パターンを列挙・分類（root cause 特定）
- [x] RBKC create 修正（TDD: RED→GREEN、484件全テスト GREEN）
- [x] 全5バージョン create + verify — v6:38, v5:48, v1.4:32, v1.3:28, v1.2:32
- [x] 残存 FAIL の root cause を仕様書で確認・分類
  - **Root cause A（解消済み）**: `-->` (HTML/JSP コメント閉じ) が見出し下線として誤検出 → `_is_heading_underline()` に「同一文字の繰り返し」条件を追加 → v6:0, v5:0
  - **Root cause B（残存）**: RST simple table のセパレーター行（`======= =======` 形式）が見出し下線として誤検出 → v1.4:28, v1.3:24, v1.2:28 の原因
  - Root cause B の具体例: `04_Connection.rst` のテーブル内セル `nablarch.core.db.connectionパッケージ` が見出しとして解決される
- [x] Root cause B の修正実装（TDD: simple table セパレーター行を見出し検出からスキップ）
- [x] Root cause C の修正実装（TDD: インデントされたコードブロック内 `###...` を見出し検出からスキップ）
- [x] subtitle バグ修正（TDD: docutils subtitle promotion → section として追加）
- [x] 全5バージョン create + verify — FAIL 0件確認（v6:0, v5:0, v1.4:0, v1.3:0, v1.2:0）
- [x] 設計書 §4 マトリクス QL1 — 既に ✅（Task 9 で更新済み）
- [x] PR #330 SC を ✅ に更新
- [ ] commit & push

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Task 1: Design review completed
- [x] Task 2: `TestCheckSourceLinks_JsonSide` added — committed `197bc96`
- [x] Task 3: `TestCheckSourceLinks_DocsMdSide` added — committed `197bc96`
- [x] Task 4: JSON side anchor check in `check_ql1_link_targets()` implemented — committed `38e18cc`
- [x] Task 5: Docs MD side anchor check in `check_ql1_link_targets()` implemented — committed `38e18cc`
- [x] Task 6: FAIL diff recorded (v6:656 v5:658 v1.4:613 v1.3:578 v1.2:588) — committed `3928aa4`
- [x] Task 8: Expert review (QA + SE) — 2 Findings fixed — committed `3928aa4`
- [x] Task 9: Diff check — committed `267caa7`
- [x] Issue #320 SC revised + design doc §3-2-3 updated + §4 matrix ✅
- [x] Task 10: cross-doc :ref: validation in check_source_links() + expert review (1 Finding fixed) — committed `56b91449b`
- [x] Task 11: create/verify diff check — v6:1422, v5:1443, v1.4:262, v1.3:238, v1.2:283 — all expected — committed `3f217acf5`
- [x] Task 12: Issue #333 作成→クローズ（#320 スコープ内と判明）、PR #330 SC を ❌ Blocked に戻す
