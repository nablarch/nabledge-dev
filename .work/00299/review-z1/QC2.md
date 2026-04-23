# QC2 正確性 (Accuracy — no fabrication) レビュー

**Target ID**: QC2
**Scope**: RST / MD / Excel
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (判定分岐のまとめ / Excel sequential-delete 末尾)
**Date**: 2026-04-23

---

## 1. 実装の有無

### RST ✅

- `tools/rbkc/scripts/verify/verify.py:620` `_check_rst_content_completeness`
- sequential-delete アルゴリズム: `verify.py:652-671`
- QC2 分岐 (fabricated title): `verify.py:660-661` (`prev_idx == -1` → `fabricated title`)
- QC2 分岐 (fabricated content): `verify.py:666-667` (`prev_idx == -1` → `fabricated content`)
- QC2 vs QC3 判別: `_in_consumed` (`verify.py:648-650`) で `prev_idx` が既に消費済みなら QC3、全く無ければ QC2 に分岐 (`verify.py:660-671`)
- ノーマライザ: `scripts/common/rst_normaliser.py` 経由で visitor 出力と合わせて比較するため、RST 記法差異での誤検知を排除 (`verify.py:631`)

### MD ✅

- `tools/rbkc/scripts/verify/verify.py:694` `_check_md_content_completeness`
- sequential-delete: `verify.py:747-766`
- QC2 分岐 (fabricated title): `verify.py:754-756`
- QC2 分岐 (fabricated content): `verify.py:761-762`
- QC2 vs QC3 判別: `_in_consumed` (`verify.py:743-745`) により分岐 (`verify.py:755-766`)
- ノーマライザ: `scripts/common/md_normaliser.py:normalise_md` 経由で visitor 出力と合わせて比較 (`verify.py:704-709`)

### Excel ✅

- `tools/rbkc/scripts/verify/verify.py:_verify_xlsx` 内、`verify.py:885-908`
- 逆方向 sequential-delete: ソースセルを JSON テキストから消去 (`verify.py:871-883`)、消費後の残渣をトークン分割して捏造判定 (`verify.py:900-908`)
- QC2 生成箇所: `verify.py:908` (`[QC2] JSON token not found in Excel source`)
- 2 文字以上のトークンのみを QC2 として報告 (`verify.py:907`) — 記号単発を除外

---

## 2. ユニットテストのカバレッジ

### RST / MD

| テスト | 観点 | 所在 |
|--------|------|------|
| `test_fail_qc2_fabricated_title` | ソースに存在しない section title | `test_verify.py:440-446` |
| `test_fail_qc2_fabricated_content` (CJK) | CJK 本文の捏造 (`"捏造されたテキスト。"`) | `test_verify.py:448-454` |
| `test_fail_qc3_duplicate_title` | QC2 vs QC3 分岐 (duplicate) | `test_verify.py:458-465` |
| `test_fail_qc4_misplaced_title` | QC2 vs QC4 分岐 (misplaced) | `test_verify.py:469-476` |
| `test_pass_md_verbatim_match` (MD) | QC2 誤検知なし | `test_verify.py:528-536` |
| `test_pass_rst_double_backtick_inline_code` | RST→MD 記法差異で QC2 が出ないこと | `test_verify.py:549-553` |
| `test_pass_rst_external_link_text` | `\`text <url>\`_` → `[text](url)` | `test_verify.py:565` |
| `test_pass_rst_ref_display_form_resolved` | `:ref:` 表示形解決 | `test_verify.py:571` |

### Excel

| テスト | 観点 | 所在 |
|--------|------|------|
| `test_pass_real_xlsx` | QC2 誤検知なし | `test_verify.py:647-659` |
| `test_fail_cell_missing_from_json` | QC1 (inverse) — QC2 単独はなし | `test_verify.py:661-673` |

### 不足しているテスト ⚠️

期待されるが欠落している QC2 テストケース:

1. **🟡 Excel の QC2 直接 FAIL ケース無し**
   - `TestVerifyFileExcel` に QC1 の欠落テストはあるが、**JSON 側に存在してソースに無い捏造文字列** (= QC2) を直接検証するテストが存在しない (`test_verify.py:633-686`)
   - 例: セル `"A"` のみの xlsx + JSON に `{"title": "A", "content": "捏造文"}` → `[QC2] JSON token not found in Excel source: '捏造文'` を期待
   - QC2 は Excel 実装にも存在する (`verify.py:908`) ため、TDD 原則上ユニットテスト必須

2. **🟡 CJK Visitor 境界またぎのケースなし**
   - 現行 `test_fail_qc2_fabricated_content` は単純な CJK 捏造のみ。Visitor が段落境界を越えて visit したときに、境界付近の捏造が検出できるかのテストがない
   - 例: セクションをまたぐ `"A段落最後B段落最初"` のような構築物

3. **🟡 near-miss (1 文字差) のテストなし**
   - ソース `"応答電文のステータスコード"` / JSON `"応答電文のステータス=コード"` のような 1 文字差捏造での QC2 検出テスト無し
   - 現状のアルゴリズムは正規化後に `.find()` するので検出されるはずだが、空白正規化 (`verify.py:639, 715`) により誤って吸収されないかの境界確認が必要

4. **🟡 whitespace-only discrepancy のテスト欠落**
   - ソースに空白として存在、JSON では「内容」として載っている場合 (JSON 側のみ文字として存在) の QC2 挙動のテスト無し
   - 空白正規化 (`re.sub(r"\s+", " ", ...)`) の後でどう判定されるかが不明瞭

5. **🟡 単一ファイル内複数捏造のテスト無し**
   - 現状は 1 件 FAIL の検出しかアサートしていない (`assert any(...)`)。複数セクションで QC2 が重複発生した場合、各々がレポートされることの確認なし
   - 例: `sections=[s1 捏造, s2 捏造]` → `len([i for i in issues if "QC2" in i]) >= 2` のアサート

6. **🟢 fabricated top-level title/content の QC2 テスト無し**
   - `test_fail_qc2_*` は section レベルのみ。top-level `title` / `content` が捏造されたときも QC2 が出ることの直接アサート無し
   - 実装上は RST 側 `_build_rst_search_units` は top-level を `sid="top"` で扱うため動作するはずだが、保証テストが欠けている

### 既存テストの品質 ✅

- QC2 と QC3/QC4 の分岐が 3 テストで明確に分離されている (`test_verify.py:440-476`)
- 正常系 (誤検知なし) が RST 記法 4 種 / MD 記法 1 種で網羅されており、false-positive 予防に有効

---

## 3. v6 verify 実行結果

```bash
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0

$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | tail -1
All files verified OK

$ cd tools/rbkc && python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_verify.py ................................................ [ 76%]
...........................                                              [ 95%]
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 2.79s ==============================
```

- ✅ v6 verify: 0 FAIL
- ✅ unit tests: 138 passed

---

## 4. 総合判定

| 観点 | 判定 |
|------|------|
| 実装 (RST) | ✅ 仕様通り |
| 実装 (MD) | ✅ 仕様通り |
| 実装 (Excel) | ✅ 仕様通り |
| 単体テスト (RST/MD FAIL/PASS) | ✅ 主要パスあり |
| 単体テスト (QC2 vs QC3/QC4 分岐) | ✅ 分岐ケースあり |
| 単体テスト (Excel QC2 FAIL) | ⚠️ 直接テスト欠落 |
| 単体テスト (エッジケース) | ⚠️ near-miss / 複数捏造 / whitespace / top-level などに穴 |
| v6 verify 0 FAIL | ✅ |
| pytest all pass | ✅ (138 passed) |

**総合**: ⚠️ **概ね良好だが、ゼロトレランス基準に照らすとエッジケーステストに不足あり**

実装自体は仕様 §3-1 に準拠し、v6 全体で 0 FAIL を達成している。一方、TDD 原則 (`.claude/rules/rbkc.md`「Every new check added to verify requires a corresponding test before implementation」) に照らすと、**Excel QC2 は実装があるが FAIL 系単体テストが存在しない**点が厳密には規約違反であり、補強が必要。

---

## 5. 改善案

### 🟡 [優先: 高] Excel QC2 の FAIL 系単体テスト追加

**Description**: `verify.py:908` の QC2 分岐 (`[QC2] JSON token not found in Excel source`) を直接カバーするテストが無い。
**Proposed fix**: `TestVerifyFileExcel` に下記を追加:

```python
def test_fail_qc2_fabricated_token_in_json(self, tmp_path):
    """Excel: JSON に存在するがソースセルに無いトークン → QC2."""
    wb = openpyxl.Workbook(); ws = wb.active; ws["A1"] = "正しい値"
    xlsx_path = tmp_path / "t.xlsx"; wb.save(xlsx_path)
    data = {"id": "f", "title": "正しい値", "content": "捏造トークン", "sections": []}
    issues = self._check(str(xlsx_path), data)
    assert any("QC2" in i and "捏造トークン" in i for i in issues)
```

### 🟡 [優先: 中] 複数捏造・top-level 捏造・near-miss エッジケース追加

**Description**: 上記 §2「不足しているテスト」の 2〜6 を網羅する。
**Proposed fix**: `TestCheckContentCompleteness` に以下を追加:

- `test_fail_qc2_multiple_fabrications` — 2 セクションに別々の捏造、両方レポートされることをアサート
- `test_fail_qc2_fabricated_top_level_title` / `_content` — top-level 捏造
- `test_fail_qc2_near_miss_one_char_diff` — 1 文字差の捏造が QC2 として検出されること
- `test_fail_qc2_cjk_across_visitor_boundary` — セクション境界またぎの捏造

### 🟢 [優先: 低] whitespace-only discrepancy の挙動を確定

**Description**: `re.sub(r"\s+", " ", ...)` による正規化で、空白のみ相違の QC2 取り扱い (検出するか黙過か) が仕様にも現状テストにも無い。
**Proposed fix**: 仕様側にポリシーを明記したうえで、期待挙動のテストを追加。実装変更は仕様確定後。

---

## 付録: 参照

- 実装: `tools/rbkc/scripts/verify/verify.py:599-691` (RST), `:694-796` (MD), `:798-910` (Excel)
- テスト: `tools/rbkc/tests/ut/test_verify.py:425-626` (RST/MD), `:629-686` (Excel)
- 仕様: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1
