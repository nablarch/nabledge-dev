**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録する場合、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、引数にフォーム(Java Beans)を受け取り、`BeanUtil` でエンティティに変換して `UniversalDao.insert()` で登録するのが標準パターンです。

**根拠**:

**① フォームクラスの定義**

JSONの各フィールドを受け取るフォームクラスを作成します。プロパティは全て `String` 型で宣言します。

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

`@Path` でURLを、`@POST` でHTTPメソッドを定義し、`@Consumes(MediaType.APPLICATION_JSON)` でJSON受信を宣言します。

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

- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディのJSON変換を指示する。フレームワークの「リクエストボディ変換ハンドラ」がこのアノテーションを見てJSONをフォームへ変換する
- `@Valid` — 「Jakarta RESTful Web Services Bean Validationハンドラ」がフォームに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出され、後続処理には進まない
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティクラスに変換する
- `UniversalDao.insert(entity)` — エンティティをDBに登録する
- 戻り値に `HttpResponse(201)` を返すことでリソース作成完了（`201 Created`）をクライアントに伝える

**③ メソッドシグネチャの選択指針**

| 引数の型 | 用途 |
|---|---|
| フォーム(Java Beans) | JSONリクエストボディを受け取る場合（本ケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | JSONボディ + パスパラメータが両方必要な場合 |

**注意点**:
- フォームのプロパティは全て `String` 型で宣言する必要がある
- `@QueryParam` や `@PathParam`（Jakarta RESTful Web Services規定のアノテーション）は使用できない。パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4