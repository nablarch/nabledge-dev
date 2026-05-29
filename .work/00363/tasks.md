# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-05-29

## Rules (applied to every task)

- 1コミット = 1タスク（粒度を守る）
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- RBKCのcreate/verifyを変更する場合は実装前に設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

---

## 引継ぎ情報

### 問題の本質

RST内の `:java:extdoc:` がRBKCで表示テキストのみに変換されリンク・FQCNが消える。
Javadocの詳細（メソッド・引数・戻り値・挙動）が知識ファイルに存在しない。

### 調査結果

- v6 RST内 `:java:extdoc:` 参照: 1,971件（うち nablarch.* 751件、638クラス）
- 知識JSONで「Javadoc」に言及しているファイル: 25件
- Javadoc ベースURL: `https://nablarch.github.io/docs/6u3/publishedApi/` （conf.py `extlinks` で定義）
- `:java:extdoc:` の処理箇所: `tools/rbkc/scripts/common/rst_ast_visitor.py`（`java:extdoc` → 表示テキストのみ返す）

### あるべき姿

```
jarツール → Javadoc MD → RBKC → api/ カテゴリの知識JSON + 閲覧用MD
                                          ↑
RST :java:extdoc: → 内部クロスドキュメントリンク（外部URL依存なし）
```

- キーワード検索・意味検索の両方から Javadoc 知識ファイルが参照される
- 閲覧用MDもクリッカブルなリンクになる

---

## Not Started

### Task 1: jarツール確認（入出力形式）
**前提**: ユーザーからjarファイル入手後  
**Steps:**
- [ ] jarツールを実際に実行してサンプル出力（MD）を取得する
- [ ] 出力MDの構造を全件確認する（クラス1つ分・複数クラス）
- [ ] 入力形式（ソースファイルのパス指定・オプション）を確認する
- [ ] 結果をこのファイルの引継ぎ情報に追記する

### Task 2: 設計書更新 → ユーザー承認
**前提**: Task 1 完了後  
**Steps:**
- [ ] 設計書を更新する（Task 1の結果を踏まえて対象設計書・変更内容を確定する）
- [ ] コミット・プッシュしてユーザーに確認を依頼する
- [ ] ユーザー承認後に Task 3 へ進む

### Task 3: 実装タスク（設計承認後に確定）

### Task 4: ベンチマークシナリオ追加
**前提**: Task 3 完了後  
**Steps:**
- [ ] 既存シナリオでは Javadoc 知識ファイルが参照されないことを確認する
- [ ] Javadoc参照質問のシナリオを新規追加する
- [ ] 期待値（expectations）を設定する

### Task 5: v6 検証（新シナリオ1件 → 既存スコア確認）
**前提**: Task 4 完了後  
**Steps:**
- [ ] 新シナリオ1件を v6 で実行し、正答することを確認する
- [ ] v6 既存シナリオのベンチマークを実行し、スコア低下なしを確認する（逐次実行）
- [ ] 問題があれば Task 3 に戻って修正する

### Task 6: 全バージョン適用（v5 / v1.4 / v1.3 / v1.2）
**前提**: Task 5（v6 検証 OK）後  
**Steps:**
- [ ] 全4バージョンに実装・設定を適用する
- [ ] `rbkc.sh create <v> && rbkc.sh verify <v>` を全4バージョンで実行し FAIL 増加なしを確認
- [ ] 全バージョンのベンチマークを実行し、スコア低下なしを確認（逐次実行）

### Task 7: 差分チェック + PR レビュー依頼
**前提**: Task 6 完了後  
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
