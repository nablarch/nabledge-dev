**結論**: リソースクラスに `@Path` + `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` を付与し、メソッド引数にフォームクラスを定義することで、JSON ボディを受け取って DB に登録できます。

**根拠**:

**1. フォームクラスの作成**

JSON のフィールドに対応するプロパティを持つ Form クラスを作成します。プロパティは全て `String` 型で宣言します。

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

実装のポイント:

- `@Path` アノテーションでクラスに URL を対応付ける
- `@POST` アノテーションで HTTP メソッドとマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラが JSON → Form の変換を行う
- `@Valid` アノテーションを設定することで、Jakarta RESTful Web Services Bean Validation ハンドラがフォームのバリデーションを実行する。バリデーションエラーの場合は `ApplicationException` が送出される
- `BeanUtil.createAndCopy` でフォームをエンティティに変換後、`UniversalDao.insert` で DB に登録する
- 戻り値は `HttpResponse` でステータスコード `201 Created` を返す

**メソッド引数と戻り値の型まとめ**:

| 引数 | 説明 |
|---|---|
| フォーム (Java Beans) | リクエストボディから変換したフォームを受け取る |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータが必要な場合に追加で定義 |

| 戻り値 | 説明 |
|---|---|
| `HttpResponse` | ステータスコードを明示して返す場合 |
| フォーム (Java Beans) | レスポンスボディに JSON を返す場合（`@Produces` と組み合わせ） |
| `void` | レスポンスボディが空（204 NoContent）の場合 |

**注意点**:
- `@Consumes` に指定した MIME と異なる `Content-Type` がリクエストに設定されている場合、ステータスコード `415` が返却される
- リクエストボディ変換ハンドラはルーティングアダプタより後ろに、Bean Validation ハンドラはリクエストボディ変換ハンドラより後ろにハンドラキューを設定する必要がある
- Jakarta RESTful Web Services の `@PathParam` / `@QueryParam` アノテーションは使用できないので注意

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8