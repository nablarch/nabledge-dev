**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラスに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを定義し、`BeanUtil.createAndCopy` でエンティティに変換後 `UniversalDao.insert` で登録します。

**根拠**:

**1. フォームクラスの作成**

リクエストのJSONを受け取るフォームクラスを作成します。**プロパティは全てString型で宣言すること**がポイントです。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスのアクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディがJSON形式として受け付けられ、`BodyConvertHandler` がフォームに変換する
- `@Valid` を付けることで、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを実行する（バリデーションエラー時は `ApplicationException` が送出される）
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED.getStatusCode()` （ステータスコード `201`）を返す

**3. メソッドシグネチャのまとめ**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディから変換したフォームを受け取る（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータが必要な場合 |
| `ExecutionContext` | スコープ変数にアクセスしたい場合 |
| 組み合わせ | 複数を同時に定義可能 |

戻り値は `HttpResponse`（ステータスコード指定あり）、`void`（204 NoContent）、またはフォーム（レスポンスボディに変換）が使用できます。

**注意点**:
- フォームのプロパティは全てString型で宣言すること（Nablarchの制約）
- JSON変換には `bodyConverters` に `Jackson2BodyConverter` などJSON対応のコンバータが設定されている必要がある
- `@Path` のURLアノテーションによるマッピングには「ルーティングアダプタ」の設定が必要

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4