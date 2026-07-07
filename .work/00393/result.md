# DeepEval 精度検証レポート

## このレポートについて

nabledge-6 の回答品質を自動評価する **DeepEval** が、実際にどれほど正確に判定できているかを検証した。

**検証方法**: DeepEval の判定結果（OK/NG）を、AIが各回答とナレッジを読んで独立に判定した結果（AI照合）と照らし合わせた。

**対象**: `tools/benchmark/results/20260616-1214-fullbench-classes-v6/` run-1〜run-3（34シナリオ × 3回 = 102件）  
**評価指標**: 3種類（answer_correctness / answer_relevancy / faithfulness）  
**照合日**: 2026-07-07

---

## 結論

**DeepEvalは「問題あり（NG）」を出しすぎる。問題の見逃しはほぼない。**

| 指標 | 意味 | 誤検知率 | 見逃し率 |
|------|------|------|------|
| answer_correctness | 回答が正しい事実を含んでいるか | 44.4%（4/9件） | 0.0%（0/93件） |
| answer_relevancy | 回答が質問に関連しているか | 60.9%（14/23件） | 0.0%（0/79件） |
| faithfulness | 回答がナレッジと矛盾しないか | 74.3%（26/35件） | 1.5%（1/67件） |

> **NG正検知**: DeepEvalがNGと判定し、AI照合でも本当に問題があった件  
> **誤検知**: DeepEvalがNGと判定したが、AI照合ではOKだった件  
> **見逃し**: DeepEvalがOKと判定したが、AI照合ではNGだった件

---

## 指標ごとの詳細

### answer_correctness（回答が正しい事実を含んでいるか）

DeepEvalの閾値: スコア ≥ 0.99

| | DeepEval=OK | DeepEval=NG |
|---|---|---|
| **AI照合=OK** | 93件（両者合意・問題なし） | **4件（DeepEvalの誤検知）** |
| **AI照合=NG** | 0件（見逃しなし） | 5件（両者合意・問題あり） |

**なぜ誤検知が起きるか**: DeepEvalは「回答が包括的すぎる」「参照事実と表現が異なる」といった理由でNGとするが、参照すべき事実は実際に回答に含まれている。

誤検知の例:
- [run-1-qa-12.md](checks/run-1-qa-12.md) — 参照事実は回答に含まれているが、DeepEvalは「補足情報が多い」としてNG
- [run-3-review-09.md](checks/run-3-review-09.md) — 事実は含まれているが表現が異なるためNG

---

### answer_relevancy（回答が質問に関連しているか）

DeepEvalの閾値: スコア ≥ 0.95

| | DeepEval=OK | DeepEval=NG |
|---|---|---|
| **AI照合=OK** | 79件（両者合意・問題なし） | **14件（DeepEvalの誤検知）** |
| **AI照合=NG** | 0件（見逃しなし） | 9件（両者合意・問題あり） |

**なぜ誤検知が起きるか**: nabledgeの回答末尾には `参照: libraries-xxx.json:s9` という出典メタデータが含まれる。DeepEvalはこれを「質問と無関係なコンテンツ」と解釈してスコアを0.95以下に下げるが、AI照合では回答の本文は質問に直接答えており問題なしと判断した。

誤検知の例:
- [run-1-impact-01.md](checks/run-1-impact-01.md) — 回答本文は質問に直接関連しているが、末尾の出典メタデータをDeepEvalが減点
- [run-1-qa-03.md](checks/run-1-qa-03.md) — 同上（14件中13件が同じパターン）

---

### faithfulness（回答がナレッジと矛盾しないか）

DeepEvalの閾値: スコア ≥ 0.99

| | DeepEval=OK | DeepEval=NG |
|---|---|---|
| **AI照合=OK** | 66件（両者合意・問題なし） | **26件（DeepEvalの誤検知）** |
| **AI照合=NG** | 1件（見逃し） | 9件（両者合意・問題あり） |

**なぜ誤検知が起きるか**: DeepEvalは「ナレッジに書かれている情報を回答が省略している」ことを「矛盾」と解釈するが、省略は矛盾ではない。AI照合では「回答に含まれている内容がナレッジと矛盾しているか」のみを基準とした。

誤検知の例:
- [run-1-impact-01.md](checks/run-1-impact-01.md) — コンストラクタの引数パターンを一部省略しているとDeepEvalがNG判定。ナレッジとの矛盾はない。

見逃しの例（1件）:
- [run-2-qa-11.md](checks/run-2-qa-11.md) — DeepEval=OKだが、回答にナレッジに存在しない記述が含まれている

---

## 全確認ファイル

102件の照合結果: [checks/](checks/)
