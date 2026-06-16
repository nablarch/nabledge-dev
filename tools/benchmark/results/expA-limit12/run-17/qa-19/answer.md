**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormを受け取り、`UniversalDao.insert(BeanUtil.createAndCopy(Entity.class, form))` でDBに登録する。

**根拠**:

**処理の流れ**

1. `WebFrontController` がリクエストを受信し、ハンドラキューに委譲
2. ルーティングアダプタがURIからアクションクラスを特定
3. **`BodyConvertHandler`** が `@Consumes(MediaType.APPLICATION_JSON)` を見て、`Jackson2BodyConverter` でJSONリクエストボディをFormクラスに変換
4. **`JaxRsBeanValidationHandler`** が `@Valid` アノテーションを見てBean Validationを実行
5. アクションメソッドが業務ロジック（DB登録）を実行
6. `JaxRsResponseHandler` がレスポンスをクライアントに返却
7. `トランザクション制御ハンドラ` が復路でコミット（例外時はロールバック）

**フォームクラス**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```
- プロパティは全て `String` 型で宣言する

**アクションクラス**

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

- `@Path` + `@POST` でURLとのマッピングを定義
- `BeanUtil.createAndCopy` でFormからEntityに変換し、`UniversalDao.insert` でDB登録
- 戻り値はステータスコード `201` の `HttpResponse`

**ハンドラキューの最小構成**（参考）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 例外発生時のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット/ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | BodyConvertHandler | JSONリクエスト/レスポンスの変換 |
| 7 | JaxRsBeanValidationHandler | バリデーション実行 |

**注意点**: Jerseyを使用する場合、`JerseyJaxRsHandlerListFactory` をファクトリインジェクションすると `BodyConvertHandler`（`Jackson2BodyConverter` を含む）と `JaxRsBeanValidationHandler` が自動設定される。Consumes に指定したMIMEと異なるContent-Typeのリクエストが来た場合、ステータスコード `415` が返却される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2