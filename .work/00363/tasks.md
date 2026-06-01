# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-06-01 (session 5 rewrite)

## Rules (applied to every task)

- 1コミット = 1タスク（粒度を守る）
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- RBKCのcreate/verifyを変更する場合は実装前に設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する
- **各タスクは TDD 順（テスト RED → 実装 GREEN）で進める。実装ファイルとテストは同一コミットにまとめない**
- **1タスク完了後に必ず `python -m pytest tests/ut/ -q` を実行し、全テスト GREEN を確認してからコミットする**

---

## 設計書サマリー（実装の根拠）

設計書: `tools/rbkc/docs/rbkc-converter-design.md` §5-1 / §5-2
verify 設計書: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2-3 / §3-3

### 変換ルール（converter design §5-1）
- `:java:extdoc:` display text only → `[DisplayText](../javadoc/{file_id}.md)` へ昇格
  - `nablarch.*` + javadoc_map 解決成功 → 内部リンク（象限 1）
  - `nablarch.*` + javadoc_map 解決失敗 → **FAIL**（象限 2、パイプラインバグ）
  - `java.*`/`jakarta.*`/`javax.*` → WARNING + display text（象限 3、scope 外）
- `:javadoc_url:` → `[DisplayText](URL)` 外部リンク

### Javadoc 生成パイプライン（converter design §5-2）
```
javadoc_generate(version, repo_root, output_dir, docs_dir) → javadoc_map
  1. RST 全走査 → nablarch.* FQCN 列挙
  2. BOM POM から artifact 一覧取得 → mvn dependency:get で sources.jar 取得
  3. sources.jar から .java 抽出
  4. source-to-document-converter.jar 実行 → Javadoc MD
  5. Javadoc MD → JSON (knowledge/javadoc/{file_id}.json)
  6. JSON → docs MD (docs/javadoc/{file_id}.md)
  7. javadoc_map (FQCN → file_id) を返す
```

### verify への影響（verify design §3-2-3 / §3-3）
- QL1: `:java:extdoc:` が JSON に `[DisplayText](../javadoc/{file_id}.md)` として出力されているか検証
  - display text のみ → FAIL (QL1)
  - `knowledge/javadoc/{file_id}.json` が存在しない → FAIL (QL1)
- QO4: `knowledge/javadoc/` 配下 JSON を対象外とする（755クラス追加で semantic-search 破綻のため）

### ファイル配置
- `knowledge/javadoc/javadoc-{FQCN-dot-to-hyphen}.json`
- `docs/javadoc/javadoc-{FQCN-dot-to-hyphen}.md`
- `tools/rbkc/lib/source-to-document-converter-0.0.1.jar`

---

## In Progress

### Task 2-A: linkfmt.py — emit_javadoc_link() 追加

verify に依存しない純粋な単体テスト対象。

**Steps:**
- [ ] `test_linkfmt.py` に `emit_javadoc_link` のテストを追加する（RED）
  - `emit_javadoc_link("UniversalDao", "javadoc-nablarch-common-dao-UniversalDao")` → `[UniversalDao](../javadoc/javadoc-nablarch-common-dao-UniversalDao.md)` を確認
  - `JAVADOC_LINK_RE` で生成リンクが検出できることを確認
  - `pytest tests/ut/test_linkfmt.py -q` → FAIL を確認
- [ ] `linkfmt.py` に `emit_javadoc_link()` / `JAVADOC_LINK_RE` を実装する（GREEN）
  - `pytest tests/ut/test_linkfmt.py -q` → 全 PASS を確認
  - `pytest tests/ut/ -q` → 全 PASS を確認（既存テスト無退行確認）
- [ ] コミット: `feat: add emit_javadoc_link / JAVADOC_LINK_RE to linkfmt.py (#363)`

### Task 2-B: verify.py — QO4: javadoc/ 除外

**Steps:**
- [ ] `test_verify.py` に QO4 javadoc 除外テストを追加する（RED）
  - `knowledge/javadoc/` 配下の JSON が QO4 対象外になること
  - `pytest tests/ut/test_verify.py -k qo4 -q` → FAIL を確認
- [ ] `verify.py` に QO4 除外を実装する（GREEN）
  - `pytest tests/ut/test_verify.py -q` → 全 PASS
  - `pytest tests/ut/ -q` → 全 PASS
- [ ] コミット: `feat: verify QO4 — exclude knowledge/javadoc/ from index.md coverage check (#363)`

### Task 2-C: verify.py — QL1: :java:extdoc: 検証

**Steps:**
- [ ] `test_verify.py` に QL1 javadoc チェックテストを追加する（RED）
  - 象限 1 (javadoc MD リンクあり) → PASS
  - 象限 2 (display text のみ) → FAIL (QL1)
  - 象限 2 (javadoc JSON ファイルなし) → FAIL (QL1)
  - `nablarch.*` 以外 (java.*) → チェック対象外（PASS）
  - method suffix 付き FQCN はクラスに正規化して判定
  - `pytest tests/ut/test_verify.py -k extdoc -q` → FAIL を確認
- [ ] `verify.py` に QL1 extdoc チェックを実装する（GREEN）
  - `pytest tests/ut/test_verify.py -q` → 全 PASS
  - `pytest tests/ut/ -q` → 全 PASS
  - `bash rbkc.sh verify 6` を実行 → **QL1 extdoc FAIL が増加することを確認（期待する RED）**
  - ベースライン FAIL 数を `.work/00363/verify-baseline.md` に記録する
- [ ] コミット: `feat: verify QL1 — check :java:extdoc: resolves to javadoc MD link (#363)`

### Task 2-D: jar 配置

**Steps:**
- [ ] `tools/rbkc/lib/` ディレクトリを作成する
- [ ] `/home/tie303177/work/source-to-document-converter/target/source-to-document-converter-0.0.1.jar` を `tools/rbkc/lib/` にコピーする
- [ ] `java -jar tools/rbkc/lib/source-to-document-converter-0.0.1.jar {サンプル.java}` で動作確認する（stdout に MD 出力）
- [ ] コミット: `chore: add source-to-document-converter-0.0.1.jar to tools/rbkc/lib/ (#363)`

### Task 2-E: javadoc.py — javadoc_generate() 実装

**Steps:**
- [ ] `test_javadoc.py` を新規作成し、各関数のテストを書く（RED）
  - `_extract_fqcns(rst_text)`: nablarch.* FQCN 抽出、method suffix 除去、java.* 除外
  - `fqcn_to_file_id(fqcn)`: FQCN → file_id 変換
  - `_class_fqcn(fqcn)`: method suffix 除去でクラス FQCN を返す
  - `_parse_javadoc_md(md_text)`: jar 出力 MD → JSON dict 変換（title/content/sections/id）
  - `pytest tests/ut/test_javadoc.py -q` → FAIL を確認
- [ ] `scripts/create/javadoc.py` を実装する（GREEN）
  - `pytest tests/ut/test_javadoc.py -q` → 全 PASS
  - `pytest tests/ut/ -q` → 全 PASS
  - UniversalDao.java を 1 件手動変換し、JSON が正しく生成されることを確認する
- [ ] コミット: `feat: add javadoc.py — Javadoc knowledge file generator (#363)`

### Task 2-G: rst_ast_visitor.py — :java:extdoc: 内部リンク化

visitor に `javadoc_map` パラメータを追加する。run.py の wiring より先に行う（run.py が visitor にマップを渡せるよう、受け口を先に作る）。

**Steps:**
- [ ] `test_rst_ast_visitor.py` に `:java:extdoc:` 内部リンクのテストを追加する（RED）
  - javadoc_map あり + nablarch.* → `[DisplayText](../javadoc/{file_id}.md)`
  - javadoc_map になし + nablarch.* → WARN を出して display text を返す
  - java.* / jakarta.* → WARN + display text
  - method suffix 付き FQCN はクラスで解決
  - `pytest tests/ut/test_rst_ast_visitor.py -k extdoc -q` → FAIL を確認
- [ ] `rst_ast_visitor.py` を実装する（GREEN）
  - `pytest tests/ut/test_rst_ast_visitor.py -q` → 全 PASS
  - `pytest tests/ut/ -q` → 全 PASS
- [ ] コミット: `feat: rst_ast_visitor — resolve :java:extdoc: as internal javadoc link (#363)`

### Task 2-H: rst_ast_visitor.py — :javadoc_url: 外部URL化

**Steps:**
- [ ] `test_rst_ast_visitor.py` に `:javadoc_url:` 外部リンクのテストを追加する（RED）
  - `:javadoc_url:\`DisplayText <path>\`` → `[DisplayText](path)`
  - `pytest tests/ut/test_rst_ast_visitor.py -k javadoc_url -q` → FAIL を確認
- [ ] `rst_ast_visitor.py` を実装する（GREEN）
  - `pytest tests/ut/ -q` → 全 PASS
- [ ] コミット: `feat: rst_ast_visitor — resolve :javadoc_url: as external link (#363)`

### Task 2-F: run.py — javadoc_generate() を create() 冒頭で呼び出す

visitor（2-G/2-H）が `javadoc_map` パラメータを受け取れる状態になってから行う。

**Steps:**
- [ ] `run.py` の `create()` に `javadoc_generate()` 呼び出しを追加し、返した `javadoc_map` を `_convert_and_write()` に渡す
  - テストは既存の run テストで `javadoc_map` が渡されることを確認（または新規テスト追加）
  - `pytest tests/ut/ -q` → 全 PASS
- [ ] コミット: `feat: run.py — call javadoc_generate() at start of create() (#363)`

### Task 2-I: index.py — javadoc/ 除外

**Steps:**
- [ ] `test_index.py`（または既存の index テスト）に javadoc/ 除外テストを追加する（RED）
  - `knowledge/javadoc/` 配下 JSON が index.md に含まれないこと
  - `pytest tests/ut/ -k index -q` → FAIL を確認
- [ ] `index.py` を実装する（GREEN）
  - `pytest tests/ut/ -q` → 全 PASS
- [ ] コミット: `fix: index.py — exclude knowledge/javadoc/ from index.md generation (#363)`

### Task 2-J: 全バージョン verify 確認

Task 2-C で記録したベースラインとの差分を確認する。

**Steps:**
- [ ] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` を実行し、FAIL 数とベースラインを比較する
  - 期待: QL1 extdoc FAIL が 0 件になること（Task 2-C の RED が GREEN になる）
  - 期待外の FAIL 増加があれば原因を特定して修正する
- [ ] v5 / v1.4 / v1.3 / v1.2 も同様に実行し、FAIL 増加なしを確認する
- [ ] 生成された知識ファイルを `.claude/skills/nabledge-6/` にコミットする

---

## Not Started

### Task 3: 検索フロー検証・改善
**前提**: Task 2-J 完了後
**Steps:**
- [ ] 「UniversalDao#existsの使い方」等の質問でJavadocリンクが実際に使われるか確認する
- [ ] 使われない場合は検索ワークフロー（qa.md / semantic-search.md）に明示的な手順を追加する

### Task 4: ベンチマークシナリオ追加
**前提**: Task 2-J 完了後
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
- [x] jarツール動作確認・設計方針合意
- [x] Task 1: 設計書更新 → ユーザー承認 — committed `12053d029` (設計書), `f771ecbfa` (未使用roleホワイトリスト削除ポリシー追加), `fb631766c` (nablarch.* scope)
- [x] 実装コミット (session 3-5) を revert — committed `f2dd8fc2a`
