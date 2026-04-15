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

### Phase 10: コンバータ修正

調査で判明したコンバータの欠陥を修正する。全修正 TDD で実施。

#### 10-1: preamble 消滅バグ修正（rst.py）

h1 前に `.. _label:` がある場合（v6: 225/334ファイル）、h1〜最初のh2 間のコンテンツが消える。

`_flush()` の `elif current_lines and not preamble_lines:` を `elif current_lines:` に変更し `extend` で追記。

**Steps（TDD）:**
- [ ] テスト: pre-h1 ラベルありRSTでpreamble内容が保持されることを確認 → RED
- [ ] `scripts/converters/rst.py` `_flush()` 修正 → GREEN
- [ ] `pytest` 全通過確認 → コミット

---

#### 10-2: 脚注（`.. [N]`）の出力（全バージョン）

脚注に知識コンテンツが含まれる（v6/v5: 92-97件、v1.x: 46-57件）。現在全件スキップされている。
脚注は本文の補足情報として当該セクションの `content` に追記する。

**Steps（TDD）:**
- [ ] テスト: 脚注コンテンツが `content` に含まれることを確認 → RED
- [ ] `scripts/converters/rst.py` 脚注処理実装 → GREEN
- [ ] `pytest` 全通過確認 → コミット

---

#### 10-3: `class` ディレクティブのコンテンツ出力（v1.x）

`class` ディレクティブのブロックに API 説明が含まれる（v1.x: 4件）。現在スキップされている。
ブロックコンテンツを通常テキストとして出力する。

**Steps（TDD）:**
- [ ] テスト: `class` ディレクティブのブロックが `content` に含まれることを確認 → RED
- [ ] `scripts/converters/rst.py` `_SKIP_DIRECTIVES` から `class` を除外し本文出力 → GREEN
- [ ] `pytest` 全通過確認 → コミット

---

#### 10-4: 名前付きリンク参照の URL 解決（全バージョン）

`` `Name`_ `` 形式の参照について、ターゲット定義（同ファイル内 `.. _Name: url` または `.. include::` 経由の link.rst）からURLを解決して `[Name](URL)` に変換する。

現状: `` `Name`_ `` → プレーンテキスト（URLが消える）
あるべき姿: `` `Name`_ `` → `[Name](URL)`

影響範囲:
- 同ファイル内ターゲット: v6/v5 で外部URL 39-40件
- include ファイル内ターゲット: v1.x link.rst で 51件実際使用（Javadoc + 解説書リンク）

**Steps（TDD）:**
- [ ] テスト: 同ファイル内ターゲット定義 → `[Name](URL)` に変換されることを確認 → RED
- [ ] テスト: include 経由ターゲット定義 → `[Name](URL)` に変換されることを確認 → RED
- [ ] `scripts/converters/rst.py` ターゲット収集 + 参照解決ロジック実装 → GREEN
- [ ] `pytest` 全通過確認 → コミット

---

#### 10-5: raw `:file:` 参照の処理（v1.x）

v1.x の raw ディレクティブが `:file: ../Handler.js` 形式でJSファイルを参照している。
Handler.js に各ハンドラの動作説明（inbound/outbound/error、96件）が含まれており、本文には一切記述がない。

Handler.js の構造:
```javascript
HandlerName: {
  name: "日本語名"
, package: "nablarch.fw.handler"
, behavior: {
    inbound:  "動作説明"
  , outbound: "動作説明"
  , error:    "エラー時の動作説明"
  }
}
```

JSをパースし、ハンドラ名・日本語名・パッケージ・動作説明を当該セクションの `content` に追記する。
また、同様の `:file:` 参照が他にないか調査して対処する。

**Steps（TDD）:**
- [ ] `:file:` 参照を使うrawブロックの種類を全バージョンで調査
- [ ] テスト: Handler.js の動作説明が `content` に含まれることを確認 → RED
- [ ] `scripts/converters/rst.py` raw `:file:` パーサー実装 → GREEN
- [ ] `pytest` 全通過確認 → コミット

---

#### 10-6: hints の修正（Stage 1 削除・Stage 2 マッピング戦略を刷新）

**Stage 1 削除**: Route 1（全文検索）が primary なので、content に含まれる PascalCase 等は不要。

**Stage 2 マッピング戦略**: 調査により以下が判明した。

- KC は `catalog.json` の `section_range.sections`（Expected Sections）を受け取り、その順にセクションを生成する
- KC のセクション ID は常に `s1` からのローカル連番（catalog のグローバル ID と一致しない）
- KC タイトルは Expected Sections のタイトルと原則一致するが、大きいセクション（≥2000文字 + h3あり）は h3 に分割して別タイトルになることがある
- catalog に `section_range.sections` がないファイル（v1.x で多い）は KC が独自にセクション検出した

これを踏まえ、以下の 2 ステップ戦略でマッピングする。

**ステップ A: Expected Sections ありのファイル（catalog に `section_range.sections` がある）**

catalog から Expected Sections（空見出しを除外した RST h2 見出しリスト）を取得し、KC index を順番に走査して割り当てる:

1. KC タイトルが Expected に**直接一致** → そのまま割り当て、ポインタを進める
2. KC タイトルが Expected にないが、Expected のいずれかが KC タイトルに**部分文字列として含まれる** → 最長一致の Expected に割り当て（h3 分割ケース）
3. 上記どちらにも該当しない → 現在のポインタが示す Expected に割り当て
4. ポインタが末尾を超えた場合 → 最後の Expected に割り当て（破棄しない）

検証結果（全バージョン）:
- 割り当てができる: 94〜97%
- ヒント 0 になる 107 件は KC に対応エントリがないため対応不要（確認済み）

**ステップ B: Expected Sections なしのファイル（catalog に `section_range.sections` がない）**

KC セクション本文と RST ソースの各セクション本文をキーワード重複率で照合し、**重複率 ≥ 25% の最近傍 RST セクション**（= RBKC のセクションタイトル）に割り当てる。

- RST のセクション境界: オーバーライン付きでない見出しアンダーライン（`----`, `====` 等）で検出
- 重複率 = KC 本文のキーワードのうち RST セクション本文に出現する割合
- 閾値未満は破棄

検証結果（全バージョン）:
- v6: 100%, v5: 100%, v1.4: 99%, v1.3: 94%, v1.2: 94%
- 未マッチは内容が薄いセクション（`エラー発生時の処理`、`終了処理` 等）

**実装変更箇所**:

- `scripts/hints.py`
  - `build_hints_index(cache_dir, catalog_path)` に変更（catalog_path を追加）
  - ステップ A: catalog の Expected Sections を使った走査ロジック
  - ステップ B: KC 本文と RST 本文のキーワードオーバーラップ（RST ソースパスは caller から渡す）
  - 戻り値: `{base_file_id: {rst_heading: hints_list}}`（キーは RST 見出しのまま）
- `scripts/run.py`
  - `_hints_index()` に catalog_path を渡すよう修正
  - `lookup_hints(hints_idx, fi.file_id, sec.title)` の呼び出しはそのまま

**Steps（TDD）:**
- [ ] テスト: Stage 1 ロジックが呼ばれないことを確認
- [ ] テスト: ステップ A（直接一致・substring・末尾超え）が正しく動作することを確認 → RED
- [ ] テスト: ステップ B（コンテンツオーバーラップ）が正しく動作することを確認 → RED
- [ ] `scripts/hints.py` Stage 1 削除、ステップ A・B 実装 → GREEN
- [ ] `scripts/run.py` 呼び出し側を合わせて修正
- [ ] `pytest` 全通過確認 → コミット

---

### Phase 11: verify の完全チェック化

#### verify の検証仕様

ソース → 生成物の**完全性**を確認する。ルールベース変換でソース以外のコンテンツは入らないため、逆方向（生成物 → ソース）のチェックは不要。

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

#### Steps（TDD）

**Unit tests（RED → 実装 → GREEN）**
- [ ] A: タイトル完全一致チェックのユニットテスト作成 → RED確認
- [ ] B: テキスト完全一致チェックのユニットテスト作成 → RED確認
- [ ] C: 内部リンク到達確認のユニットテスト作成（HTTPモック）→ RED確認
- [ ] D: 外部URL完全一致チェックのユニットテスト作成 → RED確認
- [ ] F: index.toon 網羅性チェックのユニットテスト作成 → RED確認
- [ ] H: 閲覧用MD 網羅性チェックのユニットテスト作成 → RED確認
- [ ] `scripts/verify.py` を A〜D・F・H の仕様で全面書き換え → GREEN確認

**E2E tests（RED → 実装 → GREEN）**
- [ ] v6 実データ（`universal_dao.rst` 等）を使った E2E テスト作成 → RED確認
- [ ] Excel 実データを使った E2E テスト作成 → RED確認
- [ ] E2E GREEN確認

**完了確認**
- [ ] `pytest` 全通過確認
- [ ] コミット

---

### Phase 12: 統合検証 — v6

**前提**: Phase 11 (verify完全チェック化) 完了後に実施。

verify FAIL が出たらバグ修正タスクを追加し、FAIL 0件になるまで 生成→検証→バグ修正 を繰り返す。

**Steps:**
- [ ] `bash rbkc.sh create 6` を実行（出力先: `.claude/skills/nabledge-6/knowledge/`）
- [ ] `bash rbkc.sh verify 6` を実行 — FAIL 0件になるまで下記ループ:
  1. FAIL内容を分析して根本原因と対応案をユーザーに報告
  2. ユーザー承認後に修正実施
  3. 再verify
- [ ] nabledge-test v6 を実行して品質劣化なし（ベースライン比）を確認
- [ ] コミット（生成済み知識ファイルをコミット）

v6 検証通過後 → Phase 13 (v5) へ

---

### Phase 13: 統合検証 — v5

**前提**: Phase 12 (v6) 通過後に実施。

**Steps:**
- [ ] `bash rbkc.sh create 5` を実行（出力先: `.claude/skills/nabledge-5/knowledge/`）
- [ ] `bash rbkc.sh verify 5` を実行 — FAIL 0件になるまで下記ループ:
  1. FAIL内容を分析して根本原因と対応案をユーザーに報告
  2. ユーザー承認後に修正実施
  3. 再verify
- [ ] nabledge-test v5 を実行して品質劣化なし（ベースライン比）を確認
- [ ] コミット

v5 検証通過後 → Phase 14 (v1.4/1.3/1.2) へ

---

### Phase 14: 統合検証 — v1.4 / v1.3 / v1.2

**前提**: Phase 13 (v5) 通過後に実施。

**Steps:**
- [ ] `bash rbkc.sh create 1.4` → `bash rbkc.sh verify 1.4` — FAIL 0件になるまで下記ループ:
  1. FAIL内容を分析して根本原因と対応案をユーザーに報告
  2. ユーザー承認後に修正実施
  3. 再verify
- [ ] `bash rbkc.sh create 1.3` → `bash rbkc.sh verify 1.3` — FAIL 0件になるまで下記ループ:
  1. FAIL内容を分析して根本原因と対応案をユーザーに報告
  2. ユーザー承認後に修正実施
  3. 再verify
- [ ] `bash rbkc.sh create 1.2` → `bash rbkc.sh verify 1.2` — FAIL 0件になるまで下記ループ:
  1. FAIL内容を分析して根本原因と対応案をユーザーに報告
  2. ユーザー承認後に修正実施
  3. 再verify
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
