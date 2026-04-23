# QO4 Review (r6): index.toon 網羅性

**Reviewer**: QA Engineer (independent context, bias-avoidance)
**Scope**: RBKC verify QO4 — spec `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3
の 4 FAIL ケース (①index.toon 不在 / ②未登録 JSON / ③dangling entry / ④JSON parse 失敗)
について、実装・テスト・実データ verify の三点でゼロトレランスが満たされているかを
r6 時点で独立検証する。

---

## 1. 実装評価

対象: `tools/rbkc/scripts/verify/verify.py:247-312` `check_index_coverage()`

Spec §3-3 (`tools/rbkc/docs/rbkc-verify-quality-design.md:299-306`) vs 実装:

| # | Spec §3-3 | 実装位置 | 判定 |
|---|-----------|----------|------|
| ① | index.toon 不在 → `no_knowledge_content: true` でない JSON を**全件** FAIL 列挙 | `verify.py:273-281` `if not idx.exists(): ... for rel in sorted(content_jsons): issues.append(... "JSON not registered in index.toon (index.toon absent)")` | ✅ |
| ② | 未登録 JSON → FAIL | `verify.py:302-305` forward loop `if rel not in indexed_paths: issues.append(... "JSON not registered in index.toon: {rel}")` | ✅ |
| ③ | dangling entry → FAIL | `verify.py:307-310` reverse loop `if rel not in content_jsons: issues.append("[QO4] index.toon lists missing JSON: {rel}")` | ✅ |
| ④ | JSON parse 失敗 → FAIL (silent skip 禁止) | `verify.py:264-268` `except Exception as exc: issues.append(f"[QO4] {rel}: JSON parse failed: {exc}"); continue` | ✅ |

### 実装補足

- **no_knowledge 除外** (`verify.py:269-271`): parse 成功後に `d.get("no_knowledge_content")`
  で skip。index 不在列挙 (L279) は `content_jsons` dict をベースにしているので no_knowledge
  は自動的に対象外となる — ケース①で過剰 FAIL しない。
- **相対パス正規化** (`verify.py:263`): `replace("\\", "/")` で Windows separator 吸収。
- **TOON parse** (`verify.py:286-300`): header `files[N,]{cols}:` を state トリガとし、
  indent 2 スペース行のみ row として採用。path は最終カンマ以降 (`stripped[last_comma + 1:].strip()`)
  を使うため title に `, ` を含むエントリでも path 抽出が安定。
- **silent fallback なし**: parse 失敗を try/except で飲み込まず issue に詰めてから `continue`
  する。`no_knowledge_content` flag も「parse 成功後」に限定して適用するため、壊れた JSON が
  no_knowledge 扱いになって落ちることはない — ゼロトレランスを満たす。

実装は 4 FAIL ケース全てを正面から扱っており、spec §3-3 との乖離なし。

---

## 2. テスト評価

対象: `tools/rbkc/tests/ut/test_verify.py:313-425` `TestCheckIndexCoverage` (10 テスト)

| # | テスト (`test_verify.py` 行) | カバー観点 | 対応 FAIL ケース |
|---|------------------------------|-----------|-----------------|
| 1 | `test_pass_all_files_indexed` (L331) | 正常系 | — |
| 2 | `test_fail_json_not_in_index` (L339) | 未登録 JSON | ② |
| 3 | `test_pass_no_knowledge_content_excluded` (L348) | no_knowledge 除外 | (除外) |
| 4 | `test_pass_nested_path_indexed` (L356) | ネスト path + title にカンマ | 実装の TOON parse 補助 |
| 5 | `test_fail_missing_index_file` (L365) | index 不在 (基本) | ① |
| 6 | `test_fail_missing_index_lists_every_content_json` (L374) | index 不在時の**全列挙** + no_knowledge 除外 | ① |
| 7 | `test_fail_dangling_entry_in_index` (L388) | index entry に対応 JSON 無し | ③ |
| 8 | `test_empty_knowledge_dir_without_index_passes` (L401) | 空 dir + index 無し → PASS | ケース①の境界 (content 0 件) |
| 9 | `test_cjk_filename_indexed` (L407) | CJK 日本語ファイル名 ネスト | 実装補助 |
| 10 | `test_fail_broken_json_surfaces_qo4` (L415) | 壊れた JSON | ④ |

### 4 FAIL ケースとのマッピング

| Spec FAIL ケース | 直接担保するテスト |
|-----------------|-------------------|
| ① index.toon 不在 | test_fail_missing_index_file, test_fail_missing_index_lists_every_content_json |
| ② 未登録 JSON | test_fail_json_not_in_index |
| ③ dangling entry | test_fail_dangling_entry_in_index |
| ④ JSON parse 失敗 | test_fail_broken_json_surfaces_qo4 |

4 FAIL ケース全てに 1 件以上の固定テストが存在し、加えて境界 (空 dir, CJK, nested, no_knowledge
除外, 全件列挙) もカバーされている。

### Circular test check

- テストは `check_index_coverage` 公開 API のみ import (`test_verify.py:317`)。
- index.toon 入力は `_write_toon` ヘルパ (`test_verify.py:320-329`) で spec 準拠フォーマット
  (`files[N,]{cols}:` header + 2 スペース indent + comma-separated row) を独立に組み立てている。
  これは verify 側のパース処理を参照せずに spec から直接導出したフォーマット。
- `_no_knowledge` などの verify 内部ヘルパを import / 再実装していない。
- **Non-circular** — テストの合否は verify の実装を鏡写しにしているのではなく、spec に由来する。

### Assertion 品質

単なる `!= []` ではなく `"QO4" in i and "<filename>" in i and "parse failed" in i`
のように内容を指定 (例: `test_verify.py:425`)。False positive / false negative を分離できる
assertion 設計。

### Edge / bug-revealing ケース

- CJK filename nested: `test_cjk_filename_indexed` (L407)
- title にカンマを含む行: `test_pass_nested_path_indexed` (L356) — last-comma parsing の
  バグ顕在化テスト
- 複数 FAIL 混在 (dangling + 正常): `test_fail_dangling_entry_in_index` (L388)
- 複数 content + no_knowledge 混在 + index 不在: `test_fail_missing_index_lists_every_content_json`
  (L374) — ケース① 全件列挙と除外の同時検証
- 壊れた JSON + 正常 JSON 共存: `test_fail_broken_json_surfaces_qo4` (L415)

ゼロトレランスの核である「silent skip 禁止」が ④ のテストで明示確認されている。

---

## 3. 実行結果 (v6 + pytest)

独立に実行 (r6 時点):

```
$ cd tools/rbkc && python3 -m pytest tests/ut/test_verify.py::TestCheckIndexCoverage -v
10 passed in 0.02s

$ python3 -m pytest tests/
221 passed in 1.69s

$ bash rbkc.sh verify 6
All files verified OK
```

- TestCheckIndexCoverage 10/10 PASS
- 全 221 ユニットテスト PASS (既存回帰なし)
- v6 実データで verify FAIL 0 件 (QO4 含む)

---

## 4. 総合判定

**判定**: ✅ **PASS (bias-avoidance 通過)**

Spec §3-3 QO4 の成立条件を照合:

1. ✅ 実装が spec §3-3 の 4 FAIL ケース全てを正面から処理 (`verify.py:247-312`)、silent fallback 無し
2. ✅ 4 FAIL ケース全てに unit test が存在 (`test_verify.py:313-425`)。non-circular (spec 由来の独立 TOON 組立、公開 API only)
3. ✅ v6 実データで verify FAIL 0 件
4. ✅ bias-avoidance 明示の独立 QA レビュー (本レビュー) を通過

design doc §4 の QO4 マトリクス行に ✅ を付与してよい水準。

---

## 5. 改善案 (Optional — Z-1 合格判定には不要)

**[Low] TOON header 形式ドリフトのフェイルセーフ**
- Description: `verify.py:292` の `stripped.startswith("files[") and stripped.endswith(":")`
  が唯一のトリガ。gen-index 側で将来 header 形式が変わると header 未検出 → `in_table=False`
  のまま全行 skip → 結果的に全 JSON が「未登録」FAIL として列挙される
  (fail-safe 側に倒れるので実害は低い)。
- Proposed fix: index.toon が非空かつ header を一度も検出しなかった場合のみ
  `[QO4] index.toon header not recognised` を 1 件追加する診断を入れる。既存 FAIL と
  併発しても情報量が増えるだけで害は無い。

**[Low] TOON row 列数不一致の診断**
- Description: header で宣言した列数 (`files[N,]{...}:` の `N`) と row 実数の不一致は
  現在 silent。4 FAIL ケースのいずれにも属さないため spec 上は問題無いが、将来 gen-index
  バグで列数ズレが起きた時に早期検出できる。
- Proposed fix: 補助診断として `[QO4] index.toon row count mismatch: declared N, got M` を追加。

両者とも現行 4 FAIL ケースの検出品質を落とさないための fail-safe 追加案であり、
Z-1 マトリクス ✅ 付与の阻害要因ではない。

---

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L247-312)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L313-425)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (L299-306)
