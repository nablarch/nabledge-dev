# QO4 Review (r5): index.toon 網羅性

**Reviewer**: QA Engineer (independent context, bias-avoidance)
**Scope**: RBKC verify QO4 — spec §3-3 の 4 FAIL ケース (index 不在 / 未登録 JSON / dangling entry / 壊れた JSON) について、実装・テスト・実データ verify の三点でゼロトレランスが満たされているか

---

## 1. 実装評価 — 4 FAIL ケースすべて実装済み

対象: `tools/rbkc/scripts/verify/verify.py:246-311` `check_index_coverage()`

| # | Spec §3-3 要件 | 実装箇所 | 判定 |
|---|---------------|----------|------|
| 1 | index.toon 不在 → 全コンテンツ JSON を FAIL 列挙 | L272-280 — `idx.exists()` が False なら `[QO4] index.toon missing` に加えて `sorted(content_jsons)` を1件ずつ列挙 | ✅ |
| 2 | 未登録 JSON → FAIL | L302-304 — `content_jsons` の各 rel が `indexed_paths` になければ `[QO4] ... JSON not registered in index.toon` | ✅ |
| 3 | dangling entry (index には在るが実ファイル無し) → FAIL | L307-309 — 逆方向ループで `indexed_paths` の各 rel が `content_jsons` にないと `[QO4] index.toon lists missing JSON` | ✅ |
| 4 | JSON parse 失敗 → FAIL (silent skip 禁止) | L261-267 — `json.loads` の `except Exception as exc` で `[QO4] ... parse failed: {exc}` を issue 追加し `continue`、無音スキップなし | ✅ |

### 補足確認
- **no_knowledge_content 除外** (L268-269): parse 成功後に `d.get("no_knowledge_content")` で分岐。index 不在分岐 (L275-280) は `content_jsons` をベースに列挙するので、no_knowledge ファイルは自動的に FAIL 対象外。
- **TOON パース** (L285-299): `files[` で始まり `:` で終わる header を state トリガにし、indent 2 スペース行のみを row として扱う。最終カンマ以降を path として採用 — title に `, ` が混じる `test_pass_nested_path_indexed` で動作確認済み。
- **相対パス正規化** (L262): `replace("\\", "/")` で Windows path separator を吸収。

実装は 4 ケースをすべて正面から扱っており、silent fallback や条件付き skip は見当たらない。

---

## 2. テスト評価

対象: `tools/rbkc/tests/ut/test_verify.py:279-391` `TestCheckIndexCoverage` (10 テスト)

| # | テスト | カバー観点 | 判定 |
|---|--------|-----------|------|
| 1 | `test_pass_all_files_indexed` (L297) | 正常系 | ✅ |
| 2 | `test_fail_json_not_in_index` (L305) | FAIL ケース ② 未登録 JSON | ✅ |
| 3 | `test_pass_no_knowledge_content_excluded` (L314) | no_knowledge 除外 | ✅ |
| 4 | `test_pass_nested_path_indexed` (L322) | ネスト path + title にカンマ | ✅ |
| 5 | `test_fail_missing_index_file` (L331) | FAIL ケース ① index 不在 (基本) | ✅ |
| 6 | `test_fail_missing_index_lists_every_content_json` (L340) | FAIL ケース ① index 不在時の**全列挙** + no_knowledge 除外 | ✅ |
| 7 | `test_fail_dangling_entry_in_index` (L354) | FAIL ケース ③ dangling entry | ✅ |
| 8 | `test_empty_knowledge_dir_without_index_passes` (L367) | 空 dir + index なし → PASS | ✅ |
| 9 | `test_cjk_filename_indexed` (L373) | CJK ファイル名 (`日本語.json` ネスト) | ✅ |
| 10 | `test_fail_broken_json_surfaces_qo4` (L381) | FAIL ケース ④ 壊れた JSON | ✅ |

### 4 FAIL ケース × no_knowledge 除外 × CJK × ネスト: 全充足

r1 レビューで挙げたギャップ (dangling, missing 時の全列挙, CJK, broken JSON) はすべて r5 時点でテスト追加済み。

### Circular test check

テストは `check_index_coverage` 公開 API のみを import し、TOON 入力は `_write_toon` ヘルパで spec 準拠フォーマット (`files[N,]{cols}:` header + indent 2 スペース comma-separated rows) を独立に構築している。verify 内部の `_no_knowledge` などのヘルパ import なし。**Non-circular**。

### 評価指標

- **network / spec coverage**: spec §3-3 の 4 FAIL ケース全てに 1 対 1 以上のテストあり。
- **edge case**: CJK / nested / no_knowledge 混在 / 空 dir / 複数 FAIL 混在 をカバー。
- **assertion 品質**: 単なる `!= []` ではなく `"QO4" in i and "<filename>" in i and "parse failed" in i` のような内容 assertion。false positive/negative の分離に寄与。

**テストとして合格**。

---

## 3. verify + pytest 実行結果

```
$ cd tools/rbkc && python3 -m pytest tests/ut/test_verify.py::TestCheckIndexCoverage -v
10 passed in 0.04s

$ python3 -m pytest tests/
219 passed in 3.38s

$ bash rbkc.sh verify 6
All files verified OK
```

- TestCheckIndexCoverage 10/10 PASS
- 全 219 ユニットテスト PASS (既存回帰なし)
- v6 実データで verify FAIL 0 件 (QO4 含む)

---

## 4. 総合判定

**判定**: ✅ **PASS (bias-avoidance 通過)**

Spec §3-3 の成立条件を照合:

1. ✅ 実装が存在 — 4 FAIL ケース全てを正面から処理、silent fallback なし
2. ✅ 主要 FAIL ケースとエッジケースが unit test で固定 — circular でない
3. ✅ v6 実データで verify FAIL 0 件
4. ✅ QA エキスパートレビュー (bias-avoidance 明示) を通過 — 本レビュー

QO4 マトリクス (design doc §4 QO4 行) に ✅ を付与して良い水準に到達している。

---

## 5. 改善案 (optional, マトリクス ✅ 付与の阻害要因ではない)

**[Low] TOON ヘッダ形式ドリフトのフェイルセーフ**
- Description: 現行 `stripped.startswith("files[") and stripped.endswith(":")` が唯一のトリガ。gen-index 側で将来 header 形式が変わった場合、header が検出されず `in_table=False` のまま全行 skip → すべての JSON が「未登録」として FAIL 列挙される挙動になる (fail-safe 側なので実害は少ない)。
- Proposed fix: header を見つけられなかった & index.toon が非空 のケースに限り `[QO4] index.toon header not recognised` を 1 件出す診断を追加。既存 FAIL と併発しても情報量が増えるだけで害はない。

**[Low] TOON row の列数不一致診断**
- Description: header で宣言した列数 (`files[N,]{...}:` の `N`) と row 実数の不一致は現在 silent。
- Proposed fix: 補助診断として `[QO4] index.toon row count mismatch: declared N, got M` を追加。Spec §3-3 の 4 ケースには無いので必須ではない。

両者とも現行 4 FAIL ケースの検出品質を落とさないための fail-safe 追加案。Z-1 の合格判定には不要。

---

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L246-311)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L279-391)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 QO4 (L299-306)
