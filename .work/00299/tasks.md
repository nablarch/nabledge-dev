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

#### verify の検証仕様

ソース → 生成物の**完全性**を確認する。ルールベース変換でソース以外のコンテンツは入らないため、逆方向（生成物 → ソース）のチェックは不要。

バグが見つかった場合は verify が FAIL を出す → 修正タスクを追加して対処する。

**コンテンツ（全フォーマット共通: RST / MD / Excel）**

| # | チェック対象 | 内容 |
|---|------------|------|
| A | `sections[].title` | ソースの見出しと完全一致 |
| B | `sections[].content` | ソースのテキストと完全一致（リンク表示テキスト含む、リンクマークアップ除く） |

**リンク（全フォーマット共通）**

| # | チェック対象 | 内容 |
|---|------------|------|
| C | 内部リンク | 生成されたリンクURLに実際にアクセスして目的のページ（タイトル一致）か確認 |
| D | 外部URL | ソースの `https?://` URL と JSON の URL が文字列完全一致 |

**網羅性**

| # | チェック対象 | 内容 |
|---|------------|------|
| F | index.toon | 全JSONファイルのエントリが存在する |
| H | 閲覧用 MD | 全JSONファイルに対応するMDファイルが存在する |

閲覧用 MD にも A〜D を適用する（JSON と同じ基準）。

#### Steps

- [ ] `scripts/verify.py` を上記 A〜D・F・H の仕様で全面書き換え
- [ ] テスト: 各チェック項目を網羅するテストを追加/更新
- [ ] `pytest` 全通過確認
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
