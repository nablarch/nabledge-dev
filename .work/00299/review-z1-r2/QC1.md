# QC1 完全性 (Completeness) レビュー — R2 独立 QA

**日付**: 2026-04-23
**レビュー観点**: QC1 (RST / MD / Excel) — 実装、単体テスト、v6 実測

---

## 1. 実装の有無

### 1-1. RST (✅ 実装あり、§3-1 準拠)

- `check_content_completeness` エントリ: `tools/rbkc/scripts/verify/verify.py:610-628`
- RST 分岐: `_check_rst_content_completeness` (`verify.py:631-710`)
  - 手順 0（AST 正規化）: `_normalize_rst_source` → `scripts/common/rst_normaliser.py:32-60` の `normalise_rst(strict_unknown=True)`
  - 手順 1（抽出）: `_build_rst_search_units` (`verify.py:563-607`) が top-level title/content + 各セクション title/content を JSON 順で収集
  - 手順 2（削除 + 配置 QC4）: `verify.py:664-690` — `current_pos` を前進させる sequential-delete。見つからなければ QC2/QC3/QC4 を分岐（`prev_idx == -1` / `_in_consumed` / それ以外）
  - 手順 3（残存 QC1）: `verify.py:697-708` — 全 unit を削除後、`residue.strip()` が残れば `[QC1] residue not captured in JSON` を報告
- ゼロトレランス: §3-1 「空白文字 / 改行 / タブ以外のテキストが残ったら QC1 FAIL」の通り、許容パターンリストなし (`if residue.strip(): ...`)
- §3-1b zero-exception: `strict_unknown=True` で Visitor 由来 (`UnknownNodeError`/`UnknownRoleError`/`UnresolvedReferenceError`) を `UnknownSyntaxError` に包み、`verify.py:646-650` で `[QC1] RST parse/visitor error` として報告。silent fallback 無し（`rst_normaliser.py:55-58` の `except VisitorError` は `strict_unknown=True` なら必ず raise）

**懸念 (Low)**: `verify.py:706` の `residue.strip()[:80]` により残存が 80 文字で切り詰められ、1 件の QC1 にまとめられる。複数箇所に残存があっても 1 件のサマリになり、デバッグ情報が不足する (MD 側は `verify.py:809-811` でフラグメント単位で列挙しており非対称)。仕様は件数形式を規定していないが、ゼロトレランスの報告品質としては MD 側方式が優れる。

### 1-2. MD (✅ 実装あり、§3-1 準拠)

- MD 分岐: `_check_md_content_completeness` (`verify.py:713-813`)
  - 手順 0: `normalise_md(strict_unknown=True)` (`md_normaliser.py:46-63`) → `md_ast.parse` + `md_ast_visitor.extract_document`
  - 手順 2–4: `verify.py:766-785` で QC2/QC3/QC4 を RST と対称に分岐
  - 手順 3 (QC1 残存): `verify.py:787-811` — 既消費 span をマージして `remaining` を算出し、非空白 フラグメントがあれば `[QC1] source content not captured` を **フラグメント単位で** 報告 (RST 側より詳細)
- §3-1b zero-exception: `UnknownTokenError` → `UnknownSyntaxError` → `[QC1] markdown parse/visitor error` (`verify.py:723-729`)
- MD visitor 側も `md_ast_visitor.py` に 4 箇所 `raise UnknownTokenError(...)` を持ち、silent fallback なし (grep 結果: line 220/235/330/336/463)

**問題なし** — 仕様 §3-1 §3-1b に完全準拠。

### 1-3. Excel (⚠️ 実装あり、ただし仕様比で一部弱化)

- `_verify_xlsx` (`verify.py:870-929`)
  - ソーストークン構築: `_xlsx_source_tokens` (`verify.py:832-857`) — `.xlsx` は `openpyxl`、`.xls` は `xlrd`。非空セル値を前後 strip して行優先・列順で収集 (§3-1 Excel 「ソーストークンの構築」に一致)
  - JSON テキスト構築: `_xlsx_json_text` (`verify.py:860-867`) — 改行結合。仕様は「空白で結合」と記述するが実装は `\n` で結合。`find()` ベースなので単一文字の差は機能的に等価（strトークン内部に含まれない限り）。
  - 手順 1-4: `verify.py:890-902` で QC1/QC3 を分岐、`verify.py:904-927` で QC2 残存チェック
- zero-exception: `.xls`/`.xlsx` 未知拡張子は else 分岐に落ち `openpyxl` で読み、失敗すれば例外が素通り → 実質 parse error で即停止。Excel については仕様の「zero-exception」は構文 visitor 概念がないため該当なし。

**問題 1 (High)**: QC2 残存チェックが `_MD_SYNTAX_RE.sub` (`verify.py:820-829, 923`) で MD 記法 (`|`, `**`, `#`, `` ` `` 等) を一律削除し、さらに `if t and len(t) >= 2:` (`verify.py:926`) で 1 文字トークンを無視している。
- 仕様 §3-1 Excel「許容構文要素リスト（QC2 残存判定）」は `**` / `|` / `---` などテーブル/強調記号を除外してよいと明記するため、MD 記法ストリップ自体は仕様許容範囲。
- しかし **「1 文字残存を無視」は仕様に根拠がない**。例えば JSON 側に `X` という 1 文字の捏造があった場合、Excel QC2 は見逃す。§2-1 ゼロトレランスと整合しない silent tolerance。
- また `_MD_SYNTAX_RE` は `^\d+\.\s+` を含むため、JSON 内の任意の箇条書き先頭番号（Excel ソースに存在しない捏造番号でも）は QC2 検出されない。

**問題 2 (Medium)**: `_xlsx_json_text` は section title もセル値由来として JSON テキストに含めるが、§3-1 Excel 「JSON テキストの構築」も同意見 (「section title はセル値であるため JSON テキストに含める」) なので仕様準拠。ただし仕様の「空白で結合」に対し `\n` で結合している点は微差（改行が挟まる分、トークンが改行跨ぎにマッチしなくなるケースがありうる — ソーストークンは単一セル値なのでリスクは低い）。

---

## 2. ユニットテストのカバレッジ

対象: `tools/rbkc/tests/ut/test_verify.py` の `TestCheckContentCompleteness` (RST/MD) と `TestVerifyFileExcel`。

### 2-1. 仕様の FAIL 条件がアサートされているか

| 仕様上の FAIL パス | 対応テスト | 評価 |
| --- | --- | --- |
| RST 残存テキスト | `test_fail_qc1_residual_content` (L756-763) | ✅ RST 源で「追加情報はここにあります。」が未取込 → QC1 検出をアサート |
| RST Visitor error (未対応 role) | `test_fail_qc1_rst_unknown_role_surfaces` (L925-931) | ✅ `:unknownshim:` で `[QC1] RST parse/visitor error` を確認 |
| MD parse/visitor error | `test_fail_qc1_md_parse_visitor_error` (L906-923) | ⚠️ `md_ast_visitor.extract_document` をモンキーパッチして強制 raise。実トークンから error を誘発していない（実トークンの異常系は visitor 側の 4 箇所 raise のうち 1 つも E2E で踏んでいない） |
| RST 未解決 `:ref:` | なし | ❌ **不在** — §3-1b 「未解決 reference → FAIL (QC1)」の経路が test で固定されていない（`test_pass_rst_ref_unknown_label_skipped` L1147 は QL1 のテストで、QC1 経路ではない） |
| RST 未解決 substitution (`|name|` 未定義) | なし | ❌ **不在** — §3-1b 「未解決 substitution → FAIL (QC1)」のテストがない |
| docutils parse error (level≥3) | なし | ❌ **不在** — §3-1 「docutils が parse error を返した → QC1」のテストがない |
| 未登録 markdown-it token | 上記モンキーパッチ版のみ | ⚠️ 実トークンから誘発していないため、visitor が将来新 token に silent fallback を追加しても test は通ってしまう |
| Excel .xls 形式 | なし | ❌ **不在** — `test_verify.py` の Excel テスト 5 件すべて `.xlsx` のみ。`xlrd` パスの動作確認なし |
| Excel 空セル / 空白セル | なし | ❌ **不在** — 空白のみ/前後空白 strip 動作が未検証 |
| Excel QC2 1 文字残存 | なし | ❌ **不在** — 上記「問題 1」の silent tolerance を検出するテストがない |

### 2-2. エッジケース

| エッジケース | 対応 | 評価 |
| --- | --- | --- |
| 空ソース | `test_pass_empty_data_no_issues` (L800) | ⚠️ 空 **JSON** のテスト。空 **source** (RST/MD) のテストなし |
| 空白のみソース | なし | ❌ 不在 |
| CJK 境界 | RST 全テストが日本語ソース使用 | ✅ 事実上カバー。ただし「CJK 文字の substring 部分一致による誤検出」(例: 「概要」と「要約」の共通文字) は明示的に tested でない |
| 未登録 RST role | `test_fail_qc1_rst_unknown_role_surfaces` | ✅ |
| 未解決 substitution | なし | ❌ 不在 |
| 未解決 `:ref:` | なし | ❌ 不在 |
| docutils halt 相当 parse error | なし | ❌ 不在 |
| 不明 markdown-it token | モンキーパッチ版のみ | ⚠️ 実データ由来の誘発なし |
| `.xls` vs `.xlsx` | `.xlsx` のみ | ❌ `.xls` パス未検証 |
| Residue フラグメント切り詰め | なし | ❌ 不在 — RST 側 80 文字切り詰め挙動が pin されていない |
| 複数 residue | MD 側 `remaining.split()` は `test_fail_qc1_residual_content` で部分カバー | ⚠️ 複数 fragment 列挙を明示的に確認するテストなし |

### 2-3. 循環テスト (circular assertion) の検出

- **`test_fail_qc1_md_parse_visitor_error` (L906-923)**: 🔴 **Circular**. モンキーパッチで `extract_document` 自体を差し替え、「実装が呼ぶ関数が raise すれば実装が QC1 を報告する」という自明の経路を検証しているだけ。実 MD ソースで markdown-it visitor が UnknownTokenError を raise するシナリオ（例: 新しいプラグイン token、HTML inline タグ等の扱い）を一切 cover しない。visitor 側に silent fallback が将来追加されたとき、このテストは通り続ける。
- **`test_pass_rst_syntax_in_residual_allowed` (L765-775)**: ⚠️ **半 circular**. JSON content を `"本文。\n\n> **Note:**\n> 注記内容。"` と記述し、これは RST→MD visitor が生成する形式。テストは「verify が自分自身の normaliser の出力と一致すれば PASS」を確認しており、**仕様 §3-1「.. note:: を MD admonition に変換する」** のルール本体を独立に検証していない。RST→MD 変換規則がドリフトしたとき、create 側と verify 側が同時に同じドリフトを起こせば test は通ってしまう（これは設計上の独立性原則 §2-2 に則る姿だが、テスト観点では「仕様の定める出力形」を期待値にするほうが頑健）。
- **`test_pass_rst_comment_line_is_syntax` / `test_pass_rst_comment_block_with_indented_body` (L860-881)**: ✅ 非 circular。RST 仕様由来の「コメントは捨ててよい」を確認。JSON 側に何も含まれなくても QC1 PASS という仕様を独立に検証。
- **Excel `test_pass_real_xlsx` (L1026-1038)**: ✅ 非 circular — 実 .xlsx 読込経路を踏む。
- **Excel `test_fail_cell_missing_from_json` (L1040-1052)**: ✅ 非 circular — 仕様 §3-1 Excel 手順 2「見つからなかった → QC1」を独立に検証。

### 2-4. "v6 passes" 保証の弱さ

`test_pass_*` 群のうち `test_pass_rst_*` 系 (L765-902) はいずれも「現在の verify/converter 実装が出す形式」に JSON 側を合わせる形で書かれている。**仕様 §3-1 本文の「正規化ソース生成規則」を独立に検証するテスト（docutils AST → 期待される MD 文字列、という対応表の各エントリに対するユニットテスト）は本ファイル内には見当たらない**。RST/MD node → MD 対応表の各エントリについての単位テストは `common/` 側に期待されるが (visitor テストは `tests/ut/test_md_ast_visitor.py` にあるのみ)、RST 側 visitor の node ごとテストが無いため、verify の QC1 精度は「v6 現状の converter が現状通り動くこと」に暗黙依存している。

---

## 3. v6 verify 実行結果

実行コマンドと結果:

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0

$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK

$ cd tools/rbkc && python3 -m pytest tests/ 2>&1 | tail -3
(中略)
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 190 passed in 2.28s ==============================
```

- v6 実データの verify FAIL: **0 件**
- pytest: **190 passed** (skipなし、失敗なし)

**評価の注意**: §2-1 マトリクス注記の通り、v6 PASS = ゼロトレランス達成ではない。v6 で意図的な欠落を注入した fault-injection テストが存在しないため、「FAIL 0」は「QC1 検出器が正しく動いている」の強い証拠にならない。具体的には本レビュー 2-1 で指摘した「未解決 `:ref:` / 未解決 substitution / .xls / Excel QC2 1 文字残存」は v6 では発生していないだけで、検出能力が保証されているわけではない。

---

## 4. 総合判定

**⚠️ 条件付き ✅** — 仕様 §3-1 / §3-1b の主要経路は実装・テスト・v6 実行の 3 条件を満たしており、マトリクス上の ✅ は妥当。ただし以下のギャップがあり、ゼロトレランス原則に対して**完全な保証にはなっていない**:

1. **High**: Excel QC2 で 1 文字残存を silent tolerance (`verify.py:926` の `len(t) >= 2`) — 仕様に根拠なし、§2-1 ゼロトレランス違反の疑い
2. **Medium**: §3-1b zero-exception 4 経路のうち 2 経路 (「未解決 reference」「未解決 substitution」) の単体テストが不在
3. **Medium**: `test_fail_qc1_md_parse_visitor_error` はモンキーパッチ依存の circular test — 実データで MD visitor が raise する経路がゼロ
4. **Medium**: Excel `.xls` (xlrd) 経路の単体テストが不在。`.xls` ソースを持つ v6 実データが存在しないため「動作未保証」
5. **Low**: RST 残存フラグメントが 80 文字で切り詰められ、かつ 1 件にまとめられる (MD 側は列挙)。ゼロトレランス時代のデバッグ容易性として非対称

---

## 5. 改善案

| 優先 | 問題 | 改善案 |
| --- | --- | --- |
| 🔴 High | Excel QC2 の 1 文字 silent tolerance (`verify.py:926`) | `len(t) >= 2` 条件を削除し、全非空残存トークンを QC2 として列挙する。併せて `_MD_SYNTAX_RE` ストリップ後に 1 文字捏造が検出されることを確認する test (`test_fail_qc2_single_char_fabrication_in_xlsx` 等) を RED→GREEN で追加 |
| 🟡 Medium | 未解決 `:ref:` / `\|sub\|` の QC1 経路がテスト不在 | RST 源に未登録 label の `:ref:`cross_file_missing`` を記述し、`label_map={}` で `[QC1] RST parse/visitor error` が報告されることをアサートする test を追加。substitution 未定義パターン (`\|undefined\|`) も同様 |
| 🟡 Medium | `test_fail_qc1_md_parse_visitor_error` が circular | 実 MD ソースで `md_ast_visitor` が raise するパターン (例: 未知プラグイン token を含むソース) を特定し、モンキーパッチを外す。特定できない場合は「現 visitor ではすべての token が登録済み」であることを別 test (visitor 側 token 集合の exhaustiveness test) で固定する |
| 🟡 Medium | `.xls` 経路の未検証 | `xlrd` インストール前提で `.xls` fixture を合成し、`_xlsx_source_tokens` が正しく非空セル値を返すことを確認する test を追加。`xlrd` 不在環境は `pytest.skip` を使わず fixture を別パッケージ依存で閉じる (§development.md の No Test Skipping 原則) |
| 🟡 Medium | docutils parse error (halt) の QC1 経路がテスト不在 | `..` 直後に不正な indent / incomplete directive を書いた minimal RST を作り、`[QC1] RST parse/visitor error` の報告を確認 |
| 🟢 Low | RST 側 residue 報告の情報量 | MD 側と同様に `residue.split()` でフラグメント単位列挙に統一する。80 文字切り詰めを撤廃、または全件列挙に変更 |
| 🟢 Low | v6 実データに fault injection テストがない | v6 の 1 ファイルから意図的にセクション 1 つの content を削った JSON を作り、verify が QC1 FAIL を返すことを確認する E2E test を `tests/e2e/` に 1 件追加 |

---

## 6. 根拠ファイル一覧

- 仕様: `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1, §3-1b, §4
- 実装: `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py:610-710` (RST), `:713-813` (MD), `:832-929` (Excel)
- Normaliser: `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/rst_normaliser.py:32-60`, `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/md_normaliser.py:46-63`
- Visitor zero-exception: `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/rst_ast_visitor.py:147,561,586,599,603,646,655` / `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/md_ast_visitor.py:220,235,330,336,463`
- テスト: `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py:701-1103`
