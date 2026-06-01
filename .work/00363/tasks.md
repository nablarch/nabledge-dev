# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-06-02

## Rules（全タスク共通）

- 1コミット = 1タスク
- 推測せず事実ベースで作業・判断する（実物・全件を確認し、確認範囲を明示する）
- RBKC の create/verify を変更する場合は実装前に設計書を更新してユーザーに確認する
- 各タスクは TDD 順（RED → GREEN）。1タスク=1コミット
- 1タスク完了後に必ず `python -m pytest tests/ut/ -q`（`tools/rbkc/` で実行）を行い全 GREEN を確認してからコミットする
- 統合 verify を変化させるタスクは、完了時に検知ゲートで FAIL 集合の差分を確認する

## 検知設計

QL1（2-C）有効化後、パイプライン（2-E〜2-I）完成まで `rbkc.sh verify` は意図的に FAIL する。本物の FAIL を見落とさないため:
1. 2-C2 で extdoc FAIL を FQCN 全件 + 他カテゴリ0件で `.work/00363/verify-baseline.md` に固定
2. 2-J で FAIL 集合を取得し、照合A（ベースラインの extdoc 全件消滅）+ 照合B（ベースライン外0件）で判定

設計書: `tools/rbkc/docs/rbkc-converter-design.md` §5-1 / §5-2、`rbkc-verify-quality-design.md` §3-2-3 / §3-3

---

## In Progress

### Task 2-A: linkfmt.py — emit_javadoc_link() 追加
- **前提**: なし
- **完了条件**: `emit_javadoc_link` / `JAVADOC_LINK_RE` 実装、単体テスト GREEN、既存無退行
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS

- [ ] `tests/ut/test_linkfmt.py` にテスト追加（RED）
  - `emit_javadoc_link("UniversalDao", "javadoc-nablarch-common-dao-UniversalDao")` → `[UniversalDao](../javadoc/javadoc-nablarch-common-dao-UniversalDao.md)`
  - `JAVADOC_LINK_RE` で生成リンクが検出できること
  - `pytest tests/ut/test_linkfmt.py -q` → FAIL
- [ ] `scripts/common/linkfmt.py` に実装（GREEN）→ `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `feat: add emit_javadoc_link / JAVADOC_LINK_RE to linkfmt.py (#363)`

### Task 2-B: verify.py — QO4: javadoc/ 除外
- **前提**: なし
- **完了条件**: `knowledge/javadoc/` 配下 JSON が QO4 網羅性チェック対象外、単体テスト GREEN
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS

- [ ] `tests/ut/test_verify.py`（`TestCheckIndexCoverage`）に QO4 javadoc 除外テスト追加（RED）
  - `pytest tests/ut/test_verify.py -k IndexCoverage -q` → FAIL
- [ ] `scripts/verify/verify.py` に除外を実装（既存 `assets` 除外と同型で `javadoc` を追加）（GREEN）→ `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `feat: verify QO4 — exclude knowledge/javadoc/ from index.md coverage check (#363)`

### Task 2-C: verify.py — QL1: :java:extdoc: 検証（単体テストのみ）
- **前提**: Task 2-A
- **完了条件**: QL1 extdoc 検証ロジック実装、単体テスト RED→GREEN 固定
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS。**統合 verify の実行・ベースライン記録は本タスクで行わない**（2-C2 で行う）

- [ ] `tests/ut/test_verify.py`（`TestCheckSourceLinks_JsonSide`）に QL1 extdoc テスト追加（RED）
  - 象限1（javadoc MD リンクあり）→ PASS / 象限2（display text のみ）→ FAIL (QL1) / 象限2（javadoc JSON 不在）→ FAIL (QL1)
  - java.* / jakarta.* → 対象外（PASS）
  - method suffix 付き FQCN はクラスに正規化して判定
  - `pytest tests/ut/test_verify.py -k extdoc -q` → FAIL
- [ ] `scripts/verify/verify.py` に QL1 extdoc チェック実装（GREEN）→ `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `feat: verify QL1 — check :java:extdoc: resolves to javadoc MD link (#363)`

### Task 2-C2: QL1 ベースライン全件記録
- **前提**: Task 2-C
- **完了条件**: QL1 起因 extdoc FAIL を FQCN 全件、`.work/00363/verify-baseline.md` に固定
- **検知ゲート**: この時点の FAIL がすべて QL1 extdoc 起因（QC/QO/QP の混入0件）。混入があれば 2-A/2-B/2-C にバグ → 止める

- [ ] `bash rbkc.sh verify 6` を実行（create は走らせず現行 knowledge/ に対し verify のみ）
- [ ] FAIL を全件抽出し `.work/00363/verify-baseline.md` に記録
  - QL1 extdoc FAIL の対象 FQCN を1件残らず列挙（サマリ件数ではなく全件）
  - QL1 以外のカテゴリ FAIL が0件であることを明記
- [ ] コミット: `docs: record QL1 extdoc verify baseline before pipeline (#363)`

### Task 2-D: jar 復元（環境非依存）
- **前提**: なし
- **完了条件**: `tools/rbkc/lib/source-to-document-converter-0.0.1.jar` が追跡され `java -jar` で動作
- **検知ゲート**: `git ls-files tools/rbkc/lib/` に jar が出る。`java -jar ... {サンプル.java}` が stdout に MD を出す
- **指示**: ローカル絶対パスからの cp は禁止。過去コミットから復元する

- [ ] `git checkout ff6108c9 -- tools/rbkc/lib/source-to-document-converter-0.0.1.jar`
- [ ] `git ls-files tools/rbkc/lib/` で追跡確認
- [ ] `java -jar tools/rbkc/lib/source-to-document-converter-0.0.1.jar {サンプル.java}` で stdout に MD 出力を確認
- [ ] コミット: `chore: restore source-to-document-converter-0.0.1.jar to tools/rbkc/lib/ (#363)`

### Task 2-E: javadoc.py — javadoc_generate() 実装（JSON + docs MD 両方）
- **前提**: Task 2-A、Task 2-D
- **完了条件**: `javadoc_generate()` と補助関数の単体テスト GREEN。UniversalDao 1件を手動変換し JSON（knowledge/javadoc/）と docs MD（docs/javadoc/）の両方が生成される
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS。手動変換1件で JSON が `id/title/content/sections` を満たし、同 file_id の docs MD が生成される
- **指示**: docs MD 生成は `javadoc_generate` の責務（手順6）。汎用 `generate_docs()` には生成させない（2-I で除外）

- [ ] `tests/ut/test_javadoc.py` を新規作成（RED）
  - `_extract_fqcns(rst_text)`: nablarch.* 抽出 / method suffix 除去 / java.* 除外
  - `fqcn_to_file_id(fqcn)`: FQCN → file_id
  - `_class_fqcn(fqcn)`: method suffix 除去でクラス FQCN
  - `_parse_javadoc_md(md_text)`: jar 出力 MD → JSON dict（title/content/sections/id）
  - `pytest tests/ut/test_javadoc.py -q` → FAIL
- [ ] `scripts/create/javadoc.py` を実装（GREEN）。手順5（JSON 書き込み）と手順6（docs MD 書き込み）を両方含む
  - `pytest tests/ut/ -q` 全 PASS
  - UniversalDao.java を1件手動変換し JSON と docs MD の両方が生成されることを確認
- [ ] コミット: `feat: add javadoc.py — Javadoc knowledge file generator (#363)`

### Task 2-G: rst_ast_visitor.py — :java:extdoc: 内部リンク化
- **前提**: Task 2-A（run.py 配線 2-F より前に visitor の受け口を作る）
- **完了条件**: visitor が `javadoc_map` を受け取り象限別に内部リンク / WARN+display を返す。単体テスト GREEN
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS

- [ ] `tests/ut/test_rst_ast_visitor.py` に extdoc テスト追加（RED）
  - javadoc_map あり + nablarch.* → `[DisplayText](../javadoc/{file_id}.md)`
  - javadoc_map になし + nablarch.* → WARN + display text
  - java.* / jakarta.* → WARN + display text
  - method suffix 付き FQCN はクラスで解決
  - `pytest tests/ut/test_rst_ast_visitor.py -k extdoc -q` → FAIL
- [ ] `scripts/common/rst_ast_visitor.py` に `javadoc_map` パラメータを追加して実装（GREEN）→ `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `feat: rst_ast_visitor — resolve :java:extdoc: as internal javadoc link (#363)`

### Task 2-H: rst_ast_visitor.py — :javadoc_url: 外部URL化
- **前提**: Task 2-G
- **完了条件**: `:javadoc_url:` が外部リンクに変換され単体テスト GREEN
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS

- [ ] `tests/ut/test_rst_ast_visitor.py` に javadoc_url テスト追加（RED）
  - `:javadoc_url:\`DisplayText <path>\`` → `[DisplayText](path)`
  - `pytest tests/ut/test_rst_ast_visitor.py -k javadoc_url -q` → FAIL
- [ ] `scripts/common/rst_ast_visitor.py` を実装（GREEN）→ `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `feat: rst_ast_visitor — resolve :javadoc_url: as external link (#363)`

### Task 2-F: run.py — javadoc_generate() 配線（create + update 両方）
- **前提**: Task 2-E、Task 2-G/2-H
- **完了条件**: `create()` と `update()` の冒頭で `javadoc_generate()` を呼び、`javadoc_map` を `_convert_and_write` 経由で RST コンバータに渡す。単体テスト GREEN
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS

**必須変更（この通りに。該当箇所は grep で再確認すること）:**
1. `_convert_and_write` のシグネチャに `javadoc_map=None` を追加
   - After: `def _convert_and_write(fi, output_dir, label_map=None, doc_map=None, sheet_subtype_map=None, javadoc_map=None) -> None:`
2. RST 分岐の `convert(...)` 呼び出しに `javadoc_map=javadoc_map` を追加。**MD・xlsx 分岐は変更しない**
3. `create()` 内の `_convert_and_write(...)` 呼び出しに `javadoc_map` を追加
4. `update()` 内の `_convert_and_write(...)` 呼び出しにも `javadoc_map` を追加（**両方必須**）
5. `create()` と `update()` の冒頭（scan より前）で `javadoc_map = javadoc_generate(version)` を呼ぶ

- [ ] 上記1〜5を実装。`tests/ut/test_run.py` で `javadoc_map` が RST convert に渡ること、create/update 双方で `javadoc_generate` が呼ばれることを確認
  - `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `feat: run.py — wire javadoc_generate() into create() and update() (#363)`

### Task 2-I: docs.py + index.py — javadoc/ 二重生成・登録除外
- **前提**: Task 2-F
- **完了条件**: `knowledge/javadoc/` 配下 JSON が (a) index.md に含まれない（index.py）、(b) generate_docs の走査対象から除外される（docs.py）。両方の単体テスト GREEN
- **検知ゲート**: `pytest tests/ut/ -q` 全 PASS

- [ ] `tests/ut/test_index.py` に javadoc 除外テスト追加（RED）— index.md に含まれないこと
- [ ] `tests/ut/test_docs.py` に javadoc 除外テスト追加（RED）— generate_docs が docs MD 化しないこと（既存 `assets` 除外と同型の判定）
  - `pytest tests/ut/ -k "index or docs" -q` → FAIL
- [ ] `scripts/create/index.py` と `scripts/create/docs.py` に除外を実装（GREEN）→ `pytest tests/ut/ -q` 全 PASS
- [ ] コミット: `fix: exclude knowledge/javadoc/ from index.md and generate_docs (#363)`

### Task 2-J: 統合 verify 確認（ベースライン照合）
- **前提**: Task 2-I + Task 2-C2 のベースライン
- **完了条件**: v6 を create→verify し QL1 extdoc FAIL 0 件、ベースライン外の新規 FAIL 0 件。他バージョンも FAIL 増加なし。生成知識をコミット
- **検知ゲート**: 照合A（ベースラインの extdoc 全件解決）+ 照合B（ベースライン外0件）。照合B で FAIL が出たら原因タスクを特定し 2-x に戻る

- [ ] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` を実行し FAIL 集合を取得
- [ ] 照合A: ベースラインの extdoc FQCN 全件解決を確認（QL1 extdoc FAIL = 0）
- [ ] 照合B: ベースライン外 FAIL 0 件を確認。差分を `.work/00363/verify-2j-diff.md` に記録
- [ ] v5 / v1.4 / v1.3 / v1.2 も `create && verify` し FAIL 増加なしを確認
- [ ] 生成知識を `.claude/skills/nabledge-6/` にコミット
- [ ] コミット: `feat: regenerate v6 knowledge with javadoc files (#363)`

---

## Not Started

### Task 3: 検索フロー検証・改善
- **前提**: Task 2-J 完了
- **完了条件**: Javadoc 参照質問で javadoc リンクが検索フローで使われることを確認。使われなければワークフローに手順追加
- [ ] 「UniversalDao#exists の使い方」等で Javadoc リンクが使われるか確認
- [ ] 使われない場合は qa.md / semantic-search.md に明示手順を追加

### Task 4: ベンチマークシナリオ追加
- **前提**: Task 2-J 完了
- **完了条件**: Javadoc 参照を要する新規シナリオ追加 + expectations 設定。既存シナリオが javadoc 非参照と確認済み
- [ ] 既存シナリオで Javadoc 知識ファイルが参照されないことを確認
- [ ] Javadoc 参照質問のシナリオを新規追加
- [ ] 期待値（expectations）を設定

### Task 5: v6 検証（新シナリオ1件 → 既存スコア確認）
- **前提**: Task 3 / 4 完了
- **完了条件**: 新シナリオ正答 + 既存スコア低下なし（逐次実行）
- [ ] 新シナリオ1件を v6 で実行し正答を確認
- [ ] v6 既存ベンチマークを実行しスコア低下なしを確認（逐次実行）
- [ ] 問題あれば Task 2 に戻って修正

### Task 6: 差分チェック + PR レビュー依頼
- **前提**: Task 5 完了
- **完了条件**: 全変更差分が想定どおりと記録、Expert review 通過、PR 更新
- [ ] `git diff main...HEAD --stat` で変更ファイルを全件確認
- [ ] 想定外変更がないかをチェックし `.work/00363/diff-check.md` に記録
- [ ] ユーザーに確認依頼
- [ ] Expert review（Software Engineer + QA Engineer）
- [ ] PR を更新

---

## Done

- [x] `.work/00363/tasks.md` と `notes.md` 作成 — `521ac200d`
- [x] PR #365 作成
- [x] jar ツール動作確認・設計方針合意
- [x] Task 1: 設計書更新 → ユーザー承認 — `12053d029` / `f771ecbfa` / `fb631766c`
- [x] 実装コミット（session 3-5）を revert — `f2dd8fc2a`
