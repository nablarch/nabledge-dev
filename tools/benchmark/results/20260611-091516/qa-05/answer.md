**結論**: RESTful ウェブサービスでJSON を受け取ってDBに登録するには、リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` アノテーションを付与し、引数にフォームクラスを受け取り、`BeanUtil` でエンティティに変換後 `UniversalDao.insert()` でDBに登録する。

**根拠**:

**フォームクラスの作成**

クライアントから受け取るJSONのフィールドに対応したフォームクラスを作成する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // その他フィールド / ゲッタ・セッタは省略
}
```

**リソースクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディをJSON形式で受け付けることを宣言する。リクエストボディ変換ハンドラがこのアノテーションを見てJSON→Formへの変換を行う。
- `@Valid` — Jakarta RESTful Web Services Bean Validationハンドラによってフォームのバリデーションが実行される。
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティに変換する。
- `UniversalDao.insert(...)` — エンティティをDBに登録する。
- 戻り値は `HttpResponse` を返す。登録完了時はステータスコード `201 (Created)` を返すのが一般的。

**URLマッピング（`@Path` アノテーション使用）**

`@Path` アノテーションでクラスにパスを、`@POST` でHTTPメソッドをマッピングする。これには `PathOptionsProviderRoutesMapping` をディスパッチハンドラとして使用する必要がある（XMLマッピング方式でも可）。

**注意点**:

- `@Consumes` に指定したMIMEとリクエストのContent-Typeが異なる場合、ステータスコード `415 (Unsupported Media Type)` が返却される。
- フォームのプロパティは全て `String` 型で宣言する必要がある。
- `@Valid` によるバリデーションエラーが発生した場合はステータスコード `400` が返却される。
- Jakarta RESTful Web Servicesで規定されている `@QueryParam` や `@PathParam` は使用できない点に注意。

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-resource-signature.json:s1`, `handlers-body-convert-handler.json:s5`