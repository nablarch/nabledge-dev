# Tasks: fix: remove quality escape hatches from verify design spec (#334)

**PR**: #340
**Issue**: #334
**Updated**: 2026-05-11

## Fact-Based Investigation Rule

> 推測せず事実ベースで調査、作業、判断する。
> コード・設計書の現状を実際に確認してから結論を出す。
> 「おそらく〜だろう」という推測で変更や判断を行わない。
> 変更前後で影響範囲をコードレベルで確認し、事実として記録する。

## In Progress

(none)

## Not Started

### Task 1: 設計書変更 — §3-2-2 象限3/4 を PASS+WARNING → FAIL (QL1) に変更

**事実確認（変更前に実施）**:
- [ ] §3-2-2 判定テーブルの象限3・4の現行記述を確認（PASS+WARNING）
- [ ] 象限3の根拠記述「ユーザの mapping scope 決定を尊重」の行番号を特定
- [ ] 象限4の根拠記述「Sphinx parity」の行番号を特定
- [ ] 同セクションの補足文（WARNING列挙の説明）で象限3/4 PASSに言及している箇所を特定

**Steps:**
- [ ] §3-2-2 判定テーブルの象限3: `PASS + WARNING` → `FAIL (QL1)`、根拠記述を更新
- [ ] §3-2-2 判定テーブルの象限4: `PASS + WARNING` → `FAIL (QL1)`、根拠記述を更新
- [ ] 同セクションの補足文から象限3/4 PASS の記述を削除・修正

### Task 2: 設計書変更 — §3-1 手順0 の level 3 (ERROR) を QC1 FAIL に変更

**事実確認（変更前に実施）**:
- [ ] §3-1 手順0の現行記述の行番号を特定（level ≥ 4 のみ FAIL、level 3 は warning 扱い）
- [ ] §3-2 Sphinx 追従原則の「独自に厳しくすることは避ける」の行番号を特定
- [ ] §3-2-2 末尾の `docutils system_message の扱い` 段落で level ≤ 3 / ≥ 4 に言及している箇所を特定

**Steps:**
- [ ] §3-1 手順0: level 3 (ERROR) も QC1 FAIL に変更
- [ ] §3-2 Sphinx 追従原則: `verify が独自に厳しくして RBKC が RST 上流より多く FAIL することは避ける` を削除
- [ ] §3-2-2 末尾の `docutils system_message の扱い` 段落: level ≤ 3 は warning 継続の記述を修正
- [ ] §3-1 判定分岐まとめテーブル: `docutils が parse error を返した` 行を更新（level 3 も含む）

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

### Task 5: verify実装変更 — docutils level 3 (ERROR) を QC1 FAIL に変更

**事実確認（変更前に実施）**:
- [ ] verify実装で level 3 の判定を行っているファイル・行番号を特定
- [ ] 現行の実装が level 3 を WARNING として継続していることをコードで確認
- [ ] 対応するverifyテストの場所を特定

**Steps:**
- [ ] TDD: level 3 (ERROR) が QC1 FAIL を返すことを確認するテストを追加 (RED)
- [ ] verify実装: level 3 (ERROR) を QC1 FAIL に変更 (GREEN)
- [ ] 既存のverifyテストが全てパスすることを確認

### Task 6: 全5バージョンで create/verify 実行、FAIL 0件確認

**事実確認**:
- [ ] 変更前の全5バージョンの FAIL 件数をベースラインとして記録
- [ ] `bash rbkc.sh create v6 && bash rbkc.sh verify v6` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v5 && bash rbkc.sh verify v5` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v1.4 && bash rbkc.sh verify v1.4` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v1.3 && bash rbkc.sh verify v1.3` を実行し FAIL 件数確認
- [ ] `bash rbkc.sh create v1.2 && bash rbkc.sh verify v1.2` を実行し FAIL 件数確認

**Steps:**
- [ ] FAIL が出た場合: インプット（ソースRST/MD）とアウトプット（JSON）を照合し、create/verifyのどちらに問題があるかを事実ベースで調査・記録
- [ ] create側のバグであれば create を修正、verify側のバグであれば verify を修正（verify を弱めることは禁止）
- [ ] 全5バージョンで FAIL 0件になるまで繰り返す

### Task 7: 変更差分チェック＆PRでユーザー確認

**Steps:**
- [ ] `git diff main...HEAD` で変更差分を取得し、想定した変更のみであることを確認
- [ ] 差分チェック結果を `.work/00334/diff-check.md` に出力
- [ ] PRにコメントしてユーザーに確認依頼

## Done

- [x] Issue #334 取得、フィーチャーブランチ作成 (`334-fix-verify-design-escape-hatches`) — committed `5b108601c`
- [x] tasks.md 作成 — committed `5b108601c`
- [x] Issue #334 SC更新（実装修正SCを追加、spec-only記述を削除）
