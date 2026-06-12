十分な情報が揃いました。Step 5: 回答を生成します。

**verify:** すべてのNablarch固有のクレームはsections_contentに直接記載されています。PASS。

---

**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` アノテーションを付与したメソッドを実装し、`BeanUtil.createAndCopy` でFormをエンティティに変換後、`UniversalDao.insert` でDB登録する。

**根拠**:

### 1. フォームクラスの作成

リクエストボディを受け取るFormクラスを作成する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

### 2. リソースクラスのメソッド実装

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

- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストをJSON形式で受け付けることを指定する。リクエストボディはリクエストボディ変換ハンドラ（`BodyConvertHandler`）によって自動的にFormオブジェクトに変換される
- `@Valid` — Jakarta RESTful Web Services Bean ValidationハンドラがFormに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` を送出して処理を終了する
- `BeanUtil.createAndCopy(Project.class, project)` — FormをEntityに変換する
- `UniversalDao.insert(...)` — エンティティをDBに登録する
- 戻り値は `HttpResponse(201)` — リソース作成完了（Created）を示す

### 3. URLマッピングの定義（`@Path` アノテーション方式）

クラスに `@Path`、メソッドに `@POST` を付与することで、ルーティングアダプタがURLとメソッドを自動マッピングする。

```java
@Path("/projects")         // ← クラスレベルのパス
public class ProjectAction {

    @POST                  // ← POSTリクエストにマッピング
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) { ... }
}
```

### リソースクラスメソッドのシグネチャ一覧

| 引数の型 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディのJSON → Form変換 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダの取得 |
| `ExecutionContext` | スコープ変数へのアクセス |
| 組み合わせ | 上記を複数指定可能 |

| 戻り値の型 | 挙動 |
|---|---|
| `void` | ステータスコード `204 NoContent` を返却 |
| フォーム(Java Beans) | レスポンスボディに変換して返却 |
| `HttpResponse` | HttpResponseの内容をそのまま返却 |

**注意点**:
- `@Path` アノテーション方式は JBoss / WildFly では使用不可（vfsファイルシステム非対応）。その場合は `routes.xml` によるXMLマッピングを使用する
- RESTfulウェブサービスでは `@QueryParam` や `@PathParam`（JAX-RS標準）は使用できない。パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で取得する

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-resource-signature.json:s1`, `handlers-body-convert-handler.json:s5`, `handlers-jaxrs-bean-validation-handler.json:s4`, `adapters-router-adaptor.json:s6`, `adapters-router-adaptor.json:s8`

---