**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスを定義してリソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**1. Formクラスの作成**

クライアントから受け取る値を受け付けるFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

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
- `@Path` アノテーションでURLとのマッピングを定義する
- `@POST` アノテーションでPOSTリクエストと紐づける
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを指定する。これによりリクエストボディ変換ハンドラがJSONをFormに変換する
- `@Valid` アノテーションでリクエストのバリデーションを実行する
- `BeanUtil.createAndCopy` でFormをエンティティに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値としてリソース作成完了を示すステータスコード `201` を返却する

**3. メソッドシグネチャの選択肢**

リソースクラスのメソッド引数には以下が使用できる:

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディをFormに変換して受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 複数を組み合わせることも可能 |

**注意点**:
- `@Consumes` に設定したMIMEとリクエストヘッダの `Content-Type` が一致しない場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却される
- JBoss/WildflyではPathアノテーションによるルーティングが使用できない場合があるため、その場合はXMLによるルーティング定義を使用すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s8