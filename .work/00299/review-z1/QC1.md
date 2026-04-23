# QC1 完全性 — QA Review

## 1. 実装の有無

### RST
- 実装箇所:
  - `tools/rbkc/scripts/verify/verify.py:599` `check_content_completeness` ディスパッチ
  - `tools/rbkc/scripts/verify/verify.py:620` `_check_rst_content_completeness` (QC1-QC4 本体)
  - `tools/rbkc/scripts/verify/verify.py:673-689` QC1 residue チェック (sequential-delete 後の非空白残存を FAIL)
  - `tools/rbkc/scripts/verify/verify.py:346-354` `_normalize_rst_source` → `scripts/common/rst_normaliser.py:normalise_rst` (docutils AST 経由の正規化)
  - `scripts/common/rst_normaliser.py:56-57` `strict_unknown=True` で未登録 node / 未登録 role / 未解決 reference / 未解決 substitution を `UnknownSyntaxError` に昇格 (§3-1b zero-exception)
- ただし verify.py:354 で `strict_unknown=False` を渡している点は要確認 → docutils が parse error を投げた場合や未登録 node を visitor が skip した場合、residue check でのみ検出される。未登録 node 自体を明示的に QC1 FAIL として report する経路はここでは使われていない。
- 判定: ✅ 存在 (ただし strict_unknown=False 採用の妥当性は §3-1b との整合で要確認、後述)

### MD
- 実装箇所:
  - `tools/rbkc/scripts/verify/verify.py:694-794` `_check_md_content_completeness`
  - `tools/rbkc/scripts/verify/verify.py:706-709` `normalise_md(..., strict_unknown=True)` で visitor error を捕捉し `[QC1] markdown parse/visitor error:` として FAIL 出力 (§3-1b zero-exception 直接適用)
  - `tools/rbkc/scripts/verify/verify.py:787-792` sequential-delete 後の non-whitespace residue を fragment 単位で QC1 FAIL
- 判定: ✅ 存在 (仕様通り strict_unknown=True)

### Excel
- 実装箇所:
  - `tools/rbkc/scripts/verify/verify.py:851-883` `_verify_xlsx`
  - `tools/rbkc/scripts/verify/verify.py:878-883` ソースセル値が JSON に存在しない場合 `[QC1] Excel cell value missing from JSON` を FAIL 出力
  - `tools/rbkc/scripts/verify/verify.py:813-838` `_xlsx_source_tokens` (.xlsx / .xls 両対応、全シート行優先・非空セル)
- 判定: ✅ 存在

## 2. ユニットテストのカバレッジ

| 分岐 / エッジケース | 該当テスト | 判定 |
|---|---|---|
| QC1 RST residue: ソース側に取りこぼしあり | `test_verify.py:480 test_fail_qc1_residual_content` | ✅ |
| QC1 RST: visitor が対応 (note→blockquote) 残存なし | `test_verify.py:489 test_pass_rst_syntax_in_residual_allowed` | ✅ |
| QC1 RST: RST コメント (``.. textlint-disable``) が残存とならない | `test_verify.py:584 test_pass_rst_comment_line_is_syntax` | ✅ |
| QC1 RST: RST コメントブロック + indented body | `test_verify.py:593 test_pass_rst_comment_block_with_indented_body` | ✅ |
| QC1 RST: field_list 正規化 | `test_verify.py:607 / 616` | ✅ |
| QC1 RST: `:ref:` 解決後タイトル | `test_verify.py:555 test_pass_rst_ref_label_resolved_text` | ✅ |
| QC1 RST: substitution 解決 (間接) | rst_normaliser 側テストに委譲 | △ verify レイヤで substitution-only ソースの residue 0 を直接確認するケースなし |
| QC1 MD: heading + content すべて消費 | `test_verify.py:501 test_pass_md_heading_captured_as_title` | ✅ |
| QC1 MD: verbatim match (strong 記法) | `test_verify.py:528 test_pass_md_verbatim_match` | ✅ |
| QC1 MD: markdown-it parse / visitor error → `[QC1] markdown parse/visitor error:` | **該当テストなし** | ❌ |
| QC1 MD: HTML コメント (`<!-- -->`) のソース | 直接テストなし | ❌ |
| QC1 RST: 未登録 node → UnknownSyntaxError 昇格 | verify 層には直接テストなし (normaliser 層のテストに委譲) | △ |
| QC1 RST: 未解決 reference / substitution → FAIL | verify 層には直接テストなし | △ |
| QC1 RST: docutils parse error (halt 相当) | 直接テストなし | ❌ |
| QC1 Excel: セル値欠落 → FAIL | `test_verify.py:661 test_fail_cell_missing_from_json` | ✅ |
| QC1 Excel: no_knowledge_content skip | `test_verify.py:675` | ✅ |
| QC1 Excel: .xls 形式 | **該当テストなし** (.xlsx のみ) | ❌ |
| QC1 Excel: 空ソース (tokens 空) | 直接テストなし | △ |
| QC1 Excel: 空白のみセル (strip 後に空) | 直接テストなし | △ |
| QC1 共通: 空ソース / 空 JSON | `test_verify.py:524 test_pass_empty_data_no_issues` (空 data のみ) | △ ソース側の空ケース直接なし |
| QC1 共通: 空白のみソース | 直接テストなし | ❌ |
| QC1 共通: 長い residue fragment の切り詰め (`:80` / `:50`) | 直接テストなし | △ |
| QC1 共通: CJK 境界 | 明示的テストなし (JP ケースでカバーされるが境界条件テストなし) | △ |

### 不足しているテスト
1. **MD parse / visitor error を QC1 として報告するケースが未検証** — verify.py:708 の分岐は `UnknownSyntaxError` 発生時にそれを `[QC1] markdown parse/visitor error:` として report する重要な zero-exception 経路だが、この経路を踏む RED テストが 1 つもない。未登録トークン (未登録 inline token / 未登録 block token) や markdown-it の構文エラーを人工的に起こすケースを追加すべき。
2. **RST 未登録 node / 未解決 reference / substitution の QC1 報告ケース** — verify.py:354 が `strict_unknown=False` で呼んでいるため、未登録 node は visitor 側で silent drop されず例外となるが、verify 層は `UnknownSyntaxError` を QC1 に mapping していない可能性がある (MD のようなキャッチがない)。verify 層の挙動を fixate するテストが必要。
3. **Excel .xls バイナリ形式のテスト** — xlrd 経路 (verify.py:815-825) が全くテストされていない。短い .xls fixture を追加し、`_xlsx_source_tokens` の xlrd 分岐を RED→GREEN する。
4. **空白のみソース / 空 tokens のエッジケース** — Excel/RST/MD ともに空白のみソースで FAIL を誤出力しないことを fixate するテストが欠如。
5. **長い residue の切り詰め** — `:80` / `:50` のインデックス操作は境界バグの温床。長大な文字列でインデックス例外が起きないことを保証するテストを追加。

## 3. v6 verify 実行結果

- `cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"` → **0 件**
- `bash rbkc.sh verify 6 2>&1 | tail -3` → `All files verified OK`
- `python3 -m pytest tests/` → **138 passed, 0 failed** (所要 3.81s)

## 総合判定

- ⚠️ 部分的 — v6 実データ 0 FAIL + 全 unit tests PASS は確認済み。RST / MD / Excel いずれも QC1 の sequential-delete + residue ロジックは実装されている。ただしユニットテストは**成功経路への偏り**があり、§3-1b zero-exception 原則 (未登録 node / 未登録 role / 未解決 reference / parse error / markdown-it error) の FAIL 経路を verify レイヤで fixate する RED テストが欠落している。また Excel の .xls 経路、空白のみソース、長い residue などエッジケースのテストも未整備。QA Engineer の視点では、ゼロトレランス品質標準に対して「今 verify が FAIL 検出できる」ことの回帰保証が不十分。

## 改善案

### テスト追加 (優先高)
1. `TestCheckContentCompleteness` に MD の `UnknownSyntaxError` → `[QC1] markdown parse/visitor error:` FAIL を fixate するテスト。未登録トークンを仕込むか、markdown_it Visitor が raise する最小ソースを用意する。
2. 同上で RST について、未登録 directive / 未登録 role を含むソースを渡し、verify 層が silent に PASS しないことを fixate。現状の `strict_unknown=False` で正規化 MD に FAIL 相当の痕跡が残り residue → QC1 になる、という contract をテストで固定する。
3. `TestVerifyFileExcel` に .xls ケース (xlrd 経由) を追加。可能なら最小 .xls バイナリをリポジトリ or fixture 生成で用意する。
4. `TestCheckContentCompleteness` / `TestVerifyFileExcel` に「空白のみソース」「空 tokens」ケースを追加。
5. residue snippet truncation (80 chars / 50 chars) の境界テスト — 100 文字超の fabricated 文字列で IndexError が出ないことを保証。

### 実装の補強
1. `verify.py:354` の `strict_unknown=False` について、設計書 §3-1b (未登録 node → QC1 FAIL、silent な children 再帰 fallback 禁止) と整合しているか再確認。MD 側と同じ `try / except UnknownSyntaxError → QC1 FAIL` パターンに揃えることを提案する。現状 MD だけが strict で、RST だけ lax な非対称は設計書の「create / verify 対称」原則からもブレている。
