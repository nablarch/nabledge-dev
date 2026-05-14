# Tasks: Maintain verify design quality assurance matrix accuracy

**PR**: #342
**Issue**: #321
**Updated**: 2026-05-14

## In Progress

### Task 3: rbkc 設計書全般を実装を知らない読者にも分かるように更新

**目的**: 実装を知らないユーザーが設計書を読んで理解できるよう、前提知識の説明・用語定義・構造説明を補完する。情報は落とさない。

**対象ファイル**:
- `tools/rbkc/docs/rbkc-verify-quality-design.md`
- `tools/rbkc/docs/rbkc-converter-design.md`
- `tools/rbkc/docs/rbkc-json-schema-design.md`

**Steps:**
- [ ] 対象設計書を通読し、理解困難な箇所を `.work/00321/notes.md` に列挙（事実ベース）
- [ ] 補完内容をユーザーに提案して承認取得
- [ ] 承認後、各設計書を更新
- [ ] 変更差分チェックして `.work/00321/diff-check.md` に追記
- [ ] コミット

---

### Task 4: 変更差分チェック（全タスク統合・PRレビュー依頼前）

**目的**: PRレビュー依頼前に変更差分が Task 1〜3 の想定範囲のみかを確認する。

**Steps:**
- [ ] `git diff main` を実行して全変更差分を確認
- [ ] 想定外の変更（対象ファイル以外、意図しない削除等）がないかチェック
- [ ] チェック結果を `.work/00321/diff-check.md` に記録
- [ ] ユーザーに確認

## Done

- [x] Task 1: シンボル統一（⚠️ 廃止、§3-x と §4 を ✅/❌/— に揃える） — committed `8466ac7`
- [x] Task 2: 全 ✅ 項目の bias-avoidance QA レビュー実施 — v6 FAIL 0 確認、QA レビュー 0 Findings、test fixes committed `436798e`

---

## 原則: 推測せず事実ベースで調査・判断

- **調査**: コードを実際に読んで確認する。「〜のはず」で判断しない
- **作業**: 設計書の文言と実装の事実に基づいて変更する
- **判断**: 数値・ファイル内容・実行結果等の具体的な証拠を示してから判断する
- 不明な点はユーザーに確認する（推測で進めない）
