# oos-qa-01 — run-1

## 質問

バッチ処理の進捗状況をWebSocketでリアルタイムにブラウザへ通知したい。NablarchでWebSocketを使う方法はあるか？

## 回答

**結論**: NablarchにはWebSocketのサポート機能は提供されていません。

NablarchのウェブアプリケーションはServlet APIを前提とした構成を採用しており、知識ファイルにはWebSocketを利用するための機能やAPIに関する記載は含まれていません。

**根拠**:
Nablarchのウェブアプリケーションアーキテクチャは、リクエスト/レスポンス型のHTTP通信をハンドラキューで処理する設計です。WebSocketはこのモデルとは異なる常時接続型のプロトコルであり、Nablarchのフレームワーク機能として提供されている範囲外となります。

**注意点**:
- NablarchはServlet APIベースでアプリケーションを構成するため、アプリケーションサーバー（TomcatなどのServlet 5.0以上対応）がWebSocketをサポートしていれば、Nablarchのフレームワーク外でJakarta WebSocket API（`jakarta.websocket`）を直接使用して実装することは技術的に可能です。ただし、この場合はNablarchのハンドラキューやセッションストアなどの機能は使用できません。
- バッチ処理の進捗をブラウザへリアルタイム通知する要件については、Nablarchのパターンとして「テーブルをキューとして使ったメッセージング」でバッチの状態をDBに書き込み、ブラウザ側がポーリングで取得する方式が知識ファイルに記載されたアーキテクチャパターンに沿った代替アプローチです。

参照: processing-pattern/web-application/web-application-architecture.json:s1

## 参照ナレッジ

- [ウェブアプリケーションの構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-architecture.md#ウェブアプリケーションの構成) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly states that Nablarch does not provide WebSocket support functionality ('NablarchにはWebSocketのサポート機能は提供されていません'), which directly aligns with the single expected fact in the Expected Output. The response not only confirms the absence of WebSocket support but also provides detailed reasoning and context, fully covering the expected fact without contradicting it. |
| answer_relevancy | 0.95 | 0.92 | NG | The score is 0.92 because the actual output was largely relevant and addressed the question about using WebSocket with Nablarch for real-time batch progress notifications. However, it lost a few points due to the inclusion of a source document reference that did not contribute any useful information toward answering the question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- NablarchにはWebSocketのサポートがないと回答している
