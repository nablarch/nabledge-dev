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

## In Progress

### ギャップ対応: 既完了フェーズの補完テスト

Phase 4コミット前に実施する。

#### Gap 1: Phase 2 — `test_section_count` マジックナンバー修正

`tests/e2e/test_rst_converter.py:50` の `assert len(result.sections) == 26` が brittle。
universal_dao.rst が更新されると意味不明な失敗になる。

**Fix**: RST ソースの見出し数を動的にカウントして比較に変える。

```python
def test_section_count(self, result):
    # Count expected sections from source: h2 + h3 headings + preamble
    lines = UNIVERSAL_DAO_RST.read_text().splitlines()
    heading_chars = _detect_heading_chars(lines)
    # h2 = heading_chars[1], h3 = heading_chars[2]
    section_chars = set(heading_chars[1:3]) if len(heading_chars) >= 2 else set()
    expected = sum(
        1 for i, line in enumerate(lines)
        if line and set(line) <= section_chars and len(line) >= 2
        and i > 0 and lines[i-1].strip()
    ) + 1  # +1 for preamble section
    assert len(result.sections) == expected
```

あるいはシンプルに `>= 20` の下限チェックに変えてもよい（要判断）。

- [x] `test_section_count` を動的カウントまたは下限チェックに修正

#### Gap 2: Phase 1 — 実KCキャッシュに対するE2Eテスト

合成フィクスチャのみでは実データとの構造差を検知できない。
実キャッシュパス: `tools/knowledge-creator/.cache/v6/knowledge/`

追加テスト（`tests/e2e/` に `test_hints_e2e.py` として追加）:
- `build_hints_index` が非空の辞書を返す
- 既知のfile_id（例: `about-nablarch-about_nablarch`）が存在する
- split suffixを含むファイルがベースidにマージされている（`--s` がキーに含まれない）
- `lookup_hints` で既知のsection title（例: `Nablarchのライセンスについて`）が正しいhintsを返す

- [x] `tests/e2e/test_hints_e2e.py` を作成して実キャッシュE2Eテストを追加

#### Gap 3: Phase 2+3 — パイプライン統合テスト

RST → `convert()` → `extract_hints()` → `merge_hints()` の連鎖が未検証。
各ステップ単体は通っても結合で壊れる可能性がある。

追加テスト（`tests/e2e/test_pipeline_e2e.py` として追加）:
- `universal_dao.rst` を `convert()` → 各セクションの `content` に対して `extract_hints()` を実行
- 既知のクラス名（例: `UniversalDao`, `BasicDaoContextFactory`）が少なくとも1セクションで抽出される
- Stage 2マージ（`lookup_hints` 経由）によってStage 1単体より hints数が増える

- [x] `tests/e2e/test_pipeline_e2e.py` を作成してパイプライン統合テストを追加

---

## Not Started

### ~~Phase 4: Cross-reference resolution + asset copying~~ — DONE

Phase 4 implementation is complete and all 113 tests pass (run from repo root).
Untracked files: `scripts/resolver.py`, `tests/e2e/test_resolver.py`, `tests/ut/test_resolver.py`

**Note on scope**: `:ref:`/`:doc:` resolution to Markdown links is handled in the RST converter
(Phase 2) as plain-text stripping. The resolver handles label map building, asset collection,
and copying. This is sufficient for knowledge file generation (links resolved at browsable-docs
generation time, not in the JSON content).

**Steps:**
- [x] 全RSTファイルから `.. _label:` 定義を収集してラベルマップを構築 (`build_label_map`)
- [x] 参照画像を `assets/{id}/` にコピー (`collect_asset_refs` + `copy_assets`)
- [x] `:download:` → `[text](assets/{id}/filename)` + ファイルコピー
- [x] Unit test: ラベルマップ・アセット収集・コピーの全ケース
- [x] E2E test: v6実データ (mail.rst) でのアセット収集・コピー、全v6ラベルマップ
- [x] **Commit** the 3 untracked files
- [x] **サブエージェント品質チェック**: Pass（条件付き）— Medium: インデントラベル見逃し修正済み、path_to_id衝突はPhase 8で対処

---

### ~~Phase 5: MD converter~~ — DONE

committed `232df686`

---

### ~~Phase 6: Excel converters~~ — DONE

committed `edce71eb`

---

### ~~Phase 7: Index + browsable docs generation~~ — DONE

committed `dc019759`

---

### ~~Phase 8: CLI + create/update/delete/verify operations~~ — DONE

committed `5baf7a6d`

---

### ~~Phase 9: v1.x固有ディレクティブ対応~~ — DONE

committed `bc632d0f`

---

## Done

- [x] Phase 1: KC cache → hints mapping (`scripts/hints.py`) — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — committed `5913ff6e`, `1b62c4c4`, `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
