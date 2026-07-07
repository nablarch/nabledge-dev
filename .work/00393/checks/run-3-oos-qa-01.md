# oos-qa-01 — run-3

## 質問

バッチ処理の進捗状況をWebSocketでリアルタイムにブラウザへ通知したい。NablarchでWebSocketを使う方法はあるか？

## 回答

**結論**: NablarchにはWebSocketのサポートは提供されていません。Nablarchのプロダクションコードはすべて「OSSを使用しない」方針のため、WebSocketライブラリを利用した機能やアダプタは存在しません。

**根拠**: Nablarchの基本方針として以下が定められています：

> Nablarchのプロダクションコードは、致命的な不具合や脆弱性が見つかった際に、迅速に対応かつリリースすることを目的としてOSSを使用していない。なお、OSSを使用することでメリットがあるものは、アダプタとしてOSSを使用できるコンポーネントを提供している。

知識ファイルに含まれるアダプタ一覧（component/adapters/）にはWebSocket用アダプタは存在しません。

**注意点**:
- バッチ処理の進捗状況をブラウザへ通知したい場合、WebSocketではなくHTTPポーリングまたはServer-Sent Eventsをアプリケーション側で独自実装する形になります。ただしこれらの具体的な実装方法はNablarchの知識ファイルの対象範囲外です。
- WebSocketを使いたい場合は、Nablarchのハンドラキューの外側（サーブレットコンテナレベル）でWebSocketエンドポイントを実装する方法が考えられますが、この情報は知識ファイルの対象範囲外です。

参照: about/about-nablarch/about-nablarch-policy.json:s6

## 参照ナレッジ

- [OSSは使用しない](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/about-nablarch/about-nablarch-policy.md#ossは使用しない) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly states that Nablarch does not provide WebSocket support ('NablarchにはWebSocketのサポートは提供されていません'), which directly matches the single expected fact in the Expected Output. The response goes further with detailed explanations and references, but the core expected fact is fully covered. |
| answer_relevancy | 0.95 | 0.91 | NG | The score is 0.91 because the response is largely relevant and addresses the question about using WebSocket with Nablarch for real-time batch processing progress notifications. However, it loses a small amount of points due to the inclusion of a reference citation to a source file, which does not contribute substantively to answering the question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- NablarchにはWebSocketのサポートがないと回答している
