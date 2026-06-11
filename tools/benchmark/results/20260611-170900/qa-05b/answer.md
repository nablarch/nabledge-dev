**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormを引数に取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録します。

**根拠**:

**① Formクラスの作成**（プロパティは全てString型）

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスの実装**

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

各アノテーション・APIの役割：

| 要素 | 役割 |
|------|------|
| `@Path("/projects")` + `@POST` | URLとメソッドのマッピング定義 |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSON形式のリクエストボディをFormに変換するよう `BodyConvertHandler` に指示 |
| `@Valid` | `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをエンティティBeanに変換 |
| `UniversalDao.insert(...)` | エンティティをDBに登録 |
| 戻り値 `HttpResponse(201)` | リソース作成完了（Created）をクライアントに返す |

**注意点**:
- Formのプロパティは全てString型で宣言すること
- `@Consumes` で指定したMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード `415`（Unsupported Media Type）が返される
- `@Valid` によるバリデーションでエラーが発生した場合、`JaxRsBeanValidationHandler` が `ApplicationException` を送出して後続処理は実行されない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4