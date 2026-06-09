# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-09

## In Progress

### Task 9: ベンチマーク実行 — qa-05 pass と全体回帰確認

## Rules

- 1コミット = 1タスク
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- SCを満たすようタスクを分割し、タスクリストを作業記録に出力する
- タスクリストをコミットし、PRを作成する
- PR上でIssueの目的とタスクリストの対応関係を示し、ユーザーに確認を依頼する
- 承認後、1コミット = 1タスクで各タスクを実装する
- RBKCのcreate/verifyを変更するため: 実装前に設計を行い、設計書・verify設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

## Not Started

### Task 9: ベンチマーク実行 — qa-05 pass と全体回帰確認
**Steps:**
- [ ] qa-05 シングル実行でクラス名が選択・回答に含まれることを確認
  - `bash tools/rbkc/rbkc.sh verify v6` で FAIL 0 確認後
  - **qa-05 で対象ページ (`adapters-jaxrs-adaptor`) が選択されなかった場合**: Step 2 の10件トリムで押し出された可能性を調査（選択候補数とソート順を確認）。押し出しが原因なら Task 8 パッチ3 の優先規則を強化（classes.md 由来の質問内クラス名一致候補を上位固定）し、Task 8 を再コミット
- [ ] HOW-TO-RUN.md の手順に従い全ベンチマーク実行
- [ ] 結果を `.work/00368/benchmark-results.md` に記録
- [ ] ベースラインと比較して regression なし (≥ 95.9%) を確認

### Task 10: 全バージョン RBKC 展開 (v5/v1.4/v1.3/v1.2)
**Steps:**
- [ ] 各バージョンで `bash tools/rbkc/rbkc.sh create <v> && bash tools/rbkc/rbkc.sh verify <v>` を実行
  - v5: 対象3カテゴリにクラス名あり（156ファイル）→ classes.md に中身が生成されることを確認
  - v1.4 / v1.3 / v1.2: javadoc 未生成（クラス名0件）→ classes.md が固定メッセージ `_No class index available for this version..._` のみで生成されることを確認
- [ ] 全バージョン FAIL 0 を確認（ゼロバージョンも coverage 対象が空集合のため FAIL 0 が正常）
- [ ] コミット・プッシュ (生成された classes.md ファイルを含む)

## Done

- [x] Task 0: タスクリスト作成・PR作成・ユーザー確認 — committed `5ff81b145`
- [x] Task 1: 設計書更新 (classes-md-spec.md, rbkc-verify-quality-design.md QO5) — committed `0dd249d45`
- [x] Task 2: TDD — test_classes.py 作成 (RED) — committed `ac7f7a1f8`
- [x] Task 3: TDD — TestCheckClassesCoverage を test_verify.py に追加 (RED) — committed `4c04146f5`
- [x] Task 4: 実装 — classes.py (generate_classes_md) — committed `fc35cabf4`
- [x] Task 5: 実装 — verify.py (check_classes_coverage) — committed `b1ab38c53`
- [x] Task 6: run.py 統合 (generate_classes_md + check_classes_coverage) — committed `e3da286b8`
- [x] Task 7: v6 classes.md 生成、FAIL 0 確認 — committed `40d313761`
- [x] Task 8: semantic-search.md パッチ1〜3 全5バージョン適用 — committed `f75480b40`
- [x] Task 10: 全バージョン RBKC 展開 (v5/v1.4/v1.3/v1.2) FAIL 0 確認 — committed `d89204139`
