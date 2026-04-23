# QC3 非重複性 (No duplication) — QA Review

**Target**: QC3 — 同一コンテンツが JSON に重複して含まれている場合を検出する
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1

---

## 1. 実装の有無

### RST — ✅ 実装あり

`tools/rbkc/scripts/verify/verify.py:620-691` `_check_rst_content_completeness`

削除アルゴリズム:
- `verify.py:645` `consumed: list[tuple[int, int]] = []` — 消費済み区間を記録
- `verify.py:648-650` `_in_consumed(pos, length)` — 区間オーバーラップ判定
- `verify.py:653-656` 逐次前進検索 → 見つかれば consumed に追加
- `verify.py:662-663` タイトル重複 → `[QC3] section '{sid}': duplicate title: ...`
- `verify.py:668-669` 本文重複 → `[QC3] section '{sid}': duplicate content: ...`

判定ロジックは spec (§3-1 手順 4) に一致: 前方検索では見つからないが source 全体では見つかり、かつ位置が既消費領域と重複 → QC3。

### MD — ✅ 実装あり

`verify.py:694-794` `_check_md_content_completeness`

- `verify.py:740` `consumed` リスト
- `verify.py:743-745` `_in_consumed`
- `verify.py:757-758` タイトル重複 QC3
- `verify.py:763-764` 本文重複 QC3

RST 版と同一構造で、MD AST 正規化後のテキストに対して動作。✅ spec 準拠。

### Excel — ✅ 実装あり

`verify.py:851-883` `_verify_xlsx`

- `verify.py:864` `consumed` リスト
- `verify.py:867-869` `_in_consumed`
- `verify.py:880-881` `[QC3] Excel cell value duplicated in JSON: ...`

spec Excel 条項 "ソーストークンが見つかったが、その位置が既消費領域と重複していた → QC3" に一致。

---

## 2. ユニットテストのカバレッジ

対象: `tools/rbkc/tests/ut/test_verify.py`

### 実在するテスト

| テスト | 位置 | カバー対象 |
|---|---|---|
| `test_fail_qc3_duplicate_title` | `test_verify.py:458-465` | RST: 同一タイトル "概要" が 2 セクション → QC3 |

### 欠落しているケース — ⚠️ 重大な不足

| 期待ケース | 現状 |
|---|---|
| RST: 同一 **content** ブロックが 2 セクションに出現 | ❌ なし (コードパス `verify.py:668-669` が無テスト) |
| RST: 短い識別子衝突 (e.g. 両セクションが "概要") | △ タイトル側は `test_fail_qc3_duplicate_title` が部分的にカバー。ただし "概要" は 2 文字 CJK で衝突しやすいエッジの確認目的ではない |
| MD: 重複タイトル検出 (`verify.py:757-758`) | ❌ なし |
| MD: 重複 content 検出 (`verify.py:763-764`) | ❌ なし |
| Excel: セル値重複検出 (`verify.py:880-881`) | ❌ なし — `TestVerifyFileExcel` (`test_verify.py:633-686`) は pass 2 件 + QC1 fail 1 件のみ |
| 空白のみトークンで誤 QC3 発火しないこと | ❌ 明示テストなし |
| top-level と section 間の同一テキスト重複 | ❌ なし |
| CJK テキスト重複 (正規化後のマルチバイト境界) | ❌ なし |

QC3 検出パスのうち、**ユニットテストで実行されているのは RST タイトル重複の 1 パスのみ**。MD の 2 パス、Excel の 1 パス、RST content の 1 パス、計 4 パスが未カバー。

**判定: ⚠️ カバレッジ不足** — 実装は 3 フォーマットに存在するが、テストは 1 フォーマット 1 パスに留まる。リグレッションを検出できない状態。

---

## 3. v6 verify 実行結果 + ユニットテスト結果

### v6 verify

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0
$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK
```

✅ **0 FAIL** — QC3 を含む全チェックが現時点の v6 出力を通過。

### ユニットテスト

```
$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 3.71s ==============================
```

✅ 138 件全 pass。

---

## 4. 総合判定

**⚠️ 条件付き合格 (要追加テスト)**

- 実装: ✅ RST / MD / Excel の 3 フォーマット全てに QC3 検出ロジックが存在し、spec §3-1 手順 4 に一致
- v6 出力: ✅ 0 FAIL
- ユニットテスト: ⚠️ 4/5 の QC3 検出コードパスがテスト未カバー。プロジェクト品質基準「1% のリスクも許容しない」「verify は品質ゲート」に照らすと**現状は不合格水準**。verify の検出ロジックに静かなリグレッションが入っても検知できない。

---

## 5. 改善案

### [High] QC3 テストを検出パスの数まで拡張

以下 4 ケースを `test_verify.py` に追加する。いずれも verify のみを対象とし、RBKC 実装には手を入れない。

1. **RST content 重複** (`verify.py:668-669` をカバー)
   - ソース: 2 セクション、同一 content 文字列 "本文A。"
   - JSON: 両セクションが `content="本文A。"`
   - 期待: `QC3` かつ `duplicate content` を含む issue

2. **MD タイトル重複** (`verify.py:757-758`)
   - `fmt="md"` で `test_fail_qc3_duplicate_title` と同等ケース

3. **MD content 重複** (`verify.py:763-764`)

4. **Excel セル値重複** (`verify.py:880-881`)
   - `TestVerifyFileExcel` に追加。ソース: A1="値X" (単一セル)、JSON: `title="値X", content="値X"` → QC3

### [Medium] エッジケーステスト追加

5. **短い CJK 衝突の検出境界**
   - 両セクションが `title="概要"` (2 文字) で source に "概要" が 2 回出現する場合に、2 回目のセクションが **正しく消費される** (QC3 にならない) パス — sequential-delete が意図通り動くことを保証

6. **Top-level と section 間の同一 title 重複**
   - top-level `title="X"`, section `title="X"` で source には "X" が 1 回のみ → 2 つ目が QC3

7. **空白のみ unit で QC3 誤発火なし**
   - `_squash` / normalization で unit が空文字列になる場合、consumed に登録されず QC3 も発火しないことを確認

### [Low] テストファイル構成

- 既存の `# --- QC3: duplicate content ---` コメント直下に RST content 重複テストを並べ、MD は `TestVerifyMd` 相当、Excel は `TestVerifyFileExcel` 内と、フォーマット別に集約する。

---

## 引用 file:line 一覧

- `tools/rbkc/scripts/verify/verify.py:600` QC1/QC2/QC3/QC4 dispatcher
- `tools/rbkc/scripts/verify/verify.py:645-669` RST QC3 implementation
- `tools/rbkc/scripts/verify/verify.py:740-764` MD QC3 implementation
- `tools/rbkc/scripts/verify/verify.py:864-881` Excel QC3 implementation
- `tools/rbkc/tests/ut/test_verify.py:458-465` 唯一の QC3 テスト (RST title 重複)
- `tools/rbkc/tests/ut/test_verify.py:633-686` Excel テストクラス (QC3 テスト欠落)
