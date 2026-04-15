# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-15 (session 4)

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

## 発見されたバグ一覧（v6 verify 実行で特定、2026-04-15）

統合検証（Phase 17相当）を先行実施して549件のFAILが発生。根本原因を分析した結果、以下の8バグを特定：

| ID | バグ | FAILへの影響 | 修正フェーズ |
|----|------|-------------|-------------|
| B1 | verify `assets/`スキップ（"asset copy not implemented" workaround） | 隠れFAIL（assetsコピー後に顕在化） | Phase 12 |
| B2 | verify: docs MD に A/B/C/D チェックなし（仕様未実装） | 隠れFAIL | Phase 12 |
| B3 | verify: FAILメッセージがファイル名のみ（相対パスなし） | 診断不可 | Phase 12 |
| B4 | create: copy_assets/generate_index/generate_docs/pre-clean 未呼び出し | 218+211 FAIL | Phase 13 |
| B5 | classify: 出力パス衝突10件（同名ファイルが同一JSONに上書き） | 44+多数 FAIL | Phase 14 |
| B6 | verify Check D: URL正規表現がバッククォートを取り込む | 5 FAIL | Phase 15 |
| B7 | converter: 一部URLがJSONに出力されない（テーブル内RST外部リンク等） | 4 FAIL | Phase 15 |
| B8 | verify/converter: toctree-only index.rstのtoken coverage 0%（40件） | 40 FAIL | Phase 16 |

---

## Not Started

### Phase 13: create pipeline 完全修正

**背景**: `run.py` の `create()` は JSON変換しか行わず、index.toon/docs MD/assetsを生成しない。
また既存ファイルを削除しないため、旧KC生成ファイルが混在し続ける。

**修正するバグ**: B4

#### create の完全仕様

```
create(version):
  1. output_dir (knowledge/) の JSON を全削除（pre-clean）
  2. docs_dir (docs/) を全削除（pre-clean）
  3. assets/ を全削除（pre-clean）
  4. index.toon を削除（pre-clean）
  5. 全ソースファイルを変換して JSON 書き込み
  6. copy_assets() — JSON内で参照されるassetファイルをコピー
  7. generate_index() — index.toon を生成
  8. generate_docs() — docs MD を生成
```

`update()` と `delete()` も同様に index.toon/docs/assets を再生成すること（差分適用後に再生成）。

#### Steps（TDD）

**テスト作成（RED）**

- [ ] `create` 後に index.toon が生成されていることのE2Eテスト → RED確認
- [ ] `create` 後に docs MD が生成されていることのE2Eテスト → RED確認
- [ ] `create` 後に assets がコピーされていることのE2Eテスト → RED確認
- [ ] `create` が出力ディレクトリを事前クリーンすることのE2Eテスト → RED確認
- [ ] `update` 後に index.toon が再生成されることのE2Eテスト → RED確認
- [ ] `delete` 後に index.toon が再生成されることのE2Eテスト → RED確認

**実装**

- [ ] `run.py` の `create()` に pre-clean + copy_assets + generate_index + generate_docs を追加
- [ ] `run.py` の `update()` に generate_index + generate_docs + copy_assets(差分) を追加
- [ ] `run.py` の `delete()` に generate_index + generate_docs を追加

**GREEN確認・品質チェック**

- [ ] 全E2Eテスト GREEN
- [ ] `pytest` 全通過
- [ ] サブエージェント品質チェック（Pass になるまで修正）
- [ ] コミット

---

### Phase 14: classify 出力パス衝突修正

**背景**: `classify_sources()` の file_id 生成がファイル名のみに基づくため、
異なるディレクトリの同名ファイルが同一 JSON に上書きされる（last-wins）。
v6で10件の衝突が確認済み：

| 出力JSON | 衝突ソース数 | 代表的な衝突 |
|---------|------------|------------|
| `testing-framework-delayed-receive.json` | 2 | 02_RequestUnitTest/ vs 03_DealUnitTest/ |
| `testing-framework-batch.json` | 2 | 同上パターン（6ファイル） |
| `libraries-functional-comparison.json` | 3 | data_io/ vs validation/ vs database/ |
| `libraries-permission-check.json` | 2 | libraries/ vs authorization/ |
| `about-nablarch-application-framework.json` | 2 | application_framework/ vs application_framework/application_framework/ |

**修正するバグ**: B5

#### 修正方針

衝突する各ソースに対して**固有の output_path**を割り当てる。
classify_sources() に衝突検知を追加し、衝突が発生したら **エラーで停止**（サイレント上書き禁止）。

具体的な衝突解消:
- `02_RequestUnitTest/delayed_receive.rst` → `testing-framework-request-delayed-receive.json`
- `03_DealUnitTest/delayed_receive.rst` → `testing-framework-deal-delayed-receive.json`
- `libraries/data_io/functional_comparison.rst` → `libraries-data-io-functional-comparison.json`
- `libraries/validation/functional_comparison.rst` → `libraries-validation-functional-comparison.json`
- `libraries/database/functional_comparison.rst` → `libraries-database-functional-comparison.json`
- その他4件も同様にパスセグメントを使って固有IDを生成

または: マッピングファイル（`.claude/skills/nabledge-6/docs/mapping/`等）で明示的に衝突解消。

#### Steps（TDD）

**テスト作成（RED）**

- [ ] 衝突するソースを与えたとき `classify_sources()` がエラーを返すテスト → RED確認
- [ ] 衝突解消後、各ソースが固有の output_path を持つことのテスト → RED確認

**実装**

- [ ] `scripts/classify.py` に衝突検知（エラー）を追加
- [ ] 10件の衝突を具体的に解消（file_id 生成ロジック or マッピングで固有IDを付与）
- [ ] v5/v1.4/v1.3/v1.2でも同様の衝突がないかチェック（水平展開）

**GREEN確認・品質チェック**

- [ ] 全テスト GREEN
- [ ] `pytest` 全通過
- [ ] `bash rbkc.sh create 6` で衝突エラーが出ないこと確認
- [ ] サブエージェント品質チェック
- [ ] コミット

---

### Phase 15: converter/verify URL バグ修正

**背景**: Check D の URL抽出・照合に2種類のバグがある。

**修正するバグ**: B6, B7

#### B6: URL正規表現がバッククォートを取り込む

現象: `` ``http://localhost:9080/`` `` （RST inline code）→ URL_RE が `http://localhost:9080/\`\`` を抽出  
原因: `_URL_RE = re.compile(r"https?://[^\s>\)\]\"']+")` にバッククォートが含まれない  
修正: `[^\s>\)\]\"'\`]` に変更

**→ Phase 12のCheck D正規表現修正で対応済みのため、ここではconverter側を確認のみ**

#### B7: テーブル内RST外部リンクがJSONに出力されない

現象: `data_format.rst` の `:JSON: ... \`Jackson <https://github.com/FasterXML/jackson>\`_` がJSON contentに入らない  
確認すべきこと:
1. RSTコンバーターがフィールドリスト `:JSON:` のコンテンツを出力しているか
2. 同様に `https://jakarta.ee/specifications/xml-binding/` `https://jakarta.ee/specifications/bean-validation/` が欠落しているか
3. batch.rstの `https://github.com/nablarch/nablarch-testing/...` が欠落している理由

**Steps（TDD）**

- [ ] B7: 各失敗URLについてソースRSTを確認し根本原因を特定
- [ ] converter unittest: RST fieldlist (`.. list-table::`, `:JSON:` 等) のURL保存テスト → RED
- [ ] 修正 → GREEN
- [ ] `pytest` 全通過
- [ ] サブエージェント品質チェック
- [ ] コミット

---

### Phase 16: toctree-only index.rst の token coverage 修正

**背景**: 多くの `index.rst` は toctree ディレクティブのみを含み、テキストコンテンツがほぼ存在しない。
これらを変換すると「空のセクション」または「内容なしドキュメント」になり、
Check B が 0/N (0% < 70%) を報告する（v6で40件）。

**修正するバグ**: B8

#### 根本原因の調査

toctree-onlyファイルが FAIL する理由は2つの可能性がある：

1. **converter が `no_knowledge_content: true` を付けるべきなのに付けていない**
   → verify は `no_knowledge_content: true` ファイルをCheck Bでスキップするが、このフラグが立っていない
2. **mapping が不適切なファイルを変換対象に含めている**
   → toctree-onlyファイルは知識ファイルとして不要かもしれない

#### Steps（TDD）

- [ ] 40件の failing index.rst を分類：toctree-only / 有意なコンテンツあり
- [ ] toctree-only の扱いを決定（ユーザーに確認）:
  - **案A**: converter が toctree-only を検出して `no_knowledge_content: true` を自動付与
  - **案B**: mapping から除外
- [ ] 決定した方針でテスト作成 → RED確認
- [ ] 実装 → GREEN確認
- [ ] 残りの token coverage FAIL（index.rst以外：validation/jsp_session/ModifySettings等）の原因調査・修正
- [ ] `pytest` 全通過
- [ ] サブエージェント品質チェック
- [ ] コミット

---

### Phase 17: 統合検証 — v6

**前提**: Phase 12〜16 完了後に実施。`bash rbkc.sh verify 6` が FAIL 0件であること。

**Steps:**
- [ ] `bash rbkc.sh create 6` を実行
- [ ] `bash rbkc.sh verify 6` を実行 — FAIL 0件確認
  - FAILが出た場合: 根本原因を分析→ユーザーに報告→承認後修正→再verify
- [ ] nabledge-test v6 を実行して品質劣化なし（ベースライン比）を確認
- [ ] コミット（生成済み知識ファイル）

---

### Phase 18: 統合検証 — v5

**前提**: Phase 17 (v6) 通過後。

**Steps:**
- [ ] `bash rbkc.sh create 5` → `bash rbkc.sh verify 5` — FAIL 0件
  - FAILが出た場合: 分析→報告→承認→修正→再verify
- [ ] nabledge-test v5 — 劣化なし確認
- [ ] コミット

---

### Phase 19: 統合検証 — v1.4 / v1.3 / v1.2

**前提**: Phase 18 (v5) 通過後。

**Steps:**
- [ ] `bash rbkc.sh create 1.4` → `bash rbkc.sh verify 1.4` — FAIL 0件
- [ ] `bash rbkc.sh create 1.3` → `bash rbkc.sh verify 1.3` — FAIL 0件
- [ ] `bash rbkc.sh create 1.2` → `bash rbkc.sh verify 1.2` — FAIL 0件
  - 各バージョンでFAILが出た場合: 分析→報告→承認→修正→再verify
- [ ] nabledge-test v1.4 / v1.3 / v1.2 — 劣化なし確認
- [ ] コミット（全3バージョン）

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
- [x] Phase 10: コンバータ修正 (10-1〜10-6) — committed `54fe3ef8`, `d5a6961d`, `cd856500`, `d2303716`, `7eac70f6`, `10b239b1`
- [x] Test fix: update pipeline E2E test for Phase 10-6 hints API change — committed `88a8c7a6`
- [x] Phase 11: verify の完全チェック化 (checks A/B/C/D/F/H) — committed `6c664a59`
  - **※ Phase 12で書き直し済み（B1/B2/B3バグを修正）**
- [x] Phase 12: verify 完全書き直し (B1/B2/B3修正) + エキスパートレビュー — committed `1eff2740`
- [x] Phase 13: create pipeline 完全修正 (B4修正) — committed `e85488cb`
- [x] Phase 14: classify 出力パス衝突修正 (B5修正) — auto-disambiguation + mappings独立化 — committed `b6a4a630`
- [x] Phase 15: converter/verify URL バグ修正 (B6/B7修正) — admonition field list + backtick — committed `63ac0ec9`
