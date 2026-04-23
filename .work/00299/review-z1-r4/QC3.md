# QC3 非重複性 — Independent QA Review (Z-1 R4)

**Reviewer role**: QA Engineer (independent; bias-avoidance — did not read R3 findings before forming the assessment; cross-referenced only at the end for delta)
**Scope**: QC3 detection — duplicate JSON content against normalised source (RST / MD / Excel)
**Authoritative spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 手順 4 (RST/MD), §3-1 Excel 節 手順 4
**Date**: 2026-04-23

---

## 1. 実装

仕様 §3-1 手順 4 は「未削除 JSON テキスト」を 2 分岐させる:

- 正規化ソースに一度も出現しない → **QC2 (捏造)**
- 正規化ソースに存在するが先行削除済みの領域と重複 → **QC3 (重複)**

Excel (§3-1 Excel 節 手順 4) は方向が逆 (ソースセル値を JSON テキストから削除):

- JSON に一度も出現しない → QC1 (欠落)
- JSON に存在するが既消費領域と重複 → **QC3 (重複)**

したがって「5 経路 (RST title / RST content / MD title / MD content / Excel cell)」が存在する。

### Spec vs 実装 照合

| # | Path             | 実装位置 (verify.py) | 条件                                                     | 仕様準拠 |
|---|------------------|-----------------------|----------------------------------------------------------|----------|
| 1 | RST title        | L580                  | `not is_content` かつ `_in_consumed(prev_idx, len(norm_unit))` | ✅ |
| 2 | RST content      | L586                  | `is_content` かつ `_in_consumed(...)`                       | ✅ |
| 3 | MD title         | L675                  | 同上 (title)                                              | ✅ |
| 4 | MD content       | L681                  | 同上 (content)                                            | ✅ |
| 5 | Excel cell       | L798                  | `_in_consumed(prev_idx, len(token))` (title/content 区別なし、仕様どおり) | ✅ |

**判定ロジック (3 経路で同一構造)**:

1. `norm_source.find(unit, current_pos)` で前方検索 (sequential-delete)
2. 見つからなければ `prev_idx = norm_source.find(unit)` で先頭から再検索
3. `prev_idx == -1` → **QC2 (捏造)**
4. `prev_idx` が既 consumed 区間と重複 → **QC3 (重複)**
5. それ以外 → RST/MD は **QC4**、Excel は **QC1** 側 (L800)

**`_in_consumed` 判定 (verify.py:565-567, 660-662, 784-786)**:

```python
any(pos < e and end > s for s, e in consumed)
```

半開区間の open-interval overlap として数学的に正しい。

**silent fallback なし**: RST parse error (L547)、MD parse error (L626) はどちらも QC1 FAIL として `issues` に append。`no_knowledge_content` ガード (`_no_knowledge` L510) は仕様上の除外。QC3 を隠蔽する経路は存在しない。

### 観察所見

**I-1 [Info]**: Excel 側 fallback は **QC1** (L800)、RST/MD は **QC4**。Excel は方向が逆で位置順保証の概念がないため仕様上妥当。QC3 本体の検出には影響しない。

**I-2 [Info]**: `current_pos = idx + len(unit)` (L573, L668) で「直前 unit の末尾」まで進む。「先行セクションで消費済み」の判定が仕様どおり機能する。

---

## 2. テストカバレッジ

### 5 経路の RED テスト

| Path              | テスト名                                       | 行       | アサーション |
|-------------------|------------------------------------------------|----------|--------------|
| RST title 重複    | `test_fail_qc3_duplicate_title`                | L839     | `"QC3" in i` ✅ 純粋 |
| RST content 重複  | `test_fail_qc3_duplicate_content_rst`          | L1070    | `"QC3" in i or "duplicate content" in i` ⚠️ OR 残存 |
| MD title 重複     | `test_fail_qc3_duplicate_title_md`             | L1079    | `"QC3" in i` ✅ 純粋 |
| MD content 重複   | `test_fail_qc3_duplicate_content_md`           | L1112    | `"QC3" in i or "duplicate content" in i` ⚠️ OR 残存 |
| Excel cell 重複   | `test_fail_qc3_duplicate_cell_in_json`         | L1274    | `"QC3" in i or "duplicated" in i` ⚠️ OR 残存 |

**5/5 経路すべて RED テスト存在**。Z-1 gap fill コメント (L1068) で明示。

### 境界テスト (R4 ラウンドで追加済)

| 観点                                       | テスト名                                                        | 行     | 結果 |
|--------------------------------------------|-----------------------------------------------------------------|--------|------|
| 短 CJK タイトル同数繰返し (false-positive 耐性) | `test_pass_qc3_short_cjk_repeated_in_source_and_json`           | L1088  | ✅ 追加済 |
| top-level × section 重複検出                 | `test_fail_qc3_top_level_and_section_content_duplicated`        | L1101  | ✅ 追加済 |
| QC3 / QC4 境界 (重複テキスト + 単一消費のみ) | `test_fail_qc3_qc4_boundary_duplicate_text_misplaced`           | L1154  | ✅ 追加済 (R4 PASS 期待ガード) |

**R3 High-priority 指摘 2 件 (H-1: 短 CJK 繰返し / H-2: top×section) は R4 で回帰テストとして結実**している。

### 未解決ギャップ

**G-1 [Medium]**: **whitespace-only unit の PASS 回帰テスト無し**。
`_norm` / `_squash` 後に空文字になる unit が `if norm:` / `if title:` / `if content:` ガードで skip されるかの回帰テストが存在しない (grep 検索 `whitespace-only unit` → `test_verify.py:239` は QO2 用で QC3 非該当)。
R3 M-2 で指摘されながら未追加。
**Proposed fix**:
```python
def test_pass_qc3_whitespace_only_unit(self):
    src = "# T\n\n## 概要\n\n本文。\n"
    data = self._data(title="T", sections=[
        {"id": "s1", "title": "概要", "content": "本文。"},
        {"id": "s2", "title": "   ", "content": "\n\n"},  # whitespace-only
    ])
    issues = self._check(src, data, fmt="md")
    assert not any("QC3" in i for i in issues)
    assert not any("QC2" in i for i in issues)
```

**G-2 [Medium]**: **OR アサーションによる循環の芽が 3 箇所残存** (L1077, L1110, L1119, L1291)。
`"duplicate content" in i` / `"duplicated" in i` は `verify.py:586, 681, 798` の実装文字列を直接ミラーしており、実装メッセージを書き換えるだけで赤が緑に化ける可能性がある。左辺 `"QC3"` は spec ラベルなので完全な循環ではないが、右辺を残す意味が無い (現在の実装メッセージに「QC3」が確実に含まれることが実機確認できる)。
**Proposed fix**: OR 右辺を削除し `assert any("QC3" in i for i in issues)` に統一。4 行の機械的修正。

**G-3 [Low]**: L1274 Excel 重複テストが **cell 1 個 / JSON 1 回** の最小ケース。spec §3-1 Excel 節 手順 4 の「ソース中に N 回、JSON に M < N 回」の一般ケース (例: N=3, M=1) の境界テストなし。
**Proposed fix**:
```python
def test_fail_qc3_three_source_cells_one_json_occurrence(self, tmp_path):
    # 3 cells of "同じ" but JSON contains it only once → 2 QC3 fires
    ...
    assert sum("QC3" in i for i in issues) == 2
```

**G-4 [Low]**: 既存テストはセクション ID をアサートしていない (`assert any("QC3" in i ...)` のみ)。メッセージ書式が `section '{sid}': duplicate ...` に準拠していることの保証が無い。
**Proposed fix**: `assert any("QC3" in i and "'s2'" in i for i in issues)`。

### 循環テスト精査

| テスト           | 左辺             | 右辺                                | 判定 |
|------------------|------------------|-------------------------------------|------|
| L839 RST title   | `"QC3" in i`     | (無し)                              | 循環なし ✅ |
| L1079 MD title   | `"QC3" in i`     | (無し)                              | 循環なし ✅ |
| L1088 PASS CJK   | `not any("QC3" in i and "概要" in i)` | -                    | 循環なし ✅ |
| L1101 top×sec    | `"QC3" in i`     | `"duplicate content" in i`          | **軽循環 G-2** |
| L1070 RST content| `"QC3" in i`     | `"duplicate content" in i`          | **軽循環 G-2** |
| L1119 MD content | `"QC3" in i`     | `"duplicate content" in i`          | **軽循環 G-2** |
| L1168 境界ガード | `not any("QC3" in i)` | -                              | 循環なし ✅ |
| L1291 Excel      | `"QC3" in i`     | `"duplicated" in i`                 | **軽循環 G-2** |

左辺が spec ラベル `"QC3"` である限り実装を逆にしたら赤になる (bias-avoidance の最低保証あり) が、右辺の存在は QA 規律上望ましくない。

### 独立 fault injection (bias-avoidance)

レビュー本体とは別に直接 `verify_file` / `check_content_completeness` をシェルから呼び出し、QC3 が実際に発火するかを確認:

- **F-1**: source `共通。\n` + JSON top-level content=`共通。` + section content=`共通。` → `[QC3] section 's1': duplicate content` が発火 ✅
- **F-2**: source `概要\n====\n\nA。\n\n概要\n====\n\nB。\n` + JSON sections=[(概要,A。),(概要,B。)] → `[]` (PASS) ✅ 誤検出なし
- **F-3**: Excel `A1=同じ, B1=同じ` + JSON title=`同じ` → `[QC3] Excel cell value duplicated in JSON: '同じ'` ✅

「v6 PASS は QC3 が骨抜きだから」という可能性は 3 つの独立注入で否定された。

---

## 3. v6 実行 / pytest

```
$ cd tools/rbkc && bash rbkc.sh verify 6 | tail -1
All files verified OK

$ python3 -m pytest tests/ | tail -1
============================= 211 passed in 3.36s ==============================
```

- v6 FAIL 件数: **0**
- pytest: **211 / 211 PASS** (R3 197 → R4 211、+14 のうち QC3 境界テスト 3 件が寄与)
- Fault injection F-1 / F-2 / F-3 で QC3 が正しく発火/不発火することを独立確認済み

---

## 4. 総合

**評価: 4 / 5** (R3 と同値、維持)

**正の面**:
- 実装は spec §3-1 手順 4 に忠実。RST/MD/Excel 5 経路すべてに QC3 分岐があり silent fallback なし。
- R3 High 2 件 (H-1 短 CJK PASS / H-2 top×section 重複) は R4 で回帰テストとして追加済。
- QC3 / QC4 境界の positive guard テスト (L1154) も R4 で追加済。
- v6 FAIL=0、pytest 211/211。fault injection で誤検出/検出漏れともに無し。

**減点要因 (1 pt)**:
- R3 Medium (M-1 OR アサート廃止 / M-2 whitespace-only 回帰) が R4 で未対応のまま。
- G-3 (Excel N>1 境界) / G-4 (section ID アサート) も未対応。

**ブロッキング所見なし** — 実装は正しく、検出性能も fault injection で立証済み。残存ギャップはすべて回帰耐性・循環予防の改善であり、現出力の品質を疑わせるものではない。

---

## 5. 改善案

### [Medium] G-1: whitespace-only unit PASS 回帰テスト追加

§2 G-1 の fix をそのまま適用。1 テスト追加、30 秒作業。

### [Medium] G-2: OR アサーションの機械的削除

`test_verify.py` L1077, L1110, L1119, L1291 の OR 右辺を削除 (4 箇所、sed 可)。実装メッセージを書き換えても `"QC3"` ラベル単独で検出可能。循環の芽を構造的に除去。

### [Low] G-3: Excel N>1 境界テスト

§2 G-3 の fix を適用。QC3 発火回数を `==` で固定することで「1 回発火で満足」の弱さを補強。

### [Low] G-4: セクション ID アサート強化

既存 5 経路テストの `assert any("QC3" in i ...)` に `and "'sN'" in i` を追加 (メッセージ書式への回帰耐性)。

---

## 引用元

- `tools/rbkc/scripts/verify/verify.py:508-608` (RST), `:611-711` (MD), `:768-814` (Excel)
- 主要 FAIL 発出行: `verify.py:580, 586, 675, 681, 798`
- `_in_consumed`: `verify.py:565-567, 660-662, 784-786`
- `tools/rbkc/tests/ut/test_verify.py:839, 1068-1168, 1274-1291`
- `tools/rbkc/docs/rbkc-verify-quality-design.md:83, 171-184, 219-224`
