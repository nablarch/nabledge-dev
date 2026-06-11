**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、引数にFormクラスを定義し、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` で登録する。

**根拠**:

#### 実装の全体像

**Formクラス** (`ProjectForm.java`):

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
    // ※ プロパティは全てString型で宣言する
}
```

**リソースクラス** (`ProjectAction.java`):

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

#### 各ポイントの解説

| 要素 | 役割 |
|---|---|
| `@Path("/projects")` + `@POST` | URLとメソッドをマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディのJSONをFormに変換するフォーマットを指定 |
| `@Valid` | 引数のFormに対してBean Validationを実行 |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをEntityクラスに変換 |
| `UniversalDao.insert(...)` | DBへの登録 |
| `HttpResponse.Status.CREATED.getStatusCode()` | 201ステータスを返す |

#### メソッドシグネチャの選択肢

| 引数 | 用途 |
|---|---|
| Formクラス (Java Beans) | リクエストボディ（JSON等）をFormに変換して受け取る |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得 |
| `ExecutionContext` | スコープ変数へのアクセス |
| 組み合わせ | 例: `public HttpResponse save(SampleForm form, JaxRsHttpRequest request)` |

| 戻り値 | 動作 |
|---|---|
| `void` | 204 NoContent を返す |
| Formクラス (Java Beans) | Producesで指定したフォーマットに変換してレスポンスボディとして返す |
| `HttpResponse` | HttpResponseの情報をそのまま返す |

**注意点**:
- Formのプロパティはすべて `String` 型で宣言する（Bean Validationの仕様）
- リクエストヘッダの `Content-Type` が `application/json` でない場合、ステータスコード `415` が返る
- `@QueryParam` や `@PathParam`（Jakarta RESTful Web Services標準のアノテーション）は使用できない。パスパラメータは `JaxRsHttpRequest` の `getPathParam()` で取得する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8