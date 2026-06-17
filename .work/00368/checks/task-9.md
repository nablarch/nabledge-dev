# task-9 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence |
|---|---|---|
| 条件1・2 有効20回の結果が揃っている | OK | `expA-limit12/run-{1..20}` + `expA-limit20/run-{1..20}` 全40dir確認、TIMEOUT発生なし |
| correctness分布・s2到達率・read・cost/time が2条件並べて示されている | OK | 下記集計表参照 |
| correctness<1.0 の全回について reason 全文が列挙されている | OK | 条件1: run-04/11/16/19 の reason全文を抽出、条件2: run-11 の reason全文を抽出 |
| 実験後に上限12コミット済み状態に戻っていること | OK | `grep -n "reaches 12"` + `grep -n "Maximum 12"` 両方確認済み |

## 集計表（裏取り済み）

| 指標 | 上限12（n=20） | 上限20（n=20） |
|---|---|---|
| correctness 平均 | 0.9400 | 0.9900 |
| 1.0 / 0.8 / 0.7 / 0.6 の回数 | 16 / 1 / 2 / 1 | 19 / 1 / 0 / 0 |
| s2到達率 | 20/20 | 20/20 |
| read 中央値 / 最大 | 8.0 / 12 | 8.0 / 13 |
| 12 binding（read>=12）回数 | 4/20（run-03,06,09,14） | 3/20（run-04,15,17） |
| cost平均 / time平均 | $0.93321 / 171.3s | $0.86504 / 178.7s |

## QA Expert Review

N/A（ベンチマーク実行・裏取りタスクのためコードレビュー不要。結果の整合性は上記Criteriaで確認）

## Overall Verdict

- Self-check: OK
- QA: N/A
- Language expert: N/A
- Software-engineering expert: N/A
- Ready for user review: Yes
