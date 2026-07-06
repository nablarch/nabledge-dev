# nabledge-6 コード分析 品質評価レポート

**対象**: リライト前ベースライン（685行版）
**前版**: なし（これが基準版）
**測定条件**: 3シナリオ × 1回 = 3評価
**評価方法**: 自動採点（DeepEval: answer_correctness / answer_relevancy / faithfulness）

---

## 総合評価: 注意あり

ca-01（ProjectAction）で answer_correctness が 0.30 と低く、期待する fact の一部が出力に含まれていない。
ca-02・ca-03 は全指標で高スコア。
これはリライト前の状態を示す基準版であり、Task #5 リライト後の比較対象となる。

---

## 合否判定

### ① 正しい知識を選定し回答できているか → FAIL（ca-01 で到達不足）

| シナリオ | 入力クラス | correctness | relevancy | faithfulness | 判定 |
|---|---|---|---|---|---|
| ca-01 | ProjectAction | 0.300 | 0.960 | 1.000 | ❌ |
| ca-02 | AuthenticationAction | 1.000 | 0.988 | 1.000 | ✅ |
| ca-03 | ImportZipCodeFileAction | 1.000 | 0.968 | 1.000 | ✅ |

→ ca-01 で expected facts（@Path("/projects")・BeanUtil・ValidatorUtil 等）の一部が出力に含まれず、correctness 0.30。
  ca-02・ca-03 は期待 fact をすべてカバー。

### ② 推測や捏造が含まれていないか → PASS

全シナリオで faithfulness 1.00。ナレッジにない作り話は 0 件。

---

## 計測

### ③ 1回あたりコスト

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | $0.979 | $0.886 | $1.181 |

### ④ 1回あたり時間

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | 193秒 | 191秒 | 199秒 |

---

## 退行

これが基準版（前版なし）のため、退行対比は対象外。以降のバージョンはこの版と対比する。

---

## ベンチからの見解

- ca-01 の correctness 低下の原因: JAX-RS アノテーション・BeanUtil・ValidatorUtil 関連の fact が出力に現れていない。リライト後の改善が期待される箇所。
- faithfulness 全件 1.00 — 捏造リスクなし。
- ca-03（バッチ処理クラス）は正確な回答を出せており、複雑なクラスにも対応できている。

---

## 詳細根拠

各シナリオの個別スコア・回答は各シナリオディレクトリ内の `evaluation.json` / `answer.md` を参照。
