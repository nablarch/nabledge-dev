**結論**: REST APIでJSONを受け取ってDBに登録するには、アクションクラスに `@Path`・`@POST`・`@Consumes(APPLICATION_JSON)` アノテーションを付与したメソッドを実装し、`UniversalDao.insert()` でDB登録します。

**根拠**:

**1. フォームクラスの作成**

リクエストボディのJSONを受け取るフォームを定義します。プロパティは全て `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

**2. リソースクラス（アクションクラス）の実装**

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

**実装のポイント**:
- `@Path("/projects")` でURLマッピングを定義
- `@POST` でHTTPメソッドをPOSTに限定
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBeanValidationを実行
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録
- 戻り値は `HttpResponse.Status.CREATED`（ステータスコード201）を返却

**3. メソッドシグネチャの選択肢**

| 引数定義 | 用途 |
|---|---|
| フォーム（Java Beans）| リクエストボディから変換した値を処理する（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 複数の型を同時に定義可能 |

**注意点**:
- `@Context` アノテーションによるServletリソースのインジェクションは使用不可（Nablarchのウェブアプリベースのため）
- Jakarta RESTful Web Servicesで規定されている `@PathParam`・`@QueryParam` は使用不可。パラメータ取得には `JaxRsHttpRequest` を使うこと
- DB処理にはハンドラキューに **データベース接続管理ハンドラ** と **トランザクション制御ハンドラ** が必要（最小ハンドラ構成：GlobalErrorHandler → JaxRsResponseHandler → DB接続管理 → トランザクション制御 → ルーティング → BodyConvertHandler → BeanValidationハンドラ）
- `@Valid` を使ったバリデーションは **Jakarta RESTful Web Services Bean Validationハンドラ** がハンドラキューに設定されていることが前提

**参照**:
- `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json#s1`
- `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s1`
- `processing-pattern/restful-web-service/restful-web-service-architecture.json#s4`