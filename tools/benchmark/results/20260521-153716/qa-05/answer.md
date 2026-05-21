セクション内容を確認しました。回答を生成します。

---

**結論**: RESTful WebサービスでJSONを受け取りDBに登録するには、`@Path`/`@POST`/`@Consumes(APPLICATION_JSON)`でアノテートしたリソースクラスのメソッドを作成し、`BeanUtil`でFormをEntityに変換後、`UniversalDao.insert()`でDB登録する。

**根拠**:

**1. Formクラスの作成**

リクエストボディのJSONを受け取るFormを作成する。プロパティは全て`String`型で宣言する。

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストボディを受け付ける。`@Path`と`@POST`でURLとHTTPメソッドをマッピングする
- `@Valid` アノテーションで Bean Validation によるバリデーションを実行する
- `BeanUtil.createAndCopy()` でFormをEntityクラスに変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値に `HttpResponse(201)` を返すことで、リソース作成完了を示すステータスコード `201 Created` をクライアントに返す

**メソッドシグネチャのパターン一覧**（用途に合わせて選択）:

| 引数 | 用途 |
|------|------|
| `SampleForm form` | リクエストボディ（JSON等）を受け取る場合 |
| `JaxRsHttpRequest request` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | `save(SampleForm form, JaxRsHttpRequest request)` のように組み合わせ可能 |

| 戻り値 | 意味 |
|--------|------|
| `HttpResponse` | ステータスコードを明示的に指定したいとき（登録: 201等） |
| フォーム (Java Beans) | レスポンスボディにJSONを返すとき（`@Produces`と組み合わせ） |
| `void` | レスポンスボディが空（204 NoContent）のとき |

**注意点**:
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が一致しない場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却される
- Jakarta RESTful Web Servicesの `@QueryParam` / `@PathParam` アノテーションは使用できない。パスパラメータ・クエリパラメータは `JaxRsHttpRequest#getPathParam()` / `getParamMap()` で取得する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s8

---