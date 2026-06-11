**結論**: リソースクラスに `@Path` / `@POST` / `@Consumes(MediaType.APPLICATION_JSON)` / `@Valid` を付け、`BeanUtil.createAndCopy` でフォームをエンティティへ変換して `UniversalDao.insert` で登録するパターンが基本です。登録完了時はステータスコード `201` を返します。

**根拠**:

**① フォームクラスの作成**

クライアントから受け取る値を保持するフォームを作成します。プロパティは**全て `String` 型**で宣言します（型変換失敗による予期せぬ例外を防ぐため）。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスの実装**

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

| アノテーション / API | 役割 |
|---|---|
| `@Path("/projects")` | クラスをURLパスにマッピング |
| `@POST` | HTTPメソッド `POST` にバインド |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディを `application/json` として受け取り、フォームへ変換 |
| `@Valid` | JaxRs Bean Validationハンドラがフォームのバリデーションを実行 |
| `BeanUtil.createAndCopy(Project.class, project)` | フォームからエンティティへコピー変換 |
| `UniversalDao.insert(...)` | SQLを書かずにDBへ登録 |
| `HttpResponse.Status.CREATED.getStatusCode()` | ステータスコード `201` を返却 |

**③ メソッドシグネチャの選択肢**

リクエストボディを受け取る場合はフォーム(Java Beans)を引数に指定します。パスパラメータやHTTPヘッダも必要な場合は `JaxRsHttpRequest` を追加できます。

```java
// フォームのみ
public HttpResponse save(ProjectForm form) { ... }

// フォーム + リクエスト情報が必要な場合
public HttpResponse save(ProjectForm form, JaxRsHttpRequest request) { ... }
```

**注意点**:
- ユニバーサルDAOを使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要です（`name="daoContextFactory"` で登録）。
- `@Path` アノテーションによるルーティングを使用する場合は、ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更する必要があります。
- Jersey環境では `JerseyJaxRsHandlerListFactory` を設定することで、JSON変換用の `Jackson2BodyConverter` が自動的に組み込まれます。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8, libraries-bean-validation.json:s8, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6