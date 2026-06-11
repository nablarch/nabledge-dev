**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスを作成し、リソース（アクション）クラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与して `UniversalDao.insert()` でDB登録し、`HttpResponse(201)` を返す実装パターンを使用する。

---

**根拠**:

**1. Formクラスの作成**

クライアントから送信されたJSONを受け取るFormクラスを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する。

**2. リソースクラス（アクションメソッド）の実装**

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

各アノテーション・APIの役割:

| 要素 | 役割 |
|------|------|
| `@Path("/projects")` | URLとのマッピングを定義（ルーティングアダプタ使用） |
| `@POST` | POSTリクエスト時にこのメソッドを呼び出す |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSONリクエストボディをFormに変換するようBodyConvertHandlerに指示 |
| `@Valid` | JaxRsBeanValidationHandlerにFormのバリデーション実行を指示 |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをEntityクラスに変換 |
| `UniversalDao.insert(...)` | Entityをデータベースに登録 |
| `HttpResponse(201)` | リソース作成完了（CREATED）をクライアントに返却 |

**3. 処理の仕組み（ハンドラキューの流れ）**

```
リクエスト受信
  → WebFrontController
  → グローバルエラーハンドラ
  → JaxRsResponseHandler（レスポンス書き込み・エラー変換）
  → DB接続管理ハンドラ（接続取得/解放）
  → トランザクション制御ハンドラ（開始/コミット/ロールバック）
  → ルーティングアダプタ（URLからアクションを特定）
  → BodyConvertHandler（JSONボディ → Formに変換）  ← @Consumesで制御
  → JaxRsBeanValidationHandler（Formのバリデーション）  ← @Validで制御
  → アクションメソッド（業務ロジック実行）
```

- `BodyConvertHandler` はアクションメソッドの `@Consumes` の値（`application/json`）に対応する `BodyConverter` を使ってJSONをFormに変換する
- `JaxRsBeanValidationHandler` は `@Valid` が設定されたメソッドのFormに対してBean Validationを実行し、エラー時は `ApplicationException` を送出して後続処理を行わない

---

**注意点**:
- `BodyConvertHandler` と `JaxRsBeanValidationHandler` は、**ルーティングアダプタより後ろ**に設定する必要がある（アクションメソッドのアノテーション情報が必要なため）
- `@Consumes` に設定したMIMEと、リクエストヘッダの `Content-Type` が異なる場合、ステータスコード `415`（Unsupported Media Type）が返却される
- Formのプロパティは全てString型で宣言すること（バリデーションルール設定の制約）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4