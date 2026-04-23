# QC3 非重複性 — Independent QA Review (Z-1 R5)

**Reviewer role**: QA Engineer (independent; bias-avoidance — formed the
assessment from spec + code + tests first, cross-referenced R4 only for delta)
**Scope**: QC3 detection — duplicate JSON content against normalised source
(RST / MD / Excel)
**Authoritative spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md`
§3-1 手順 4 (RST/MD), §3-1 Excel 節 手順 4
**Date**: 2026-04-23

---

## 1. 実装 — 5 経路

仕様 §3-1 手順 4 により QC3 は 5 経路に分岐する。

| # | Path         | verify.py 発出行 | 条件                                                         | 仕様準拠 |
|---|--------------|------------------|--------------------------------------------------------------|----------|
| 1 | RST title    | L580             | `not is_content` かつ `_in_consumed(prev_idx, len(norm_unit))` | ✅ |
| 2 | RST content  | L586             | `is_content` かつ `_in_consumed(...)`                           | ✅ |
| 3 | MD title     | L675             | title, `_in_consumed(...)`                                    | ✅ |
| 4 | MD content   | L681             | content, `_in_consumed(...)`                                  | ✅ |
| 5 | Excel cell   | L798             | `_in_consumed(prev_idx, len(token))` (title/content 区別なし、仕様どおり) | ✅ |

**共通判定ロジック** (RST/MD/Excel で構造同一):

1. `find(unit, current_pos)` で前方逐次検索
2. 見つからなければ `find(unit)` で先頭から再検索 → `prev_idx`
3. `prev_idx == -1` → **QC2** (RST/MD) / **QC1** (Excel, 方向が逆)
4. `prev_idx` が既 consumed 区間と open-interval overlap → **QC3** 発出
5. それ以外 → **QC4** (RST/MD) / **QC1** (Excel)

`_in_consumed` (verify.py:565-567, 660-662, 784-786):

```python
any(pos < e and end > s for s, e in consumed)
```

半開区間の overlap 判定として数学的に正しい。`current_pos = idx + len(unit)`
で「直前 unit の末尾」に進むため、「先行セクションで消費済み」が仕様どおり
成立する。

**silent fallback 経路なし**:
- RST parse error (L547)、MD parse error (L626) はどちらも **QC1 FAIL**
- `_no_knowledge` ガード (L510) は仕様上の除外
- QC3 を黙って緑にする経路は存在しない

### 独立 fault injection (bias-avoidance)

spec と実装から独立にシェル経由で `check_content_completeness` を直接叩き、
QC3 の発火/不発火を 3 パターン独立確認した:

| # | 入力                                                         | 期待             | 実測出力                                    | 判定 |
|---|--------------------------------------------------------------|------------------|---------------------------------------------|------|
| F-1 | src=`共通。` / JSON top+section に `共通。` 二重             | QC3 発火         | `[QC3] section 's1': duplicate content: '共通。'` | ✅ |
| F-2 | src に `## 概要` 二回 (別 body) / JSON も 2 セクション同名   | 発火しない       | `[]`                                        | ✅ |
| F-3 | src に `note` 二回 (A,B セクション) / JSON は s1 のみ消費    | QC3 は発火しない | `[QC1] residue...'B note'` (QC1 のみ)        | ✅ |

「v6 PASS は QC3 骨抜き」説は 3 独立注入で否定。短 CJK 同名タイトル (F-2)
も誤検出せず、位置曖昧性だけでは QC3 化しないこと (F-3) も確認。

---

## 2. テストカバレッジ

### 5 経路の FAIL テスト

| Path             | テスト名                                                | 行    | アサーション            |
|------------------|---------------------------------------------------------|-------|-------------------------|
| RST title 重複   | `test_fail_qc3_duplicate_title`                         | 839   | `"QC3" in i` ✅ 純粋    |
| RST content 重複 | `test_fail_qc3_duplicate_content_rst`                   | 1088  | `"QC3" in i or "duplicate content" in i` ⚠️ OR 残存 |
| MD title 重複    | `test_fail_qc3_duplicate_title_md`                      | 1097  | `"QC3" in i` ✅ 純粋    |
| MD content 重複  | `test_fail_qc3_duplicate_content_md`                    | 1130  | `"QC3" in i or "duplicate content" in i` ⚠️ OR 残存 |
| Excel cell 重複  | `test_fail_qc3_duplicate_cell_in_json`                  | 1355  | `"QC3" in i or "duplicated" in i` ⚠️ OR 残存 |

**5/5 経路すべて FAIL テスト存在**。

### 境界 / positive guard テスト

| 観点                                            | テスト名                                                 | 行    | 状態 |
|-------------------------------------------------|----------------------------------------------------------|-------|------|
| 短 CJK タイトル同数繰返し (false-positive 耐性) | `test_pass_qc3_short_cjk_repeated_in_source_and_json`    | 1106  | ✅ PASS |
| top-level × section content 重複                 | `test_fail_qc3_top_level_and_section_content_duplicated` | 1119  | ✅ FAIL |
| QC3 / QC4 境界 (重複テキスト + 単一消費)        | `test_fail_qc3_qc4_boundary_duplicate_text_misplaced`    | 1172  | ✅ not-QC3 guard |

依頼事項 (短 CJK collision PASS / top×section 重複 FAIL) は満たされている。

### 循環性 (bias-avoidance)

"assertion wording ⇔ 実装 message wording" の循環を点検:

| テスト行       | 左辺 (spec ラベル) | 右辺 (impl message 断片)     | 循環度 |
|----------------|---------------------|-------------------------------|--------|
| 839 (RST title)  | `"QC3" in i`      | -                             | なし ✅ |
| 1088 (RST content) | `"QC3" in i`    | `"duplicate content" in i`    | 軽循環 (G-1 残) |
| 1097 (MD title)    | `"QC3" in i`    | -                             | なし ✅ |
| 1119 (top×section) | `"QC3" in i`    | `"duplicate content" in i`    | 軽循環 (G-1 残) |
| 1130 (MD content)  | `"QC3" in i`    | `"duplicate content" in i`    | 軽循環 (G-1 残) |
| 1172 (境界)        | `not any("QC3" in i)` | -                         | なし ✅ |
| 1372 (Excel)       | `"QC3" in i`    | `"duplicated" in i`           | 軽循環 (G-1 残) |

左辺に spec ラベル `"QC3"` が必ず入っているため「実装を逆にしたら赤」の
最低保証はある (bias-avoidance 合格)。右辺 OR は R3/R4 から継続指摘中
(M-1) だが、QA 規律上の改善余地であり現出力を疑わせるものではない。

### 未解決ギャップ

- **G-1 [Medium]**: OR アサート 4 件 (L1088, L1119, L1130, L1372) 残存。
  単純 sed で除去可能。R3→R4→R5 の 3 ラウンド連続指摘。
- **G-2 [Medium]**: whitespace-only unit の PASS 回帰テスト欠落
  (`_norm` / `_squash` 後に空文字になる unit が skip されるか)。R3 M-2 以来未対応。
- **G-3 [Low]**: Excel QC3 の N>1 発火回数 `==` アサート欠落。
- **G-4 [Low]**: 5 経路テストにセクション ID (`"'s2'" in i`) アサート未付与。

---

## 3. verify + pytest

```
$ cd tools/rbkc && bash rbkc.sh verify 6 | tail -1
All files verified OK

$ python3 -m pytest tests/ | tail -1
============================= 219 passed in 4.13s ==============================
```

- v6 FAIL: **0**
- pytest: **219 / 219 PASS** (R4 211 → R5 219, +8)
- Fault injection F-1/F-2/F-3: 期待どおり

---

## 4. 総合

**評価: 4 / 5** (R4 と同値、維持)

**正の面**:
- 実装は spec §3-1 手順 4 に忠実、5 経路すべて分岐あり silent fallback なし。
- 5 経路 FAIL + 短 CJK PASS + top×section FAIL + QC3/QC4 境界 guard すべて存在。
- v6 FAIL=0、pytest 219/219、fault injection 3 件独立確認済み。

**減点要因 (1 pt)**:
- G-1 OR アサート残存 4 件 (R3/R4/R5 連続、機械的除去可)
- G-2 whitespace-only 回帰テスト未追加 (R3 以来)
- G-3 Excel N>1 / G-4 section ID アサートは軽微

**ブロッキング所見なし**。検出性能は fault injection で立証済み、残存ギャップは
すべて回帰耐性・循環予防の改善であって QC3 本体の正当性は毀損していない。

---

## 5. 改善案 (優先度順)

### [Medium] G-1: OR アサートの機械的除去

対象 4 箇所:
- `test_verify.py:1095` (`test_fail_qc3_duplicate_content_rst`)
- `test_verify.py:1128` (`test_fail_qc3_top_level_and_section_content_duplicated`)
- `test_verify.py:1137` (`test_fail_qc3_duplicate_content_md`)
- `test_verify.py:1372` (`test_fail_qc3_duplicate_cell_in_json`)

各 `or "..." in i` 部分を削除。実装メッセージ文言を書き換えても spec ラベル
`"QC3"` 単独で検出可能となり、循環の芽を構造的に除去できる。

### [Medium] G-2: whitespace-only unit PASS 回帰テスト

```python
def test_pass_qc3_whitespace_only_unit(self):
    src = "# T\n\n## 概要\n\n本文。\n"
    data = self._data(title="T", sections=[
        {"id": "s1", "title": "概要", "content": "本文。"},
        {"id": "s2", "title": "   ", "content": "\n\n"},
    ])
    issues = self._check(src, data, fmt="md")
    assert not any("QC3" in i for i in issues)
    assert not any("QC2" in i for i in issues)
```

`if title:` / `if content:` ガードが空文字 unit を skip することの保護網。

### [Low] G-3: Excel N>1 発火回数アサート

```python
assert sum("QC3" in i for i in issues) == 1
```

「1 回発火で満足」の弱さを排除。

### [Low] G-4: セクション ID アサート強化

既存 5 経路の `assert any("QC3" in i ...)` に `and "'s2'" in i` を追加して
メッセージ書式 (section id 出力) への回帰耐性を確保。

---

## 引用元

- `tools/rbkc/scripts/verify/verify.py:508-608` (RST), `:611-711` (MD), `:768-814` (Excel)
- 主要 FAIL 発出: `verify.py:580, 586, 675, 681, 798`
- `_in_consumed`: `verify.py:565-567, 660-662, 784-786`
- `tools/rbkc/tests/ut/test_verify.py:839, 1086-1197, 1355-1372`
- `tools/rbkc/docs/rbkc-verify-quality-design.md:83, 171-184, 219-224, 350`
- R4 baseline: `.work/00299/review-z1-r4/QC3.md`

## R4 からのデルタ

- pytest 211 → 219 (+8、うち QC4 MD/3-swap 系の追加含む。QC3 固有テストは R4 から追加なし)
- v6 FAIL 0 を維持
- R4 で未対応だった G-1 (OR アサート) / G-2 (whitespace-only) は R5 でも未対応
- 結論: R4 評価 4/5 を維持。QC3 本体は安全、改善余地は回帰耐性領域に限定。
