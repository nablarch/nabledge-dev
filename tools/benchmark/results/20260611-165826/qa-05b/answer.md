**結論**: RESTful ウェブサービスでJSON受信・DB登録を行うには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` をメソッドに付加し、引数にフォームを受け取って `BeanUtil.createAndCopy` でエンティティに変換後 `UniversalDao.insert` で登録します。

**根拠**:

**① フォームクラスの作成**

リクエストボディのJSONを受け取るフォームを作成します。プロパティは**全てString型**で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストボディを受け付けることを宣言する。リクエストボディ変換ハンドラがこのアノテーションに基づいてフォームへの変換を行う
- `@Valid` でBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換する
- `UniversalDao.insert()` でデータベースに登録する
- 戻り値はリソース作成完了を示す `201 Created` の `HttpResponse` を返す
- `@Path` と `@POST` でURLとメソッドのマッピングを定義する

**③ メソッドのシグネチャ**

引数には以下の型を使用できます：

| 引数定義 | 用途 |
|---|---|
| フォーム (Java Beans) | リクエストボディから変換したフォームを受け取る（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータ、クエリパラメータ、HTTPヘッダを取得する場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 例: `public HttpResponse save(SampleForm form, JaxRsHttpRequest request)` |

**注意点**:
- フォームのプロパティは必ず全てString型で宣言すること（Bean Validationの仕様による）
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード `415` が返却される
- JSON変換には `Jackson2BodyConverter` などのBodyConverterをハンドラ設定の `bodyConverters` に含める必要がある

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5