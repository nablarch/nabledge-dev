# Tasks: fix: format PCIDSS table in security-check-3 docs (v5/v6)

**PR**: #332
**Issue**: #327
**Updated**: 2026-05-08

## Rules

- **調査・作業・判断はすべて事実ベースで行う**: 推測・推論・「おそらく〜」は禁止。コード/ファイルを実際に読んで確認してから判断する
- **変更前に影響範囲を網羅的に列挙**: サンプリングではなく、影響するすべてのファイル・行を特定してから着手する
- **設計決定は根拠を明示**: 選択した理由とその根拠（ファイル名・行番号・仕様条文）を必ず記録する

## In Progress

### Task 7: xlsx-sheet-mapping を create/verify 両側の正式定義にする

**背景決定事項（このセッションで確定）:**
- 手動変更はNGと確定（`eb36437d7`でrevert済み）
- 当初方針（閾値変更）は廃棄：副作用でバージョンアップ手順もP1化される、verifyとの不整合
- SE/QAエキスパートレビュー実施済み → アプローチB採用
- **確定方針**: `xlsx-sheet-mapping.md` を create/verify 両側の正式定義にする
  - mapping に P1/P2 を明示 → create も verify もそれを読んで従う
  - mapping にないシートは FAIL（自動判定廃止）
  - PCIDSS対応表を `P1` に変更 → テーブル出力
- v1.4/v1.3/v1.2 も含めて全バージョンを同時対応（自動判定結果を mapping に焼き込む）
- **現在の状態**: 途中実装あり（WIP stash対象）

**現在の未コミット変更（途中実装 — WIP）:**
- `tools/rbkc/scripts/create/converters/xlsx_common.py` — P1 override 実装（方針変更で廃棄予定）
- `tools/rbkc/docs/rbkc-converter-design.md` — P1 override の設計書追記（廃棄予定）
- `tools/rbkc/docs/xlsx-sheet-mapping.md` — PCIDSS対応表を P1 に変更（一部正しい）
- `.claude/skills/nabledge-5/`, `.claude/skills/nabledge-6/` — rbkc create の出力（廃棄予定）

**Steps:**
- [ ] Step 0: WIP変更をrevert（xlsx_common.py の P1 override、設計書追記、knowledge files）
- [ ] Step 1: スクリプトで全バージョン(v6/v5/v1.4/v1.3/v1.2) の全 xlsx シートを走査し、現在の自動判定（P1/P2）を列挙する
- [ ] Step 2: 列挙結果で `xlsx-sheet-mapping.md` を更新（v1.x セクション追加、PCIDSS対応表を P1 に変更）
- [ ] Step 3: create 側（`xlsx_common.py`）を mapping 優先に変更（mapping にないシートはエラー）
- [ ] Step 4: verify 側（`verify.py`）を mapping 優先に変更（mapping にないシートはエラー）
- [ ] Step 5: PCIDSS対応表が P1 として正しく生成されることを確認（`rbkc create 6/5`）
- [ ] Step 6: `rbkc.sh verify 6` および `rbkc.sh verify 5` で FAIL 0件を確認
- [ ] Step 7: `rbkc.md` に手動編集禁止ルール追加
- [ ] Step 8: PRボディ更新
- [ ] Step 9: PR変更差分チェック
- [ ] Step 10: レビュー依頼

**調査済み事実:**
- v6/v5 の xlsx シートは `tools/rbkc/docs/xlsx-sheet-mapping.md` に全212シート列挙済み
- v1.4/v1.3/v1.2 の xlsx は `tools/rbkc/mappings/v1.x.json` の `xlsx` キーで定義（releasenote.xlsx のみ）
- releasenote.xlsx の件数: v1.4/v1.3/v1.2 合計32ファイル
- `_detect_header()` @ `xlsx_common.py:341` が自動判定を行っている
- PCIDSS対応表: ヘッダ行の連続非空セルが2列（col B, col C）、run_length=2 → 現在 P2
- 自動判定を走らせた際の影響: v6 で PCIDSS対応表+リリースノート3件変更（リリースノートはP2-2のまま維持すべき）

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
