**結論**: リソースクラスのPOSTメソッドに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、引数にフォームクラスを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDB登録するのが基本パターンです。

**根拠**:

#### 1. フォームクラスの作成

クライアントから受け取るJSONのフィールドに対応するフォームクラスを作成します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> **ポイント**: フォームのプロパティは**全てString型**で宣言します。

---

#### 2. リソースクラスの実装

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

各アノテーションの役割:

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | URLとリソースクラスをマッピングする |
| `@POST` | POSTリクエスト時にこのメソッドを呼び出すことを定義する |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSONフォーマットのリクエストを受け付けることを宣言する |
| `@Valid` | リクエストボディをFormに変換後、Bean Validationを実行する |

戻り値の `HttpResponse(201)` はリソース作成完了を示します。

---

#### 3. 処理の流れ（仕組み）

```
クライアント
    ↓ POST /projects (JSON body)
WebFrontController (Servletフィルタ)
    ↓
ハンドラキュー
    ↓ [RoutesMapping] URLからアクションメソッドを特定
    ↓ [BodyConvertHandler] JSONボディを ProjectForm に変換
    ↓ [JaxRsBeanValidationHandler] @Valid に基づきバリデーション実行
    ↓
ProjectAction#save(ProjectForm)
    ↓ BeanUtil.createAndCopy() でフォーム→エンティティ変換
    ↓ UniversalDao.insert() でDB登録
    ↓ return new HttpResponse(201)
    ↓
JaxRsResponseHandler → クライアントへ 201 返却
```

ハンドラキューの最小構成（DB登録に必要な部分）:

| No. | ハンドラ | 役割 |
|---|---|---|
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URLからアクションメソッドを特定 |
| 6 | リクエストボディ変換ハンドラ | JSONボディ→フォームクラスへ変換 |
| 7 | Bean Validationハンドラ | `@Valid` によるバリデーション実行 |

---

#### 4. メソッドシグネチャの選択肢

| 引数の型 | 使いどき |
|---|---|
| フォーム(Java Beans) | リクエストボディからJSONを受け取る場合（今回のパターン） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得したい場合 |
| 引数なし | パラメータ不要な場合 |
| 組み合わせ | `(ProjectForm form, JaxRsHttpRequest request)` のように組み合わせ可能 |

| 戻り値の型 | 意味 |
|---|---|
| `HttpResponse` | 任意のステータスコードを返す（201 Created など） |
| `void` | 204 NoContent を返す |
| フォーム(Java Beans) | レスポンスボディにJSONとして変換して返す |

**注意点**:
- `@Consumes` に設定したMIMEタイプとリクエストの `Content-Type` が異なる場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却されます。
- パスパラメータの取得には Jakarta RESTful Web Services の `@PathParam` は使用できません。`JaxRsHttpRequest#getPathParam()` を使用してください。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4