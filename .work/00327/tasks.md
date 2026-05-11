# Tasks: fix: format PCIDSS table in security-check-3 docs (v5/v6)

**PR**: #332
**Issue**: #327
**Updated**: 2026-05-11 (session 3)

## Rules

- **調査・作業・判断はすべて事実ベースで行う**: 推測・推論・「おそらく〜」は禁止。コード/ファイルを実際に読んで確認してから判断する
- **変更前に影響範囲を網羅的に列挙**: サンプリングではなく、影響するすべてのファイル・行を特定してから着手する
- **設計決定は根拠を明示**: 選択した理由とその根拠（ファイル名・行番号・仕様条文）を必ず記録する

## In Progress (remaining steps)

### Task 7: PCIDSS対応表専用の P2-4 パターンを追加する

**背景決定事項:**
- 手動変更はNGと確定（`eb36437d7`でrevert済み）
- mapping一元化アプローチ（前セッションのアプローチB）は複雑すぎと判断 → 廃棄
- **確定方針（今セッション確定）**: PCIDSS対応表専用の P2-4 パターンを新設する
  - xlsx-sheet-mapping.md の `3.PCIDSS対応表` を `P2-3` → `P2-4` に変更
  - create 側: P2-4 ハンドラーを追加（2列テーブル＋セル内LF→`<br>`）
  - verify 側: P2-4 対応の QO2 チェックを追加
  - docs.py: P2-4 の MDテーブルレンダラーを追加
- **WIP stash**: `stash@{0}` は廃棄（前セッションの P1 override — 不要）

**PCIDSS Excel 構造（調査済み）:**
- ファイル: `Nablarch機能のセキュリティ対応表.xlsx` / シート: `3.PCIDSS対応表`
- 3列（col A: 常に空、col B: 要件番号、col C: 対応内容）
- rows 1-4: 前文（col A のみ）
- row 5: 空行
- row 6: ヘッダ（B=`PCI DSS 要件 `、C=`2.チェックリストとの対応`）
- rows 7-16: データ 10行（B=`6.5.1`〜`6.5.10`、C=対応内容。embedded LF あり）
- `_useful_width` は B+C の2列のみ使用 → `<= 2` で P1判定スキップ → 現在 P2-3

**目標 docs MD:**
- 前文 → プレーンテキスト（P2-3と同じ）
- ヘッダ+データ → Markdownテーブル（セル内LFは `<br>` 変換）
- v5 は v6 と同じ Excel 構造・同じ処理

**変更対象ファイル:**
- `tools/rbkc/docs/xlsx-sheet-mapping.md` — `3.PCIDSS対応表` を `P2-3` → `P2-4`（v6, v5 の2行）
- `tools/rbkc/scripts/create/converters/xlsx_common.py` — `_build_p2_4_meta()` 追加、`sheet_to_result()` に P2-4 分岐追加
- `tools/rbkc/scripts/create/docs.py` — `_render_xlsx_p2()` に P2-4 ブランチ追加
- `tools/rbkc/scripts/verify/verify.py` — `check_content_completeness()` に P2-4 QO2 対応追加

**Steps:**
- [x] Step 0: WIP stash 確認済み（`stash@{0}` は廃棄 — 不要）
- [x] Step 1: テスト作成（TDD — RED）— `c309aa893`
- [x] Step 2: `xlsx-sheet-mapping.md` 更新（P2-3 → P2-4 を v6/v5 の2行）— `ff9062009`
- [x] Step 3: `xlsx_common.py` に `_build_p2_4_meta()` + `sheet_to_result()` 分岐追加 — `ff9062009`
- [x] Step 4: `docs.py` に P2-4 レンダラー追加（前文 + MDテーブル、セル内LF→`<br>`）— `ff9062009`
- [x] Step 5: `verify.py` に P2-4 QO2 対応追加 — `ff9062009`
- [x] Step 6: テストが GREEN になることを確認（494 passed）
- [x] Step 7: `bash rbkc.sh create 6/5` 実行 → MDテーブル確認 — `8f18dd964`
- [x] Step 8: `bash rbkc.sh verify 6/5` で FAIL 0件確認
- [x] Step 9: 全5バージョン verify FAIL 0件確認
- [x] Step 10: `rbkc.md` に手動編集禁止ルール追加 — `a7728e9a2`
- [ ] Step 11: PRボディ更新
- [ ] Step 12: PR変更差分チェック
- [ ] Step 13: レビュー依頼

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
- [x] SE/QAエキスパートレビュー実施 — 途中実装（P1 override）の問題を特定、方針確定

## Success Criteria Check

| 基準 | 状態 |
|------|------|
| v5・v6 両ファイルが Markdown テーブル形式（RBKC自動生成） | 未達 — Task 7 完了後 |
| 10要件（6.5.1〜6.5.10）とチェックリスト対応が全件保持 | 未達 — Task 7 完了後 |
| `rbkc.sh create` 実行後も手動変更なしでMDテーブルが維持される | 未達 — Task 7 完了後 |
| RBKC生成ファイルの手動編集禁止ルールが `rbkc.md` に追加される | 未達 — Task 7-Step 7 |
