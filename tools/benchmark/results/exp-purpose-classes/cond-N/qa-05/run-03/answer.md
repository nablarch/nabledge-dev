**結論**: REST APIでJSONを受け取ってDBに登録するには、リソースクラスに `@Path`/`@POST`/`@Consumes(MediaType.APPLICATION_JSON)`/`@Valid` を付け、`BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録します。ステータスコード `201` を返す `HttpResponse` を戻り値にします。

---

**根拠**:

#### 1. フォームクラスの作成

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言する（バリデーションルールの設定方法に従う）

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

**実装ポイント**:

- `@Path("/projects")` と `@POST` でPOSTリクエスト時のURLマッピングを定義する
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付ける
- `@Valid` でリクエストのBean Validationを実行する（`JaxRsBeanValidationHandler` が処理する）
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換する
- `UniversalDao.insert()` でDBに登録する
- `HttpResponse.Status.CREATED.getStatusCode()` でステータスコード `201` を返す

---

#### 3. メソッド引数・戻り値の選択肢

| 引数 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディから変換したフォームを処理する場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータを扱う場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 複数の引数型を組み合わせることも可能 |

| 戻り値 | 動作 |
|---|---|
| `HttpResponse` | 指定したステータスコード・ヘッダをクライアントに返却する |
| `void` | `204: NoContent` を返却する |
| フォーム(Java Beans) | `BodyConvertHandler` がレスポンスボディに変換して返却する |

---

**注意点**:
- `@Consumes` と `@Produces` を使用する場合は、`BodyConvertHandler` に対応する `BodyConverter`（JSON用）が設定されていること。対応していないMIMEタイプが指定された場合はステータスコード `415` が返される。
- `@Path` アノテーションによるルーティングは、JBossやWildflyでは使用できない。その場合は `routes.xml` によるXMLマッピングを使用すること。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, adapters-router-adaptor.json:s6, adapters-router-adaptor.json:s8, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5