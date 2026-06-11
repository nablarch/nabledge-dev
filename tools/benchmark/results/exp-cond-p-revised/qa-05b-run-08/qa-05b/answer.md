**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラス・アクションメソッド・URLマッピングの3点を実装する。フレームワークがハンドラキューを通じてJSON変換・バリデーション・トランザクション制御を自動的に担う仕組みになっている。

**根拠**:

**処理の仕組み（流れ）**

リクエスト受信からDB登録までの処理はハンドラキューを通じて行われる：

1. Webフロントコントローラがリクエストを受信し、ハンドラキューに委譲する
2. ルーティングアダプタ（DispatchHandler）がURIからアクションクラスを特定する
3. **リクエストボディ変換ハンドラ**（BodyConvertHandler）がJSONボディをフォームクラスに変換する
4. **Bean Validationハンドラ**（JaxRsBeanValidationHandler）がフォームをバリデーションする
5. アクションクラスがDB登録処理を実行する
6. JaxRsResponseHandlerがレスポンスをクライアントに返す

**最小ハンドラ構成**

| No. | ハンドラ | 主な役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・エラー応答 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URI → アクション解決 |
| 6 | リクエストボディ変換ハンドラ | JSON → フォームクラス変換 |
| 7 | Bean Validationハンドラ | フォームバリデーション |

**実装例（登録機能）**

①フォームクラス（プロパティはすべてString型で宣言する）:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

②アクションメソッド（JSONを受け取りDBに登録する）:

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

**各アノテーション・APIの役割**

- `@Consumes(MediaType.APPLICATION_JSON)` — このメソッドが `application/json` のリクエストボディを受け付けることを宣言。BodyConvertHandlerはこれを参照してJSONをフォームに変換する
- `@Valid` — JaxRsBeanValidationHandlerにバリデーション実行を指示する
- `@Path("/projects")` + `@POST` — URLとHTTPメソッドのマッピングを定義
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティクラスに変換
- `UniversalDao.insert(...)` — エンティティをDBに登録
- `new HttpResponse(201)` — ステータスコード201（作成完了）をレスポンスとして返却

**注意点**: `@Consumes` に設定したMIMEとリクエストヘッダの `Content-Type` が一致しない場合は、ステータスコード `415`（Unsupported Media Type）が返却される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4