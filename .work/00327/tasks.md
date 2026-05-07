# Tasks: fix: format PCIDSS table in security-check-3 docs (v5/v6)

**PR**: #332
**Issue**: #327
**Updated**: 2026-05-07 (session 2)

## Rules

- **調査・作業・判断はすべて事実ベースで行う**: 推測・推論・「おそらく〜」は禁止。コード/ファイルを実際に読んで確認してから判断する
- **変更前に影響範囲を網羅的に列挙**: サンプリングではなく、影響するすべてのファイル・行を特定してから着手する
- **設計決定は根拠を明示**: 選択した理由とその根拠（ファイル名・行番号・仕様条文）を必ず記録する

## Done

- [x] ブランチ作成 `327-format-pcidss-table`
- [x] 対象ファイル調査（v6, v5 とも同一内容28行、テーブルがフラットテキスト）
- [x] Task 1: tasks.md 作成・コミット — `9f9e7c040`
- [x] Task 2: プレビューMD作成・コミット・PR作成・ユーザー確認依頼 — `9f9e7c040` / PR #332

## In Progress

### Task 3: v6・v5 ファイルへのMarkdownテーブル適用

**対象ファイル（2ファイル、同一内容）:**
- `.claude/skills/nabledge-6/docs/check/security-check/security-check-3.PCIDSS対応表.md`
- `.claude/skills/nabledge-5/docs/check/security-check/security-check-3.PCIDSS対応表.md`

**決定事項（このセッションで確定）:**
- フォーマット: 脚注スタイル（※1〜※3 をテーブル外に置く）— preview-security-check-3.md のまま採用
- 根拠: ユーザーがレビューコメントへの返信で「今までと同じスタイルでいきましょう」と確認 (2026-05-07)
- このファイルは RBKC 生成対象外（Mapping 未登録）。手動編集のみで対応可。RBKC ロジック追加不要。

**Steps:**
- [ ] v6 ファイルを preview-security-check-3.md の内容で更新
- [ ] v5 ファイルを preview-security-check-3.md の内容で更新
- [ ] 1コミットでv5・v6 まとめてコミット（クロスバージョン一括変更ルール）

## Not Started

### Task 4: 変更差分チェック → ユーザー確認

PRレビュー依頼前に変更差分が想定した変更のみかを確認する。

**Steps:**
- [ ] `git diff main...HEAD` で変更内容を確認
- [ ] .work/00327/diff-check.md に差分チェック結果を記録
- [ ] コミット & プッシュ
- [ ] ユーザーに差分確認依頼

### Task 5: エキスパートレビュー（Technical Writer）

**前提:** Task 4 でユーザーが差分を確認・承認済みであること

**Steps:**
- [ ] Technical Writer エキスパートレビュー実行
- [ ] .work/00327/review-by-technical-writer.md に保存
- [ ] コミット & プッシュ

### Task 6: PR レビュー依頼

**Steps:**
- [ ] PR ボディにエキスパートレビューリンクを追加
- [ ] ユーザーにレビュー依頼

## Success Criteria Check

| 基準 | 対応タスク |
|------|-----------|
| v5・v6 両ファイルが Markdown テーブル形式（ヘッダ行＋区切り行＋データ行） | Task 3 |
| 10要件（6.5.1〜6.5.10）とチェックリスト対応が全件保持 | Task 3 |
| 長いセル内容（注記・説明）がインラインまたは脚注として保持 | Task 2 (設計確認) |
| GitHub Markdown プレビューでテーブルとして正しくレンダリング | Task 2 (確認) |
