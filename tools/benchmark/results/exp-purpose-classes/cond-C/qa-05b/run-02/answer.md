**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`を付与したリソースクラスを作成し、フォームを引数に受け取って`UniversalDao.insert()`でDB登録するパターンを使う。

**根拠**:

**① フォームクラスの作成**

クライアントから送信されたJSONを受け付けるフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

`@Consumes(MediaType.APPLICATION_JSON)` でJSON受信を宣言し、`@Valid` でバリデーションを有効化する。`BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する。

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストボディを受け付ける宣言。リクエストボディ変換ハンドラ（`BodyConvertHandler`）がこのアノテーションを見てJSONをFormに変換する
- `@Valid` — Jakarta RESTful Web Servcies Bean Validationハンドラ（`JaxRsBeanValidationHandler`）がFormのバリデーションを実行する。バリデーションエラー時は`ApplicationException`を送出して処理終了
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティクラスにコピー変換
- `UniversalDao.insert()` — エンティティをDBに登録
- 戻り値 `HttpResponse(201)` — リソース作成完了を示すステータスコード201を返却

**③ URLマッピング**

`@Path` アノテーションと `@POST` アノテーションで、POSTリクエスト時にこのメソッドをマッピングする。ルーティングアダプタ（`PathOptionsProviderRoutesMapping`）を使う場合は、`JaxRsPathOptionsProvider` の `basePackage` にアクションクラスのパッケージを設定することで自動認識される。

**注意点**:
- フォームのプロパティは全てString型で宣言すること
- バリデーションアノテーション（`@Required`、`@Domain` 等）はフォームクラスに設定すること
- `Jakarta RESTful Web Services` で規定されている `@QueryParam` や `@PathParam` は使用できないため、パスパラメータが必要な場合は `JaxRsHttpRequest#getPathParam()` を使うこと
- Content-TypeヘッダのMIMEが`@Consumes`に指定したMIMEと異なる場合はステータスコード`415`が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8