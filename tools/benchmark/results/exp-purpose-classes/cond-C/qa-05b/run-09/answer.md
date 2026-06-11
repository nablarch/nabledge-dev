**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、リソースクラスのメソッドにFormをフォーム引数として受け取り、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` を呼び出す。

**根拠**:

**1. Formクラスの作成**

リクエストボディを受け付けるFormを作成する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
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

| 要素 | 説明 |
|---|---|
| `@Path("/projects")` | クラスにパスを設定してURLとのマッピングを定義する |
| `@POST` | POSTリクエスト時に呼び出すメソッドを指定する |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストをJSON形式で受け付けるために指定する |
| `@Valid` | リクエストのBean Validationを実行する（`JaxRsBeanValidationHandler` が処理） |
| メソッド引数 `ProjectForm project` | リクエストボディが `BodyConvertHandler` によって自動的にFormオブジェクトに変換される |
| `BeanUtil.createAndCopy()` | フォームをエンティティに変換する |
| `UniversalDao.insert()` | エンティティをDBに登録する |
| 戻り値 `201 CREATED` | リソース作成完了を示すステータスコードを返却する |

**3. メソッドシグネチャのバリエーション**

| 引数定義 | 説明 |
|---|---|
| `Form form` | リクエストボディをFormに変換して受け取る（今回のケース） |
| `JaxRsHttpRequest request` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| `Form form, JaxRsHttpRequest request` | 両方を組み合わせて使う場合 |

戻り値は `HttpResponse`（ステータスコード指定可）、または `void`（204 NoContent）、またはFormオブジェクト（レスポンスボディに変換）が使用できる。

**注意点**:
- `@Consumes` のMIMEとリクエストの `Content-Type` が一致しない場合、ステータスコード `415` が返却される
- Jakarta RESTful Web Services標準の `@QueryParam` / `@PathParam` は使用できないため注意

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8