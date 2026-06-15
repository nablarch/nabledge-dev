# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
**Issue**: #368
**Updated**: 2026-06-15 (session 14)

## In Progress

### Step 5: v6 semantic-search.md を直接書き換え

**目的**: index.md 10件 + classes.md 10件 → 合計 20件 → セクション選定 → 回答生成 という設計をクリーンな semantic-search.md として実装する。

**制約**:
- 亜種（exp-semantic-search 等）を作らず v6 本体を直接書き換える
- 全ステップ番号を振り直したクリーンな構成にする
- e2e-prompt / qa.md の「Step スキップ」指示との番号整合を取る（番号衝突禁止）
- 整合確認はレビュアー（ユーザー）が実物で確認して設計を渡す

**Steps:**
- [BLOCKED: e2e-prompt / qa.md の Step 番号整合確認をユーザーから受け取る]
- [ ] v6 `semantic-search.md` を直接書き換え（全ステップ番号振り直し）
- [ ] コミット・プッシュし停止して報告

---

### Step 6: 変更後の検索で qa-05・qa-19 各 1 回実行・裏取り報告

**目的**: Step 5 の semantic-search.md 変更が設計通り動くか確認する。

**裏取り確認項目**: 測定が設計通り動いたか・scenario_id・must・中間記録

**Steps:**
- [ ] qa-05・qa-19 を各 1 回実行
- [ ] 裏取り（測定が設計通り動いたか、scenario_id・must・中間記録）
- [ ] 結果＋裏取りをセットで報告し停止
- [ ] コミット・プッシュ

---

### Step 7: classes.md 追加状態で qa-05・qa-19 × 各 10 回・裏取り報告

**目的**: classes.md 効果を Step 4（ベースライン）と比較する。

**Steps:**
- [ ] qa-05・qa-19 を各 10 回実行
- [ ] 裏取り（scenario_id・must・各ステップ記録）
- [ ] Step 4（ベースライン）と比較
- [ ] 結果＋裏取りをセットで報告
- [ ] コミット・プッシュ

---

## Done (this session)

### フルベースライン取得 (34シナリオ × 3run) — committed `bed4b930c`

- 3 run完了（run-1〜run-3、各34シナリオ）
- 既知スキル挙動問題: qa-17、qa-19（review-06 は評価器の誤検出と確定。回答はナレッジと一致、flaky吸収）
- baseline.json生成済み（stable 9/34、flaky 25/34）、退行検出可能

### Step 3後半: qa-05・qa-19 各1回実行・裏取り報告 ✅ — committed `20260612-115048`

---

### Step 1: 実験ゴミ一掃・リバート — committed `5c7634c84`

- classes.md(5件) + tools/rbkc + .work/00368/tasks.md のみが origin/main との差分になるよう整理
- benchmark/results を origin/main の7エントリに復元
- 実験亜種プロンプト・スクリプト・結果ディレクトリを全削除

---

### Step 2: qa.json に 2 シナリオ反映 — committed `2ceeee364` ✅

- qa-05: input 修正（誘導文削除）、must を Form+String型 の2つに、Converter を acceptable に移動
- qa-19: 末尾に追加、input は qa-05 と同一、purpose=「仕組み・動作を理解したい」、must=Jackson2BodyConverter(s2)

---

### Step 3前半: evaluate.py 改修 + マーカー化 cherry-pick — committed `a042301e4`, `8efacba3f` ✅

- evaluate.py: `purpose` + `expected_facts` を evaluation.json に記録（採点 must の取り違え検出用）
- e2e-prompt.md: `<<<WORKFLOW_DETAILS_JSON>>>` / `<<<END_WORKFLOW_DETAILS>>>` マーカー化再適用（cherry-pick 5a19d445）
- run_qa.py: マーカーベースパースに対応済み
- test_run_qa.py: 57 passed GREEN

---

### Step 4: classes.md なし状態で qa-05・qa-19 × 各 10 回（ベースライン） ✅

- [x] qa-05・qa-19 を各 10 回実行（`baseline-no-classes/`）
- [x] 裏取り完了（markers 全20 OK, scenario_id/purpose/expected_facts 全正）
- [x] 結果＋裏取り報告（qa-05: avg 1.000 / qa-19: avg 0.130, s2到達 1/10）
- [x] コミット・プッシュ `272820720`

---

### Step 5: v6 semantic-search.md を直接書き換え

**目的**: index.md 10件 + classes.md 10件 → 合計 20件 → セクション選定 → 回答生成 という設計をクリーンな semantic-search.md として実装する。

**制約**:
- 亜種（exp-semantic-search 等）を作らず v6 本体を直接書き換える
- 全ステップ番号を振り直したクリーンな構成にする
- e2e-prompt / qa.md の「Step スキップ」指示との番号整合を取る（番号衝突禁止）
- 整合確認はレビュアー（ユーザー）が実物で確認して設計を渡す

**Steps:**
- [ ] [BLOCKED: e2e-prompt / qa.md の Step 番号整合確認をユーザーから受け取る]
- [ ] v6 `semantic-search.md` を直接書き換え（全ステップ番号振り直し）
- [ ] コミット・プッシュし停止して報告

---

### Step 6: 変更後の検索で qa-05・qa-19 各 1 回実行・裏取り報告

**目的**: Step 5 の semantic-search.md 変更が設計通り動くか確認する。

**裏取り確認項目**: 測定が設計通り動いたか・scenario_id・must・中間記録

**Steps:**
- [ ] qa-05・qa-19 を各 1 回実行
- [ ] 裏取り（測定が設計通り動いたか、scenario_id・must・中間記録）
- [ ] 結果＋裏取りをセットで報告し停止
- [ ] コミット・プッシュ

---

### Step 7: classes.md 追加状態で qa-05・qa-19 × 各 10 回・裏取り報告

**目的**: classes.md 効果を Step 4（ベースライン）と比較する。

**Steps:**
- [ ] qa-05・qa-19 を各 10 回実行
- [ ] 裏取り（scenario_id・must・各ステップ記録）
- [ ] Step 4（ベースライン）と比較
- [ ] 結果＋裏取りをセットで報告
- [ ] コミット・プッシュ

---

## 共通規律

- 報告前に必ず敵対的レビュー（結果を自分で疑い実物で裏付け）
- 亜種ファイルを増やさず本体を直接変更
- 各ステップでコミット・プッシュし、次ステップ前に停止して報告



## Rules

- 1コミット = 1タスク
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- SCを満たすようタスクを分割し、タスクリストを作業記録に出力する
- タスクリストをコミットし、PRを作成する
- PR上でIssueの目的とタスクリストの対応関係を示し、ユーザーに確認を依頼する
- 承認後、1コミット = 1タスクで各タスクを実装する
- RBKCのcreate/verifyを変更するため: 実装前に設計を行い、設計書・verify設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

## Done

- [x] Task 0: タスクリスト作成・PR作成・ユーザー確認 — committed `5ff81b145`
- [x] Task 1: 設計書更新 (classes-md-spec.md, rbkc-verify-quality-design.md QO5) — committed `0dd249d45`
- [x] Task 2: TDD — test_classes.py 作成 (RED) — committed `ac7f7a1f8`
- [x] Task 3: TDD — TestCheckClassesCoverage を test_verify.py に追加 (RED) — committed `4c04146f5`
- [x] Task 4: 実装 — classes.py (generate_classes_md) — committed `fc35cabf4`
- [x] Task 5: 実装 — verify.py (check_classes_coverage) — committed `b1ab38c53`
- [x] Task 6: run.py 統合 (generate_classes_md + check_classes_coverage) — committed `e3da286b8`
- [x] Task 7: v6 classes.md 生成、FAIL 0 確認 — committed `40d313761`
- [x] Task 8: semantic-search.md パッチ1〜3 全5バージョン適用 — committed `f75480b40`
- [x] Task 10: 全バージョン RBKC 展開 (v5/v1.4/v1.3/v1.2) FAIL 0 確認 — committed `d89204139`
- [x] Task 9: ベンチマーク実行 — 全33シナリオ 95.8% (regression なし) — committed `0f702f7ba`
- [x] Task 11: ベンチマーク詳細分析 + qa-11a 5回再実行 (5/5=1.0、単発ブレ確定) — committed `ce20c5dac`
- [x] PR #369 body 更新 (benchmark-results.md リンク + SC最終状態)
- [x] Task 12: ベンチマーク再実行 (HOW-TO-RUN 手順通り) + qa-05 根本原因調査 — committed `e4ca8a50c`
- [x] Task 13: 実験A（classes.md索引比較）+ 実験B（ページ上限40）— committed `5ac667383`
- [x] Task 14: 実験C — 条件M（独立2経路マージ）qa-05×3 + 回帰4本 — committed `5ac667383`
- [x] Task 15: 実験D — 条件20（関門1: 両経路20件）qa-05×10 → 10/10 adapter含有 — committed `fd3dbc052`
- [x] Task 16: 実験E — 条件S（3段階判定）qa-05×10 → 2/10 adapter含有 — committed `84edd9cc7`
- [x] Task 17: 実験F — 条件5step（両経路20件マージ）qa-05×10 + 他4シナリオ × 各1回 — committed `6b72072fb`
- [x] Task 18: 実験G — 条件5step v2（e2e経路）qa-05×10 → 2/10 adapter含有（検証ゲート失敗）— committed `f2a004c1e`
- [x] Task 19: 実験H — exp-purpose-classes（条件N/C × qa-05/qa-05b × 10回）— committed `327e681f7`
- [x] Task 20: 実験P — 条件P × qa-05b × 10回 — committed `07689cc8e`
- [x] Task 21: 実験P revised — qa-05/qa-05b input統一 × 各10回 + Task 21 qa.json更新 — committed `216262340`
- [x] Task 22 (partial): qa-05b must絞り込み版 × 10回実行・結果保存 — committed `c0c06dacc`

---

## 過去の実験結果サマリー（参照用）

### Task 22: 実験P qa-05b must絞り込み版 × 10回

**経緯**: qa-05b の must を s2 のみ（Jackson2BodyConverter担当）に絞り、s4（MIME拡張）を acceptable に格下げ。前回 s2到達5回が全て correctness=0.5 だったのは must2 が質問範囲外だったため。

**集計結果**（条件P構成、10回）:
| 試行 | index | classes | merged | adapter選出 | s2到達 | correctness |
|------|-------|---------|--------|------------|--------|-------------|
| run-01 | 3 | 2 | 5 | なし | × | 0.0 |
| run-02 | 6 | 0 | 6 | なし | × | 0.0 |
| run-03 | 6 | 0 | 6 | なし | × | 0.0 |
| run-04 | 6 | 3 | 6 | なし | × | 0.8 |
| run-05 | 6 | 4 | 6 | なし | × | 0.0 |
| run-06 | 6 | 4 | 6 | なし | × | 1.0 |
| run-07 | 5 | 3 | 5 | なし | × | 1.0 |
| run-08 | 6 | 4 | 6 | なし |× | 0.0 |
| run-09 | 8 | 0 | 8 | あり | ○ | 1.0 |
| run-10 | 5 | 0 | 5 | なし | × | 0.0 |
| **集計** | | | | **1/10** | **1/10** | **avg: 0.380** |

詳細: `tools/benchmark/results/exp-cond-p-qa05b-revised/results.md`

**特記事項**:
- s2到達（run-09 のみ）: correctness=1.0 — 「s2到達→1.0」成立を確認
- adapter選出率 1/10（前回同条件で 5/10）— セッション間の揺らぎ
- s2非到達でも 3/10 が correctness≥0.8 — adapterページを読まずに Jackson2BodyConverter を言及（handlers-body-convert-handler.json 内の記述 or LLM事前知識）
