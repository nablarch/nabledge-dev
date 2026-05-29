# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-05-29

## Rules (applied to every task)

- 1コミット = 1タスク（粒度を守る）
- SCを満たすようタスクを分割し、このファイルで管理する
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- 既存の RST/MD/xlsx パイプラインへの変更は最小限
- RBKCのcreate/verifyを変更する場合は実装前に設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する
- 全タスク共通: 変更差分チェック → ユーザー確認 → PRレビュー依頼の順を守る

---

## 背景・設計理解

### 問題の本質

RST内の `:java:extdoc:` (nablarch.* 751件) が現在は表示テキストのみに変換されリンクが消える。
Javadocの詳細（メソッド・引数・戻り値・挙動）が知識ファイルに存在しない。

### あるべき姿

```
jarツール → Javadoc MD → RBKC → api/ カテゴリの知識JSON + 閲覧用MD
                                          ↑
RST :java:extdoc: → 内部クロスドキュメントリンク（外部URL依存なし）
```

- キーワード検索・意味検索の両方から Javadoc 知識ファイルが参照される
- 閲覧用MDもクリッカブルなリンクになる
- 外部 `nablarch.github.io` Javadoc URL依存が消える

---

## Not Started

### Task 1: jarツール確認（入出力形式）
**Goal**: SC「Identify the input/output format of the provided jar tool」を満たす。  
**前提**: ユーザーからjarファイル入手後  
**Steps:**
- [ ] jarツールを実際に実行してサンプル出力（MD）を取得する
- [ ] 出力MDの構造を全件確認する（クラス1つ分・複数クラス）
- [ ] 入力形式（ソースファイルのパス指定・オプション）を確認する
- [ ] 調査結果を `.work/00363/notes.md` に記録する

### Task 2: 設計書更新 → ユーザー承認
**Goal**: 実装前に設計を確定する。jarツール出力形式を踏まえて以下を更新。  
**前提**: Task 1 完了後  
**更新対象設計書:**
- [ ] `tools/rbkc/docs/rbkc-converter-design.md` — Javadoc MD → 知識JSONの変換ルール、`:java:extdoc:` 内部リンク出力ルール
- [ ] `tools/rbkc/docs/rbkc-json-schema-design.md` — `api/` カテゴリのJSONスキーマ
- [ ] `.claude/skills/nabledge-6/workflows/semantic-search.md` — `api/` カテゴリの扱い（分離 or 混在）
- [ ] `.claude/skills/nabledge-6/workflows/qa.md` — Javadoc質問への対応
- [ ] コミット・プッシュしてユーザーに確認を依頼する
- [ ] ユーザー承認後に Task 3 へ進む

### Task 3: コンバータ実装
**Goal**: Javadoc MDを知識JSON/閲覧用MDに変換し、`:java:extdoc:` が内部リンクになること。  
**前提**: Task 2 完了後  
**Steps:**
- [ ] `tools/rbkc/scripts/create/converters/javadoc.py` を新規作成（TDD: テスト先行）
- [ ] `rst_ast_visitor.py` の `:java:extdoc:` 処理を内部リンク出力に変更（対応JSONが存在すれば内部リンク、なければ表示テキスト）
- [ ] `mappings/v6.json` に `api/` カテゴリエントリを追加
- [ ] `scan_sources()` / `_converter_for()` に javadoc フォーマットの分岐を追加
- [ ] `rbkc.sh create 6 && rbkc.sh verify 6` を実行し FAIL 増加なしを確認
- [ ] 全既存テストが通ることを確認: `pytest tools/rbkc/tests/ -x`

### Task 4: 検索修正
**Goal**: 意味検索・QAワークフローから Javadoc 知識ファイルが参照されること。  
**前提**: Task 3 完了後（index.mdにapi/エントリが生成されていること）  
**Steps:**
- [ ] `workflows/semantic-search.md` を設計通りに更新
- [ ] `workflows/qa.md` を設計通りに更新
- [ ] キーワード検索: スキャン対象に自動追加されていることを確認（変更不要なら記録）

### Task 5: ベンチマークシナリオ追加
**Goal**: Javadoc参照質問に答えられることを検証するシナリオを用意する。  
**前提**: Task 4 完了後  
**Steps:**
- [ ] 既存シナリオでは Javadoc 知識ファイルが参照されないことを確認する
- [ ] Javadoc参照質問のシナリオを新規追加する（例: 「`UniversalDao#exist` の戻り値・挙動は？」）
- [ ] 期待値（expectations）を設定する

### Task 6: v6 検証（新シナリオ1件 → 既存スコア確認）
**Goal**: SC「nabledge can correctly answer questions about Javadoc-deferred API details」「Benchmark scores do not decrease」をv6で確認する。  
**前提**: Task 5 完了後  
**Steps:**
- [ ] 新シナリオ1件を v6 で実行し、Javadoc 知識ファイルが参照されること・正答することを確認する
- [ ] v6 既存シナリオのベンチマークを実行し、ベースライン（95.9%）から低下がないことを確認する（逐次実行）
- [ ] 問題があれば Task 3〜5 に戻って修正する
- [ ] 結果を `.work/00363/notes.md` に記録する

### Task 7: 全バージョン適用（v5 / v1.4 / v1.3 / v1.2）
**Goal**: SC「all 5 versions」を満たす。  
**前提**: Task 6（v6 検証 OK）後  
**Steps:**
- [ ] Task 2 の設計書を全バージョン向けに適用する（mappings/v5.json 等）
- [ ] 各バージョンで jarツールを実行して Javadoc MD を生成する
- [ ] `rbkc.sh create <v> && rbkc.sh verify <v>` を全4バージョンで実行し FAIL 増加なしを確認
- [ ] 全バージョンのベンチマークを実行し、スコア低下なしを確認（逐次実行）

### Task 8: 差分チェック + PR レビュー依頼
**Goal**: 変更差分が想定どおりかをチェックしてレビュー依頼。  
**前提**: Task 7 完了後  
**Steps:**
- [ ] `git diff main...HEAD --stat` で変更ファイル一覧を全件確認する
- [ ] 想定外の変更がないかをチェックし、`.work/00363/diff-check.md` に記録する
- [ ] ユーザーに確認を依頼する
- [ ] Expert review を実行する（Software Engineer + QA Engineer）
- [ ] PR を更新する

---

## Done

- [x] `.work/00363/tasks.md` と `notes.md` 作成 — committed `521ac200d`
- [x] PR #365 作成
