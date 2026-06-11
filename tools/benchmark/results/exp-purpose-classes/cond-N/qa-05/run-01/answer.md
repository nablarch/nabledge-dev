**結論**: REST APIでJSONを受け取りDBに登録するには、Formクラスを作成し、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与して `UniversalDao.insert()` で登録する。URLマッピングはクラスに `@Path`、メソッドに `@POST` アノテーションで定義する。

**根拠**:

**① Formクラスの作成**

リクエストボディを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスの実装**

`@Path` でURLを指定し、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けるメソッドを定義する。

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディがリクエストボディ変換ハンドラによりFormに変換される
- `@Valid` でBean Validationによるバリデーションが実行される
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
- 登録成功時はステータスコード `201 Created` を返す

**③ メソッドシグネチャのバリエーション**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | JSONボディから変換したFormを受け取る場合（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| 組み合わせ | `(SampleForm form, JaxRsHttpRequest request)` のように併用可能 |

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの仕様による）
- Content-TypeヘッダにJSONが指定されていない場合、ステータスコード `415` が返却される
- `@Path` アノテーションを使用したルーティングには `PathOptionsProviderRoutesMapping` を設定する必要がある（JBoss/Wildfly等、vfsを使うサーバでは使用不可）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s6, adapters-router-adaptor.json:s8