**結論**: NablarchのRESTful Webサービスでは、リソースクラス（アクションクラス）に `@Path` / `@POST` / `@Consumes(MediaType.APPLICATION_JSON)` / `@Valid` を付与し、フォームを引数に受け取って `UniversalDao.insert()` でDBに登録するパターンが標準実装です。

**根拠**:

**① フォームクラスの作成**

リクエストJSONを受け取るフォームクラスをJava Beansとして作成します。プロパティは `String` 型で宣言し、バリデーションアノテーションを付与します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラス（アクションクラス）の実装**

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
- `@Path` にURLパスを定義し、`@POST` でPOSTリクエストにマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付ける
- `@Valid` でリクエストボディのBean Validationを実行（Jakarta RESTful Web Services Bean Validationハンドラが処理）
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換してから `UniversalDao.insert()` でDB登録
- 戻り値は `HttpResponse` でステータスコード `201 Created` を返却

**③ メソッドシグネチャのバリエーション**

| 引数 | 用途 |
|---|---|
| `SampleForm form` | リクエストボディをフォームに変換して受け取る（今回のケース） |
| `JaxRsHttpRequest request` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ `(SampleForm form, JaxRsHttpRequest request)` | 両方必要な場合 |

戻り値は `HttpResponse` （ステータスコードを明示したい場合）か、フォーム（Java Beans）を返す（レスポンスJSONに変換される）ことも可能です。

**④ 必要なハンドラ構成**

DB登録処理には最低限以下のハンドラが必要です：
- **データベース接続管理ハンドラ**: DB接続の取得・解放
- **トランザクション制御ハンドラ**: コミット・ロールバック
- **リクエストボディ変換ハンドラ**: リクエストJSONをフォームクラスに変換
- **Bean Validationハンドラ**: `@Valid` によるバリデーション実行

`Jakarta RESTful Web Servicesアダプタ` を使用すると、リクエストボディ変換ハンドラとBean Validationハンドラが自動的に追加されます。

**注意点**:
- フォームのプロパティは `String` 型で宣言すること（型変換はバリデーション設定で行う）
- `UniversalDao.insert()` を使う場合、エンティティクラスにJakarta Persistenceアノテーション（`@Table`、`@Column` 等）が必要
- `@Table` アノテーションでスキーマ指定はできるが、環境ごとのスキーマ切り替えには対応していないため、その場合はJDBCラッパーを使用すること
- `JaxRsHttpRequest` は後方互換のため `HttpRequest` も使えるが、原則 `JaxRsHttpRequest` を使用すること

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json#s1`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s1`, `component/libraries/libraries-universal-dao.json#s2`, `processing-pattern/restful-web-service/restful-web-service-architecture.json#s4`