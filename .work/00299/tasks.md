# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-15

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → **サブエージェント品質チェック**

## サブエージェント品質チェック（全フェーズ共通）

各フェーズ完了後、以下のプロンプトでサブエージェントを起動する。
別コンテキストで実装を検証することで、実装バイアスなしの独立レビューを確保する。

```
Agent(
  subagent_type: "general-purpose",
  description: "Phase {N} quality check",
  prompt: """
あなたはコードレビュアーです。以下のRBKC Phase {N}の実装を独立した視点でレビューしてください。

## レビュー対象ファイル
{変更ファイルのdiff または 全文}

## 仕様（tasks.mdより）
{該当フェーズのSteps}

## チェック項目
1. **仕様カバレッジ**: 仕様のすべてのStepが実装されているか
2. **テストの意味**: テストが実装の内部に依存しすぎていないか（実装を変えたとき壊れるべきテストが壊れるか）
3. **エッジケース**: 仕様に明示されていないが重要な境界値・異常系が漏れていないか
4. **実装の正確性**: 変換ロジックに論理的な誤りはないか（特にパーサー・正規表現・テーブル変換）
5. **フェーズ間結合**: 前フェーズの出力を正しく受け取っているか

## 出力形式
- 問題点: [High/Medium/Low] 説明 + 改善案
- 良い点: 特筆すべき設計・テストの優れた点
- 合否判定: Pass / Needs Fix
"""
)
```

チェック結果で "Needs Fix" が出た場合は修正してから次フェーズへ進む。

---

## Not Started

### Phase 10: verify の完全チェック化

#### 調査結果（実施済み）

**バグ発見: preamble消滅バグ (rst.py)**

`_split_sections` の `_flush()` に論理バグがある。
RST ファイルの h1 前に `.. _label:` が存在する場合（v6では225/334ファイル=67%）、
h1〜最初のh2間のpreamble内容（概要テキスト、外部URLなど）が消滅する。

**原因**:
`_flush()` の `elif current_lines and not preamble_lines:` 分岐が、
h1 前の `.. _label:` 行を `preamble_lines` に格納した時点で
`not preamble_lines` が False になり、実際のpreamble内容（h1後〜h2前）が捨てられる。

**影響**: v6で65個の外部URLが消滅する（SC「リンクはターゲットURLを変えない」に直接違反）。

**修正**: `_flush()` を以下のように変更する:
```python
# Before (buggy):
elif current_lines and not preamble_lines:
    preamble_lines = current_lines

# After (fixed):
elif current_lines:
    preamble_lines.extend(current_lines)   # append, don't replace
```

**verify の正しいアプローチ**

ルールベース変換なので、**再変換diffが最も完全なチェック**。

- 再変換: `convert(source, file_id)` を実行（file_idはJSON内の"id"フィールドから取得）
- JSON の `title` / `sections[].title` / `sections[].content` と比較
- 一致 → ソースとJSONは意味的に同一
- 不一致 → コンバータのバグ or ソース変更後に再生成していない

さらに **外部URLの独立チェック** を追加（コンバータのバグをダブルチェック）:
- ソースの `https?://` URLをすべて抽出
- JSONテキストに全URL存在すること確認
- これにより「リンクはターゲットURLを変えない」SC を直接検証する

#### Steps

**Step 1: preamble消滅バグ修正（rst.py）**
- [ ] `scripts/converters/rst.py` の `_flush()` を修正（`extend` に変更）
- [ ] `test_preamble_becomes_overview_section` を pre-h1 ラベルありケースで拡充
- [ ] 修正後 `pytest` 全通過確認

**Step 2: verify を再変換diff + URL独立チェックに置き換え**
- [ ] `verify_file(source_path, json_path, fmt)` の RST/MD ロジックを書き換え:
  1. JSON の "id" フィールドから file_id を取得
  2. `convert(source_text, file_id)` を実行（fresh result）
  3. `fresh.title` vs `data["title"]`、`fresh.no_knowledge_content` vs `data["no_knowledge_content"]` を比較
  4. `len(fresh.sections)` vs `len(data["sections"])` を比較
  5. 各セクションの `title` と `content` を比較（strip後一致）
  6. 独立チェック: ソースの `https?://` URL全件が JSON テキストに存在すること
- [ ] 既存の `_verify_rst_md` テストを新ロジックに合わせて更新
- [ ] 新規テスト: pre-h1 ラベルありRST → preamble内容とURLが verify を通過
- [ ] `pytest` 全通過確認

**Step 3: コミット**
- [ ] `fix: restore preamble content lost when pre-h1 RST label exists` でコミット
- [ ] `feat: replace verify with re-conversion diff + URL presence check` でコミット

---

### Phase 11: 統合検証 — v6

**前提**: Phase 10 (verify完全チェック化) 完了後に実施。

**Steps:**
- [ ] `bash rbkc.sh create 6` を実行（出力先: `.claude/skills/nabledge-6/knowledge/`）
- [ ] `bash rbkc.sh verify 6` を実行 — FAIL 0件であること
- [ ] nabledge-test v6 を実行して品質劣化なし（ベースライン比）を確認
- [ ] コミット（生成済み知識ファイルをコミット）

v6 検証通過後 → Phase 12 (v5) へ

---

### Phase 12: 統合検証 — v5

**前提**: Phase 11 (v6) 通過後に実施。

**Steps:**
- [ ] `bash rbkc.sh create 5` を実行（出力先: `.claude/skills/nabledge-5/knowledge/`）
- [ ] `bash rbkc.sh verify 5` を実行 — FAIL 0件であること
- [ ] nabledge-test v5 を実行して品質劣化なし（ベースライン比）を確認
- [ ] コミット

v5 検証通過後 → Phase 13 (v1.4/1.3/1.2) へ

---

### Phase 13: 統合検証 — v1.4 / v1.3 / v1.2

**前提**: Phase 12 (v5) 通過後に実施。

**Steps:**
- [ ] `bash rbkc.sh create 1.4` → `bash rbkc.sh verify 1.4` — FAIL 0件
- [ ] `bash rbkc.sh create 1.3` → `bash rbkc.sh verify 1.3` — FAIL 0件
- [ ] `bash rbkc.sh create 1.2` → `bash rbkc.sh verify 1.2` — FAIL 0件
- [ ] nabledge-test v1.4 / v1.3 / v1.2 を実行して品質劣化なし（ベースライン比）を確認
- [ ] コミット（全3バージョンの生成済み知識ファイル）

---

## Done

- [x] Phase 1: KC cache → hints mapping (`scripts/hints.py`) — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — committed `5913ff6e`, `1b62c4c4`, `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
- [x] Gap fill: Phase 2 `test_section_count` 修正 + Phase 1/3 E2Eテスト追加 — committed `010d0c2f`
- [x] Phase 4: Cross-reference resolution + asset copying — committed `9336f900`, `87654126`
- [x] Phase 5: MD converter — committed `232df686`
- [x] Phase 6: Excel converters — committed `edce71eb`
- [x] Phase 7: Index + browsable docs generation — committed `dc019759`
- [x] Phase 8: CLI + create/update/delete/verify operations — committed `5baf7a6d`
- [x] Phase 9: v1.x固有ディレクティブ対応 — committed `bc632d0f`
