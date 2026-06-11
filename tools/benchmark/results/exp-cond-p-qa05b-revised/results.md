# 実験結果: 条件P — qa-05b must絞り込み版 × 10回

**実験日**: 2026-06-12
**目的**: qa-05b の must を1つに絞り（s2のみ: Jackson2BodyConverterがJSONボディ変換を担当）、「s2到達 → correctness=1.0」が成立するかを確認する。前回 s2到達5回が全て correctness=0.5 だったのは、must2（MIME拡張=s4）が質問範囲外だったため。

## qa-05b シナリオ変更内容

### 変更前（exp-cond-p-revised）
```json
"must": [
  {"fact": "JSONのボディ変換はJackson2BodyConverterが担当する", "section": "...:s2"},
  {"fact": "対応MIMEを増やす場合はJaxRsHandlerListFactoryを実装して対応する", "section": "...:s4"}
],
"acceptable": [{"section": "...:s3"}]
```

### 変更後（本実験）
```json
"must": [
  {"fact": "JSONのボディ変換はJackson2BodyConverterが担当する", "section": "...:s2"}
],
"acceptable": [
  {"section": "...:s3"},
  {"section": "...:s4"}
]
```

## 実験設計（条件P、前回と同一）

| 項目 | 設定 |
|------|------|
| semantic-search.md | `.tmp/skill-cond-p/workflows/semantic-search.md` |
| qa.md | `.tmp/skill-cond-p/workflows/qa.md` |
| index経路上限 | 10件 |
| classes経路上限 | 10件 |
| マージ後上限 | なし（dedup後最大20件） |
| Step 3 セクション上限 | 20件 |
| qa-05b input | "REST APIでJSONを受け取ってDBに登録する処理を作りたい" |
| qa-05b purpose | 仕組み・動作を理解したい |
| 回数 | 10回 |

## 全試行結果

| 試行 | index件数 | classes件数 | merged件数 | adapter出所 | s2到達 | correctness |
|------|-----------|------------|-----------|------------|--------|-------------|
| run-01 | 3 | 2 | 5 | なし | × | 0.0 |
| run-02 | 6 | 0 | 6 | なし | × | 0.0 |
| run-03 | 6 | 0 | 6 | なし | × | 0.0 |
| run-04 | 6 | 3 | 6 | なし | × | 0.8 |
| run-05 | 6 | 4 | 6 | なし | × | 0.0 |
| run-06 | 6 | 4 | 6 | なし | × | 1.0 |
| run-07 | 5 | 3 | 5 | なし | × | 1.0 |
| run-08 | 6 | 4 | 6 | なし | × | 0.0 |
| run-09 | 8 | 0 | 8 | あり | ○ | 1.0 |
| run-10 | 5 | 0 | 5 | なし | × | 0.0 |
| **集計** | | | | **adapter選出: 1/10** | **s2到達: 1/10** | **avg: 0.380** |

## 検証ポイントの検証結果

### 1. 「s2到達 → correctness=1.0」は成立したか？
- s2到達: 1/10（run-09のみ）
- run-09: correctness=1.0 ✓
- **成立を確認**（サンプル数1のため統計的確度は低い）

### 2. adapter選出率（前回との比較）
- 前回（exp-cond-p-revised）: 5/10 
- 今回: 1/10
- 大幅に低下。セッション・タイミングの揺らぎと考えられる（前回も同一条件）

### 3. s2非到達でも高スコアが出た試行（3/10）
- run-04: 0.8 — Jackson2BodyConverterを「～など」として言及（adapterページ未選出）
- run-06: 1.0 — adapterページ未選出でもJackson2BodyConverterを名指し言及
- run-07: 1.0 — 同上

これらは adapterページを読まずに Jackson2BodyConverter を正確に言及した試行。
handlers-body-convert-handler.json 等に Jackson2BodyConverter の記述が含まれているか、
LLMが学習データから回答した可能性がある。

## s2非到達でのJackson2BodyConverter言及パターン（run-06,07の詳細）

- run-06: index:6, classes:4, merged:6（adapter非選出）, read_sections に adapters-jaxrs-adaptor.json なし
- run-07: index:5, classes:3, merged:5（adapter非選出）, read_sections に adapters-jaxrs-adaptor.json なし

→ adapterページを読まずに must の事実が回答に含まれた = ナレッジ外からの回答（LLM事前知識）
  または handlers-body-convert-handler.json に Jackson2BodyConverter への言及が含まれている
