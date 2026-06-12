**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、①Formクラスの作成、②`@Consumes`・`@Valid`・`UniversalDao.insert`を使った業務アクションメソッドの実装、③`@Path`・`@POST`アノテーションによるURLマッピングの3ステップで実装します。

**根拠**:

**1. Formクラスの作成**

JSONのリクエストボディを受け取るFormクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. 業務アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストボディを受け付けることを宣言する
- `@Valid` — Jakarta RESTful Web Servcies Bean ValidaionハンドラによってFormのバリデーションを実行する
- `BeanUtil.createAndCopy(Project.class, project)` — FormをEntityに変換する
- `UniversalDao.insert(...)` — EntityをDBに登録する（SQLを書かずにCRUDが可能）
- ステータスコード `201`（Created）を返却する

**3. URLマッピング**

`@Path` アノテーションでクラスにベースパスを、`@POST` アノテーションでメソッドにHTTPメソッドを対応付けます（上記コード参照）。これにより `POST /projects` が `save` メソッドにマッピングされます。

**注意点**:
- Formのプロパティは全てString型で宣言すること
- `@Valid` によるバリデーションは、リクエストボディ変換ハンドラよりも後ろにJaxRsBeanValidationHandlerが設定されている必要がある（通常はフレームワークの標準ハンドラ構成で満たされている）
- Jakarta RESTful Web Servicesで規定されている `@QueryParam` や `@PathParam` は使用できないため、パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得すること

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s3, component/adapters/adapters-router-adaptor.json:s8