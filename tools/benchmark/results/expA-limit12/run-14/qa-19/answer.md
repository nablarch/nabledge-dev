**結論**: NablarchのRESTfulウェブサービスでは、`BodyConvertHandler`がJSONリクエストボディをFormクラスに変換し、アクションメソッドで`UniversalDao.insert`を使ってDBに登録する。URLとアクションのマッピングは`@Path`/`@POST`アノテーションで定義する。

**根拠**:

**処理の流れ**（リクエスト受信からDB登録まで）:

1. WebFrontController（`jakarta.servlet.Filter`実装）がリクエスト受信
2. ハンドラキューに処理委譲
3. ディスパッチハンドラがURIからアクションクラスを特定
4. `BodyConvertHandler`がリクエストボディをFormクラスに変換
5. `JaxRsBeanValidationHandler`がバリデーション実行
6. アクションクラスが業務ロジック（DB登録）を実行
7. `JaxRsResponseHandler`がレスポンスをクライアントに返す

**最小ハンドラ構成**:

| No. | ハンドラ | 主な役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外時ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み、エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ（RoutesMapping） | URIからアクション特定 |
| 6 | BodyConvertHandler | リクエストボディ↔フォームの変換 |
| 7 | JaxRsBeanValidationHandler | @Validによるバリデーション |

> **ポイント**: No.6とNo.7はルーティングアダプタより後ろに設定する必要がある。`Jakarta RESTful Web Servicesアダプタ`（Jersey用/RESTEasy用）を使うと、No.6とNo.7が自動設定される。

**実装例**（POSTリクエストでJSONを受け取りDBに登録する）:

フォームクラス:
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

アクションクラス:
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

**実装のポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言。`BodyConvertHandler`がこのアノテーションを参照してJSONをFormに変換する
- JSON変換には`Jackson2BodyConverter`が使用される（Jersey/RESTEasyアダプタで自動設定）
- `@Valid` を付けることで、`JaxRsBeanValidationHandler`がFormクラスのバリデーションを実行する（エラー時は`ApplicationException`をスロー）
- Formクラスのプロパティは全てString型で宣言する
- `BeanUtil.createAndCopy`でFormをEntityに変換後、`UniversalDao.insert`でDB登録
- 登録成功時はステータスコード`201`（Created）を返却

**注意点**:
- `BodyConvertHandler`に設定されていないMIMEタイプのリクエストが来た場合、ステータスコード`415`（Unsupported Media Type）が返る
- `BodyConvertHandler`はルーティングアダプタより後ろに設定すること（アノテーション情報をディスパッチ後に参照するため）
- RESTfulウェブサービスでは`@Context`アノテーションによるServletリソースのインジェクションやCDIは使用不可

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2