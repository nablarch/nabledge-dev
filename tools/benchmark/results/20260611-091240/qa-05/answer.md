**結論**: リソースクラスに `@Path` + `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付与したメソッドを定義し、引数のフォームを `BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

**① フォームクラスの作成**

リクエストボディを受け付けるフォームを作成する。プロパティは全て `String` 型で宣言すること。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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

| アノテーション/API | 役割 |
|---|---|
| `@Path("/projects")` + `@POST` | URLとHTTPメソッドのマッピング定義（ルーティングアダプタが解釈） |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け取る指定。BodyConvertHandlerがこのアノテーションを見てJSONをフォームに変換する |
| `@Valid` | JaxRsBeanValidationHandlerがフォームに対してBean Validationを実行する |
| `BeanUtil.createAndCopy(Project.class, project)` | フォームをエンティティに変換 |
| `UniversalDao.insert(...)` | DBへの登録 |
| `HttpResponse.Status.CREATED` (201) | リソース作成完了を示すステータスコードを返却 |

---

**注意点**:

- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が異なる場合、BodyConvertHandlerがステータスコード `415`（Unsupported Media Type）を返却する
- `@Valid` は必須。省略するとバリデーションが実行されない
- ルーティングアダプタ（`PathOptionsProviderRoutesMapping`）のコンポーネント設定でアノテーションベースのルーティングを有効にしておく必要がある

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8