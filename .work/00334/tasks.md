# Tasks: fix: verify design spec contains quality escape hatches (§3-2-2 PASS+WARNING, §3-1 level 3 ERROR tolerance)

**PR**: (TBD)
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

このIssueは設計書（`tools/rbkc/docs/rbkc-verify-quality-design.md`）の仕様変更のみ。
実装変更は含まない（SCに「spec-only change, no implementation change in this issue」と明記）。

**事実確認（変更前に実施）**:
- [ ] `§3-2-2 判定テーブル` の象限3・4の現行記述を確認（PASS+WARNING）
- [ ] 変更対象のテキスト範囲を特定（行番号）
- [ ] 象限3の根拠記述「ユーザの mapping scope 決定を尊重」を確認
- [ ] 象限4の根拠記述「Sphinx parity」を確認

**Steps:**
- [ ] §3-2-2 判定テーブルの象限3: `PASS + WARNING` → `FAIL (QL1)` に変更し、根拠記述を更新
- [ ] §3-2-2 判定テーブルの象限4: `PASS + WARNING` → `FAIL (QL1)` に変更し、根拠記述を更新
- [ ] 同セクションの補足文（WARNING列挙の説明）から象限3/4 PASS の記述を削除・修正
- [ ] 変更差分チェック → PRでユーザー確認（Task 4）

### Task 2: 設計書変更 — §3-1 手順0 の level 3 (ERROR) を QC1 FAIL に変更

**事実確認（変更前に実施）**:
- [ ] §3-1 手順0の現行記述を確認（level ≥ 4 のみ FAIL、level 3 は warning 扱い）
- [ ] 同じ内容が §3-2 Sphinx 追従原則にも記述されている箇所を確認
- [ ] `§3-2-2 dangling reference の扱い` セクション末尾の WARNING/PASS 記述との整合を確認

**Steps:**
- [ ] §3-1 手順0: `level 3 (ERROR) までは warning 記録扱いで render を継続する (Sphinx 追従原則 §3-2-3)` → level 3 も QC1 FAIL に変更
- [ ] §3-2 Sphinx 追従原則: `verify が独自に厳しくして RBKC が RST 上流より多く FAIL することは避ける` の記述を削除
- [ ] §3-2-2 末尾の `docutils system_message の扱い` 段落（level ≤ 3 は warning、level ≥ 4 のみ FAIL）の記述を修正
- [ ] §3-1 判定分岐まとめテーブルの `docutils が parse error を返した` 行を更新（level 3 も含む）
- [ ] 変更差分チェック → PRでユーザー確認（Task 4）

### Task 3: 水平チェック — 同じ escape hatch パターンが設計書の他箇所に存在しないか確認

**事実確認**:
- [ ] `rbkc-verify-quality-design.md` 全文を検索: `PASS + WARNING` パターンが他にないか
- [ ] `PASS + WARNING` / `WARNING 扱い` / `Sphinx 追従` のパターンで grep し、全箇所を列挙
- [ ] 列挙結果を `.work/00334/notes.md` に記録
- [ ] 追加修正が必要な箇所があれば Task 1/2 に反映

### Task 4: 変更差分チェック＆PRでユーザー確認

**Steps:**
- [ ] `git diff` で変更差分を取得し、想定した変更のみであることを確認
- [ ] 差分チェック結果を `.work/00334/diff-check.md` に出力
- [ ] PRにコメントしてユーザーに確認依頼

## Done

- [x] Issue #334 取得、フィーチャーブランチ作成 (`334-fix-verify-design-escape-hatches`)
- [x] tasks.md 作成
