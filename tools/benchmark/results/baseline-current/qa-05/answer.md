**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、フォームを引数として受け取り、`BeanUtil` でエンティティに変換後 `UniversalDao.insert()` で登録する。

**根拠**:

**リソースクラスの実装パターン（全体像）**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

**① フォームクラスの作成**

JSONリクエストを受け取るフォームを Java Beans として定義する。プロパティは全て `String` 型で宣言し、アノテーションでバリデーションルールを設定する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

**② メソッド引数と戻り値**

| 引数定義 | 使用場面 |
|---|---|
| フォーム (Java Beans) | リクエストボディから変換したフォームを処理する場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | 上記を複数必要とする場合 |

戻り値に `HttpResponse` を返す場合はステータスコードを明示指定できる。登録完了は `201 Created` を返すのが典型。

**③ BodyConvertHandler の役割**

`@Consumes(MediaType.APPLICATION_JSON)` を設定すると、`BodyConvertHandler` がリクエストボディを自動的にフォームへ変換する。Content-Type が `application/json` と一致しない場合は `415 Unsupported Media Type` が返却される。

**注意点**:

- フォームのプロパティは**全て `String` 型**で宣言すること（バリデーション仕様上の制約）
- `@Valid` アノテーションを付与することでリクエストのバリデーションが実行される（`JaxRsBeanValidationHandler` が動作）
- Jakarta RESTful Web Services 標準の `@PathParam` / `@QueryParam` は**使用不可**。パスパラメータは `JaxRsHttpRequest` から取得すること
- `BodyConvertHandler` は `RoutingJobRequestFactory`（ルーティングアダプタ）よりも**後ろ**に設定する必要がある
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換してから `UniversalDao.insert()` に渡す

参照: `restful-web-service-getting-started-create.json#s1`, `restful-web-service-resource-signature.json#s1`, `handlers-body-convert-handler.json#s5`