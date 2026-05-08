# Tasks: fix: format PCIDSS table in security-check-3 docs (v5/v6)

**PR**: #332
**Issue**: #327
**Updated**: 2026-05-08

## Rules

- **調査・作業・判断はすべて事実ベースで行う**: 推測・推論・「おそらく〜」は禁止。コード/ファイルを実際に読んで確認してから判断する
- **変更前に影響範囲を網羅的に列挙**: サンプリングではなく、影響するすべてのファイル・行を特定してから着手する
- **設計決定は根拠を明示**: 選択した理由とその根拠（ファイル名・行番号・仕様条文）を必ず記録する

## In Progress

### Task 7: RBKC P1閾値変更の影響調査

**背景決定事項:**
- 手動変更はNGと確定（`eb36437d7`でrevert済み）
- 正しい対応: RBKC側（`_detect_header`）を修正してMDテーブルを自動生成する
- 方針: `_run_length ≥ 3` を `≥ 2` に変更することで3.PCIDSS対応表（2列テーブル）をP1として自動判定させる
- 設計書（`rbkc-converter-design.md` §8-2）の `≥ 3` 記述も合わせて変更が必要
- verify設計書（`rbkc-verify-quality-design.md`）は §8-2 参照のため変更不要だが確認要
- `rbkc.md` にRBKC生成ファイルの手動編集禁止ルール追加が必要

**Steps:**
- [ ] Step 1: 閾値を `≥ 2` に変更して `rbkc.sh create 6` を実行し、差分が出るファイルを全列挙する
- [ ] Step 2: 同様に `rbkc.sh create 5` を実行し差分確認
- [ ] Step 3: 差分ファイルを精査し、意図しない変更（3.PCIDSS対応表以外のシートがP1化されていないか）を確認
- [ ] Step 4: 影響確認後、設計書・verify設計書の要更新箇所を特定して提案
- [ ] Step 5: ユーザー承認後に実装（TDD: テスト→RED→実装→GREEN）
- [ ] Step 6: `rbkc.sh verify 6` および `rbkc.sh verify 5` でFAIL 0件を確認
- [ ] Step 7: `rbkc.md` に手動編集禁止ルール追加
- [ ] Step 8: PRボディ更新
- [ ] Step 9: PR変更差分チェック — `git diff origin/main..HEAD --stat` でRBKC修正・設計書・テスト・work logのみであること、意図しないファイルが含まれていないことを確認し、結果を `.work/00327/diff-check.md` に記録する
- [ ] Step 10: レビュー依頼

**調査済み事実:**
- `_detect_header()` @ `tools/rbkc/scripts/create/converters/xlsx_common.py:341` が `_run_length(row_h) < 3` で閾値判定
- `_run_length()` は行の「最長連続非空セル数」を返す
- `3.PCIDSS対応表` はヘッダ行の非空セルが2列（col B, col C）のみ → `< 3` で P2 扱い
- P2-3 として `xlsx-sheet-mapping.md:23,45` に手動登録されている（v6/v5 両方）
- `rbkc-converter-design.md` §8-2 に「連続非空セル ≥ 3」と明記

## Not Started

(なし)

## Done

- [x] ブランチ作成 `327-format-pcidss-table`
- [x] 対象ファイル調査（v6, v5 とも同一内容28行、テーブルがフラットテキスト）
- [x] Task 1: tasks.md 作成・コミット — `9f9e7c040`
- [x] Task 2: プレビューMD作成・コミット・PR作成・ユーザー確認依頼 — `9f9e7c040` / PR #332
- [x] Task 3 (廃棄): v6・v5 ファイルへのMarkdownテーブル手動適用 — `1b09a73ea` → `eb36437d7` でrevert
- [x] Task 4: 変更差分チェック — `db8291d80`
- [x] Task 5: Technical Writer エキスパートレビュー（0 Findings） — `a82db3d24`
- [x] Task 6: PR ボディ更新・レビュー依頼済み — `a82db3d24`
- [x] レビューコメント（@kiyotis）への返信 — 手動変更が `rbkc.sh create` で上書きされる問題を報告
- [x] 手動変更のrevert — `eb36437d7`（RBKC修正で対応する方針に変更）

## Success Criteria Check

| 基準 | 状態 |
|------|------|
| v5・v6 両ファイルが Markdown テーブル形式（RBKC自動生成） | 未達 — Task 7 完了後 |
| 10要件（6.5.1〜6.5.10）とチェックリスト対応が全件保持 | 未達 — Task 7 完了後 |
| `rbkc.sh create` 実行後も手動変更なしでMDテーブルが維持される | 未達 — Task 7 完了後 |
| RBKC生成ファイルの手動編集禁止ルールが `rbkc.md` に追加される | 未達 — Task 7-Step 7 |
