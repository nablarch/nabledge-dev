# QC3 非重複性 — Independent QA Review (Z-1 R3)

**Reviewer role**: QA Engineer (independent; referenced R2 only for delta)
**Scope**: QC3 detection — duplicate JSON content against normalised source
**Authoritative spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 手順 4 (RST/MD), §3-1 Excel 節 手順 4
**Date**: 2026-04-23

---

## 1. 実装

QC3 は RST / MD / Excel の 3 経路に存在し、各経路で **title / content** の区別があるため、実装上の分岐は 5 つ:

| # | Path            | FAIL 発出箇所                   | 条件 |
|---|-----------------|--------------------------------|------|
| 1 | RST title 重複  | `verify.py:729-730`            | `not is_content` かつ `_in_consumed(prev_idx, len(norm_unit))` |
| 2 | RST content 重複| `verify.py:735-736`            | `is_content` かつ `_in_consumed(...)` |
| 3 | MD title 重複   | `verify.py:824-825`            | 同上 (title) |
| 4 | MD content 重複 | `verify.py:830-831`            | 同上 (content) |
| 5 | Excel cell 重複 | `verify.py:947-948`            | `_in_consumed(prev_idx, len(token))` (Excel は title/content 区別なし) |

**判定ロジック** (3 経路で同一構造、直接照合):

1. `norm_source.find(unit, current_pos)` で前方検索 (spec §3-1 手順 2 "sequential-delete" に対応)
2. 見つからなければ `prev_idx = norm_source.find(unit)` で全域先頭から再検索
3. `prev_idx == -1` → **QC2** (捏造)
4. `prev_idx` が既 consumed 区間と重複 → **QC3** (重複)
5. それ以外 → **QC4** (順序違反) / Excel は **QC1** へ分類 (`verify.py:950`)

**`_in_consumed` (verify.py:715-717, 810-812, 934-936)**:
```
any(pos < e and end > s for s, e in consumed)   # 半開区間のオーバーラップ判定
```
open-interval overlap として正しい。

**Spec との対応照合**:

| Spec §3-1 手順 4 条件                                    | 実装                                                                        |
|----------------------------------------------------------|-----------------------------------------------------------------------------|
| "一度も出現しなかった" → QC2                             | `prev_idx == -1` ✅                                                         |
| "既に削除済みの領域と重複 (先行セクションで消費済み)"→ QC3| `_in_consumed(prev_idx, len(unit))` ✅                                      |
| Excel 手順 4「JSON に既消費領域と重複する位置で出現」→QC3| `verify.py:947-948` — 方向性は JSON 側を削除していく逆方向だが同一判定式 ✅ |

### 実装上の観察

**I-1 [Low]: Excel 側フォールバックは QC1 (not QC4)**

RST/MD の non-content fallback は QC4 (`verify.py:732, 827`)、Excel は QC1 (`verify.py:950`)。
Excel 仕様は「ソースセル値を JSON から削除」という逆方向で、位置順保証が要求されないため QC4 相当の判定自体が発生しないのは仕様上妥当。QC3 検出性能には影響なし。

**I-2 [Low]: `current_pos` は i-1 番目の末尾に進む (i-1 の先頭ではない)**

`current_pos = idx + len(unit)` (L723, L818)。これは spec §3-1 手順 2 の "delete" に合致し、
QC3 のトリガは「先行セクションで消費済みの位置に次の unit が落ちる」ケースに限定される。仕様どおり。

**I-3 [Info]: silent fallback なし**

RST/MD parse error (`verify.py:664-670, 775-777`) は FAIL として issues に append。
no_knowledge_content (早期 return) は spec §3-1 で該当ファイル除外と明記済み。QC3 を隠蔽する経路は存在しない。

---

## 2. テストカバレッジ

### 5 経路の RED テスト

| Path              | テスト名                                     | Location                                   |
|-------------------|----------------------------------------------|--------------------------------------------|
| RST title 重複    | `test_fail_qc3_duplicate_title`              | `test_verify.py:783-790`                   |
| RST content 重複  | `test_fail_qc3_duplicate_content_rst`        | `test_verify.py:1014-1021`                 |
| MD title 重複     | `test_fail_qc3_duplicate_title_md`           | `test_verify.py:1023-1030`                 |
| MD content 重複   | `test_fail_qc3_duplicate_content_md`         | `test_verify.py:1032-1039`                 |
| Excel cell 重複   | `test_fail_qc3_duplicate_cell_in_json`       | `test_verify.py:1156-1173`                 |

**5/5 経路すべて RED テスト存在 (Z-1 gap fill、コメント `test_verify.py:1012`)**。

### 独立 fault injection 検証

R2 で指摘された H-1/H-2 シナリオを本レビューでも独立実機確認:

- **H-1**: source に `概要` 2 回 / JSON sections も 2 回 (同タイトル・異本文) → `[]` (PASS)。誤検出なし ✅
- **H-2**: top-level content=`共通。` と section content=`共通。` で source 側 `共通。` 1 回のみ →
  `[QC3] section 's1': duplicate content: '共通。'` + `[QC1] residue '別。'` 発火。仕様どおり ✅

実装は 両ケースで仕様準拠。ただし **両ケースとも回帰テストは未追加**。

### R2 指摘の改善残存状況

| R2 指摘                                                             | R3 時点の状態           |
|---------------------------------------------------------------------|-------------------------|
| H-1: 短 CJK 繰返し PASS 回帰テスト追加                              | ❌ 未追加               |
| H-2: top-level × section 重複テスト追加                             | ❌ 未追加               |
| M-1: OR アサーション `"QC3" in i or "duplicate content" in i` 廃止  | ❌ 未修正 (L1021, L1039, L1173) |
| M-2: whitespace-only unit PASS 回帰テスト追加                       | ❌ 未追加               |
| L-1: Excel 1 セル vs JSON 2 回の境界テスト                          | ❌ 未追加               |
| L-2: メッセージのセクション ID アサート強化                         | ❌ 未追加               |

R2 と R3 の間でテスト件数は 190 → 197 (+7) に増加しているが、これらの追加は QC3 以外の領域
(grep では QC3 関連テストの追加はゼロ)。**R2 High-priority 指摘 2 件が未対応のまま**。

### 循環テスト懸念

- RST title 重複 (L783-790): `assert any("QC3" in i for i in issues)` — 仕様ラベル単独。循環なし ✅
- MD title 重複 (L1030): 同上。循環なし ✅
- RST/MD content 重複 (L1021, L1039): `"QC3" in i or "duplicate content" in i` — "duplicate content" は
  `verify.py:736, 831` の実装文字列そのまま。実装変更で OR 右辺がマッチし続ける可能性あり → **循環の芽**。
- Excel (L1173): `"QC3" in i or "duplicated" in i` — 実装文字列 `"duplicated in JSON"` (verify.py:948) を
  部分マッチ。同じく **循環の芽**。

アサーション左辺 `"QC3"` は spec ラベル由来なので完全な循環ではないが、OR 右辺の存在は
実装文字列への依存を残し、spec-first 原則を弱める。

---

## 3. v6 実行

```
$ cd tools/rbkc && bash rbkc.sh verify 6 | tail -1
All files verified OK

$ python3 -m pytest tests/ | tail -1
============================= 197 passed in 3.56s ==============================
```

- v6 FAIL 件数: **0**
- pytest: **197 / 197 PASS**
- Fault injection (§2) で QC3 が実際に発火することを独立確認済み。
  「v6 が通るのは QC3 が骨抜きだから」という可能性は否定された。

---

## 4. 総合

**評価: 4 / 5** (R2 と同値、維持)

- 実装は spec §3-1 手順 4 に忠実。RST/MD/Excel 5 経路すべてに QC3 分岐があり、silent fallback なし。
- 5 経路すべて RED テスト存在。v6 FAIL=0、pytest 全通。fault injection で誤検出/検出漏れともに無いことを独立確認。
- 減点は R2 と同一: **R2 High 指摘 (H-1, H-2) が 1 ラウンド経過しても未対応**。ゼロトレランス原則の
  観点では短 CJK 繰返しの回帰テスト欠落が依然最大のリスク (v6 には同一タイトル section 複数が頻出)。
- R2 以降の +7 テスト増は QC3 以外のカバレッジ改善であり、QC3 のロバスト性には反映されていない。

**ブロッキング所見なし** — 実装は正しく、v6 でも破綻していない。テストギャップは回帰耐性の問題。

---

## 5. 改善案 (R2 から継続)

### [High] H-1 (再掲): 短 CJK 繰返しの PASS 回帰テスト

**Issue**: source/JSON に `概要` が同数 (2 回) あるケースの PASS テストがない。
false-positive 耐性が固定されていない。
**Proposed fix**: `test_verify.py` の PASS 節 (L180 周辺) に追加:
```python
def test_pass_qc3_repeated_cjk_title_matching_source(self):
    src = '概要\n====\n\nA。\n\n概要\n====\n\nB。\n'
    data = self._data(sections=[
        {'id':'s1','title':'概要','content':'A。'},
        {'id':'s2','title':'概要','content':'B。'},
    ])
    assert self._check(src, data) == []
```
MD 版 (`fmt="md"`) も追加。

### [High] H-2 (再掲): top-level × section 重複検出テスト

**Issue**: spec §3-1 手順 1 抽出順序 "top-level → sections" に沿った QC3 検出のテストが無い。
**Proposed fix**:
```python
def test_fail_qc3_duplicate_top_and_section_content(self):
    src = 'T\n=\n\n共通。\n\n概要\n====\n\n別。\n'
    data = self._data(title='T', content='共通。', sections=[
        {'id':'s1','title':'概要','content':'共通。'},
    ])
    issues = self._check(src, data)
    assert any('QC3' in i for i in issues)
```

### [Medium] M-1 (再掲): OR アサーション廃止

**Issue**: `test_verify.py:1021, 1039, 1173` の `or "duplicate content" / "duplicated"` は
実装文字列への依存で循環の芽。
**Proposed fix**: OR 右辺を削除し `assert any("QC3" in i for i in issues)` に統一。

### [Medium] M-2 (再掲): whitespace-only unit PASS 回帰テスト

**Proposed fix**: `{'title':'   ','content':'\n\n'}` の section を含む data で `issues == []` をアサート。

### [Low] L-1 / L-2 (再掲): Excel 境界テスト / セクション ID アサート強化

R2 と同内容。

---

## 引用元

- `tools/rbkc/scripts/verify/verify.py:659-758` (RST), `:761-862` (MD), `:865-979` (Excel)
- 主要 FAIL 発出行: `verify.py:729-730, 735-736, 824-825, 830-831, 947-948`
- `_in_consumed`: `verify.py:715-717, 810-812, 934-936`
- `tools/rbkc/tests/ut/test_verify.py:783-790, 1012-1039, 1156-1173`
- `tools/rbkc/docs/rbkc-verify-quality-design.md:83, 171-184, 219-224`
