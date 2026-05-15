**結論**: Nablarch 6でREST APIからJSONを受け取りDBに登録するには、`@Path`・`@POST`・`@Consumes(APPLICATION_JSON)`・`@Valid` アノテーションを組み合わせたリソースクラス（アクションクラス）を実装し、`BeanUtil` でフォームをエンティティに変換して `UniversalDao.insert()` で登録します。

**根拠**:

### 実装の全体像

3つのクラスを作成します。

**1. フォームクラス（リクエストボディのマッピング先）**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ・セッタは省略
}
```

- プロパティは全て `String` 型で宣言する

**2. リソースクラス（アクションクラス）**

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

各アノテーションの役割：
| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | URLとのマッピング（ルーティングアダプタと連携） |
| `@POST` | POSTリクエストにバインド |
| `@Consumes(APPLICATION_JSON)` | リクエストボディをJSON形式で受け付ける |
| `@Valid` | リクエストのBeanValidationを実行する |

処理の流れ：
1. `@Consumes(APPLICATION_JSON)` → リクエストボディをJSONとして受け付け、`BodyConvertHandler` が `ProjectForm` に変換
2. `@Valid` → `JaxRsBeanValidationHandler` がバリデーションを実行
3. `BeanUtil.createAndCopy(Project.class, project)` → フォームをエンティティに変換
4. `UniversalDao.insert(...)` → DB登録
5. `HttpResponse(201)` → 作成完了レスポンスを返却

**3. メソッドシグネチャのバリエーション**

用途に応じて引数を組み合わせられます：

| 引数定義 | 使いどころ |
|---|---|
| `save(ProjectForm form)` | リクエストボディのみ使う場合 |
| `save(ProjectForm form, JaxRsHttpRequest request)` | ヘッダやパスパラメータも使う場合 |
| `save(JaxRsHttpRequest request)` | フォーム不要でリクエスト情報のみ使う場合 |

戻り値は `HttpResponse`（ステータスコード制御が必要な場合）または フォームクラス（レスポンスボディを返す場合）を使います。

**注意点**:

- **ハンドラキューの設定が必要**: DB登録には最低限、**データベース接続管理ハンドラ**（DB接続の取得・解放）と**トランザクション制御ハンドラ**（コミット・ロールバック）をハンドラキューに設定する必要があります。`Jakarta RESTful Web Servicesアダプタ`を使用すれば `BodyConvertHandler` と `JaxRsBeanValidationHandler` は自動追加されます。
- **エンティティのJakarta Persistenceアノテーション**: `UniversalDao.insert()` を使うには、エンティティクラスに `@Table`・`@Id` 等のJakarta Persistenceアノテーションを付ける必要があります。
- **スキーマの環境切り替えには非対応**: `UniversalDao` のCRUD機能は `@Table` でスキーマ指定できますが、環境毎のスキーマ切り替えは非対応です。その場合はJDBCラッパーを使用してください。

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json#s1`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s1`, `processing-pattern/restful-web-service/restful-web-service-architecture.json#s4`, `component/libraries/libraries-universal-dao.json#s2`