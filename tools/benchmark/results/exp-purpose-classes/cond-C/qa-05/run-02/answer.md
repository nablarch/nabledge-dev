**結論**: リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付けてFormを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDBに登録し、ステータスコード201の `HttpResponse` を返すのが標準パターンです。

**根拠**:

**Formクラスの作成**

JSONのフィールドを受け付けるFormクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**リソースクラス（アクションメソッド）の実装**

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

各ポイントの説明:

| アノテーション/API | 役割 |
|---|---|
| `@Path("/projects")` | クラスに付与してURLプレフィックスを定義 |
| `@POST` | POSTリクエストにこのメソッドをマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付け、BodyConvertHandlerがFormに変換 |
| `@Valid` | JaxRsBeanValidationHandlerがFormに対してBean Validationを実行。エラー時は`ApplicationException`を送出 |
| `BeanUtil.createAndCopy()` | FormをエンティティBeanに変換 |
| `UniversalDao.insert()` | エンティティをDBに登録 |
| `HttpResponse.Status.CREATED` | リソース作成完了を表すステータスコード201を返却 |

**メソッドシグネチャの選択肢**

| 引数の型 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディをJSONから変換した値を扱う場合（今回はこちら） |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータを扱う場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 例：`save(ProjectForm form, JaxRsHttpRequest request)` |

**注意点**:
- Formのプロパティは全てString型で宣言すること（型変換はBean Validationの仕組みが行う）
- `@Valid` は`@Consumes`を指定してFormを引数に取るメソッドにのみ機能する（BodyConvertHandlerがFormに変換した後にBeanValidationHandlerが処理するため）
- ルーティングアダプタとして `PathOptionsProviderRoutesMapping` を使用する場合は、`@Path` アノテーションが有効になる設定が必要

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8