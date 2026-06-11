**結論**: REST APIでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付け、フォームを引数に取って `UniversalDao.insert()` でDB登録する。

**根拠**:

**① フォームクラスの作成**

クライアントから送信されたJSONを受け付けるフォームを作成する。プロパティは全てString型で宣言する。

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

- **`@Consumes(MediaType.APPLICATION_JSON)`**: リクエストをJSON形式で受け付けるために指定する。リクエストボディ変換ハンドラが、このアノテーションを元にJSONをフォームオブジェクトに変換する。
- **`@Valid`**: フォームに対してBean Validationを実行するために指定する。バリデーションエラーが発生した場合は `ApplicationException` が送出される。
- **`BeanUtil.createAndCopy(Project.class, project)`**: フォームをエンティティに変換する。
- **`UniversalDao.insert()`**: エンティティをDBに登録する。
- **戻り値**: リソース作成完了（ステータスコード `201`）を表す `HttpResponse` を返却する。

**③ メソッドの引数の組み合わせ**

| 引数の型 | 使用場面 |
|---|---|
| フォーム (Java Beans) | リクエストボディから変換したフォームで処理する場合（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| 組み合わせ | `public HttpResponse sample(SampleForm form, JaxRsHttpRequest request)` のように両方定義可能 |

**注意点**:
- `@Consumes` に設定されたMIMEと異なるContent-Typeがリクエストヘッダに設定されていた場合、ステータスコード `415` (Unsupported Media Type) が返却される。
- URLとのマッピングには `@Path`・`@POST` アノテーション（ルーティングアダプタ経由）を使用する。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4