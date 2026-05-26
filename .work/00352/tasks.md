# Tasks: release nabledge-dev (marketplace next version)

**PR**: TBD
**Issue**: #352
**Updated**: 2026-05-26

## 調査・判断の原則

すべての調査・判断はコード・ファイル・コマンド出力などの事実を確認した上で行う。推測で進めない。

## In Progress

### Task 1: コミット分析と作業記録
**目的**: `release.md` Step 1 — 前回リリース(marketplace 0.8, 2026-03-30)以降のコミットを事実ベースで分類し、作業記録に残す

**Steps:**
- [ ] 前回リリース以降でデプロイ対象ファイル(`sync-manifest.txt`記載パス)に触れるコミットを列挙
- [ ] 各コミットのユーザー影響を「あり/なし」で分類（推測不可、`git show --stat`で確認）
- [ ] 各プラグイン(v6/v5/v1.4/v1.3/v1.2)の `[Unreleased]` 内容がコミット分析結果と一致するか確認
- [ ] 分析結果を `.work/00352/notes.md` に記録
- [ ] commit: `docs: add commit analysis and release notes for #352`

## Not Started

### Task 2: CHANGELOG [Unreleased] 内容の確認・改訂とユーザー承認
**目的**: `release.md` Step 2 — [Unreleased]内容をユーザー視点に整え、承認を得る

**Steps:**
- [ ] Task 1の分析結果をもとに、全プラグインの `[Unreleased]` 改訂案を作成
  - 技術詳細の除去、ユーザー視点への書き換え、`changelog.md`ライティングルール適用
- [ ] 改訂案をユーザーに提示し、承認を得る（承認なしに次タスクへ進まない）

### Task 3: バージョン決定とユーザー承認
**目的**: `release.md` Step 3の前提 — 各プラグインとmarketplaceの新バージョンを算出してユーザーに承認

**Steps:**
- [ ] 現在バージョンを事実確認（`plugin.json` × 5、`marketplace.json`を実際に読む）
- [ ] `release.md`のバージョンルール（MINOR/PATCH、marketplace = 最高プラグインバージョン）に基づき算出
- [ ] 算出結果をユーザーに提示し、承認を得る（承認なしに次タスクへ進まない）

### Task 4: 全プラグイン CHANGELOG 更新
**目的**: `release.md` Step 3 — 全プラグインのCHANGELOG [Unreleased]を承認済みバージョン節に変換

**Steps:**
- [ ] Task 2・3で承認済みの内容・バージョン・日付でCHANGELOGを更新 (nabledge-6/5/1.4/1.3/1.2 すべて)
  - `[Unreleased]` → `[X.Y] - YYYY-MM-DD` に変換
  - ファイル末尾にタグリンクを追記
- [ ] commit: `release: move [Unreleased] to versioned section in all plugin CHANGELOGs`

### Task 5: plugin.json 更新
**目的**: `release.md` Step 3 — 全プラグインの plugin.json バージョンを更新

**Steps:**
- [ ] 全プラグインの `plugin.json` バージョンをTask 3承認済み番号に更新 (nabledge-6/5/1.4/1.3/1.2)
- [ ] commit: `release: bump version in all plugin.json files`

### Task 6: marketplace ファイル更新
**目的**: `release.md` Step 3 — marketplace.json と marketplace CHANGELOG.md を更新

**Steps:**
- [ ] `marketplace.json` のバージョンをTask 3承認済み番号に更新
- [ ] `marketplace/CHANGELOG.md` のバージョン表に新行を追記
- [ ] commit: `release: update marketplace.json and marketplace CHANGELOG.md`

### Task 7: 前回リリースPRとの比較確認
**目的**: `release.md` Step 4 — 必須ファイルセットに欠落がないか確認

**Steps:**
- [ ] 前回リリースPR (#280) と今回の変更ファイルセットを突き合わせ
- [ ] 必須4ファイル（plugin CHANGELOG × n、plugin.json × n、marketplace.json、marketplace CHANGELOG）が揃っていることを確認
- [ ] 確認結果を `.work/00352/notes.md` に記録（欠落がある場合は修正してから次へ）

### Task 8: 変更差分チェックとユーザー確認
**目的**: 全コミット対象：PRレビュー依頼前に変更差分が想定した変更のみであることを確認

**Steps:**
- [ ] `git diff main...HEAD` で全変更ファイルを列挙
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

### Task 10: PR作成
**Steps:**
- [ ] `Skill(skill: "pr", args: "create")` でPRを作成

## Done

- [x] ブランチ作成: `352-release-nabledge` — initial
- [x] tasks.md 初期作成 — this commit
