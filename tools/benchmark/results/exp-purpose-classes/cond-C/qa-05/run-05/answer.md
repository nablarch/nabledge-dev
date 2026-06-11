**結論**: リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付けたメソッドを定義し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換後、`UniversalDao.insert()` でDBに登録し、ステータス `201` の `HttpResponse` を返す。

---

**根拠**:

**1. フォームクラスの作成**

クライアントから受け取るJSONのフィールドに対応するフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソース(アクション)クラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` ― リクエストボディをJSON形式で受け付ける指定。リクエストボディ変換ハンドラ（`BodyConvertHandler`）がこのアノテーションを参照してFormへの変換を行う
- `@Valid` ― Jakarta RESTful Web Services Bean Validationハンドラがこのアノテーションを検知してFormに対してBean Validationを実行する
- `@Path("/projects")` と `@POST` ― `POST /projects` へのリクエストをこのメソッドにマッピングする（ルーティングアダプタが`@Path`アノテーションを解析）
- `BeanUtil.createAndCopy(Project.class, project)` ― フォームからエンティティへの変換
- `UniversalDao.insert(...)` ― エンティティをDBに登録
- 戻り値 ― リソース作成完了を示すステータスコード `201` を持つ `HttpResponse` を返す

**3. URL マッピングの設定（`@Path`アノテーション方式）**

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定した場合、クラスに付けた `@Path` アノテーションとメソッドに付けた `@POST` などのHTTPメソッドアノテーションが自動的に読み込まれ、URLとメソッドが紐づけられる。

---

**注意点**:

- フォームのプロパティは全て `String` 型で宣言すること（Bean Validationのルール）
- バリデーションエラー時は `ApplicationException` が送出され、後続の `UniversalDao.insert()` は実行されない
- `@Consumes` に設定されたMIMEとリクエストの `Content-Type` が異なる場合はステータスコード `415` が返却される

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-resource-signature.json:s1`, `handlers-body-convert-handler.json:s5`, `handlers-jaxrs-bean-validation-handler.json:s4`, `adapters-router-adaptor.json:s8`