# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-06-01

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

### 今セッションで合意した設計方針

#### 対象role
- `:java:extdoc:` (v6: 1,862件 / v5: 1,886件) → 内部リンク化
- `:javadoc_url:` (v6: 4件 / v5: 4件) → 外部URL（QL2）として出力
- その他のtext-only role（java:ref / java:type等）: v6/v5ともに0件 → 対応不要

#### パイプライン設計（run.py create の流れ）
```
① javadoc_generate() ← 新規追加（先に実行）
   - RST全体をスキャンしてFQCNリスト抽出
   - sources.jar（mvn取得）から.java展開
   - jar実行 → Javadoc MD（クラス1つ1ファイル）
   - Javadoc MD → JSON（knowledge/javadoc/に書き込み）
   - javadoc_map（FQCN → file_id）を返す

② （既存）scan → classify → convert（RST）
   - :java:extdoc: に javadoc_map を渡してリンク解決
   - 解決できた場合: 内部リンク [DisplayText](../../javadoc/{file_id}.md)
   - 解決できない場合: FAIL（象限2相当、テキストのみは許容しない）

③ index.md生成 → docs MD生成（既存のまま）
   - Javadoc JSONはindex.mdに含めない（755クラス追加で semantic-search破綻のため）
   - verify QO4（index.md網羅性）の対象からJavadoc JSONを除外する設計変更が必要
```

#### ソース取得方法
- v6/v5: `mvn dependency:get` で sources.jar 取得（Nexus経由、全33 artifact対応確認済み）
- v1.x: `:java:extdoc:` 使用なし（v1.2/v1.3/v1.4ともに0件）→ 対応不要

#### Javadoc知識ファイルの配置
```
knowledge/javadoc/javadoc-nablarch-common-dao-UniversalDao.json
docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md
```
- file_id形式: `javadoc-{FQCNのドット→ハイフン変換}`
- リンク形式: `[DisplayText](../../javadoc/{file_id}.md)`（linkfmt.pyに新関数追加）

#### jarツール
- 場所: `/home/tie303177/work/source-to-document-converter/target/source-to-document-converter-0.0.1.jar`
- 配置先: `tools/rbkc/lib/source-to-document-converter-0.0.1.jar`
- 入力: `.java`ファイルパス1つ / 出力: stdout にMarkdown
- 出力構造: `# class ClassName` / `## フィールドの詳細` / `## コンストラクタの詳細` / `## メソッドの詳細` / `### methodName` + コードブロック + 説明

#### 検索フロー（仮説 → 検証が必要）
- index.mdに追加しないため、既存知識ファイルの `:java:extdoc:` リンク経由でのみ到達
- 「リンクを辿って回答できる」は仮説 → 実装後に検証し、不十分なら検索ワークフローへの明示的な手順追加等で改善

#### verify設計書・converter設計書への影響
- converter design §5-1: `:java:extdoc:` をリンク化対象roleに昇格（display text only → 内部リンク）
- converter design §5-1: `:javadoc_url:` を外部URL（QL2）として出力
- verify: QL1の象限分類をJavadocリンクにも適用
- verify QO4: Javadoc JSONをindex.md網羅性チェックの対象外にする

### 調査結果（確認済み）

- v6 RST内 `:java:extdoc:` 参照: 1,862件（ユニークFQCN: 755クラス）
- v5 RST内 `:java:extdoc:` 参照: 1,886件（ユニークFQCN: 776クラス）
- v1.x: `:java:extdoc:` 使用なし
- Javadoc ベースURL: `https://nablarch.github.io/docs/{version}/publishedApi/`（conf.py `extlinks`）
- `:java:extdoc:` の処理箇所: `tools/rbkc/scripts/common/rst_ast_visitor.py` L781
- sources.jar取得: Nexus経由で全33 artifact取得確認済み（SNAPSHOT含む）
- jarツール動作確認済み（UniversalDao.java → MD出力、existsメソッド含む確認）
- 現在の index.md: 353ページ → 755追加すると1108ページ（semantic-search破綻）

---

## In Progress

### Task 1: 設計書更新 → ユーザー承認
**Steps:**
- [ ] `rbkc-converter-design.md` を更新する（`:java:extdoc:` リンク化 / `:javadoc_url:` 外部URL化）
- [ ] `rbkc-verify-quality-design.md` を更新する（QL1象限分類へのJavadoc適用 / QO4対象外化）
- [ ] Javadoc MDパース仕様を設計書に追記する（jar出力MD → JSON変換ルール）
- [ ] コミット・プッシュしてユーザーに確認を依頼する
- [ ] ユーザー承認後に Task 2 へ進む

---

## Not Started

### Task 2: 実装
**前提**: Task 1（設計書承認）後  
**Steps:**
- [ ] `tools/rbkc/lib/` に jar を配置する
- [ ] `linkfmt.py` に `emit_javadoc_link` / `JAVADOC_LINK_RE` を追加する
- [ ] `run.py` に `javadoc_generate()` を追加し、`create()` の先頭で呼び出す
- [ ] Javadoc MD → JSON コンバーターを実装する（jar出力MDをパース、セクション分割）
- [ ] `rst_ast_visitor.py` の `:java:extdoc:` 処理を内部リンク化する（javadoc_map参照）
- [ ] `rst_ast_visitor.py` の `:javadoc_url:` 処理を外部URL化する
- [ ] verify を更新する（QL1象限分類 / QO4対象外）
- [ ] `rbkc.sh create v6 && rbkc.sh verify v6` を実行し FAIL増加なしを確認（全5バージョン）

### Task 3: 検索フロー検証・改善
**前提**: Task 2 完了後  
**Steps:**
- [ ] 「UniversalDao#existsの使い方」等の質問でJavadocリンクが実際に使われるか確認する
- [ ] 使われない場合は検索ワークフロー（qa.md / semantic-search.md）に明示的な手順を追加する

### Task 4: ベンチマークシナリオ追加
**前提**: Task 2 完了後  
**Steps:**
- [ ] 既存シナリオではJavadoc知識ファイルが参照されないことを確認する
- [ ] Javadoc参照質問のシナリオを新規追加する
- [ ] 期待値（expectations）を設定する

### Task 5: v6 検証（新シナリオ1件 → 既存スコア確認）
**前提**: Task 3/4 完了後  
**Steps:**
- [ ] 新シナリオ1件を v6 で実行し、正答することを確認する
- [ ] v6 既存シナリオのベンチマークを実行し、スコア低下なしを確認する（逐次実行）
- [ ] 問題があれば Task 2 に戻って修正する

### Task 6: 差分チェック + PR レビュー依頼
**前提**: Task 5 完了後  
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
- [x] jarツール動作確認・設計方針合意（今セッション）
