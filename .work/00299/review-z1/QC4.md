# QC4 配置正確性 (Correct placement) — QA Review

**Target**: ソースのセクション A のコンテンツが JSON の異なるセクションに配置されている場合の検出
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (sequential-delete 手順 2) + §2-3 (セクション順序保存 / content の連続性)
**Scope**: RST / MD (Excel 対象外)

---

## 1. 実装の有無

### RST
✅ **実装あり**
- `tools/rbkc/scripts/verify/verify.py:620` `_check_rst_content_completeness`
- 核アルゴリズム: `tools/rbkc/scripts/verify/verify.py:652-671`
  - `norm_source.find(norm_unit, current_pos)` で JSON 順に逐次前進検索 (L653)
  - 見つからない場合、先頭からの `prev_idx` と `_in_consumed` で QC2 / QC3 / QC4 を判別
  - QC4 判定: `tools/rbkc/scripts/verify/verify.py:665` (misplaced title) / `verify.py:671` (misplaced content)
- `prev_idx != -1` かつ consumed 範囲外 ⇒ 「ソース内に単独の出現箇所があるが、JSON 順との前進検索では見つからない（＝ JSON 順 i 番目の出現位置が i-1 番目より前）」を検出。§3-1 手順 2 の仕様に一致。

### MD
✅ **実装あり**
- `tools/rbkc/scripts/verify/verify.py:694` `_check_md_content_completeness`
- 核アルゴリズム: `verify.py:747-766`
- QC4 判定: `verify.py:760` (misplaced title) / `verify.py:766` (misplaced content)
- RST と同一のロジック構造（AST 正規化後に逐次削除）。

### Excel
✅ 対象外（仕様通り、本関数は `fmt == "rst"` / `"md"` のみ分岐: `verify.py:613-616`）

---

## 2. ユニットテストのカバレッジ

テストファイル: `tools/rbkc/tests/ut/test_verify.py`（`TestCheckContentCompleteness`, L425-519）

| # | ケース | テスト有無 | 所在 |
|---|-------|-----------|------|
| 1 | Two sections swapped → QC4 | ✅ | `test_fail_qc4_misplaced_title` (test_verify.py:469-476). 2 セクション swap ケース（「概要/詳細」が source 内で逆順）| 
| 2 | Section content misplaced to different section | ⚠️ 部分的 | 上記テストは **title** の misplacement のみ。`content` の misplacement 専用テスト欠落 |
| 3 | Neighbouring sections with similar content | ❌ | なし |
| 4 | Top-level content appearing after first section (misplaced into section) | ❌ | なし |
| 5 | Content with duplicate substrings where order disambiguates | ❌ | なし |
| 6 | Minimal pair (only 2 sections) | ✅ | `test_fail_qc4_misplaced_title` が該当（2 セクション） |
| 7 | MD 側 QC4 テスト | ❌ | RST のみテスト。MD の QC4 経路 (verify.py:760/766) はユニット未カバー |

**判定**: ⚠️ **不足**。核の 1 ケース（RST/title swap）のみ。仕様上の QC4 境界（content misplacement, MD 経路, top-level vs section の混在, 曖昧性のある重複含有）が未検証。

---

## 3. v6 verify 実行結果

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0

$ tail -3:
All files verified OK

$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 4.24s ==============================
```

✅ v6 verify: 0 FAIL
✅ ユニットテスト: 138 passed

---

## 4. 総合判定

⚠️ **Needs Improvement (条件付き合格)**

- 実装: ✅ RST / MD ともに §3-1 仕様通り
- 実行結果: ✅ v6 0 FAIL、全テスト pass
- テストカバレッジ: ⚠️ QC4 の単一ケース（RST/title/2-section-swap）のみ。仕様で定義される境界・MD 経路・content 系の検出漏れのリスクを拾えない

ゼロトレランスの品質基準に照らすと、QC4 のユニットテストは明確な不足。回帰（例: MD 経路のみを壊す変更、content vs title の一方を壊す変更、top-level content の扱いのリグレッション）を検出できない。

---

## 5. 改善案（コード変更なし、提案のみ）

以下のテストを `TestCheckContentCompleteness` に追加すべき（優先度順）：

1. **[High] MD QC4 misplaced title** — `verify.py:760` の経路をカバー。`fmt="md"` で swap シナリオ。
2. **[High] QC4 misplaced content (not title)** — title は正しい順だが `content` が他セクションの位置に出る最小ケース。`verify.py:671` / `verify.py:766`。
3. **[Medium] Top-level content appearing after first section** — `data.title` / `data.content` が source 末尾にあり、section 群より後に配置されているケース（top-level が misplaced）。
4. **[Medium] Duplicate substring where order disambiguates QC3 vs QC4** — 同一テキストが 2 箇所にあり、JSON 順が逆なら QC3（duplicate）ではなく QC4（misplaced）になることを確認する鏡像ケース。QC3/QC4 の判定境界（`_in_consumed`）を固める。
5. **[Low] Minimal-pair MD variant** — MD の 2 セクション swap（# heading）。
6. **[Low] 3-section rotation (A→B→C vs C→A→B)** — swap ではなく回転で misplacement が検出されることを確認。

これらを追加すれば、QC4 のテストカバレッジはゼロトレランス基準に適合する。

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code, QC4 ロジック)
- `tools/rbkc/tests/ut/test_verify.py` (unit tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec §3-1, §2-3)
