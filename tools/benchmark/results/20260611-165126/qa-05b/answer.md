**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、引数にフォームクラスを受け取って `BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**① フォームクラスの作成**

クライアントから受け取るJSONのフィールドにマッピングするフォームを作成する。フォームのプロパティは全てString型で宣言する。

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

**実装のポイント:**
- `@Path` + `@POST` でURLとアクションのマッピングを定義する
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストがJSON形式であることを宣言する。リクエストボディ変換ハンドラがこのアノテーションを参照してJSONをフォームクラスに変換する
- `@Valid` を付与することで、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを自動実行する。バリデーションエラーが発生した場合は `ApplicationException` が送出される
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値は `HttpResponse(201)` でリソース作成完了を返却する

**注意点**:
- フォームのプロパティは全てString型で宣言すること（バリデーションの仕様上の制約）
- `@Valid` アノテーションはメソッドレベルに付与すること（フォームクラス側のアノテーションではない）
- メソッド引数の型には「フォーム(Java Beans)」「JaxRsHttpRequest」「ExecutionContext」を組み合わせて定義できる。JSONボディのみを受け取る場合はフォームクラスのみで十分

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-jaxrs-bean-validation-handler.json:s4