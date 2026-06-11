Step 5、6、7を実行します。

**結論**: リソースクラスでJSONを受け取りDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` をメソッドに付与し、引数にFormを受け取って `UniversalDao.insert()` でDB登録する実装パターンを使います。

**根拠**:

**① Formクラスの作成**

JSONリクエストボディを受け取るFormを作成します。プロパティは全てString型で宣言します。

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディが自動的にFormに変換される
- `@Valid` を付与することで、Bean ValidationによるFormのバリデーションが実行される（バリデーションエラー時は `ApplicationException` がスローされる）
- `BeanUtil.createAndCopy()` でFormをエンティティに変換してから `UniversalDao.insert()` でDB登録する
- 戻り値として `201 Created` を示す `HttpResponse` を返す

**③ メソッドシグネチャのパターン**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディをFormに変換して受け取る（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| `ExecutionContext` | スコープ変数にアクセスしたい場合 |
| 組み合わせ | 例: `save(SampleForm form, JaxRsHttpRequest request)` |

**注意点**:
- Formのプロパティは必ず全てString型で宣言すること
- `@Consumes` に指定したMIMEタイプとリクエストヘッダの `Content-Type` が不一致の場合は、ステータスコード `415 (Unsupported Media Type)` が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8