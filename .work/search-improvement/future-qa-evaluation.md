# QA評価方式の刷新（Answer Correctness / Similarity / Faithfulness）

## 問題

現在のC-claim判定は事実の有無しか見ない。回答全体の正確性・類似性を評価できない。

## 方針

Answer Correctness + Answer Similarity + Faithfulness の3軸で評価する。

## 前提

タスク4（QAベンチマーク）の評価方式として必要。タスク4の前に完了すること。

## やること

1. ライブラリ選定 — RAGAS, DeepEval等の候補を調査・比較
2. Ground truth作成 — qa.jsonの全シナリオに参照回答を追加
3. 評価パイプライン設計
4. 実装
5. 検証 — 3件程度のシナリオで評価パイプラインを実行し、判定結果の妥当性を評価・報告
6. → ユーザーレビュー
