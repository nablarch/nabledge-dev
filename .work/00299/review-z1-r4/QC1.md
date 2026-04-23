# QC1 完全性 — 独立 QA レビュー (review-z1-r4)

**Reviewer role**: Independent QA Engineer (bias-avoidance)
**Bias-avoidance 明示**:
- 仕様 `tools/rbkc/docs/rbkc-verify-quality-design.md` を唯一の権威とする
- circular test (実装出力に合わせた期待値固定) を能動的に flag する
- v6 FAIL 0 件は「弱い証拠」として扱い、単体テストでの FAIL 再現を最優先で確認する
- 「空で returns [] になっていること」と「チェックが十分であること」を区別する

**対象仕様**:
- §3-1 削除手順 (手順 0〜4)
- §3-1b zero-exception principle
  - 未登録 node → FAIL (QC1)
  - 未登録 role → FAIL (QC1)
  - 未解決 reference / substitution → FAIL (QC1)
  - parse error (level ≥ 3) → FAIL (QC1)
  - silent fallback 禁止、drop エントリは「価値ゼロ」確認済みのみ許容
- §3-1 残存判定: 空白・改行・タブ以外が残れば QC1 FAIL、許容リスト禁止
- §3-1 Excel 節: セル値を JSON から削除、見つからなければ QC1

---

## 1. 実装レビュー

### 1-1. zero-exception の実装

**Visitor 層 (`scripts/common/rst_ast_visitor.py`)**:

- L147 `raise UnknownNodeError(f"unmapped node: {name}")` — 未登録 node で raise ✅
- L561 `raise UnknownNodeError(f"unmapped inline node: {name}")` — 未登録 inline node ✅
- L586 `raise UnknownRoleError(f"unknown role: {role}")` — 未登録 role ✅
- L599 / L603 `raise UnresolvedReferenceError(f"unresolved :ref: ...")` — 未解決 :ref: ✅
- L646 `raise UnresolvedReferenceError(f"unresolved reference: {refname}")` — 未解決 named reference ✅
- L655 `raise UnresolvedReferenceError(f"unresolved substitution: ...")` — 未解決 substitution ✅
- L160-161 `visit_system_message` で `level >= 3` → `raise VisitorError("RST parse error...")` ✅

**MD Visitor (`scripts/common/md_ast_visitor.py`)**:

- L220 / L235 / L330 / L336 / L468 で `UnknownTokenError` を raise ✅ (5 箇所で未登録 token を検出)

**Normaliser (`scripts/common/rst_normaliser.py`, `md_normaliser.py`)**:

- rst_normaliser L53-58: `VisitorError` を `UnknownSyntaxError` として再 raise (strict_unknown=True) ✅
- md_normaliser L58-62: 同上 ✅

**verify 側 (`scripts/verify/verify.py`)**:

- `_check_rst_content_completeness` L544-548: `UnknownSyntaxError` を捕捉 → `[QC1] RST parse/visitor error: ...` を issues に追加し **即 return** ✅
- `_check_md_content_completeness` L623-627: 同上 ✅

**残存チェック** (§3-1 no-tolerance):

- RST: L604-606 `if residue.strip(): issues.append(f"[QC1] residue not captured in JSON: ...")` ✅ 許容リスト無し
- MD: L705-709 同様、許容リスト無し ✅

**Excel QC1** (§3-1 Excel 節 手順 2):

- `_verify_xlsx` L794-800: `json_text.find(token)` で `prev_idx == -1` → `[QC1] Excel cell value missing from JSON` ✅
- `_in_consumed` で消費領域を追跡し QC3 と区別 ✅
- `.xls` 分岐 L732-742 (`xlrd.open_workbook`) と `.xlsx` 分岐 L744-755 (`openpyxl`) の両方をサポート ✅

### 1-2. silent fallback / "tolerance"-style コード有無

仕様に反する silent fallback を探索した結果、以下を確認:

- verify.py 全体で `try ... except ... pass` / 無声化 `except Exception: return []` が存在する箇所:
  - L399-400 `_source_urls` (QL2) の `doctree, _ = rst_ast.parse(...)` に try/except — **QL2 用途で QC1 とは別チェック**。ただしここで parse error を飲むこと自体は QC1 側で既に同じ source を normalise して FAIL するため二重検出は避けられるが、**QC1 側の parse error を先行させる実装順** (verify_file L853 `check_content_completeness` が先、L855 `check_external_urls` が後) になっているので整合 ✅
  - L898-901 `check_source_links` (QL1) も同様に try/except — QC1 側が先に FAIL するので許容 ✅
- L458 `_normalize_rst_source` は `strict_unknown=True` を渡しているため **silent fallback なし** ✅
- L557-558 `if not search_units: return issues` — 空 JSON は検証スキップ。これは仕様 §3-1 手順1 の「JSON テキストリスト抽出」が空集合の場合の妥当な早期 return であり tolerance ではない。ただし後述 §3 で懸念点として記載する。
- L773-774 `_verify_xlsx` の `if not tokens: return []` — ソースセル 0 件なら検証不能だが、**空 Excel ソースを正しい入力とみなす**前提に依存。§3 で懸念点として記載。
- L776-778 `if not json_text.strip(): return []` — 空 JSON + 非空セルなら本来 QC1 FAIL すべき **懸念あり** (§3 参照)

### 1-3. 「廃棄 (drop)」対応表エントリの確認

- `rst_ast_visitor.visit_comment` L166-167 が `return None` (comment node を drop)
- `visit_target` L169 以降も drop 対象
- `visit_system_message` L164 は level < 2 で drop

これらは仕様 §3-1b の「価値ゼロ確認済み」枠。comment / target / system_message(level<2) は読者視認コンテンツではないため妥当。**ただし横断的に全 drop を一覧化した監査証跡が 5 章変更プロセス文書に残っているかは未確認**。これは本レビューの直接対象外。

---

## 2. テストカバレッジレビュー

### 2-1. 仕様由来の FAIL 条件を単体テストが主張しているか

| 仕様上の FAIL トリガー | テスト | 評価 |
|-----------------------|--------|------|
| 未登録 node | (なし — inline 側の代替は L1035) | ⚠️ 欠落 |
| 未登録 role | `test_fail_qc1_rst_unknown_role_surfaces` L1035-1041 | ✅ |
| 未解決 :ref: | (負テスト無し — L938 のコメントで言及のみ) | ⚠️ 欠落 |
| 未解決 named reference | (無し) | ⚠️ 欠落 |
| 未解決 substitution | (無し) | ❌ **欠落** (§3-1b 明示項目) |
| parse error level≥3 | (無し) | ❌ **欠落** (§3-1b 明示項目) |
| 未登録 MD token | `test_fail_qc1_md_unknown_token_surfaces` L1011-1033 | ✅ (token 注入で直接 Visitor を trigger) |
| 残存 非空白テキスト | `test_fail_qc1_residual_content` L861-868 | ✅ |
| Excel セル値欠落 | `test_fail_cell_missing_from_json` L1212-1224 | ✅ |
| Excel `.xls` 形式 | (無し — `.xlsx` のみ) | ⚠️ 欠落 (仕様 §3-1 Excel 節「`.xlsx` と `.xls` の両形式」) |
| 空ソース (empty source) | (無し) | ⚠️ 欠落 |
| 空白のみソース | (無し) | ⚠️ 欠落 |
| CJK 境界 / 短い CJK | `test_pass_qc3_short_cjk_repeated_in_source_and_json` L1088 (PASS 方向のみ) | 🟡 片方向のみ |

**主要ギャップ**:

1. **未解決 substitution の負テストが存在しない**。`UnresolvedReferenceError` を実際に起こす RST (例: `|undefined_sub|`) を含むサンプルで QC1 FAIL を主張するテストが必須だが未実装。§3-1b 明示項目のため **High 優先**。
2. **parse error level≥3 の負テストが存在しない**。RST 仕様違反ソース (例: 不整合 indent、閉じない literal block) で docutils が `system_message(level=3)` を埋め込む → QC1 FAIL する path が `visit_system_message` に存在するが、verify.py L544-548 経由で QC1 issue に変換されるエンドツーエンドテストは無い。**High 優先**。
3. **`.xls` (旧 Excel) path のテストが無い**。`xlrd` 分岐は実装されているが単体テストが `.xlsx` のみ。仕様に両形式対応と明記されているため **Medium 優先**。
4. **未解決 :ref: / named reference / 未登録 node** の 3 種の `VisitorError` 派生について、unknown role 1 種類だけでは Visitor 全体の strict path 検証として不十分。**Medium 優先**。
5. **空ソース / 空白のみソース** の挙動テスト (QC1 観点では通常 PASS または JSON 空で PASS) が無い。verify.py L517-518 / L773-778 で早期 return が効く条件の境界確認が無いため、将来のリファクタで silent skip が混入するリスク。**Medium 優先**。

### 2-2. circular test の有無

|ケース|懸念|評価|
|---|---|---|
| `test_pass_rst_syntax_in_residual_allowed` L870-880 | JSON content の期待値 `"本文。\n\n> **Note:**\n> 注記内容。"` は converter (create 側) の出力形そのもの。verify 側の normaliser が converter と同じ helper を共有しているため、**「converter 出力 = verify 期待値」の循環** になる可能性がある | 🟡 構造的 circular リスクあり。ただし §3-1 は「create と verify が共通 Visitor で MD 記法を揃える」と規定しているため、この一致自体は仕様準拠。しかし **仕様違反 (例: 「注記」内容が欠落) を catch できるかは別テストが必要**。現状そのテストが無い。 |
| `test_pass_rst_ref_label_resolved_text` L936-944 | label_map を手で与えて PASS を主張 — label 解決が動くことの確認。verify 実装自体を試すもので OK | ✅ not circular |
| `test_pass_rst_field_list_*` L988-1007 | 期待値が「Visitor の現実装の出力」にぴったり合わせた形 (`` `%` 、 `_` ``) | 🟡 Visitor 出力の観測値を固定している可能性。仕様文書に「field_list は name を drop し value を残す」という原則は記載あり (§3-1a 参照) なので、この PASS 期待値は仕様由来と解釈可能。**仕様文書に対応表の詳細ルールが無ければ circular**。 |
| `test_fail_qc1_md_unknown_token_surfaces` L1011-1033 | 直接 token stream を inject して Visitor を trigger | ✅ not circular (Visitor 内部の raise を直接叩いている) |

**Circular リスク総合評価**: `test_pass_rst_syntax_in_residual_allowed` と `test_pass_rst_field_list_*` は create/verify 共通 Visitor の出力を期待値固定している。仕様 §3-1 が「create/verify が同じ Visitor を使う」ことを要求しているため、同一性テストとしては正しいが、**仕様違反を検出する負方向テスト** (例: Visitor が admonition body を drop したら必ず QC1 FAIL) が不足している。**Medium 優先**。

### 2-3. テスト実行結果

```
$ cd tools/rbkc && python3 -m pytest tests/ 2>&1 | tail -3
============================= 211 passed in 4.25s ==============================
```

全 211 件 PASS ✅

---

## 3. v6 実データ実行

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0
$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK
```

FAIL 0 件 ✅

**bias-avoidance 視点の注記**: FAIL 0 は「現状の v6 生成物と現状の verify 実装が整合している」ことのみを示す。上記 §2-1 のテストギャップがあるため、verify が見逃している未解決 substitution / parse error 等のケースが実データに存在した場合でも検出できない可能性は残る。v6 passing = 弱い証拠。

---

## 4. 総合評価

| 評価軸 | 判定 |
|--------|------|
| 実装: 仕様準拠 | ✅ zero-exception path が Visitor → Normaliser → verify の 3 層で一貫して実装 |
| 実装: silent fallback | ✅ QC1 スコープ内では確認できず |
| テスト: FAIL 条件網羅 | ⚠️ substitution / parse error / `.xls` / 未登録 node の負テストが未実装 |
| テスト: circular | ⚠️ admonition / field_list の PASS 期待値が Visitor 出力観測に依存 |
| v6 実行 | ✅ FAIL 0 |
| 単体テスト実行 | ✅ 211 passed |

**総合**: ⚠️ **条件付き通過留保**

実装は仕様 §3-1 / §3-1b に忠実だが、**仕様明示の FAIL トリガー 3 種 (未解決 substitution / parse error level≥3 / `.xls`) に対する単体テストが存在しない**。マトリクス §4 の「✅ 成立条件 2. 主要 FAIL ケースとエッジケースが unit test で RED→GREEN 固定されている」を満たしていない。

---

## 5. 改善案 (優先度付き)

### High

1. **未解決 substitution の負テストを追加**
   - Description: §3-1b で FAIL 明示されているが、`UnresolvedReferenceError` を `|undefined_sub|` 等で trigger して `[QC1] RST parse/visitor error` を主張する負テストが無い。
   - Proposed fix: `TestCheckContentCompleteness` に `test_fail_qc1_rst_unresolved_substitution_surfaces` を追加。入力は未定義 substitution reference を含む RST、期待は `[QC1]` かつ "substitution" を含む issue。

2. **parse error level≥3 の負テストを追加**
   - Description: `visit_system_message` で level≥3 raise する path のカバレッジが無い。
   - Proposed fix: docutils が level=3 `system_message` を出す最小 RST (例: 閉じない literal_block、indentation error) を固定し、`[QC1] RST parse/visitor error` を主張するテスト追加。
   - Note: docutils のバージョンによって warning level が変わる可能性があるため、テスト内で生成した RST に対し実際の doctree を一度走らせて level を確認する helper を作る (brittleness 回避)。

### Medium

3. **`.xls` (旧 Excel) の QC1 負テストを追加**
   - Description: 仕様に「`.xlsx` と `.xls` の両形式に対応する」と明記。`xlrd` 依存の分岐が未テスト。
   - Proposed fix: xlrd が利用可能な場合のみ走る `test_fail_xls_cell_missing_from_json` を追加 (現行 `openpyxl` 版と対称)。xlrd は `.xls` のみサポートなので import check + skip で可。

4. **未解決 :ref: / named reference / 未登録 node の各 1 件ずつ負テスト**
   - Description: Visitor 側の 3 種類の `VisitorError` 派生のうち単体テストでカバーされているのは `UnknownRoleError` のみ。他 2 種も QC1 FAIL に繋がる path を持つため対称的にカバーすべき。
   - Proposed fix: 3 つの独立テストを `TestCheckContentCompleteness` に追加。

5. **空ソース / 空白のみソースの境界テスト**
   - Description: `if not search_units: return issues` / `if not tokens: return []` などの早期 return path のテストが無い。リファクタで silent skip が混入した際に検出できない。
   - Proposed fix: `test_pass_empty_rst_source`、`test_pass_whitespace_only_rst_source`、`test_fail_empty_json_with_nonempty_xlsx_source` (← ここは現在 L776-778 で `return []` しており **仕様違反の疑い**。JSON が空で source セルが存在すれば QC1 FAIL すべきでは? — 後述 "懸念" 参照) を追加。

6. **admonition body / figure caption / table cell の仕様違反を catch する負テスト**
   - Description: create/verify 共通 Visitor のため PASS テストは circular になりがち。Visitor を一時的に改変して drop させた際に QC1 FAIL が必ず起きることを確認する dependency-injection 型テスト (現在 L1015-1032 が MD 側で実施している手法の RST 版) を追加すると、Visitor/残存チェックの正しさを独立に検証できる。

### Low

7. **CJK 境界 FAIL 方向テスト**
   - Description: CJK 短文字列の QC3 false positive 防止は PASS テストのみ。真に重複している場合の FAIL 検出も一対で追加すれば対称性が確保できる。

### 懸念 (仕様解釈の確認が必要)

- verify.py L776-778 `if not json_text.strip(): return []` (Excel QC1 path): ソース Excel に非空セルがあるのに JSON が空 / no_knowledge_content でもない場合、**QC1 FAIL すべき**ケースのように読めるが、現実装は early return で PASS 扱い。仕様 §3-1 Excel 節には「JSON テキストから削除」とあるが、ソースがあるのに JSON が空の場合の判定は明示されていない。**仕様側 or 実装側どちらを正とするかユーザー判断が必要**。

---

## 6. QA 判定

マトリクス §4 の ✅ 付与条件:

1. ✅ verify に実装が存在する (設計書 §3-1 / §3-1b 準拠)
2. ❌ **主要 FAIL ケースとエッジケースが unit test で RED→GREEN 固定** — substitution / parse error / `.xls` / 未登録 node の負テストが無い
3. ✅ v6 実データに対して verify FAIL 0 件
4. — QA エキスパートレビュー (= 本レビュー) → **条件付き通過留保**

**結論**: **⚠️ QC1 は現時点で ✅ を付与できない**。High 2 件 (substitution / parse error) の負テスト追加が最低条件。Medium 含めれば RST/MD/Excel 3 形式で zero-exception principle が対称的にテストされる。

