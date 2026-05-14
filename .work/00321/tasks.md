# Tasks: Maintain verify design quality assurance matrix accuracy

**PR**: #342
**Issue**: #321
**Updated**: 2026-05-14

## In Progress

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
- [x] Task 3: 設計書に §0「この文書を読む前に」追加 — 3 文書に全体像・用語定義・前提知識を補完、committed `2bf704f`

---

## 原則: 推測せず事実ベースで調査・判断

- **調査**: コードを実際に読んで確認する。「〜のはず」で判断しない
- **作業**: 設計書の文言と実装の事実に基づいて変更する
- **判断**: 数値・ファイル内容・実行結果等の具体的な証拠を示してから判断する
- 不明な点はユーザーに確認する（推測で進めない）
