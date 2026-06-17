# Goal

classes.md を使ったクラス名ベースのページ選定が qa-05（Jackson2BodyConverter を要する REST/JSON 実装質問）と qa-19 の正解率を改善することを、ベースラインとの比較で実証する。そのために v6 `semantic-search.md` を index.md + classes.md の2経路マージ設計に書き換え、効果測定を完了させる。

# Acceptance criteria

- v6 `semantic-search.md` が「index.md 10件 + classes.md 10件 → マージ・重複排除 → セクション選定 → 回答生成」の設計で動作する
- Step 4 ベースライン（qa-05: avg 1.000, qa-19: avg 0.130）と比較した改善・劣化が定量的に示されている
- 実行結果に裏取り（scenario_id / must / 中間記録）が添付されている
- 亜種ファイル（exp-semantic-search 等）を作らず v6 本体のみが変更されている

# Assumptions

- e2e-prompt / qa.md の Step 番号整合確認はユーザーから受け取る（未確認・BLOCKED）— Step 5 の前提条件
- qa-05: avg 1.000 / qa-19: avg 0.130（s2到達 1/10）が Step 4 ベースライン値（確定）
- benchmark は逐次実行（並列起動しない）

# Rules

- 1 task = 1 commit
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- 報告前に必ず敵対的レビュー（結果を自分で疑い実物で裏付け）
- 亜種ファイルを増やさず本体を直接変更
- 各タスク完了後にコミット・プッシュし、次タスク前に停止して報告

# Tasks

### #5: v6 semantic-search.md を直接書き換え ✅

**Purpose**: index.md 10件 + classes.md 10件 → 合計 20件 → セクション選定 → 回答生成 という設計をクリーンな semantic-search.md として実装する。

**Steps**:

- [x] e2e-prompt / qa.md の Step 番号整合確認（Phase A–E 接頭辞で衝突なし確認済み）
- [x] v6 `semantic-search.md` を直接書き換え（Phase A–E 構成）— commit `cc00ddbd0`
- [x] qa.md Step4 上限を 10→20 に変更 — commit `cc00ddbd0`

---

### #6: 変更後の検索で qa-05・qa-19 各 1 回実行・裏取り報告 ✅

**Purpose**: Step 5 の semantic-search.md 変更が設計通り動くか確認する。

**Steps**:

- [x] qa-05・qa-19 を各 1 回実行 — `step6-classes-v6-1run/run-1`
- [x] 裏取り完了（adapter s2 到達 Yes, Jackson2BodyConverter 出現 Yes, qa-05 退行なし）
- [x] コミット・プッシュ — commit `250351e18`

**Results**:
- qa-19: correctness=1.0, adapter `adapters-jaxrs-adaptor.json:s2` 到達（Phase B=classes.md 由来）, read_sections=9件
- qa-05: correctness=1.0, must 到達, read_sections=7件（退行なし）
- コスト増: qa-05 +$0.234 / qa-19 +$0.244（ページ読み取り増加に伴う）

---

### #7: classes.md 追加状態で qa-05・qa-19 × 各 10 回・裏取り報告 ✅

**Purpose**: classes.md 効果を Step 4（ベースライン）と比較して定量評価する。

**Prerequisites**: #6 完了

**Steps**:

- [x] qa-05・qa-19 を各 10 回実行
- [x] 裏取り（scenario_id・must・各ステップ記録）
- [x] Step 4 ベースライン（qa-05: avg 1.000 / qa-19: avg 0.130）と比較
- [x] self-check（完了基準を OK/NG で確認、checks/task-7.md に記録）
- [x] QA expert review（subagent）
- [x] user review

**Completion criteria**:

- qa-05・qa-19 各 10 回の実行結果と裏取りが揃っている
- Step 4 ベースラインとの定量比較（avg correctness、s2到達率）が示されている

# Decisions

## D-1: classes.md 設計方針（完了）
- **Issue**: クラス名ベースのページ選定をどう実現するか
- **Conclusion**: index.md と並列の classes.md を RBKC で生成し、2経路マージ
- **Rationale**: headings への class 名埋め込みはノイズ増加リスクがあり、独立ファイルが安全
- **Evidence**: Task 1〜8 の実装・ベンチマーク結果（95.8%、PR-caused regression: 0件）
- **Sources**: .work/00368/tasks.md Done セクション

## D-2: 実験経緯（完了）
- **Issue**: 単純マージでは qa-05 の adapter 選出率が低い（条件P: 1/10）
- **Conclusion**: semantic-search.md の書き換えで設計を確定させ、効果測定を行う
- **Rationale**: 実験A〜P（Task 12〜22）を経て、2経路マージの基本設計は維持しつつ実装をクリーンにする方針に落ち着いた
- **Evidence**: Task 15（条件20: 10/10）、Task 22（条件P: 1/10）等の実験結果
- **Sources**: .work/00368/tasks.md 過去の実験結果サマリー

### #8: 上限12適用後 qa-05・qa-19 × 各 10 回・裏取り報告

**Purpose**: Phase D 上限 20→12 の変更が正確率・adapter s2 到達率に退行をもたらさないことを実測で確認する。

**Prerequisites**: #7完了（Step7結果 qa-05:avg1.000 / qa-19:avg0.967、s2到達9/9が基準値）

**Steps**:

- [x] 編集3点適用・commit (`d8364e4c8` 適用済み)
- [x] qa-05・qa-19 を各 10 回実行（結果: `step8-limit12-v6-10runs`）
- [x] 裏取り（qa-19 s2到達率・correctness・cost/time・read_sections分布をStep7と比較）
- [x] self-check（checks/task-8.md 作成）
- [x] QA expert review（subagent）
- [x] user review（実験A指示を受領 → #9 に反映）

**Completion criteria**:

- qa-05・qa-19 各 10 回の実行結果が揃っている
- Step7（上限20）との定量比較（s2到達率・correctness・cost・time・read_sections）が示されている
- qa-19 s2到達率が Step7（9/9）から退行していない（退行時は報告して停止）

### #9: 実験A — 上限20 vs 上限12 の影響分離（qa-19 各20回）

**Purpose**: 上限12適用後 qa-19 correctness 0.7 発生が1→3回に増えたことが、上限変更の影響かばらつきかを n=20 で分離する。

**Prerequisites**: #8 完了

**Steps**:

- [x] `git fetch origin pull/369/head` で最新取得
- [x] 条件1（上限12・現状のまま）: qa-19 × 20 回実行 → `tools/benchmark/results/expA-limit12/run-{i}/`
- [x] 条件2（上限20・一時変更）: semantic-search.md + qa.md を上限20に変更 → qa-19 × 20 回実行 → `tools/benchmark/results/expA-limit20/run-{i}/`
- [x] 一時変更を破棄（`git checkout -- ...` で上限12復元・確認）
- [x] 裏取り（correctness分布・s2到達率・read_sections・減点回reason全文・cost/time）
- [x] self-check（checks/task-9.md 作成）
- [x] 報告

**Completion criteria**:

- 条件1・条件2 それぞれ有効20回（TIMEOUT再実行含む）の実行結果が揃っている
- correctness分布（1.0/0.8/0.7/その他 回数・平均）・s2到達率・read中央値/最大・cost/time が2条件並べて示されている
- correctness<1.0 の全回について evaluation.json の answer_correctness.reason 全文が列挙されている
- 実験後、上限12コミット済み状態（d8364e4c8）に戻っていることが確認されている

**Constraints**:

- 上限20変更をコミットしない（一時変更・実験後必ず破棄）
- 既存ベンチ結果（baseline-current/step6/7/8）を変更・削除しない
- correctness の合否・FAIL判定をしない（reason全文報告まで）
- 他バージョンのスキルを触らない

### #10: 上限20復元 + 全34シナリオフルベンチ（3run）+ 判定材料抽出

**Purpose**: 実験A結果（上限12に利得なし）を受け、上限12→20へ戻す。その状態で全34シナリオのフルベンチを実行し、ベースライン（`20260612-1404-baseline-current`）との比較で退行を検出する判定材料を抽出する。

**Prerequisites**: #9 完了（実験A結果確定・ユーザー判定受領）

**Steps**:

- [x] 上限12→20へ戻す（semantic-search.md + qa.md 2箇所）・確認・コミット — `3ce7730fb`
- [x] qa.json 全34シナリオ × 3run 実行 → `tools/benchmark/results/fullbench-classes-v6/run-{1,2,3}/`
- [x] TIMEOUT再実行（run-1: qa-04/08/19/21, run-3: qa-02 を再実行・エラーゼロ確認）— `6cdecee3f`
- [x] 結果コミット (`chore: save fullbench-classes-v6`) — `6bfdf9a63` + `6cdecee3f`
- [x] 裏取り: ベースライン比較表（共通34シナリオ、3run平均、退行フラグ付き）— 下記参照
- [x] 裏取り: correctness<1.0 全件のreason全文 — 下記参照
- [x] 裏取り: qa-01 / qa-19 の到達改善確認（read_sectionsに特定keyが入るか全run明示）— 下記参照
- [x] 裏取り: コスト・時間サマリ（baseline avg$0.733比較）— 下記参照
- [x] 報告 — 2026-06-17 ユーザーへ判定材料提示済み

**Completion criteria**:

- 上限20復元が確認されている（grep出力添付）
- 全34シナリオ × 3run の結果が `fullbench-classes-v6` に揃っている（error.jsonは再実行後も失敗の場合のみ残存・報告）
- ベースライン比較表（共通28シナリオ）に退行フラグが付いている
- correctness<1.0 の全件について reason全文が省略なく記載されている
- qa-01: read_sections に `libraries-universal-dao.json:s9` が入るか 3run 全て明示
- qa-19: adapter:s2 到達と correctness を 3run 全て明示

**Constraints**:

- 合否・FAIL・退行の最終判定をしない（材料を出すまでがCCの仕事）
- 既存ベンチ結果（baseline-current/step6/7/8/expA）を変更・削除しない
- 他バージョンのスキルを触らない
- reason を要約・取捨選択しない（閾値割れは1件残らず全文）

### #12: 全バージョン × 全入口スモークテスト

**Purpose**: semantic-search.md を全5バージョンに展開後、各入口（QA/semantic-search/keyword-search/code-analysis）が正常完了するかを確認する。特に v1.4/1.3/1.2 は classes.md が空（"_No class index available_"）なので Phase B が候補なしで正常フローするかを重点確認。

**Prerequisites**: #11 完了（最新ブランチ展開済み）

**Steps**:

- [ ] 各バージョンの代表クラス確認（v6: UniversalDao, v5: UniversalDao, v1.4/1.3/1.2: classes.md 空のためどのクラスでも Phase B 空通過）
- [ ] 20通り実行（5バージョン × 4入口 = 20回）
- [ ] 結果記録（checks/task-12.md に OK/異常 をバージョン×入口マトリクスで）
- [ ] 報告

**Completion criteria**:

- 全20通りについて OK/異常が記録されている
- v1.4/1.3/1.2 の semantic-search / QA で Phase B が空 classes.md を「候補なし」で正常通過したことが確認されている
- 異常があれば内容（エラーメッセージ等）が全文記載されている

**Constraints**:

- スキルファイル（semantic-search.md 等）を変更しない（実行のみ）
- 異常を勝手に修正しない（報告して停止）

---

### #11: fullbench-classes-v6 レポート3種生成 + HOW-TO-RUN.md 手順固定

**Purpose**: report.md（既存）・regression-check.md（baseline差分）を3run分生成し、REPORTS-INDEX.md で目次化。HOW-TO-RUN.md にレポート生成手順を追記して再現性を仕組み化する。

**Prerequisites**: #10 完了

**Steps**:

- [x] regression-check.md を3run分生成（baseline: `20260612-1404-baseline-current/baseline.json`）
- [x] REPORTS-INDEX.md 作成
- [x] HOW-TO-RUN.md に手順追記
- [x] self-check（計7ファイル存在確認・regression verdict転記・HOW-TO-RUN.md追記確認）
- [x] コミット・プッシュ — `ae92f88b1`

**Completion criteria**:

- run-1/2/3 それぞれに report.md と regression-check.md がある（計6ファイル、report.mdは既存）
- REPORTS-INDEX.md が fullbench-classes-v6/ 直下にある
- HOW-TO-RUN.md に「ベンチ後のレポート生成（必須・3種）」セクションが追記されている
- report.py 自体は変更なし

# State

- **Status**: paused
- **Date**: 2026-06-17
- **Last completed**: #12 完了。全5バージョン × 4入口 = 20/20 OK。v1.4/1.3/1.2 Phase B 空通過確認済み。commit `4f6089b8a`
- **Next**: #12 完了により全タスク完了。PR #369 の Acceptance criteria を確認してマージ判断を仰ぐ。
- **Notes**: PR #369 OPEN (branch: 368-classes-md-for-class-search)。
  全タスク完了済み。次は Acceptance criteria 確認 + ユーザーへの最終報告。
