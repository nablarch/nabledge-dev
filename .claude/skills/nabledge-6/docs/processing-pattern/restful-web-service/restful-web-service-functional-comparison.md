# Jakarta RESTful Web Servicesサポート/Jakarta RESTful Web Services/HTTPメッセージングの機能比較

<details>
<summary>keywords</summary>

機能比較, Jakarta RESTful Web Servicesサポート, HTTPメッセージング, Jakarta RESTful Web Services, リクエストマッピング, バリデーション, クライアントAPI, MessagingAction, BodyConverter, DataRecordFormatter, JaxRsResponseHandler, RESTfulウェブサービス選択, 非同期処理, トランザクション制御

</details>

ここでは、以下の機能比較を示す。

- NablarchのJakarta RESTful Web Servicesサポート
- HTTPメッセージング
- [Jakarta RESTful Web Services(外部サイト、英語)](https://jakarta.ee/specifications/restful-ws/)

> **Tip:** NablarchのJakarta RESTful Web ServicesサポートとHTTPメッセージングのみ、表内のマークをクリックすると、解説書の説明ページに遷移する。
.. |br| raw:: html

<br />

| 機能 | Jakarta RESTful \|br\| Web Services \|br\| サポート | HTTP \|br\| メッセージング | Jakarta RESTful \|br\| Web Services |
|---|---|---|---|
| リクエストとリソースメソッドのマッピング | △ | ○ | ○ |
| リクエストとパラメータのマッピング | △ | × [1]_ | ○ |
| HTTPメソッドのマッチング | △ | × [1]_ | ○ |
| メディアタイプに応じた \|br\| リクエスト/レスポンスの変換 | △ | × [1]_ | ○ |
| エンティティのバリデーション | ○ | ○ | ○ |
| リソースクラスへのインジェクション \|br\| (Jakarta Contexts and Dependency Injection) | × [2]_ | × [2]_ | ○ |
| リクエスト/レスポンスに対するフィルタ | × [3]_ | × [3]_ | ○ |
| ボディの読み書きに対するインターセプタ | × [4]_ | × [5]_ | ○ |
| クライアントAPI | × [6]_ | ○ | ○ |
| 非同期処理 | × [7]_ | × [7]_ | ○ |
| エラー時ログ出力 | ○ | ○ | － |
| リクエストボディの最大容量チェック | × [8]_ | ○ | － |
| 証跡ログの出力 | × [9]_ | ○ | － |
| 再送制御 | × [9]_ | ○ | － |
| サービス提供の可否チェック | × [10]_ | × [10]_ | － |
| トランザクション制御 | × [11]_ | × [11]_ | － |
| 業務処理エラー時のコールバック | × [12]_ | `○` | － |
HTTPメッセージングはRESTを考慮した作りになっていない。RESTfulウェブサービスには、Jakarta RESTful Web Servicesサポートを使用する。
Jakarta RESTful Web ServicesサポートとHTTPメッセージングは、Nablarchのウェブアプリケーションとして動作するため、Jakarta Contexts and Dependency Injectionは使用できない。
リクエスト/レスポンスに対するフィルタを作りたい場合は、ハンドラを作成する。
ボディの読み書きに対するインターセプタを作りたい場合は、Jakarta RESTful Web ServicesサポートのBodyConverterを作成する。
ボディの読み書きにはNablarchのデータフォーマットを使用している。変更したい場合は、データフォーマットのDataRecordFormatterを作成する。
Jakarta RESTful Web Servicesクライアントが必要な場合は、Jakarta RESTful Web Servicesの実装(JerseyやRESTEasyなど)を使用する。
サーバサイドで非同期処理が必要になる要件がないと想定している。要望があれば対応を検討する。
ウェブサーバやアプリケーションサーバにあるリクエストサイズをチェックする機能を使用する。
アプリケーションごとに要件が異なると想定している。アプリケーションで設計/実装する。
Nablarchにあるサービス提供可否チェックがアプリケーションの要件にマッチする場合はそれを使用する。マッチしない場合は、アプリケーションで設計/実装する。
Nablarchにあるトランザクション管理を使用する。
エラー処理は共通化し、JaxRsResponseHandlerをカスタマイズすることを想定している。業務処理で個別にエラー処理をしたい場合は、リソースメソッドにてtry/catchを使用する。
