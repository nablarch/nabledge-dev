# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-05-29

## Rules (applied to every task)

- 1コミット = 1タスク（粒度を守る）
- SCを満たすようタスクを分割し、このファイルで管理する
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- 既存の RST/MD/xlsx パイプラインには一切触れない（追加・変更は最小限）
- RBKCのcreate/verifyを変更する場合は実装前に設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する
- 全タスク共通: 変更差分チェック → ユーザー確認 → PRレビュー依頼の順を守る

---

## 背景・設計理解

### 問題の本質

RST内の `:java:extdoc:` (1,971件、nablarch.* 751件) が現在は表示テキストのみに変換されリンクが消える。
その結果、知識ファイルには「クラス名のテキスト」しかなく、Javadocの詳細（メソッド・引数・戻り値・挙動）が得られない。

### あるべき姿

```
jarツール → Javadoc MD → RBKC → api/ カテゴリの知識JSON + 閲覧用MD
                                          ↑
RST :java:extdoc: → 内部クロスドキュメントリンク（外部URL依存なし）
```

- Javadoc知識ファイルが内部に存在することで、キーワード検索・意味検索の両方から参照可能になる
- 閲覧用MDもクリッカブルなリンクになる
- 外部 `nablarch.github.io` JavadocへのURL依存が消える

### 実装順序の理由

検索をどう変えるか（意味検索のindex.md構成、QAワークフローの変更点）を先に設計しないと、
検索修正タスクの粒度・内容が決まらない。設計 → 実装 → 検索修正 → 検証 → 全バージョン展開の順。

---

## Not Started

### Task 0: 設計（コンバータ設計 + 検索設計）
**Goal**: 実装前に全体設計を確定し、ユーザーに承認を得る。  
**Steps:**
- [ ] jarツールの入出力形式を確認する（ユーザーからjar入手後）
- [ ] コンバータ設計:
  - [ ] Javadoc MD → 知識JSON のスキーマ設計（`api/` カテゴリ）
  - [ ] `:java:extdoc:` の内部リンク解決方式（FQCNからfile_idを引く方法）
  - [ ] verify への影響設計（既存チェックの適用範囲）
- [ ] 検索設計:
  - [ ] 意味検索: `index.md` の構成変更（`api/` セクション追加 or 分離）
  - [ ] 意味検索: `semantic-search.md` の変更点（api/ セクションの扱い）
  - [ ] QAワークフロー: `qa.md` の変更点（Javadoc質問への対応）
  - [ ] キーワード検索: 変更不要か確認（スキャン対象に自動追加される）
- [ ] 設計書を `tools/rbkc/docs/` または `.work/00363/` に作成する
- [ ] コミット・プッシュしてユーザーに確認を依頼する
- [ ] ユーザー承認後に Task 1 へ進む

### Task 1: jarツール実行 + Javadoc MD 生成確認
**Goal**: SC「Identify the input/output format of the provided jar tool」を満たす。  
**前提**: Task 0 完了後  
**Steps:**
- [ ] jarツールを実際に実行してサンプル出力（MD）を取得する
- [ ] 出力MDの構造を全件確認する（クラス1つ分・複数クラス）
- [ ] 設計（Task 0）との差異があれば設計を修正する
- [ ] 調査結果を `.work/00363/notes.md` に記録する

### Task 2: コンバータ実装（`converters/javadoc.py` + `:java:extdoc:` 内部リンク）
**Goal**: Javadoc MDを知識JSON/閲覧用MDに変換し、`:java:extdoc:` が内部リンクになること。  
**前提**: Task 0, Task 1 完了後  
**Steps:**
- [ ] `tools/rbkc/scripts/create/converters/javadoc.py` を新規作成（TDD: テスト先行）
- [ ] `rst_ast_visitor.py` の `:java:extdoc:` 処理を内部リンク出力に変更
  - 変更前: 表示テキストのみ返す
  - 変更後: 対応するJavadoc知識JSONが存在すれば内部クロスドキュメントリンク、なければ表示テキスト（後退しない）
- [ ] mappings/v6.json に `api/` カテゴリエントリを追加
- [ ] `scan_sources()` / `_converter_for()` に javadoc フォーマットの追加分岐
- [ ] `rbkc.sh create 6 && rbkc.sh verify 6` を実行し FAIL 増加なしを確認
- [ ] 全既存テストが通ることを確認: `pytest tools/rbkc/tests/ -x`

### Task 3: 検索修正（semantic-search + qa ワークフロー）
**Goal**: 意味検索・QAワークフローから Javadoc 知識ファイルが参照されること。  
**前提**: Task 2 完了後（index.mdにapi/エントリが生成されていること）  
**Steps:**
- [ ] `workflows/semantic-search.md` を設計通りに更新（api/ セクションの扱い）
- [ ] `workflows/qa.md` を設計通りに更新（Javadoc質問への対応）
- [ ] キーワード検索: スキャン対象に自動追加されていることを確認（変更不要なら記録）
- [ ] 手動動作確認: 「`UniversalDao#exist` の戻り値は？」「DAOで存在チェックするには？」の両方で Javadoc 知識ファイルが参照されることを確認

### Task 4: ベンチマークシナリオ追加 + v6 検証
**Goal**: SC「nabledge can correctly answer questions about Javadoc-deferred API details」「Benchmark scores do not decrease」を満たす。  
**前提**: Task 3 完了後  
**Steps:**
- [ ] nabledge-test に Javadoc 参照質問のシナリオを追加する（例: `UniversalDao#exist` の挙動）
- [ ] v6 ベンチマークを実行する（逐次実行 — 並列不可）
- [ ] 既存シナリオのスコアがベースライン（95.9%）から低下していないことを確認
- [ ] 新シナリオが正答することを確認
- [ ] 結果を `.work/00363/notes.md` に記録する

### Task 5: 全バージョン適用（v5 / v1.4 / v1.3 / v1.2）
**Goal**: SC「all 5 versions」を満たす。  
**前提**: Task 4（v6 検証 OK）後  
**Steps:**
- [ ] mappings/v5.json, v1.4.json, v1.3.json, v1.2.json に `api/` カテゴリエントリを追加
- [ ] 各バージョンで jarツールを実行して Javadoc MD を生成する
- [ ] `rbkc.sh create <v> && rbkc.sh verify <v>` を全4バージョンで実行し FAIL 増加なしを確認
- [ ] 全バージョンのベンチマークを実行し、スコア低下なしを確認（逐次実行）

### Task 6: 差分チェック + PR レビュー依頼
**Goal**: 全タスク完了後、変更差分が想定どおりかをチェックしてレビュー依頼。  
**前提**: Task 5 完了後  
**Steps:**
- [ ] `git diff main...HEAD --stat` で変更ファイル一覧を確認する
- [ ] 想定外の変更がないかを全件チェックし、`.work/00363/diff-check.md` に記録する
- [ ] ユーザーに確認を依頼する
- [ ] Expert review を実行する（Software Engineer + QA Engineer）
- [ ] `/pr create` でPRを更新する

---

## Done

- [x] `.work/00363/tasks.md` と `notes.md` 作成 — committed `521ac200d`
- [x] PR #365 作成
