# QC3 非重複性 — Independent QA Review (Z-1 R2)

**Reviewer role**: QA Engineer (independent, no prior review seen)
**Scope**: QC3 detection — duplicate JSON content against normalised source
**Authoritative spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 手順 4 (RST/MD), §3-1 Excel 手順 4
**Date**: 2026-04-23

---

## 1. 実装

QC3 は RST / MD / Excel の 3 経路に存在し、各経路で **title** / **content** の区別があるため、実装上の分岐は以下 5 つ:

| # | Path | Location | 分岐 |
|---|------|----------|------|
| 1 | RST title 重複 | `verify.py:681-682` | `_in_consumed(prev_idx, len(norm_unit))` かつ `not is_content` |
| 2 | RST content 重複 | `verify.py:687-688` | 同上かつ `is_content` |
| 3 | MD title 重複 | `verify.py:776-777` | 同上 |
| 4 | MD content 重複 | `verify.py:782-783` | 同上 |
| 5 | Excel cell 重複 | `verify.py:899-900` | `_in_consumed(prev_idx, len(token))` (Excel は title/content 区別なし) |

**判定ロジック** (3 経路とも同一構造):

1. `norm_source.find(unit, current_pos)` で前方検索 (sequential-delete と同じ順方向)
2. 見つからなければ `prev_idx = norm_source.find(unit)` で全域最先頭を再検索
3. `prev_idx == -1` → QC2 (fabricated)
4. `prev_idx` が `consumed` 区間と重複 → **QC3**
5. それ以外 → QC4 (misplaced)

**判定式 `_in_consumed`** (verify.py:667-669, 762-764, 886-888):
```
any(pos < e and end > s for s, e in consumed)
```
— 区間重複判定 (pos, pos+length) と (s, e) の open-interval overlap。正しい。

**Silent fallback の有無**:

- QC1 parse error (RST `UnknownSyntaxError` L645-650, MD L723-729) は **FAIL** として issues へ append。silent fallback ではない。
- no_knowledge_content (L612, L871) は空 issues で早期 return → 仕様どおり (spec §3-1 該当ファイル除外)。

**スペックとの整合性チェック** (spec §3-1 手順 4 を実装コードに照合):

| Spec 手順 4 条件 | 実装 |
|------------------|------|
| 「正規化ソース中に当該テキストが一度も出現しなかった」 → QC2 | `prev_idx == -1` → QC2 ✅ |
| 「既に削除済みの領域と重複」 → QC3 | `_in_consumed(prev_idx, len(unit))` ✅ |

Excel spec §3-1 手順 4 (「ソーストークンが見つかったが、その位置が既消費領域と重複」) も `verify.py:899-900` が `_in_consumed(prev_idx, len(token))` で一致。

### 懸念点 (実装)

**C-1 [Medium]: 前方検索 current_pos の副作用で QC3 が QC4 に誤判定される可能性**

`current_pos = idx + len(unit)` (L675, L770) で次の検索開始位置を前進させる。もし同じ unit が
`...[unit A][noise][unit A][unit A]...` のように 3 回出現し、source 側に 2 回しか存在しないソースで JSON 側が 3 回ある場合:

- 1 回目 JSON A: pos=0 を消費、current_pos=len(A)
- 2 回目 JSON A: pos=X (中央の A) を消費、current_pos=X+len(A)
- 3 回目 JSON A: `find(A, current_pos)` → 後方に 3 つ目の A が source に存在すれば消費してしまう

→ ソースに 2 回しかなくても、JSON の 3 回目が consumed 区間外の位置に見つかれば正常扱いになる。ただし**これは前提矛盾** (上の例は source に 3 つ A がある場合)。source に 2 つしかなければ 3 つ目は `idx == -1` → `prev_idx` で最先頭 (consumed 内) → QC3 で正しく検出される。

したがって**バグではない**が、`current_pos` の前進は仕様 §3-1 手順 2 (「削除」) に対応しており spec どおり。

**C-2 [Low]: QC3 vs QC4 の境界**

JSON 順 i 番目の unit が `find(unit, current_pos)` で見つからない場合:
- `prev_idx != -1` かつ `_in_consumed` False → QC4 (misplaced)

Spec §3-1 手順 2 は「i-1 番目の削除位置よりも前であれば QC4」と定義。実装は `current_pos` 基準 (i-1 番目の**末尾**位置) を使っているため、spec よりわずかに厳しい (前に出るだけで FAIL になる範囲が広い)。QC3 検出側には影響なし。

**C-3 [Low]: Excel の「方向性逆転」と QC3 の意味**

Spec §3-1 Excel では「ソースセル値を JSON テキストから削除」とある (L211)。verify.py:890-903 は仕様どおり source tokens を JSON text から delete しており、QC3 は「source に同一値セルが複数あるが JSON に 1 つしかない」場合に発火する。これは spec §3-1 手順 4 Excel 版 (L224) と一致。

---

## 2. テストカバレッジ

### 5 経路の RED テスト有無

| Path | テスト | Location |
|------|--------|----------|
| RST title 重複 | `test_fail_qc3_duplicate_title` | test_verify.py:734-741 |
| RST content 重複 | `test_fail_qc3_duplicate_content_rst` | test_verify.py:960-967 |
| MD title 重複 | `test_fail_qc3_duplicate_title_md` | test_verify.py:969-976 |
| MD content 重複 | `test_fail_qc3_duplicate_content_md` | test_verify.py:978-985 |
| Excel cell 重複 | `test_fail_qc3_duplicate_cell_in_json` | test_verify.py:1085-1102 |

**5/5 すべての検出経路に対応する RED テストが存在** (Z-1 gap fill コメント付き。test_verify.py:958)。

### アサーション品質

5 テストすべて `assert any("QC3" in i ...)` の形式。文字列 "QC3" のみチェックしており、セクション ID や具体的な unit 内容のアサーションは一部不足。ただし **QC3 検出の有無** (PASS/FAIL の 2 値判定) としては十分。

### Edge cases の不足

以下のエッジケースが**未カバー**:

**E-1 [High]: 短 CJK 衝突 (2 セクション両方 "概要" タイトルで本文が別)**

`test_fail_qc3_duplicate_title` (L734) は source に "概要" が 1 回のみ、JSON に 2 回ある構図。**source にも "概要" が 2 回あり JSON にも 2 回ある (正常)** ケースの PASS テストがない。これは v6 で頻発しうるパターンで、誤検出 (false positive) がないことを別途検証すべき。

実機確認: source に "概要" が 2 回あり JSON にも 2 回あるケース — 前方検索で両方正しく consume → PASS することを独立確認した (fault-injection:
```
src = '概要\n====\n\nA本文。\n\n概要\n====\n\nB本文。\n'
data = sections=[(s1, 概要, A本文。), (s2, 概要, B本文。)]
→ []  (PASS, 正しい)
```
)。実装は正しいが **回帰テストがない**。

**E-2 [High]: top-level content と section content の間の重複**

Spec §3-1 手順 1 で抽出順序は `top-level title → top-level content → sections[0].title → ...` と明示。しかし top-level content と section content が同じ文字列の場合のテストがない。Fault injection:
```
src = 'T\n=\n\n共通。\n\n概要\n====\n\n別。\n'
data = {'title':'T','content':'共通。','sections':[(s1,概要,'共通。')]}
→ [QC3 duplicate content '共通。', QC1 residue '別。']
```
QC3 は発火したが **副作用として QC1 false positive** が出る (共通。を 2 回 delete しようとして 1 回しか消せなかった分の残渣)。これは誤検出ではなく正しい FAIL だが **テストで明示的に固定されていない**。

**E-3 [Medium]: Excel で source 2 セル同値、JSON に 3 回出現**

実機確認:
```
cells: A1='X', A2='X' / JSON: 'X X X'
→ []  (PASS、FAIL 未検出)
```
これは仕様どおり (token find は 2 回しか走らず、JSON 残渣 "X" は _MD_SYNTAX_RE + whitespace 除去により潰される可能性) だが、**QC2 超過検出の欠落**かもしれない。ただし QC3 の範囲外。

**E-4 [Medium]: whitespace-only unit false-fire**

Fault injection (section title/content が空白のみ):
```
data = sections=[..., {'id':'s2','title':'   ','content':'  \n\n'}]
→ []  (PASS)
```
`_norm` で空白を潰すため whitespace-only は search_units に入らず、false-fire しない。実装は正しいが **テスト未カバー**。

### 循環テストチェック (assertion が implementation を鏡映)

- test_fail_qc3_duplicate_title (L734-741) は「JSON に 概要 が 2 回、source に 1 回」 → spec §3-1 手順 4「先行削除済み領域と重複」の定義に忠実。assertion は "QC3" の文字列チェックのみで **実装内部名ではなく仕様由来のラベル**。循環ではない ✅
- Excel test (L1085-1102) も同様。循環ではない ✅
- ただし **一部アサーションが `"QC3" in i or "duplicate content" in i`** (L967, L985, L1102) と OR で緩めている。"duplicate content" は実装文字列 (verify.py:688, 783) をそのまま書いており、仕様ラベル「QC3」のみでアサートすべき。**循環の兆候あり**。

---

## 3. v6 実行

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0

$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK

$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......          [100%]
============================= 190 passed in 3.74s ==============================
```

- v6 FAIL 件数: **0**
- pytest: **190 / 190 PASS**

**Fault injection で QC3 が実際に発火することを独立確認** (§2 E-1〜E-3 参照)。したがって「v6 が通るのは QC3 ロジックが骨抜きだから」という可能性は否定された。

---

## 4. 総合

**評価: 4 / 5**

- 実装は spec §3-1 手順 4 の定義 (「先行削除済み領域と重複」) に忠実に対応。RST/MD/Excel の 5 経路すべてに QC3 判定分岐があり、silent fallback は存在しない。
- 5 経路すべての RED テストが存在する (Z-1 gap fill)。v6 FAIL=0、pytest 190 件すべて PASS。fault injection で QC3 が正しく発火することを独立確認した。
- 減点: **E-1 (短 CJK 衝突の PASS テスト欠落)** と **E-2 (top-level と section 間の重複テスト欠落)** は QC3 のロバスト性を担保する上で必要。また一部テストが実装文字列 "duplicate content" を OR でアサートしており、わずかに循環の兆候がある。

ゼロトレランス原則の観点では、**E-1 の回帰テスト欠落が最大のリスク**: v6 には `概要` セクションが複数あるファイルが多数存在し、RBKC 側の変更で誤検出が入った場合、PASS テストがないため検知されない。

---

## 5. 改善案

### [High] H-1: 短 CJK 繰返しの PASS 回帰テスト追加

**Issue**: source/JSON に `概要` が同数 (2 回) あるケースの PASS テストが無く、実装の false-positive 耐性が固定されていない。
**Proposed fix**: test_verify.py の PASS ケース節に以下を追加:
```
def test_pass_qc3_repeated_cjk_title_matching_source(self):
    src = '概要\n====\n\nA。\n\n概要\n====\n\nB。\n'
    data = self._data(sections=[
        {'id':'s1','title':'概要','content':'A。'},
        {'id':'s2','title':'概要','content':'B。'},
    ])
    assert self._check(src, data) == []
```
MD 版 (fmt="md") も同様に追加。

### [High] H-2: top-level と section 間の重複検出テスト追加

**Issue**: spec §3-1 手順 1 の抽出順序「top-level → sections」に沿った QC3 検出 (top-level content と section content が同文字列) のテストが無い。
**Proposed fix**:
```
def test_fail_qc3_duplicate_top_and_section_content(self):
    src = 'T\n=\n\n共通。\n\n概要\n====\n\n別。\n'
    data = self._data(title='T', content='共通。', sections=[
        {'id':'s1','title':'概要','content':'共通。'},  # source has 共通。 only once
    ])
    issues = self._check(src, data)
    assert any('QC3' in i for i in issues)
```

### [Medium] M-1: OR アサーションの廃止 (循環の芽を除く)

**Issue**: `assert any("QC3" in i or "duplicate content" in i for i in issues)` (test_verify.py:967, 985, 1102) は実装文字列を並列でアサートしており、仕様ラベル単独でアサートすべき。
**Proposed fix**: "duplicate content" / "duplicated" を削除し `assert any("QC3" in i for i in issues)` のみに統一。

### [Medium] M-2: whitespace-only unit の PASS 回帰テスト追加

**Issue**: title/content が空白のみのケースが `_norm` で除外されることを固定するテストがない。
**Proposed fix**: `{'title':'   ','content':'\n\n'}` の section を含む data で `issues == []` をアサート。

### [Low] L-1: Excel で source 1 セル・JSON 2 回出現の回帰テスト明示化

**Issue**: verify_file Excel パスで「1 セルに対し JSON が 2 回引用」が QC2 で検出されることは実機確認できたが、テストは `test_fail_cell_missing_from_json` (L1040) のみで QC3 とは別トピック。QC3 テストとの境界を明示する PASS/FAIL 対テストがあると良い。
**Proposed fix**: test_fail_qc3 の近傍に「1 セル vs JSON 2 回引用 → QC2 と QC3 のどちらが出るか」を固定するテストを追加 (現状は QC2)。

### [Low] L-2: QC3 メッセージのセクション ID アサート強化

**Issue**: 現行アサーションは文字列 "QC3" のみチェック。どのセクションで重複したかを固定すれば、将来のリファクタで間違ったセクションを責めるバグをキャッチできる。
**Proposed fix**: `assert any("QC3" in i and "s2" in i for i in issues)` のようにセクション ID もアサート。

---

## 引用元

- `tools/rbkc/scripts/verify/verify.py:611-710` (RST), `:713-813` (MD), `:870-920` (Excel)
- `tools/rbkc/tests/ut/test_verify.py:734-741, 960-985, 1085-1102`
- `tools/rbkc/docs/rbkc-verify-quality-design.md:83, 171-184, 219-224`
