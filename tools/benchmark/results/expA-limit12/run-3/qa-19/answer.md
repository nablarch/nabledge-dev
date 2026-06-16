**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付け、引数のFormクラスを受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

### 全体の処理の流れ

リクエストはハンドラキューを順に通過して処理される。

1. `JaxRsResponseHandler` — レスポンスの生成
2. `DbConnectionManagementHandler` — DB接続の取得・解放
3. `TransactionManagementHandler` — トランザクション開始・コミット（例外時はロールバック）
4. `RoutesMapping`（ルーティングアダプタ） — URIからアクションを特定
5. `BodyConvertHandler` — **リクエストボディ（JSON）をFormクラスに変換**（往路）
6. `JaxRsBeanValidationHandler` — Formに対してBean Validationを実行

`BodyConvertHandler` の中では `Jackson2BodyConverter` がJSON変換を担当する。アクションメソッドの `@Consumes` アノテーションで指定されたMIMEタイプと一致するコンバータが自動選択される。

### アクション実装例

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

- `@Consumes(MediaType.APPLICATION_JSON)` — このメソッドが `application/json` を受け付けることを宣言。`BodyConvertHandler` はこのアノテーションを見てJSONコンバータを選択する。
- `@Valid` — `JaxRsBeanValidationHandler` がFormに対してバリデーションを実行する。
- `BeanUtil.createAndCopy(Project.class, project)` — Formのプロパティ値をEntityにコピーして変換する。
- `UniversalDao.insert(entity)` — EntityのJakarta Persistenceアノテーション（`@Table`, `@Column` 等）を元にINSERT文を自動生成してDB登録する。
- 戻り値は `HttpResponse(201)` — リソース作成完了を示すステータスコードを返す。

### Formクラスの宣言ルール

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

**注意点**: `BodyConvertHandler` に設定されたJSONコンバータ（`Jackson2BodyConverter`）がサポートしていないMIMEタイプがリクエストの `Content-Type` に指定された場合、ステータスコード `415`（Unsupported Media Type）が返却される。

参照: processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, component/libraries/libraries-universal-dao.json:s2