**結論**: リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、引数としてフォームを受け取る。`BeanUtil.createAndCopy` でエンティティに変換して `UniversalDao.insert` でDB登録し、`HttpResponse`（ステータス201）を返す。

**根拠**:

**1. フォームクラスの作成**

リクエストのJSONをバインドするフォームを作成する。プロパティは全てString型で宣言する。

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディがJSONとして `BodyConvertHandler` によりフォームに変換される
- `@Valid` でリクエストのバリデーションを実行する（`JaxRsBeanValidationHandler` が処理）
- `BeanUtil.createAndCopy` でフォームをエンティティに変換してから `UniversalDao.insert` でDB登録する
- 登録完了を示すステータスコード `201` を `HttpResponse` で返却する

**3. メソッドシグネチャのパターン**

| 引数定義 | 用途 |
|---|---|
| フォーム（Java Beans） | リクエストボディから変換したフォームで処理する場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | フォームとJaxRsHttpRequestを同時に受け取ることも可能 |

戻り値は `HttpResponse`（ステータスコードを明示する場合）または `void`（204 NoContentを返す場合）を使用する。

**注意点**:
- フォームのプロパティは全てString型で宣言すること
- `@Path` アノテーションでURLマッピングを定義し、`@POST` で対象HTTPメソッドを指定する
- JSON変換には対応した `BodyConverter`（`Jackson2BodyConverter` など）を `BodyConvertHandler` の `bodyConverters` プロパティに設定しておく必要がある

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5