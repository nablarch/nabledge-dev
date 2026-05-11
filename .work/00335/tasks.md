# Tasks: fix: verify QC2 Excel residue check silently exempts MD structural tokens not authorized by spec

**PR**: TBD
**Issue**: #335
**Updated**: 2026-05-11

## Rules

- 推測せず事実ベースで調査・作業・判断する
  - コードを読まずに動作を推測しない — 必ずgrep/実行で確認する
  - spec文書を参照せずに「specに書いてある」と言わない — 必ず該当箇所を引用する
  - 変更影響範囲は網羅的に調査する（サンプリング不可）
  - 投機的な根拠で設計判断しない — 測定値と spec 引用で判断する

## In Progress

## Not Started

### Task 1: 調査結果と設計判断をnotes.mdに記録
**Steps:**
- [ ] `_MD_SYNTAX_RE` の各トークンについてspec根拠を整理（`|`, `---`, `**`, `*`, `__`, `#`, `>`, `1.`, `` ` ``, `:`）
- [ ] `:` の P1 残留の再現を確認（実行で事実確認済み）
- [ ] `.work/00335/notes.md` に調査結果を記録
- [ ] コミット: `docs: record investigation findings for issue #335`

### Task 2: verify設計書 §3-1 Excel節 に P1コロン例外を追記・ユーザー確認
**前提**: RBKCのverifyを変更するため、実装前に設計書を更新してユーザーに確認が必要
**Steps:**
- [ ] `rbkc-verify-quality-design.md` §3-1 Excel節 のQC2手順 3 に P1構造区切り文字(`:`)の例外を明記
  - 追記対象: 「P1形式のsection.contentは`{列名}: {値}`形式（§8-4）のため、区切り文字の `:` はQC2残留チェックの対象外」
  - 根拠: `rbkc-converter-design.md` §8-4 が `{列名}: {値}` 形式を規定
- [ ] `.work/00335/` に設計変更案を記録
- [ ] コミット: `docs: update verify-quality-design.md §3-1 to document P1 colon exception`
- [ ] **ユーザーに設計書変更内容を確認依頼してから次タスクへ進む**

### Task 3: TDD RED — `|` がソースにないJSON に対してQC2 FAILするテスト追加
**前提**: Task 2 のユーザー承認後
**Steps:**
- [ ] `TestVerifyFileExcel` クラスに `test_fail_qc2_pipe_char_fabrication` を追加
  - Excel セル `"Hello"` のみ、JSON に `"Hello | world"` → QC2 FAIL
- [ ] テスト実行 → RED を確認（現在は `_MD_SYNTAX_RE` が `|` を除去するため PASS になる）
- [ ] コミット: `test: add failing test for | QC2 detection (RED phase)`

### Task 4: TDD RED — `---` がソースにないJSON に対してQC2 FAILするテスト追加
**Steps:**
- [ ] `TestVerifyFileExcel` クラスに `test_fail_qc2_triple_dash_fabrication` を追加
  - Excel セル `"Hello"` のみ、JSON に `"Hello ---"` → QC2 FAIL
- [ ] テスト実行 → RED を確認（現在は `_MD_SYNTAX_RE` が `---` を除去するため PASS になる）
- [ ] コミット: `test: add failing test for --- QC2 detection (RED phase)`

### Task 5: 実装 — `_MD_SYNTAX_RE` 削除、P1限定コロン除外に置換
**前提**: Task 2 のユーザー承認後
**Steps:**
- [ ] `verify.py` から `_MD_SYNTAX_RE` 定義を削除（lines 1047–1068）
- [ ] `_verify_xlsx` のQC2残留チェック部分（line 1703）を以下に置換:
  - P1シートの場合のみ `:` を空白に置換してから残留チェック
  - P2シート（通常）はそのまま残留チェック（`:` もQC2検出対象）
  - `sheet_type = data.get("sheet_type")` で判定
- [ ] Task 3, 4 で追加したテストが GREEN になることを確認
- [ ] 既存の全テスト（300本）が PASS することを確認
- [ ] コミット: `fix: remove _MD_SYNTAX_RE, replace with P1-scoped colon strip for QC2`

### Task 6: テスト削除・置換 — 捏造spec条項テストを削除しFAILテストに書き換え
**Steps:**
- [ ] `test_pass_qc2_standalone_triple_dash_is_tolerance_allowed`（line 1839）を削除
  - 削除理由: spec §3-1 Excel節に `---` 許容の条項は存在しない（fabricated spec citation）
- [ ] Task 4 で追加した `test_fail_qc2_triple_dash_fabrication` が代替テストになる（既にTask 4で追加済み）
- [ ] 全テスト PASS を再確認
- [ ] コミット: `test: remove fabricated spec clause test test_pass_qc2_standalone_triple_dash_is_tolerance_allowed`

### Task 7: 全5バージョン rbkc create+verify 実行・FAILカウント比較
**Steps:**
- [ ] 変更前の全5バージョンFAILカウントを記録（変更前にrun）
- [ ] 変更後の全5バージョンFAILカウントを記録
- [ ] 差分を `.work/00335/rbkc-verify-diff.md` に記録
  - 予測: v6/v5/v1.4/v1.3/v1.2 いずれも FAILカウント変化なし（`_MD_SYNTAX_RE` は verify側のみで RBKC create には影響しない）
  - 意図しない増加があれば原因を特定して修正
- [ ] コミット: `docs: record rbkc verify diff results for issue #335`

### Task 8: 変更差分チェック・ユーザー確認
**前提**: 全タスク完了後、PRレビュー依頼前
**Steps:**
- [ ] `git diff main...HEAD --stat` で変更ファイルを一覧
- [ ] 想定変更ファイル: `verify.py`, `test_verify.py`, `rbkc-verify-quality-design.md`
  - `verify.py`: `_MD_SYNTAX_RE` 削除 + QC2残留チェック部分の変更
  - `test_verify.py`: 2テスト追加 + 1テスト削除
  - `rbkc-verify-quality-design.md`: §3-1 P1コロン例外追記
- [ ] 想定外の変更ファイルがないかチェック
- [ ] 結果を `.work/00335/diff-check.md` に出力
- [ ] コミット: `docs: record diff check result for issue #335`
- [ ] **ユーザーに差分チェック結果を確認依頼してからPR作成へ進む**

### Task 9: エキスパートレビュー・PR作成
**Steps:**
- [ ] Expert review 実行（Software Engineer + QA Engineer）
- [ ] Findings があれば全て修正
- [ ] `Skill(skill: "pr", args: "create")` でPR作成

## Done

- [x] tasks.md 初版作成・ブランチ作成 (`335-fix-verify-qc2-md-syntax-exemption`)
