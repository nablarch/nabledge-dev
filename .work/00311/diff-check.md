# PR #314 変更差分チェック

**実施日**: 2026-04-28  
**比較基準**: `origin/main` vs `HEAD` (branch: `311-excel-docs-md-readability`)

---

## サマリー

| カテゴリ | ファイル数 | 判定 |
|----------|-----------|------|
| tools/rbkc ソースコード | 11 | ✅ 想定内 |
| .work/00311 作業記録 | 12 | ✅ 想定内 |
| nabledge-5/docs (P2-1対象シート) | 16 | ✅ 想定内 |
| nabledge-6/docs (P2-1対象シート) | 4 | ✅ 想定内 |
| nabledge-1.4/docs (P2-1対象シート) | 2 | ✅ 想定内 |
| nabledge-5/docs (P2-1非対象シート) | **194** | ⚠️ スコープ外 (後述) |
| nabledge-6/docs (P2-1非対象シート) | **147** | ⚠️ スコープ外 (後述) |

---

## ✅ 想定内の変更

### tools/rbkc (11ファイル)

| ファイル | 変更内容 |
|----------|----------|
| `scripts/create/converters/xlsx_common.py` | [F] P2-1 heading 判定修正 (絶対列 + 単一セル条件) |
| `scripts/create/docs.py` | 同上 (rendering 側) |
| `scripts/create/converters/xlsx_releasenote.py` | [D] P2-1/P2-3 sheet_subtype 渡し |
| `scripts/create/converters/xlsx_security.py` | 同上 |
| `scripts/run.py` | [D] sheet_subtype mapping 読み込み |
| `scripts/verify/verify.py` | [D] QO1 (p2_headings 照合) / QO2 P2-1 例外追加 |
| `tests/ut/test_docs.py` | [D][F] P2-1/P2-3 rendering テスト |
| `tests/ut/test_verify.py` | [D] QO1/QO2 verify テスト |
| `docs/rbkc-converter-design.md` | [C][F] §8 P2-1/P2-3 設計仕様 |
| `docs/rbkc-verify-quality-design.md` | [C][D] §3-3 QO1/QO2 verify 仕様 |
| `docs/xlsx-sheet-mapping.md` | [B] 全シート P1/P2-1/P2-2/P2-3 分類表 |

### nabledge-5/docs + nabledge-6/docs + nabledge-1.4/docs (P2-1対象)

P2-1として登録された全16シートの docs MD が正しく再生成されている。

**v6 対象シート (4件)**:
- `security-check-1.概要.md` — col-3本文行が `####` → 本文段落に修正 ✅
- `security-check-3.PCIDSS対応表.md` — P2-3 (LF → hard line break) ✅
- `releases-nablarch6u2-releasenote-バージョンアップ手順.md` — P2-1再生成 ✅
- `releases-nablarch6u3-releasenote-マルチパートリクエストのサポート対応.md` — col-3+本文行修正 ✅

**v5 対象シート (16件)**: security-check, releases P2-1シート全件 ✅  
**v1.4 対象シート (2件)**: JSON読み取り失敗ケース, XXE脆弱性 ✅

---

## ⚠️ スコープ外変更（内容は正常）

### nabledge-5/docs (194件) + nabledge-6/docs (147件) — P2-1非対象ファイル

**原因**: `4b11e55c3` の全再生成コミットにて `create 5` / `create 6` を実行した際、`origin/main` に入っていた PR #315 (Issue #312: RST block_quote 修正) の成果が反映された。

このブランチが分岐したとき (`bfaf68781` 以前) のベースは `origin/main` の `8f37ab917` であり、PR #315 がマージされる前の状態だった。  
全再生成により、PR #315 で修正された `block_quote` 内の空行処理が v5/v6 の RST 由来ファイルに適用された形になった。

**変更内容の性質**: Issue #312 の修正（RST `block_quote` → MD 正しい空行挿入）と同じ変更。内容は正しい。

**問題点**:
- Issue #311 のスコープを超えている
- 意図せず PR #315 の変更内容を再取り込みしている形になる

**対応方針の選択肢**:
1. **このままマージ**: 内容は正しく、verify All files OK 済み。重複コミットになるがファイル内容は問題なし
2. **対象シートのみ再コミット**: P2-1/P2-3対象シートのみを cherry-pick して余分なファイルを除外

---

## 確認コマンド

```bash
# origin/main との差分ファイル数
git diff origin/main...HEAD --name-only | wc -l
# → 1163

# tools/ 変更
git diff origin/main...HEAD --name-only | grep "^tools/"
# → 11ファイル（想定内）

# P2-1非対象のdocs変更
git diff origin/main...HEAD --name-only | grep "^\.claude/skills/nabledge-[56]/docs/" | grep -v "releases\|check" | wc -l
# → 341ファイル（スコープ外・内容は正常）
```
