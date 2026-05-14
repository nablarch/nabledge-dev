# Tasks: fix: remove quality escape hatches from verify design spec (#334)

**PR**: #340
**Issue**: #334
**Updated**: 2026-05-14

## スコープ決定 (2026-05-14)

**Task 2/5（level-3 FAIL化）はスコープ外**。

理由: level-3 ERROR でコンテンツが doctree から落ちた場合、Sphinx HTML でも同様に欠落するため RBKC の責務外。設計書は level-3 WARNING 継続を維持し、理由を明記する方針（ユーザー確認済み）。

**Task 1/4（象限3/4 FAIL化）のみ実施する。**

## Fact-Based Investigation Rule

> 推測せず事実ベースで調査、作業、判断する。
> コード・設計書の現状を実際に確認してから結論を出す。
> 「おそらく〜だろう」という推測で変更や判断を行わない。
> 変更前後で影響範囲をコードレベルで確認し、事実として記録する。

## In Progress

### Task 1: 設計書変更 — §3-2-2 象限3/4 を PASS+WARNING → FAIL (QL1) に変更

**Steps:**
- [x] 事実確認: §3-2-2 判定テーブルの現行記述を確認（行318-319）
- [x] §3-2-2 判定テーブルの象限3: `PASS + WARNING` → `FAIL (QL1)`、根拠記述を更新
- [x] §3-2-2 判定テーブルの象限4: `PASS + WARNING` → `FAIL (QL1)`、根拠記述を更新
- [x] 補足文 `verify は象限 3/4 を WARNING としてログに列挙する` を削除
- [x] Sphinx 追従原則: `verify が独自に厳しくして RBKC が RST 上流より多く FAIL することは避ける` を削除

## Not Started

### Task 3: 水平チェック — 同じ escape hatch パターンが設計書の他箇所に存在しないか確認

**事実確認**:
- [ ] `rbkc-verify-quality-design.md` 全文を検索: `PASS + WARNING` パターンが他にないか
- [ ] `WARNING 扱い` / `Sphinx 追従` / `避ける` のパターンで全箇所を列挙
- [ ] 列挙結果を `.work/00334/notes.md` に記録
- [ ] 追加修正が必要な箇所があれば Task 1/2 に反映

### Task 4: verify実装変更 — §3-2-2 象限3/4 を FAIL (QL1) に変更

**事実確認（変更前に実施）**:
- [ ] verify実装で象限3/4の判定を行っているファイル・行番号を特定
- [ ] 現行の実装が `PASS+WARNING` を返していることをコードで確認
- [ ] 対応するverifyテストの場所を特定

**Steps:**
- [ ] TDD: 象限3/4 が FAIL (QL1) を返すことを確認するテストを追加 (RED)
- [ ] verify実装: 象限3/4 を FAIL (QL1) に変更 (GREEN)
- [ ] 既存のverifyテストが全てパスすることを確認

~~### Task 5: verify実装変更 — docutils level 3 (ERROR) を QC1 FAIL に変更~~
**スコープ外** (2026-05-14): level-3 ERROR でコンテンツが落ちる場合は Sphinx HTML でも欠落するため RBKC の責務外。

### Task 5: 全5バージョンで create/verify 実行、FAIL 0件確認

**Steps:**
- [ ] `bash rbkc.sh create v6 && bash rbkc.sh verify v6` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v5 && bash rbkc.sh verify v5` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v1.4 && bash rbkc.sh verify v1.4` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v1.3 && bash rbkc.sh verify v1.3` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v1.2 && bash rbkc.sh verify v1.2` を実行し FAIL 件数確認
- [ ] FAIL が出た場合: create/verify のどちらに問題があるかを事実ベースで調査・修正

### Task 6: 変更差分チェック＆PRでユーザー確認

**Steps:**
- [ ] `git diff main...HEAD` で変更差分を取得し、想定した変更のみであることを確認
- [ ] 差分チェック結果を `.work/00334/diff-check.md` に出力
- [ ] PRにコメントしてユーザーに確認依頼

## Done

- [x] Issue #334 取得、フィーチャーブランチ作成 (`334-fix-verify-design-escape-hatches`) — committed `5b108601c`
- [x] tasks.md 作成 — committed `5b108601c`
- [x] Issue #334 SC更新（実装修正SCを追加、spec-only記述を削除）
