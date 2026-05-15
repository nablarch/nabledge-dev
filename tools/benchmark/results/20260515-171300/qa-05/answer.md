**結論**: REST APIでJSONを受け取ってDBに登録するには、リソースクラスに`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`を付けたメソッドを実装し、`BeanUtil`でフォームをエンティティに変換して`UniversalDao.insert()`を呼ぶ。

**根拠**:

### 1. フォームクラスの作成

リクエストJSONを受け取るフォームクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

### 2. リソースクラスの実装

`@Path` でURLマッピングを定義し、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` でJSONのPOSTリクエストを受け付ける。

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
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストをJSON形式で受け付けるための必須指定
- `@Valid` — リクエストのBean Validationを自動実行（Jakarta RESTful Web Services Bean Validationハンドラが処理）
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティに変換
- `UniversalDao.insert()` — DBへの登録
- 戻り値は `HttpResponse(201)` — リソース作成完了を示す

### 3. メソッド引数・戻り値の選択肢

メソッド引数:
- フォーム（Java Beans）: リクエストボディからの変換（JSON登録はこれを使用）
- `JaxRsHttpRequest`: パスパラメータ・クエリパラメータ・HTTPヘッダが必要な場合
- `ExecutionContext`: スコープ変数にアクセスしたい場合
- 組み合わせ: 例 `save(ProjectForm form, JaxRsHttpRequest request)`

戻り値:
- `HttpResponse`: ステータスコードを明示的に指定（登録では201推奨）
- `void`: 204 NoContent を返す
- フォーム（Java Beans）: レスポンスボディにJSONで出力

**注意点**:

- `@Path`アノテーションによるルーティングを使用する場合、ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更する必要がある（従来の `RoutesMapping` から切り替え）
- Jakarta RESTful Web Servicesの `@PathParam`・`@QueryParam` はNablarchでは使用できない。パスパラメータ取得は `JaxRsHttpRequest#getPathParam()` を使うこと
- JBoss/WildflyではPathアノテーションによるルーティングが使用不可。その場合はXML（routes.xml）でマッピングを定義する

参照: `restful-web-service-getting-started-create.json#s1`, `restful-web-service-resource-signature.json#s1`, `adapters-router-adaptor.json#s8`