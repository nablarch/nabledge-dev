# ベースライン ベンチマークレポート（baseline-deepeval）

**実行日**: 2026-06-01  
**スキル**: nabledge-6  
**シナリオ数**: 30  
**閾値**: answer_correctness ≥0.99 / answer_relevancy ≥0.95 / faithfulness ≥0.99

---

## 3 run 集計サマリー

| 指標 | run-1 | run-2 | run-3 | 平均 |
|---|---|---|---|---|
| answer_correctness | 0.9867 (29/30) | 0.9833 (28/30) | 0.9833 (29/30) | **0.984** |
| answer_relevancy   | 0.9757 (24/30) | 0.9732 (24/30) | 0.9765 (22/30) | **0.975** |
| faithfulness       | 0.9772 (21/30) | 0.9782 (21/30) | 0.9963 (28/30) | **0.984** |

---

## 閾値割れシナリオ一覧（3 run中1回以上）

| シナリオID | answer_correctness | answer_relevancy | faithfulness | 割れた指標 |
|---|---|---|---|---|
| impact-01  | 1.000 (0/3) | 0.982 (1/3) | 1.000 (0/3) | answer_relevancy |
| impact-03  | 1.000 (0/3) | 0.923 (3/3) | 1.000 (0/3) | answer_relevancy |
| impact-06  | 1.000 (0/3) | 1.000 (0/3) | 0.958 (2/3) | faithfulness |
| oos-qa-01  | 1.000 (0/3) | 0.961 (2/3) | 1.000 (0/3) | answer_relevancy |
| pre-01     | 1.000 (0/3) | 0.887 (3/3) | 1.000 (0/3) | answer_relevancy |
| pre-02     | 1.000 (0/3) | 1.000 (0/3) | 0.983 (1/3) | faithfulness |
| pre-03     | 1.000 (0/3) | 1.000 (0/3) | 0.968 (2/3) | faithfulness |
| qa-01      | 1.000 (0/3) | 0.923 (2/3) | 1.000 (0/3) | answer_relevancy |
| qa-02      | 1.000 (0/3) | 1.000 (0/3) | 0.967 (1/3) | faithfulness |
| qa-03      | 1.000 (0/3) | 0.978 (1/3) | 1.000 (0/3) | answer_relevancy |
| qa-04      | 1.000 (0/3) | 0.976 (0/3) | 0.967 (2/3) | faithfulness |
| qa-05      | 0.733 (2/3) | 0.870 (3/3) | 1.000 (0/3) | answer_correctness / answer_relevancy |
| qa-06      | 1.000 (0/3) | 0.916 (2/3) | 1.000 (0/3) | answer_relevancy |
| qa-08      | 1.000 (0/3) | 1.000 (0/3) | 0.976 (1/3) | faithfulness |
| qa-11a     | 1.000 (0/3) | 1.000 (0/3) | 0.984 (1/3) | faithfulness |
| qa-11b     | 1.000 (0/3) | 1.000 (0/3) | 0.986 (1/3) | faithfulness |
| qa-12a     | 0.800 (2/3) | 0.980 (1/3) | 1.000 (0/3) | answer_correctness / answer_relevancy |
| qa-12b     | 1.000 (0/3) | 1.000 (0/3) | 0.936 (2/3) | faithfulness |
| qa-13      | 1.000 (0/3) | 0.923 (1/3) | 0.974 (1/3) | answer_relevancy / faithfulness |
| review-06  | 1.000 (0/3) | 1.000 (0/3) | 0.957 (2/3) | faithfulness |
| review-07  | 1.000 (0/3) | 1.000 (0/3) | 0.933 (2/3) | faithfulness |
| review-08  | 1.000 (0/3) | 0.970 (1/3) | 1.000 (0/3) | answer_relevancy |
| review-09  | 1.000 (0/3) | 1.000 (0/3) | 0.926 (2/3) | faithfulness |

---

## 閾値割れ分類

| 分類 | シナリオ数 | シナリオID |
|---|---|---|
| スキルの挙動問題（3 run中2〜3回） | 13 | impact-03 / pre-01 / qa-01 / qa-05 / qa-06 / qa-12a / impact-06 / pre-03 / qa-04 / qa-12b / review-06 / review-07 / review-09 |
| 揺らぎ（3 run中1回のみ） | 10 | impact-01 / oos-qa-01 / qa-03 / pre-02 / qa-02 / qa-08 / qa-11a / qa-11b / qa-13 / review-08 |

---

## 各 run のレポート

- [run-1/run/report.md](run-1/run/report.md)
- [run-2/run/report.md](run-2/run/report.md)
- [run-3/run/report.md](run-3/run/report.md)
