**結論**: Nablarch で REST API を提供するには「Jakarta RESTful Web Servicesサポート」を使用する。構成の核心は「ハンドラキュー」と「リソースクラス（アクションクラス）」の2層。推奨パターンは Jersey（または RESTEasy）アダプタ + `@Path`/HTTPメソッドアノテーションによるルーティング。

---

**根拠**:

**① 全体構成の位置付け**  
NablarchのRESTサポートはウェブアプリケーション基盤の上に乗る。クライアントサイドの機能（Jakarta RESTful Web Services クライアント API）は提供されないため、外部API呼び出しが必要な場合はJerseyやRESTEasyを別途使用する。（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s1`）

**② 推奨ハンドラ構成（最小セット）**  
ハンドラキューは以下の順序で組む。これが推奨最小構成。  
（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s3`）

| No | ハンドラ | 役割 |
|----|----------|------|
| 1 | `global_error_handler` | 例外・エラーのログ出力 |
| 2 | `jaxrs_response_handler` | レスポンス書き込み・エラー時レスポンス生成 |
| 3 | `database_connection_management_handler` | DB接続の取得・解放 |
| 4 | `transaction_management_handler` | トランザクション開始・コミット・ロールバック |
| 5 | ルーティング（`RoutesMapping` or `PathOptionsProviderRoutesMapping`） | URIとリソースメソッドの紐付け |
| 6 | `body_convert_handler` | リクエスト/レスポンスボディのJava→JSON変換 |
| 7 | `jaxrs_bean_validation_handler` | フォームクラスのバリデーション |

No.6・7はルーティングハンドラに対して `JaxRsMethodBinderFactory` 経由で設定する。`jaxrs_adaptor`（JerseyまたはRESTEasy）を使うと6・7が自動追加されるため設定が簡潔になる。（`component/adapters/adapters-jaxrs_adaptor.json:s2`）

**③ ルーティング（アノテーションベース推奨）**  
バージョン1.2.0以降、`@Path`アノテーションによるルーティングが使える。ディスパッチハンドラに `PathOptionsProviderRoutesMapping` を設定し、`JaxRsPathOptionsProvider` でベースパッケージとapplicationPathを指定する。  
（`component/adapters/adapters-router_adaptor.json:s1`）

```java
@Path("/projects")
public class ProjectAction {
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Project> findAll() { ... }

    @POST
    @Produces(MediaType.APPLICATION_JSON)
    public Project register(ProjectForm form) { ... }

    @GET
    @Path("/{id : \\d+}")
    public Project find(JaxRsHttpRequest request) {
        String id = request.getPathParam("id");
    }
}
```

インターフェースに`@Path`を置き、実装クラスでメソッドを提供するパターンも可能（OpenAPI generator との組み合わせで有効）。

**④ メディアタイプ変換（Jerseyアダプタ利用時）**  
`JerseyJaxRsHandlerListFactory`を使うと、JSON（Jackson2）・XML（JAXB）・フォーム・マルチパートの4形式が自動でサポートされる。  
（`component/adapters/adapters-jaxrs_adaptor.json:s2`）

---

**注意点**:
- JBoss/WildFlyなどvfsでクラスを管理するAPサーバでは`@Path`アノテーションによるクラス検索が動作しない。その場合はXMLによるルーティング定義を使用する。（`component/adapters/adapters-router_adaptor.json:s1`）
- `@Context`によるServletリソースインジェクション、Jakarta CDIは使用不可。（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s1`）
- `PathOptionsProviderRoutesMapping`コンポーネントは `BasicApplicationInitializer` の `initializeList` への追加が必須。（`component/adapters/adapters-router_adaptor.json:s1`）
- フィルタ・インターセプタが必要な場合はハンドラ（フィルタ用）またはBodyConverter実装（インターセプタ用）を自作する。（`processing-pattern/restful-web-service/restful-web-service-functional_comparison.json:s1`）

参照: processing-pattern/restful-web-service/restful-web-service-architecture.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s3, component/adapters/adapters-router_adaptor.json:s1, component/adapters/adapters-jaxrs_adaptor.json:s2, processing-pattern/restful-web-service/restful-web-service-functional_comparison.json:s1