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

現在の `scripts/verify.py` はトークンサンプリング（最大100個、70%カバレッジ閾値）のみ。
ルールベース変換なので、変換ルールから導出できる構造的チェックに置き換える。

**調査: 意図的除去・変換対象の確定**

`rst.py` が意図的に除去または変換する要素を網羅的にリストアップし、
「除去後の残り全トークンはJSONに100%現れる」という基準を確立する。

除去対象（出力なし）:
- `toctree`, `contents`, `raw`, `include`, `class` ディレクティブのブロック
- `no_knowledge_content=true` のファイル（セクション全体が空）

変換対象（テキストは保持、形式のみ変更）:
- `note`/`warning` 等のアドモニション → blockquote
- `code-block` / `literalinclude` → fenced code
- `:ref:`, `:doc:` → プレーンテキスト
- RST テーブル → Markdown テーブル

**verify の更新内容**:

1. **セクション数チェック**: ソースのh2/h3見出し数 = JSONの `sections` 数
   （`no_knowledge_content=true` は除外）
2. **セクションタイトルチェック**: 各JSONセクションのタイトルがソース見出しと完全一致
3. **トークンカバレッジ**: サンプリング廃止 → 除去対象を除外した全トークンで100%チェック
4. **XLSX**: sections数 > 0（既存）をそのまま維持

**Steps:**
- [ ] 調査: `rst.py` の除去・変換要素を網羅的にリストアップ、除外ルール確定
- [ ] `scripts/verify.py` 更新: セクション数チェック実装
- [ ] `scripts/verify.py` 更新: セクションタイトル完全一致チェック実装
- [ ] `scripts/verify.py` 更新: 除去対象除外 + 100%トークンカバレッジに変更
- [ ] テスト更新: 新チェックに合わせてテスト追加/修正
- [ ] コミット

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
