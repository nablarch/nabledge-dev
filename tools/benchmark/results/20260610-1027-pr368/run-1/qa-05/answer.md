**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付与し、引数としてフォームBeanを受け取り、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. フォームの作成**

クライアントから受け取るJSONをマッピングするフォームクラスを作成する。プロパティは全てString型で宣言する。

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラ（`BodyConvertHandler`）がJSONをフォームに変換する
- `@Valid` を指定することで、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを自動実行する。バリデーションエラー時は `ApplicationException` が送出される
- `BeanUtil.createAndCopy()` でフォームをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse` にステータスコード `201 (Created)` を指定して返却する

**3. メソッドシグネチャのパターン**

引数には以下の型が使用できる（組み合わせも可能）：

| 引数 | 用途 |
|------|------|
| フォーム (Java Beans) | リクエストボディから変換したフォームを処理 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得 |
| `ExecutionContext` | スコープ変数にアクセス |

戻り値には `void`（204 NoContent）、フォーム/Bean（レスポンスボディへ変換）、`HttpResponse`（ステータスコード指定）が使用できる。

**注意点**:
- `BodyConvertHandler` はルーティングアダプタよりも後ろに設定すること
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` よりも後ろに設定すること（変換後のFormに対してバリデーションを行うため）
- フォームのプロパティは全てString型で宣言すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4