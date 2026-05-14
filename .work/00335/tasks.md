# Tasks: fix: verify QC2 Excel residue check silently exempts MD structural tokens not authorized by spec

**PR**: #341
**Issue**: #335
**Updated**: 2026-05-14 (complete)

## Rules

- 推測せず事実ベースで調査・作業・判断する
  - コードを読まずに動作を推測しない — 必ずgrep/実行で確認する
  - spec文書を参照せずに「specに書いてある」と言わない — 必ず該当箇所を引用する
  - 変更影響範囲は網羅的に調査する（サンプリング不可）
  - 投機的な根拠で設計判断しない — 測定値と spec 引用で判断する
- rbkc create/verify で FAIL が出たら、create と verify のどちらに問題があるかバイアスなくフラットに判断する
  - インプット（ソースファイル）とアウトプット（生成 JSON）を実際に確認する
  - verify が FAIL を出した事実だけで「verify が間違い」と結論しない
  - create が生成した JSON の内容を spec と照合して「JSON 側の問題か、verify 側の問題か」を事実で判定する
  - 判定根拠は spec 条項の引用と実際の入出力テキストで示す

## In Progress

## Not Started

## Done

## Done

- [x] tasks.md 初版作成・ブランチ作成 (`335-fix-verify-qc2-md-syntax-exemption`)
- [x] Task 1: notes.md 作成 — committed `5eab22f5d`
- [x] Task 2: 設計書 §3-1 P1コロン例外追記・ユーザー承認済み — committed `642f5eace`
- [x] Task 3+4: TDD RED — `|` と `---` のFAILテスト追加 — committed `f510b1520`
- [x] Task 5+6: 実装修正（`_MD_SYNTAX_RE` 削除、P1限定コロン除外）+ 捏造テスト削除 — committed `4cbbefe2e`
- [x] Task 7: 全5バージョン verify 実行・FAILカウント比較（全0） — committed `cf1d43a1d`
- [x] Task 8: 差分チェック・ユーザー承認済み — committed `b76eafc6a`
- [x] Task 9: エキスパートレビュー（0 Findings）、P2境界テスト追加、PR #341 更新 — committed `ec75f7165`
