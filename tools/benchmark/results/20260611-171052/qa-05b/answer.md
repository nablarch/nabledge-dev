**結論**: RESTfulウェブサービスでJSON受信→DB登録を実装するには、リソースクラスのメソッドに`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid`の3アノテーションを付与し、フォームを引数に受け取って`UniversalDao.insert()`でDB登録するのが基本パターン。

**根拠**:

### 1. フォームクラスの作成

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する

### 2. リソースクラスのメソッド実装

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
- `@Path("/projects")` + `@POST` : POSTリクエスト時にマッピングするメソッドを定義
- `@Consumes(MediaType.APPLICATION_JSON)` : リクエストボディをJSON形式で受け取ることを指定。Content-Typeが一致しない場合はステータスコード415を返却
- `@Valid` : フォームのBean Validationを実行。バリデーションエラー時はApplicationExceptionをスローして後続処理を終了

登録処理:
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換
- `UniversalDao.insert()` でDB登録
- 戻り値はリソース作成完了を示すステータスコード201(CREATED)のHttpResponse

### 3. メソッド引数と戻り値の選択肢

**メソッド引数**:

| 型 | 用途 |
|---|---|
| フォーム(Java Beans) | JSONリクエストボディを変換して受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータを使う場合 |
| `ExecutionContext` | スコープ変数にアクセスしたい場合 |
| 組み合わせ | 上記を複数指定可能（例: `save(ProjectForm form, JaxRsHttpRequest request)`） |

**メソッド戻り値**:

| 型 | 意味 |
|---|---|
| `void` | 204 NoContentを返却 |
| フォーム(Java Beans) | レスポンスボディに変換してクライアントに返却 |
| `HttpResponse` | 任意のステータスコードとともに返却 |

**注意点**:
- フォームのプロパティは全てString型で宣言すること（Bean Validationのルール）
- Jakarta RESTful Web Servicesの`@PathParam`は使用不可。パスパラメータは`JaxRsHttpRequest#getPathParam()`で取得すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8