# Tasks: release nabledge-dev (marketplace next version)

**PR**: #353
**Issue**: #352
**Updated**: 2026-05-26

## 調査・判断の原則

すべての調査・判断はコード・ファイル・コマンド出力などの事実を確認した上で行う。推測で進めない。

## In Progress

## Not Started

### Task 8: 変更差分チェックとユーザー確認
**目的**: 全コミット対象：PRレビュー依頼前に変更差分が想定した変更のみであることを確認

**Steps:**
- [ ] `git diff main...HEAD --name-only` で全変更ファイルを列挙
- [ ] 各変更ファイルが Task 4〜6 のスコープに収まっていることを事実確認
- [ ] 想定外の変更がある場合はその原因を調査・対処
- [ ] 確認結果を `.work/00352/diff-check.md` に記録
- [ ] ユーザーに確認し、承認を得る（承認なしにPR作成へ進まない）
- [ ] commit: `docs: add diff check results for #352`

### Task 9: expert review
**目的**: `.claude/rules/expert-review.md` — PR作成前の品質保証

**Steps:**
- [ ] 変更対象（CHANGELOG.md、plugin.json、marketplace.json）のartifact typeを確認
- [ ] 適切なexpertを選定してレビュー実施
- [ ] Findingを全件修正
- [ ] レビュー結果を `.work/00352/review-by-{expert-role}.md` に保存
- [ ] commit: `docs: add expert review results for #352`

### Task 10: PR作成（既存 PR #353 を更新）
**Steps:**
- [ ] PR #353 のbodyをリリース内容を反映した最終版に更新
- [ ] Success Criteria を ✅ Met に更新

## Done

- [x] ブランチ作成: `352-release-nabledge` — initial
- [x] tasks.md 初期作成 — `c728b4cb1`
- [x] Task 1: コミット分析と作業記録 — `776c9d993`
- [x] Task 2: CHANGELOG [Unreleased] 改訂案作成・ユーザー承認 — 会話で承認取得済み
- [x] Task 3: バージョン決定・ユーザー承認 — v6:0.8 / v5:0.3 / v1.4:0.2 / v1.3:0.2 / v1.2:0.2 / marketplace:0.9
- [x] Task 4: 全プラグイン CHANGELOG 更新 — `1cc82a8f2`
- [x] Task 5: plugin.json 更新 — `dac751819`
- [x] Task 6: marketplace ファイル更新 — `8a9207f08`
- [x] Task 7: 前回リリースPRとの比較確認 — 必須4ファイルセット揃い確認済み（会話内）
