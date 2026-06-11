**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、引数にFormクラスを取って `UniversalDao.insert()` で登録します。

**根拠**:

**① フォームクラスの作成**

リクエストボディのJSONを受け取るFormを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラがJSONをFormに変換する
- `@Valid` を指定することで、Jakarta RESTful Web Services Bean ValidationハンドラがFormのバリデーションを自動実行する（エラー時は `ApplicationException` を送出）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値に `HttpResponse` でステータスコード `201`（Created）を返却する

**メソッド引数・戻り値の使い分け**:

| 引数 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディから変換したFormで処理する場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを扱う場合 |
| 組み合わせ | `save(SampleForm form, JaxRsHttpRequest request)` のように併用可能 |

| 戻り値 | レスポンス |
|---|---|
| `HttpResponse` | 指定したステータスコードとボディを返却 |
| フォーム(Java Beans) | ボディ変換ハンドラがJSONに変換して返却 |
| `void` | 204 No Content を返却 |

**注意点**: `@Valid` アノテーションでバリデーションを有効にするには、リクエストボディ変換ハンドラの後段にJakarta RESTful Web Services Bean Validationハンドラを設定する必要があります。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4