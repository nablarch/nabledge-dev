**結論**: Nablarch ウェブアプリケーションは「NablarchServletContextListener（システムリポジトリ初期化） + RepositoryBasedWebFrontController（ハンドラキューへの委譲）」の2コンポーネントで起動し、13本の標準ハンドラを推奨順序で並べたハンドラキューが基本構成となる。

**根拠**:

**① 全体アーキテクチャ** [`processing-pattern/web-application/web-application-architecture.json:s1`]  
Servlet API を前提とし、以下2コンポーネントが必須:
- `NablarchServletContextListener` — 起動時にシステムリポジトリとログを初期化するサーブレットコンテキストリスナー
- `WebFrontController` — 受け取ったリクエストをハンドラキューに委譲するサーブレットフィルタ

**② web.xml 設定** [`processing-pattern/web-application/web-application-web_front_controller.json:s3`]  
`RepositoryBasedWebFrontController` をサーブレットフィルタとして登録し、`NablarchServletContextListener` をリスナーとして必ず設定する（これがないとシステムリポジトリが初期化されない）:
```xml
<context-param>
  <param-name>di.config</param-name>
  <param-value>web-boot.xml</param-value>
</context-param>
<listener>
  <listener-class>nablarch.fw.web.servlet.NablarchServletContextListener</listener-class>
</listener>
<filter>
  <filter-name>entryPoint</filter-name>
  <filter-class>nablarch.fw.web.servlet.RepositoryBasedWebFrontController</filter-class>
</filter>
<filter-mapping>
  <filter-name>entryPoint</filter-name>
  <url-pattern>/action/*</url-pattern>
</filter-mapping>
```

**③ 最小ハンドラキュー構成（推奨順）** [`processing-pattern/web-application/web-application-architecture.json:s3`]  
以下の13ハンドラがベースとなる。この順序でキューに並べ、プロジェクト要件に応じてカスタムハンドラを追加する:

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | HttpCharacterEncodingHandler | 文字エンコーディング設定 |
| 2 | GlobalErrorHandler | 実行時例外・エラー時のログ出力 |
| 3 | HttpResponseHandler | フォーワード/リダイレクト/レスポンス書き込み |
| 4 | SecureHandler | セキュリティ関連レスポンスヘッダ設定 |
| 5 | MultipartHandler | マルチパートリクエストの一時ファイル保存 |
| 6 | SessionStoreHandler | セッションストアの読み書き |
| 7 | NormalizeHandler | リクエストパラメータのノーマライズ |
| 8 | ForwardingHandler | 内部フォーワード時に後続ハンドラを再実行 |
| 9 | HttpErrorHandler | 例外種別に応じたログ出力とレスポンス生成 |
| 10 | NablarchTagHandler | Nablarchカスタムタグの事前処理 |
| 11 | DatabaseConnectionManagementHandler | DB接続の取得・解放 |
| 12 | TransactionManagementHandler | トランザクションの開始・コミット・ロールバック |
| 13 | RouterAdaptor | リクエストパスからアクションへのディスパッチ |

**④ プロジェクト生成の出発点** [`setup/blank-project/blank-project-setup_Web.json:s2`, `setup/blank-project/blank-project-setup_Web.json:s3`]  
Nablarch 提供のアーキタイプからブランクプロジェクトを生成すると、上記の基本設定・ルーティングアダプタ・疎通確認用アプリが含まれた状態で始められる:
```bash
mvn archetype:generate \
  -DarchetypeGroupId=com.nablarch.archetype \
  -DarchetypeArtifactId=nablarch-web-archetype \
  -DarchetypeVersion={nablarch_version}
```

**注意点**:
- `NablarchServletContextListener` の設定を web.xml に忘れるとシステムリポジトリが初期化されず起動に失敗する [`processing-pattern/web-application/web-application-web_front_controller.json:s3`]
- ウェブアプリと RESTful ウェブサービスを併用する場合は、`WebFrontController` を複数定義し、`<init-param>` の `controllerName` で使い分ける [`processing-pattern/web-application/web-application-web_front_controller.json:s4`]
- ルーティングには `RouterAdaptor`（XML 定義）または `@Path` アノテーション（`PathOptionsProviderRoutesMapping`）が使える。JBoss/Wildfly の VFS 環境では `@Path` アノテーション方式は使用不可 [`component/adapters/adapters-router_adaptor.json:s1`]

参照: processing-pattern/web-application/web-application-architecture.json:s1, processing-pattern/web-application/web-application-architecture.json:s3, processing-pattern/web-application/web-application-web_front_controller.json:s1, processing-pattern/web-application/web-application-web_front_controller.json:s3, processing-pattern/web-application/web-application-web_front_controller.json:s4, processing-pattern/web-application/web-application-nablarch_servlet_context_listener.json:s1, setup/blank-project/blank-project-setup_Web.json:s2, setup/blank-project/blank-project-setup_Web.json:s3, component/adapters/adapters-router_adaptor.json:s1