# 実験結果: 条件P — qa-05/qa-05b 改版 × 各10回

**実験日**: 2026-06-11
**目的**: qa-05/qa-05b の input から「リソースクラスの実装パターンを教えてほしい」を削除し、両シナリオとも `input = "REST APIでJSONを受け取ってDBに登録する処理を作りたい"` に統一。purpose の違いだけで検索・回答が分かれるかを公正に測定する。

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
| qa-05 シナリオ変更 | input から「リソースクラスの実装パターンを教えてほしい」を削除 |
| qa-05b シナリオ変更 | 同上 |
| 回数 | qa-05 × 10 + qa-05b × 10 |

## 全試行結果

| シナリオ | 試行 | index件数 | classes件数 | merged件数 | adapter出所 | adapter skip理由(あれば原文) | s2/s4到達 | correctness |
|------|-----------|------------|-----------|------------|-----------------|-----------|-------------|-------|
| qa-05 | run-01 | 5 | 0 | 5 | なし | 判定対象外 | × | 1.000 |
| qa-05 | run-02 | 7 | 2 | 7 | both | 判定対象外 | ○ | 1.000 |
| qa-05 | run-03 | 5 | 3 | 5 | なし | 判定対象外 | × | 1.000 |
| qa-05 | run-04 | 7 | 0 | 7 | なし | 判定対象外 | × | 1.000 |
| qa-05 | run-05 | 6 | 0 | 6 | index | 判定対象外 | × | 1.000 |
| qa-05 | run-06 | 5 | 0 | 5 | なし | 判定対象外 | × | 1.000 |
| qa-05 | run-07 | 10 | 0 | 10 | index | 判定対象外 | ○ | 1.000 |
| qa-05 | run-08 | 6 | 0 | 6 | なし | 判定対象外 | × | 1.000 |
| qa-05 | run-09 | 7 | 4 | 7 | both | 判定対象外 | ○ | 1.000 |
| qa-05 | run-10 | 7 | 5 | 7 | both | 判定対象外 | ○ | 1.000 |
| **qa-05 集計** | | | | | **adapter選出: 5/10** | | **s2/s4: 4/10** | **avg: 1.000** |
| qa-05b | run-01 | 5 | 0 | 5 | なし | 判定対象外 | × | 0.000 |
| qa-05b | run-02 | 5 | 2 | 7 | なし | 判定対象外 | × | 0.000 |
| qa-05b | run-03 | 8 | 1 | 8 | both | 判定対象外 | ○ | 0.500 |
| qa-05b | run-04 | 9 | 5 | 9 | both | 判定対象外 | ○ | 0.500 |
| qa-05b | run-05 | 8 | 5 | 8 | both | 判定対象外 | ○ | 0.500 |
| qa-05b | run-06 | 6 | 0 | 6 | なし | 判定対象外 | × | 0.100 |
| qa-05b | run-07 | 8 | 4 | 8 | both | 判定対象外 | ○ | 0.500 |
| qa-05b | run-08 | 5 | 3 | 5 | なし | 判定対象外 | × | 0.000 |
| qa-05b | run-09 | 6 | 4 | 6 | なし | 「Jersey/RESTEasy環境設定に特化しており、DB登録処理の仕組みとは直接関係しない」 | × | 0.500 |
| qa-05b | run-10 | 5 | 4 | 6 | both | 判定対象外 | ○ | 0.400 |
| **qa-05b 集計** | | | | | **adapter選出: 5/10** | | **s2/s4: 5/10** | **avg: 0.300** |

## 集計サマリー

| シナリオ | purpose | correctness平均 | adapter選出 | s2/s4到達 |
|--------|---------|----------------|------------|---------|
| qa-05  | 実装したい | **1.000** | 5/10 | 4/10 |
| qa-05b | 仕組み・動作を理解したい | **0.300** | 5/10 | 5/10 |

## adapter 非選出の詳細（excluded_pages 原文）

**qa-05b run-09** (skip判定):
> Jersey/RESTEasy環境設定に特化しており、DB登録処理の仕組みとは直接関係しない

その他試行: excluded_pagesに記録なし — index/classes両経路でadapterブロックが判定対象に上がらなかった。

## qa-05b でadapterが merged に入っても s2/s4 に到達しなかった試行

- run-03 (both): s4 未到達（merged 8件中 s2/s4 選定なし）
- run-04 (both): s4 未到達
- run-05 (both): s4 未到達
- run-07 (both): s4 未到達
- run-10 (both): s4 未到達

→ merged_pages に adapter が含まれた 5 試行すべてで s2/s4 到達（実際には run-03〜10 で○が 5/10）。
  ただし correctness は 0.4〜0.5 に留まる（s4 に到達しても must 片方しか満たせない）。

## 各試行の index_pages / classes_pages / merged_pages

### qa-05

#### run-01
- index (5): ['processing-pattern/restful-web-service/restful-web-service-getting-started-create.json', 'processing-pattern/restful-web-service/restful-web-service-feature-details.json', 'component/handlers/handlers-body-convert-handler.json', 'component/handlers/handlers-jaxrs-bean-validation-handler.json', 'component/libraries/libraries-universal-dao.json']
- classes (0): []
- merged (5): ['restful-web-service-getting-started-create.json (index)', 'restful-web-service-feature-details.json (index)', 'handlers-body-convert-handler.json (index)', 'handlers-jaxrs-bean-validation-handler.json (index)', 'libraries-universal-dao.json (index)']

#### run-02
- index (7): ['restful-web-service-getting-started-create.json', 'restful-web-service-feature-details.json', 'handlers-body-convert-handler.json', 'libraries-bean-validation.json', 'libraries-universal-dao.json', 'adapters-jaxrs-adaptor.json', 'restful-web-service-resource-signature.json']
- classes (2): ['adapters-jaxrs-adaptor.json', 'handlers-body-convert-handler.json']
- merged (7): [all 7 unique, adapters-jaxrs-adaptor.json (both)]

#### run-03
- index (5): ['restful-web-service-getting-started-create.json', 'restful-web-service-feature-details.json', 'handlers-body-convert-handler.json', 'handlers-jaxrs-bean-validation-handler.json', 'libraries-universal-dao.json']
- classes (3): ['restful-web-service-getting-started-create.json', 'handlers-body-convert-handler.json', 'libraries-universal-dao.json']
- merged (5): [adapter なし]

#### run-04
- index (7): [..., 'adapters-router-adaptor.json'] (adapter-jaxrs 選出なし)
- classes (0): []
- merged (7): [adapter なし]

#### run-05
- index (6): [..., 'adapters-jaxrs-adaptor.json']
- classes (0): []
- merged (6): ['adapters-jaxrs-adaptor.json (index)']

#### run-06
- index (5): [adapter なし]
- classes (0): []
- merged (5): [adapter なし]

#### run-07
- index (10 = 上限): [..., 'adapters-jaxrs-adaptor.json', ...]
- classes (0): []
- merged (10): ['adapters-jaxrs-adaptor.json (index)']

#### run-08
- index (6): [adapter なし]
- classes (0): []
- merged (6): [adapter なし]

#### run-09
- index (7): [..., 'adapters-jaxrs-adaptor.json']
- classes (4): [..., 'adapters-jaxrs-adaptor.json']
- merged (7): ['adapters-jaxrs-adaptor.json (both)']

#### run-10
- index (7): [..., 'adapters-jaxrs-adaptor.json']
- classes (5): [..., 'adapters-jaxrs-adaptor.json']
- merged (7): ['adapters-jaxrs-adaptor.json (both)']

### qa-05b

#### run-01
- index (5): ['restful-web-service-architecture.json', 'restful-web-service-getting-started-create.json', 'restful-web-service-feature-details.json', 'handlers-body-convert-handler.json', 'handlers-jaxrs-bean-validation-handler.json']
- classes (0): []
- merged (5): [adapter なし]

#### run-02
- index (5): ['restful-web-service-architecture.json', ..., 'handlers-body-convert-handler.json', 'libraries-universal-dao.json']
- classes (2): ['handlers-jaxrs-bean-validation-handler.json', 'libraries-bean-validation.json']
- merged (7): [adapter なし]

#### run-03
- index (8): [..., 'adapters-jaxrs-adaptor.json', 'adapters-router-adaptor.json', ...]
- classes (1): ['adapters-jaxrs-adaptor.json']
- merged (8): ['adapters-jaxrs-adaptor.json (both)']

#### run-04
- index (9): [..., 'adapters-jaxrs-adaptor.json', ...]
- classes (5): [..., 'adapters-jaxrs-adaptor.json', ...]
- merged (9): ['adapters-jaxrs-adaptor.json (both)']

#### run-05
- index (8): [..., 'adapters-jaxrs-adaptor.json', 'adapters-router-adaptor.json', ...]
- classes (5): [..., 'adapters-jaxrs-adaptor.json', 'adapters-router-adaptor.json', ...]
- merged (8): ['adapters-jaxrs-adaptor.json (both)']

#### run-06
- index (6): [adapter なし]
- classes (0): []
- merged (6): [adapter なし]

#### run-07
- index (8): [..., 'adapters-jaxrs-adaptor.json', ...]
- classes (4): [..., 'adapters-jaxrs-adaptor.json']
- merged (8): ['adapters-jaxrs-adaptor.json (both)']

#### run-08
- index (5): [adapter なし]
- classes (3): [adapter なし]
- merged (5): [adapter なし]

#### run-09
- index (6): [adapter なし]
- classes (4): [adapter なし, excluded: 'Jersey/RESTEasy環境設定に特化しており、DB登録処理の仕組みとは直接関係しない']
- merged (6): [adapter なし]

#### run-10
- index (5): [..., 'adapters-jaxrs-adaptor.json']
- classes (4): [..., 'adapters-jaxrs-adaptor.json']
- merged (6): ['adapters-jaxrs-adaptor.json (both)']
