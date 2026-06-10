**結論**: REST APIでJSONを受け取りDBに登録する場合、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フォームを引数として受け取り `UniversalDao.insert()` で登録する。

**根拠**:

**1. フォームクラスの作成**

リクエストのJSONを受け取るフォームクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスのメソッド実装**

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する
- `@Valid` を付けると `JaxRsBeanValidationHandler` がフォームのバリデーションを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 登録完了のレスポンスとしてステータスコード `201` を返す `HttpResponse` を返却する

**3. メソッドシグネチャのバリエーション**

| 用途 | 引数の定義 |
|------|-----------|
| リクエストボディのみ | `SampleForm form` |
| ボディ + パスパラメータ | `SampleForm form, JaxRsHttpRequest request` |
| パスパラメータのみ | `JaxRsHttpRequest request` |

パスパラメータを取得する場合は `JaxRsHttpRequest` を使う（Jakarta RESTful Web Servicesの `@PathParam` は使用不可）:
```java
Long id = Long.valueOf(req.getPathParam("id"));
```

**注意点**:
- JSONコンバータ（`Jackson2BodyConverter`）はJersey環境では `JerseyJaxRsHandlerListFactory` 経由で自動設定されるが、Jacksonがアプリケーションサーバにバンドルされていない場合はアプリケーションモジュールにJacksonを含める必要がある
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が異なる場合はステータスコード `415` が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-resource-signature.json:s2, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2