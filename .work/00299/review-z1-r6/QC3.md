# QC3 非重複性 — Independent QA Review (Z-1 R6)

**Reviewer role**: QA Engineer (independent; bias-avoidance — re-derived the
assessment from spec + code + tests, then cross-referenced R5 only for delta).
**Scope**: QC3 detection — duplicate JSON content against normalised source
(RST / MD / Excel), 5 発出経路 + edge cases + circular-reference audit.
**Authoritative spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md`
§3-1 手順 4 (RST/MD) / §3-1 Excel 節 手順 4
**Date**: 2026-04-23
**Overall rating**: 4 / 5 (R5 と同値、維持)

---

## 1. 実装 — 5 経路すべて確認

仕様 §3-1 手順 4 の QC3 定義:「JSON テキストが正規化ソースに存在するが、その
位置が既消費領域と重複している」→ RST/MD/Excel の 3 フォーマット × (title /
content) の組で、RST 2 + MD 2 + Excel 1 = **計 5 経路**。

| # | Path        | 発出箇所 | 条件                                                      | 仕様準拠 |
|---|-------------|----------|-----------------------------------------------------------|:--------:|
| 1 | RST title   | `verify.py:581` | `not is_content` かつ `_in_consumed(prev_idx, len(norm_unit))` | ✅ |
| 2 | RST content | `verify.py:587` | `is_content` かつ `_in_consumed(...)`                        | ✅ |
| 3 | MD title    | `verify.py:676` | title, `_in_consumed(...)`                                  | ✅ |
| 4 | MD content  | `verify.py:682` | content, `_in_consumed(...)`                                | ✅ |
| 5 | Excel cell  | `verify.py:799` | `_in_consumed(prev_idx, len(token))` (title/content 区別なし、仕様どおり) | ✅ |

共通判定ロジックは 3 フォーマットで構造同一:

1. `find(unit, current_pos)` で前方逐次検索
2. 見つからなければ `find(unit)` で先頭から再検索 → `prev_idx`
3. `prev_idx == -1` → **QC2** (RST/MD) / **QC1** (Excel は方向が逆)
4. `prev_idx` が既 consumed 区間と open-interval overlap → **QC3**
5. 上記以外 → **QC4** (RST/MD) / **QC1** (Excel)

`_in_consumed` の実装 (`verify.py:566-568`, `:661-663`, `:785-787`):

```python
any(pos < e and end > s for s, e in consumed)
```

半開区間 overlap 判定として数学的に正しい。`current_pos = idx + len(unit)`
(`:574`, `:669`, `:793`) により「直前 unit の末尾」に前進するため、仕様の
「先行セクションで消費済み」が構造的に成立する。

**silent fallback は存在しない**:
- RST parse error → `verify.py:548` で QC1 FAIL
- MD parse error → `verify.py:627` で QC1 FAIL
- `_no_knowledge` ガード (`:511`, `:770`) は仕様上の除外
- QC3 を黙って緑化する経路なし

### 独立 fault injection (bias-avoidance)

実装のメッセージ文字列を読まずに、spec の期待挙動だけから 4 パターンを
独立に注入。`check_content_completeness` / `_verify_xlsx` を直接呼んだ結果:

| # | 入力                                                             | 期待                 | 実測                                                  | 判定 |
|---|------------------------------------------------------------------|----------------------|-------------------------------------------------------|:----:|
| F-1 | MD: top-level content と s1 content が同一、source に 1 回のみ | QC3 発火             | `[QC3] section 's1': duplicate content: '共通。'`      | ✅ |
| F-2 | MD: 同名 H2 "概要" が 2 回、JSON も 2 セクション同名 (正当)     | 発火なし             | `[]`                                                  | ✅ |
| F-3 | RST: "note" が A/B 両セクションに、JSON は s1 のみ消費          | QC3 不発火 (残余QC1) | `[QC1] residue not captured in JSON: 'B note'`        | ✅ |
| F-4 | Excel: A1/B1 に "同じ"、JSON には 1 回のみ                       | QC3 発火             | `[QC3] Excel cell value duplicated in JSON: '同じ'`    | ✅ |

4/4 すべて仕様どおり。「v6 PASS = QC3 骨抜き」説は独立注入で否定された。
短 CJK 同名タイトルでの誤検出 (F-2) も、位置曖昧性単独での過剰検出 (F-3) も
観測されない。

---

## 2. テストカバレッジ

### 5 経路すべてに FAIL テスト存在

| Path             | テスト名                                                 | 行     | アサーション                              |
|------------------|----------------------------------------------------------|--------|-------------------------------------------|
| RST title 重複   | `test_fail_qc3_duplicate_title`                          | `:873`  | `"QC3" in i` (純粋)                        |
| RST content 重複 | `test_fail_qc3_duplicate_content_rst`                    | `:1122` | `"QC3" in i or "duplicate content" in i` (OR) |
| MD title 重複    | `test_fail_qc3_duplicate_title_md`                       | `:1131` | `"QC3" in i` (純粋)                        |
| MD content 重複  | `test_fail_qc3_duplicate_content_md`                     | `:1164` | `"QC3" in i or "duplicate content" in i` (OR) |
| Excel cell 重複  | `test_fail_qc3_duplicate_cell_in_json`                   | `:1361` | `"QC3" in i or "duplicated" in i` (OR)     |

### 境界 / positive guard テスト

| 観点                                             | テスト名                                                  | 行      |
|--------------------------------------------------|-----------------------------------------------------------|---------|
| 短 CJK 同名タイトル重複の誤検出耐性              | `test_pass_qc3_short_cjk_repeated_in_source_and_json`     | `:1140` |
| top-level × section content 重複                  | `test_fail_qc3_top_level_and_section_content_duplicated`  | `:1153` |
| QC3/QC4 境界 (dup テキスト + 単一消費で QC3 抑止) | `test_fail_qc3_qc4_boundary_duplicate_text_misplaced`     | `:1206` |

依頼の「edge cases (短 CJK collision / top×section / QC3-QC4 境界)」すべて
カバーされている。

### 循環性の点検 (bias-avoidance)

「assertion wording ⇔ 実装 message wording」循環の有無:

| テスト行 | 左辺 (spec ラベル)    | 右辺 (impl message 断片)   | 循環度     |
|----------|------------------------|-----------------------------|------------|
| `:873`    | `"QC3" in i`          | —                           | なし ✅    |
| `:1122`   | `"QC3" in i`          | `"duplicate content" in i`  | 軽循環 (G-1) |
| `:1131`   | `"QC3" in i`          | —                           | なし ✅    |
| `:1140`   | `not any("QC3" in i)` | —                           | なし ✅    |
| `:1153`   | `"QC3" in i`          | `"duplicate content" in i`  | 軽循環 (G-1) |
| `:1164`   | `"QC3" in i`          | `"duplicate content" in i`  | 軽循環 (G-1) |
| `:1206`   | `not any("QC3" in i)` | —                           | なし ✅    |
| `:1361`   | `"QC3" in i`          | `"duplicated" in i`         | 軽循環 (G-1) |

左辺には必ず spec ラベル `"QC3"` が入っており、「実装を反転したら赤」の
最低保証は全件で確保されている (bias-avoidance 基準 PASS)。右辺 OR は
実装メッセージ文言依存のため純粋な spec-only 検証ではないが、QC3 が
発火しない不具合は左辺だけで検出できる。

### 未解決ギャップ

| ID | 優先度 | 内容                                                                   | 初出 | 状態 |
|----|--------|------------------------------------------------------------------------|------|------|
| G-1 | Medium | OR アサート 4 箇所 (`:1122`, `:1153`, `:1164`, `:1361`) の残存         | R3   | R6 未対応 |
| G-2 | Medium | whitespace-only unit (`if title:` / `if content:` skip 境界) の PASS 回帰テスト欠落 | R3 | R6 未対応 |
| G-3 | Low    | Excel QC3 で `sum(...) == 1` 等の発火回数アサート欠落                 | R4   | R6 未対応 |
| G-4 | Low    | 5 経路 FAIL テストにセクション ID (`"'s2'" in i`) アサート未付与      | R5   | R6 未対応 |

---

## 3. verify + pytest

```
$ cd tools/rbkc && bash rbkc.sh verify 6
All files verified OK

$ python3 -m pytest tests/
221 passed in 2.42s
```

- v6 FAIL: **0**
- pytest: **221 / 221 PASS** (R5 219 → R6 221, +2)
- Fault injection F-1/F-2/F-3/F-4: 期待どおり発火・抑止

---

## 4. 総合評価

**Rating: 4 / 5** (R5 維持)

**正の面**:
- 実装は spec §3-1 手順 4 に忠実。5 経路すべて分岐が存在し、silent fallback なし。
- 5 経路 FAIL + 短 CJK PASS + top×section FAIL + QC3/QC4 境界 guard すべて揃う。
- v6 FAIL=0、pytest 221/221、独立 fault injection 4 件で検出性能を立証。
- 左辺 spec ラベル assertion により「実装を反転したら赤」の最低保証全件 OK。

**減点要因 (1 pt)**:
- G-1 OR アサート 4 件残存 (R3→R4→R5→R6 で 4 連続指摘、機械的除去可)
- G-2 whitespace-only 回帰テスト未追加 (R3 以来)
- G-3 Excel 発火回数 / G-4 section ID アサートは軽微

**ブロッキング所見なし**。検出性能は fault injection で立証済み、残存ギャップは
すべて回帰耐性・循環予防の改善であり QC3 本体の正当性を毀損していない。

---

## 5. 改善案 (優先度順、review-feedback.md 準拠)

### [Medium] G-1: OR アサートの機械的除去

- Description: 4 箇所 (`test_verify.py:1129, 1162, 1171, 1375`) で
  `or "duplicate content" in i` / `or "duplicated" in i` が残存し、
  実装メッセージ文言への軽循環を構成している。
- Proposed fix: 各アサートの `or "..." in i` を削除。spec ラベル `"QC3"`
  単独で検出可能にし、循環の芽を構造的に除去する。R3 から 4 ラウンド
  連続指摘のため、本 Round で機械的に適用して closeout すべき。

### [Medium] G-2: whitespace-only unit の PASS 回帰テスト

- Description: `_build_rst_search_units` / MD 側 `search_units` は
  `if title:` / `if content:` ガードで空/空白のみの unit を skip するが、
  この挙動を保護する回帰テストが無い。ガードが壊れると `_squash("   ") == ""`
  が `current_pos=0` の全一致にヒットして偽 QC3/QC4 が発火しうる。
- Proposed fix:
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

### [Low] G-3: Excel QC3 発火回数アサート

- Description: Excel テスト (`test_verify.py:1361`) は `any("QC3" in i ...)` で
  1 回以上発火を要求するのみ。N>1 発火の回帰を捕捉できない。
- Proposed fix: `assert sum("QC3" in i for i in issues) == 1` を追加。

### [Low] G-4: セクション ID アサート

- Description: 5 経路 FAIL テストは section id (`'s2'` 等) の出力を検証
  しない。メッセージ書式がリグレッションしても気付かない。
- Proposed fix: `assert any("QC3" in i and "'s2'" in i for i in issues)` に置換。

---

## 6. R5 からのデルタ

| 項目                        | R5              | R6              |
|-----------------------------|-----------------|-----------------|
| v6 verify FAIL              | 0               | 0               |
| pytest PASS 数              | 219             | 221 (+2)        |
| QC3 固有テスト追加          | —               | なし            |
| fault injection             | F-1/F-2/F-3 (3) | F-1/F-2/F-3/F-4 (4, Excel 経路追加) |
| OR アサート (G-1) 残存      | 4               | 4 (未対応)      |
| whitespace-only 回帰 (G-2)  | 未              | 未              |
| 評価                         | 4/5             | 4/5             |

---

## 引用元

- `tools/rbkc/scripts/verify/verify.py:509-609` (RST `_check_rst_content_completeness`)
- `tools/rbkc/scripts/verify/verify.py:612-712` (MD `_check_md_content_completeness`)
- `tools/rbkc/scripts/verify/verify.py:769-834` (Excel `_verify_xlsx`)
- 主要 QC3 FAIL 発出: `verify.py:581, 587, 676, 682, 799`
- `_in_consumed`: `verify.py:566-568, 661-663, 785-787`
- `tools/rbkc/tests/ut/test_verify.py:873, 1122, 1131, 1140, 1153, 1164, 1206, 1361`
- spec: `tools/rbkc/docs/rbkc-verify-quality-design.md:83, 171-185, 219-224, 350`
- R5 baseline: `.work/00299/review-z1-r5/QC3.md`
