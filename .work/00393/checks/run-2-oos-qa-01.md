# oos-qa-01 — run-2

## 質問

バッチ処理の進捗状況をWebSocketでリアルタイムにブラウザへ通知したい。NablarchでWebSocketを使う方法はあるか？

## 回答

**結論**: NablarchにはWebSocketをサポートする専用のハンドラ・アダプタは提供されておらず、この情報は知識ファイルに含まれていません。バッチ処理の進捗をWebアプリと連携させる仕組みとして、Nablarchでは「テーブルをキューとして使ったメッセージング」による非同期処理パターンが提供されています。

**根拠**: Nablarchの非同期処理パターンとして、以下の構成が推奨されています。

1. **Webアプリ側**: リクエストを受け付けて、後続処理に必要なデータをDBに登録し、レスポンスを返却する
2. **テーブルキューメッセージング側**: DBへのデータ登録を検知し、バッチ処理を実行する

この仕組みにより、処理の起動と実行を分離した非同期処理が実現できます。

ただし、このパターンは「バッチを非同期で起動・実行する」仕組みを提供するものであり、WebSocketのようなサーバーからブラウザへのリアルタイムプッシュ通知の仕組みそのものは提供しません。進捗状況をブラウザへ伝えるには、クライアント側でHTTPポーリングを行い、DBに保存された進捗データを定期的に参照する設計を別途実装することになります。

また、Nablarchの基本方針として「プロダクションコードはOSSを使用しない」とあり、アダプタとしてOSSコンポーネントは利用可能ですが、WebSocket専用のアダプタは現時点で提供されていません。

**注意点**: WebSocketのリアルタイムプッシュ通知（Jakarta WebSocket等）については、知識ファイルの対象範囲外です。アプリケーションサーバー側のJakarta WebSocket実装を活用する場合は、Nablarchのハンドラキューの管理外での実装になります。

参照: guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json, about/about-nablarch/about-nablarch-policy.json:s6

## 参照ナレッジ

- [メール送信を行う場合](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.md#メール送信を行う場合) (s1)
- [OSSは使用しない](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/about-nablarch/about-nablarch-policy.md#ossは使用しない) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly states that Nablarch does not provide a dedicated handler/adapter for WebSocket support, which directly covers the expected fact that 'Nablarch does not support WebSocket.' The response goes into considerable detail explaining the lack of WebSocket support and alternative patterns, but the core expected fact is fully covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input question about using WebSocket in Nablarch for real-time batch processing progress notifications to the browser. No irrelevant statements were identified! |
| faithfulness | 0.99 | 0.92 | NG | The score is 0.92 because the actual output slightly misrepresents Nablarch's OSS policy by suggesting a blanket 'do not use OSS in production code' policy, when in fact the retrieval context clarifies that while Nablarch's production code avoids OSS to quickly respond to critical bugs/vulnerabilities, it still provides adapter components that allow OSS usage. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「NablarchにはWebSocketのサポートがないと回答している」は回答の「NablarchにはWebSocketをサポートする専用のハンドラ・アダプタは提供されておらず」および「WebSocket専用のアダプタは現時点で提供されていません」に明確に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- NablarchにはWebSocketのサポートがないと回答している
