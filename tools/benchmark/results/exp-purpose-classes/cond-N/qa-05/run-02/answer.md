**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けた業務アクションメソッドを実装し、`BeanUtil.createAndCopy()` でFormをEntityに変換して `UniversalDao.insert()` でDB登録するパターンが基本形。

**根拠**:

**① Formクラスの作成**

リクエストのJSON項目を受け取るFormを作成する。プロパティはすべてString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② 業務アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONがFormに自動変換される（リクエストボディ変換ハンドラが処理する）
- `@Valid` でリクエストのバリデーションが実行される
- `BeanUtil.createAndCopy()` でFormをEntityクラスに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値は `HttpResponse.Status.CREATED.getStatusCode()` (201) を返す

**注意点**:
- FormのプロパティはすべてString型で宣言すること（バリデーションルールの要件）
- `@Consumes` と異なるContent-Typeのリクエストが来た場合、415（Unsupported Media Type）が返される
- URLとアクションのマッピングには `@Path`・`@POST` アノテーションを使用する（ルーティングアダプタのJakarta RESTful Web ServicesのPathアノテーション対応が必要）

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, restful-web-service-resource-signature.json:s1