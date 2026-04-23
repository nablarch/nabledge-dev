# QO4 Review: index.toon 網羅性

**Reviewer**: QA Engineer
**Scope**: RBKC verify QO4 — 変換済みの全 JSON ファイルが index.toon に登録されているかを確認

---

## 1. 実装の有無

✅ **実装あり**

- `tools/rbkc/scripts/verify/verify.py:155-207` — `check_index_coverage(knowledge_dir, index_path) -> list[str]`
- Docstring: `"QO4: every JSON (without no_knowledge_content) must be in index.toon."` (verify.py:156)
- 処理概要:
  - `index.toon` 不在時: コンテンツJSON が 1 件でもあれば `[QO4] index.toon missing: ...` を1件発行 (verify.py:161-174)
  - TOON ヘッダ `files[N,]{...}:` を検出後、indent 2 スペース行の最終カンマ以降を path として抽出 (verify.py:179-194)
  - `kdir.rglob("*.json")` を走査し、`no_knowledge_content=True` を除外した各 JSON の相対パスを `indexed_paths` と突合 (verify.py:196-205)

---

## 2. ユニットテストのカバレッジ

**場所**: `tools/rbkc/tests/ut/test_verify.py:134-191` — `class TestCheckIndexCoverage`

| # | テスト | カバー観点 | 評価 |
|---|--------|-----------|------|
| 1 | `test_pass_all_files_indexed` (L152) | index 済 → PASS | ✅ |
| 2 | `test_fail_json_not_in_index` (L160) | 未登録 JSON → FAIL (QO4) | ✅ |
| 3 | `test_pass_no_knowledge_content_excluded` (L169) | no_knowledge_content 除外 | ✅ |
| 4 | `test_pass_nested_path_indexed` (L177) | ネスト path `sub/b.json` | ✅ |
| 5 | `test_fail_missing_index_file` (L186) | index.toon 自体が不在 → FAIL | ✅ |

**実行結果**: 5 passed (`pytest tests/ut/test_verify.py::TestCheckIndexCoverage -v`)

### 不足しているケース (⚠️ ギャップ)

観測 3 条件で挙げられた以下の観点がテストされていない:

1. ⚠️ **index.toon に実在しない JSON の登録 (dangling entry)**
   - Spec §3-3 の文言は「変換済みの全 JSON が登録されているか」であり、逆方向 (index → JSON の存在) は明示対象外。
   - ただし **設計意図としては整合性確認に必要**。現実装は片方向のみチェックなので、dangling は見逃す。
   - テスト不在 & 実装不在(=仕様どおり、片方向で意図的)。spec 意図の明確化が必要。
2. ⚠️ **複数未登録ファイルを一括報告するケース**
   - 現実装は `for jf in sorted(...)` で全件 issue 追加する作りだが、「複数件ちゃんと全部出るか」のテストがない。index.toon 全欠損時に全 JSON が報告されるケース (L161-174 の分岐) も、現行 `test_fail_missing_index_file` は**1件しか issue が出ない実装** (`issues.append` 1回) を検証している。
   - 仕様書の「listing ALL JSONs」という意図と**実装が乖離**: index.toon 不在時、現行は `[QO4] index.toon missing: <path>` 1 件のみ issue を出し、個別 JSON は列挙しない。
3. ⚠️ **ファイル名にスペース / CJK を含むケース**
   - TOON は空白・日本語を含む可能性があるが、パース時 `stripped[last_comma + 1:].strip()` で末尾空白除去のみ。CJK ファイル名のエンコーディングずれ検出テストがない。
4. ⚠️ **JSON 壊れ/read 失敗時の挙動**
   - 実装は `except: pass` で無音スキップ (verify.py:199-200)。壊れたJSONが存在する場合に検出漏れする可能性が verify 的には問題 (本来 QO4 以外のゲートで拾うべきだが、テストなし)。
5. ⚠️ **TOON ヘッダ変形 (行頭インデントあり, 大文字小文字, 別キー名) の耐性**
   - `stripped.startswith("files[")` の1パターンのみ。正規 spec が固定なら可だが、gen-index 側の出力ドリフトに対する検出は未カバー。

---

## 3. v6 verify 実行結果

```
$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK

$ grep -c "^FAIL"   → 0
$ grep "QO4"        → (0 件)

$ python3 -m pytest tests/ 2>&1 | tail -3
138 passed in 3.88s
```

✅ v6 verify 0 FAIL / QO4 関連 FAIL 0 件 / ユニットテスト 138 件全 PASS。

---

## 4. 総合判定

**判定**: ⚠️ **Acceptable with gaps** (一次合格, ただし改善推奨)

- 実装あり (✅)、主要 5 ケースのテスト通過 (✅)、v6 で 0 FAIL 実績 (✅)。
- QA として見逃せない点:
  - **index.toon 不在時に個別 JSON を列挙しない**実装・テストが spec 意図 ("listing ALL JSONs") と整合しない可能性 (L161-174)。仕様の意図確認が必要。
  - **dangling entry (index ↔ JSON 双方向)** の扱いが spec・実装・テストのいずれでも不明瞭。

現状 v6 output が 0 FAIL で通っているためゲートとしては機能しているが、index 生成側のバグ (余分な登録・ファイル名ミスタイプ) を将来拾えない恐れがある。

---

## 5. 改善案

**[High] Spec 意図の明確化 + 双方向チェック**
- Description: `rbkc-verify-quality-design.md §3-3 QO4` に「index.toon → JSON 存在」方向を含めるか明記する。含めるなら `check_index_coverage` に逆方向チェック (indexed path の実ファイル存在確認) を追加。
- Proposed fix: Spec を更新 → TDD で `test_fail_index_has_dangling_entry` を追加 → 実装追加。

**[High] index.toon 欠損時に全 JSON を列挙**
- Description: 現行は `[QO4] index.toon missing: <path>` 1 件のみ。spec 意図が全列挙なら、欠損ファイル一覧をすべて issue として返すべき。
- Proposed fix: verify.py:161-174 を「index が無い場合、全コンテンツ JSON を未登録として報告」に変更。対応する `test_fail_missing_index_lists_all_jsons` を追加。

**[Medium] CJK / 空白を含むファイル名テスト追加**
- Description: TOON パースの頑健性担保。
- Proposed fix: `test_pass_cjk_filename_indexed` と `test_pass_filename_with_spaces` を追加。

**[Medium] 壊れた JSON への振る舞いテスト**
- Description: `except: pass` でスキップされる現行挙動の明示的契約化。
- Proposed fix: `test_broken_json_is_skipped_silently` を追加 (もしくは他 QO ゲートで拾う旨のコメントを verify.py に追記)。

**[Low] TOON ヘッダ形式バリエーションのテスト**
- Description: `files[N,]{...}:` のフォーマットドリフトを早期検出。
- Proposed fix: 不正ヘッダに対して FAIL / WARN を返すテスト追加。

---

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L155-207)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L131-191)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 QO4 (参照)
