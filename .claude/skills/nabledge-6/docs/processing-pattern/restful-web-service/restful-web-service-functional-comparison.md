# Jakarta RESTful Web Servicesサポート/Jakarta RESTful Web Services/HTTPメッセージングの機能比較

ここでは、以下の機能比較を示す。

* NablarchのJakarta RESTful Web Servicesサポート
* HTTPメッセージング
* [Jakarta RESTful Web Services(外部サイト、英語)](https://jakarta.ee/specifications/restful-ws/)

> **Tip:**
> NablarchのJakarta RESTful Web ServicesサポートとHTTPメッセージングのみ、表内のマークをクリックすると、解説書の説明ページに遷移する。

機能比較（○：提供あり　△：一部提供あり　×：提供なし　－:対象外）

| 機能 | Jakarta RESTful   Web Services   サポート | HTTP   メッセージング | Jakarta RESTful   Web Services |
|---|---|---|---|
| リクエストとリソースメソッドのマッピング | △ | ○ | ○ |
| リクエストとパラメータのマッピング | △ | × [1] | ○ |
| HTTPメソッドのマッチング | △ | × [1] | ○ |
| メディアタイプに応じた   リクエスト/レスポンスの変換 | △ | × [1] | ○ |
| エンティティのバリデーション | ○ | ○ | ○ |
| リソースクラスへのインジェクション   (Jakarta Contexts and Dependency Injection) | × [2] | × [2] | ○ |
| リクエスト/レスポンスに対するフィルタ | × [3] | × [3] | ○ |
| ボディの読み書きに対するインターセプタ | × [4] | × [5] | ○ |
| クライアントAPI | × [6] | ○ | ○ |
| 非同期処理 | × [7] | × [7] | ○ |
| エラー時ログ出力 | ○ | ○ | － |
| リクエストボディの最大容量チェック | × [8] | ○ | － |
| 証跡ログの出力 | × [9] | ○ | － |
| 再送制御 | × [9] | ○ | － |
| サービス提供の可否チェック | × [10] | × [10] | － |
| トランザクション制御 | × [11] | × [11] | － |
| 業務処理エラー時のコールバック | × [12] | ○ | － |

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
