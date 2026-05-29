セクション選択の結果：
- `guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json` (全体 + s1): Nablarchの非同期処理パターン — 関連
- `about/about-nablarch/about-nablarch-policy.json` s6: OSSポリシー — WebSocket非サポートの根拠として参照
- `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json` s1, s3, s4: 進捗ログ機能 — 代替手段として関連
- `processing-pattern/nablarch-batch/nablarch-batch-nablarch-batch-retention-state.json`: セクションなし（本文のみ）— 参考

read_sections:
- `guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s1`
- `about/about-nablarch/about-nablarch-policy.json:s6`
- `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s1`
- `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s3`
- `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s4`

---

## 回答

**結論**: NablarchにはWebSocketのサポートは提供されていない。バッチの進捗状況をブラウザへリアルタイム通知する仕組みは知識ファイルの対象範囲外となる。

**根拠**:

Nablarchの基本方針として、プロダクションコードはOSSを使用しない設計になっており（`about-nablarch-policy.json:s6`）、WebSocketに関するハンドラ・ライブラリも提供されていない。知識ファイル全体を通じてWebSocketへの言及は存在しない。

**Nablarchが提供する進捗通知の代替アプローチ**:

Jakarta Batchでは `ProgressManager` を使って進捗情報をログに出力できる（`jakarta-batch-progress-log.json:s1`）。出力内容はTPS・残件数・終了予測時間など：

```
INFO progress job name: [test-job] step name: [test-step] total tps: [250.00] current tps: [250.00] estimated end time: [2017/02/13 04:02:25.656] remaining count: [15]
```

ただし、これはログファイルへの出力であり、ブラウザへのプッシュ通知ではない。

**非同期処理との組み合わせパターン**:

Nablarchの非同期処理は「テーブルをキューとして使ったメッセージング」を使って実現する（`nablarch-patterns-Nablarchでの非同期処理.json`）。バッチの進捗をブラウザへ通知したい場合は、以下のポーリング方式が知識ファイルの範囲内で取り得るアプローチとなる：

1. バッチがDBのテーブルに進捗件数を定期的に書き込む（`AtomicInteger`などを使用）
2. ウェブアプリケーションのAPIエンドポイントがそのテーブルを参照して進捗値を返す
3. ブラウザ側でポーリングして進捗を表示する

**注意点**:
- WebSocket自体はJakarta EE 10の標準仕様（`jakarta.websocket`）であり、TomcatなどのJakarta EEサーバー上ではJava標準APIとして利用できるが、Nablarchフレームワークとしての統合サポート（ハンドラ、設定）は提供されていない
- WebSocketエンドポイントをNablarchのハンドラキューの外側にサーブレットコンテナとして配置する方法は、この情報は知識ファイルの対象範囲外

参照: `nablarch-patterns-Nablarchでの非同期処理.json`, `about-nablarch-policy.json:s6`, `jakarta-batch-progress-log.json:s1`

---