# PR #314 変更差分チェック

**実施日**: 2026-04-28 (更新: rebase 後再確認)
**比較基準**: `origin/main` vs `HEAD` (branch: `311-excel-docs-md-readability`)

---

## サマリー

| カテゴリ | ファイル数 | 判定 |
|----------|-----------|------|
| tools/rbkc ソースコード | 11 | ✅ 想定内 |
| .work/00311 作業記録 | 8 | ✅ 想定内 |
| nabledge-5/6/1.4 docs MD (P2-1対象シート) | 21 | ✅ 想定内 |
| nabledge-5/6/1.4 knowledge JSON (P2-1対象シート) | 21 | ✅ 想定内 |
| nabledge-5/6/1.4/1.3/1.2 docs MD (P2-1非対象) | **330** | ⚠️ スコープ外 (後述) |
| nabledge-5/6/1.4/1.3/1.2 knowledge JSON (P2-1非対象) | **351** | ⚠️ スコープ外 (後述) |

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

### nabledge docs + knowledge (P2-1対象 21件)

P2-1/P2-3として登録された全シートの docs MD と knowledge JSON が正しく再生成されている。

**v6 対象 (4件)**:
- `security-check-1.概要` — col-3本文行が `####` → 本文段落に修正 ✅
- `security-check-3.PCIDSS対応表` — P2-3 (LF → hard line break) ✅
- `releases-nablarch6u2-releasenote-バージョンアップ手順` — P2-1再生成 ✅
- `releases-nablarch6u3-releasenote-マルチパートリクエストのサポート対応` — col-3+本文行修正 ✅

**v5 対象 (15件)**: security-check, releases P2-1シート全件 ✅
**v1.4 対象 (2件)**: JSON読み取り失敗ケース, XXE脆弱性 ✅

---

## ⚠️ スコープ外変更（内容は正常）

### docs MD (330件) + knowledge JSON (351件) — P2-1非対象ファイル

**原因**: PR #315 (Issue #312: RST block_quote 修正) がこのブランチ分岐後に `origin/main` にマージされた。
その後 `4b11e55c3` (docs MD) および `fe2765c37` (knowledge JSON) で全再生成した際、PR #315 の変更が適用された形になった。

**変更内容の性質**: Issue #312 の修正 (RST `block_quote` → MD 正しい空行挿入) と同じ変更。内容は正しい。

**問題点**: Issue #311 のスコープを超えているが、`origin/main` に入れた変更と同じ内容を再適用しているため、
最終的なファイル内容は `origin/main` にマージしても変わらない (idempotent)。

**対応**: このままマージ。内容は正しく verify 全バージョン OK 済み。重複コミットになるが最終状態は同一。

---

## verify 結果 (最終)

| バージョン | 結果 |
|-----------|------|
| v6 | All files verified OK ✅ |
| v5 | All files verified OK ✅ |
| v1.4 | All files verified OK ✅ |
| v1.3 | All files verified OK ✅ |
| v1.2 | All files verified OK ✅ |

---

## 確認コマンド

```bash
# origin/main との差分ファイル数
git diff origin/main...HEAD --name-only | wc -l
# → 768

# tools/ 変更
git diff origin/main...HEAD --name-only | grep "^tools/"
# → 11ファイル（想定内）

# P2-1対象のdocs変更
git diff origin/main...HEAD --name-only | grep "/docs/" | grep "security-check\|releasenote"
# → 21ファイル（スコープ内）

# P2-1非対象のdocs変更
git diff origin/main...HEAD --name-only | grep "/docs/" | grep -v "security-check\|releasenote"
# → 330ファイル（スコープ外・内容は正常）

# verify (全バージョン)
python -m scripts.run verify 6 && python -m scripts.run verify 5 && \
python -m scripts.run verify 1.4 && python -m scripts.run verify 1.3 && python -m scripts.run verify 1.2
```
