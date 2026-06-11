# 実験結果: 条件P — qa-05b × 10回

**実験日**: 2026-06-11
**目的**: index経路10件 + classes経路10件（上限半減）でadapterが選ばれるか。中間記録（index_pages/classes_pages/merged_pages）追加版のe2e-promptで各経路の選定過程を追う。

## 実験設計（条件P）

| 項目 | 設定 |
|------|------|
| semantic-search.md | `.tmp/skill-cond-p/workflows/semantic-search.md` |
| qa.md | `.tmp/skill-cond-p/workflows/qa.md` |
| e2e-prompt.md | `tools/benchmark/prompts/e2e-prompt.md`（index_pages/classes_pages/merged_pages記録追加） |
| index経路上限 | 10件 |
| classes経路上限 | 10件 |
| マージ後上限 | なし（dedup後最大20件） |
| Step 3 セクション上限 | 20件 |
| シナリオ | qa-05b（目的: 仕組み・動作を理解したい） |
| 回数 | 10回 |

## 全試行結果

| 試行 | index件数 | classes件数 | merged件数 | adapter出所 | adapter非選出区分 | s2/s4到達 | correctness |
|------|-----------|------------|-----------|------------|-----------------|-----------|-------------|
| run-01 | 5 | 5 | 6 | なし | 判定対象外 | × | 0.000 |
| run-02 | 5 | 5 | 6 | なし | skip判定 | × | 0.000 |
| run-03 | 5 | 3 | 5 | なし | 判定対象外 | × | 0.000 |
| run-04 | 6 | 3 | 7 | classes | 判定対象外 | × | 0.000 |
| run-05 | 4 | 3 | 4 | なし | 判定対象外 | × | 0.500 |
| run-06 | 7 | 0 | 7 | なし | 判定対象外 | × | 0.000 |
| run-07 | 4 | 2 | 4 | なし | 判定対象外 | × | 0.300 |
| run-08 | 5 | 4 | 5 | なし | 判定対象外 | × | 0.000 |
| run-09 | 5 | 5 | 6 | なし | 判定対象外 | × | 0.000 |
| run-10 | 6 | 0 | 6 | なし | 判定対象外 | × | 0.000 |

## 集計

- correctness平均: **0.080**
- adapter選出: **1/10** 試行
  - うち skip判定（excluded_pagesに理由記録）: 1/10
  - うち判定対象外（excluded_pagesに記録なし）: 8/10
- s2/s4到達: **0/10** 試行（adapterがmerged_pagesに入った試行でもセクション選定で落ちた）

## adapter 非選出の詳細（excluded_pages 原文）

**run-02** (skip判定):
> JaxRsアダプタは環境設定に関する内容であり、リソースクラスの実装パターン自体の説明には不要

その他9試行: excluded_pagesに記録なし — index/classes両経路でadapterブロックが判定対象に上がらなかった。

## 各試行の index_pages / classes_pages / merged_pages

### run-01
- index (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json']
- classes (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/adapters/adapters-router-adaptor.json']
- merged (6): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (both)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (both)', 'component/adapters/adapters-router-adaptor.json (classes)']

### run-02
- index (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json']
- classes (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/libraries/libraries-universal-dao.json']
- merged (6): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (both)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (both)', 'component/libraries/libraries-universal-dao.json (classes)']

### run-03
- index (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json']
- classes (3): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-body-convert-handler.json']
- merged (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (both)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (index)']

### run-04
- index (6): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/adapters/adapters-router-adaptor.json']
- classes (3): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/adapters/adapters-jaxrs-adaptor.json']
- merged (7): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'component/handlers/handlers-body-convert-handler.json (index)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (index)', 'component/adapters/adapters-router-adaptor.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/adapters/adapters-jaxrs-adaptor.json (classes)']

### run-05
- index (4): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json']
- classes (3): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-body-convert-handler.json']
- merged (4): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (both)']

### run-06
- index (7): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/adapters/adapters-router-adaptor.json', 'component/libraries/libraries-universal-dao.json']
- classes (0): []
- merged (7): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (index)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (index)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (index)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (index)', 'component/adapters/adapters-router-adaptor.json (index)', 'component/libraries/libraries-universal-dao.json (index)']

### run-07
- index (4): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json']
- classes (2): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json']
- merged (4): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (index)']

### run-08
- index (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/handlers/handlers-body-convert-handler.json']
- classes (4): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/handlers/handlers-body-convert-handler.json']
- merged (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (both)', 'component/handlers/handlers-body-convert-handler.json (both)']

### run-09
- index (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json']
- classes (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/libraries/libraries-universal-dao.json']
- merged (6): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (both)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (both)', 'component/handlers/handlers-body-convert-handler.json (both)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (both)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/libraries/libraries-universal-dao.json (classes)']

### run-10
- index (6): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/adapters/adapters-router-adaptor.json']
- classes (0): []
- merged (6): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json (index)', 'processing-pattern/restful-web-service/restful-web-service-resource-signature.json (index)', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json (index)', 'component/handlers/handlers-body-convert-handler.json (index)', 'component/handlers/handlers-jaxrs-bean-validation-handler.json (index)', 'component/adapters/adapters-router-adaptor.json (index)']
