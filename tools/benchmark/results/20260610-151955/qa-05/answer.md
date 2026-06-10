**結論**: `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` をメソッドに付与し、引数にFormクラスを受け取る。メソッド内で `BeanUtil.createAndCopy` によりFormをEntityに変換し、`UniversalDao.insert` でDBに登録する。戻り値は `HttpResponse(201)` を返す。

**根拠**:

**1. フォームクラスの作成**

クライアントから送信されたJSONを受け付けるFormクラスを作成する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する。

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

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付ける指定。
- `@Valid`: Jakarta RESTful Web Servcies Bean Validationハンドラによるバリデーションを実行する。
- `BeanUtil.createAndCopy`: FormをEntityクラスに変換する。
- `UniversalDao.insert`: ユニバーサルDAOを使用してDBに登録する。
- 戻り値: リソースの作成完了（ステータスコード `201`）を表す `HttpResponse` を返却する。

**3. メソッドシグネチャの選択肢**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディ（JSON）から変換したFormを処理する場合（今回のパターン） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | `save(SampleForm form, JaxRsHttpRequest request)` のように併用も可能 |

| 戻り値 | 挙動 |
|---|---|
| `void` | 204 NoContent を返す |
| フォーム(Java Beans) | リクエストボディ変換ハンドラでレスポンスボディに変換される |
| `HttpResponse` | 指定したステータスコードとボディを返す（今回のパターン） |

**注意点**:
- `@Consumes` に設定したMIMEと異なるContent-TypeがリクエストされるとHTTP 415が返却される。
- `@Valid` を使用するには、コンポーネント設定ファイルでJerseyまたはRESTEasy用のアダプタ（`JerseyJaxRsHandlerListFactory` 等）を設定し、Bean Validationハンドラが有効になっている必要がある。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5