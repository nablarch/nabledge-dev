**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDB登録するには、アクションクラスに `@POST` / `@Consumes(MediaType.APPLICATION_JSON)` / `@Valid` を付けたメソッドを実装し、`BeanUtil.createAndCopy()` でFormをEntityに変換して `UniversalDao.insert()` でDBに登録する。

**根拠**:

**処理の流れ（仕組み）**

リクエストが届いてからDB登録されるまでの流れは次の通り：

1. `WebFrontController`（ServletFilter）がPOSTリクエストを受信
2. ハンドラキューに処理を委譲
3. **BodyConvertHandler** — `@Consumes(MediaType.APPLICATION_JSON)` の情報をもとに、リクエストボディ（JSON）をアクションが受け取る**Formクラスに変換**する
4. **JaxRsBeanValidationHandler** — `@Valid` アノテーションが付いたメソッドに対し、変換されたFormクラスに**Bean Validationを実行**する（バリデーションエラー時は `ApplicationException` を送出）
5. アクションメソッドが呼び出され、Formをエンティティに変換して `UniversalDao.insert()` でDB登録
6. **JaxRsResponseHandler** がレスポンスをクライアントへ返却

**最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続取得／解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | RoutesMapping（ルーティングアダプタ） | URIからアクションを特定 |
| 6 | **BodyConvertHandler** | JSON ↔ Form変換 |
| 7 | **JaxRsBeanValidationHandler** | Formのバリデーション |

> BodyConvertHandlerとBeanValidationHandlerは、**ルーティングアダプタより後ろ**に設定する（Jerseyアダプタ使用時は自動設定される）。

**JSONコンバータの仕組み**

JerseyまたはRESTEasyアダプタを使用する場合、`Jackson2BodyConverter` が `application/json` の変換を担当する。`@Consumes` で指定したMIMEとリクエストの `Content-Type` が一致しない場合はHTTP `415` を返却する。

**アクション実装例**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)  // JSONを受け付ける
    @Valid                                  // Bean Validationを実行する
    public HttpResponse save(ProjectForm project) {
        // FormをEntityに変換してDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        // 201 Created を返す
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

**Formクラス**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する

    // getter/setter省略
}
```

**注意点**:
- Formのプロパティは**全てString型**で宣言する（Bean Validationの仕様上の制約）
- `@Valid` アノテーションを付けることでバリデーションが自動実行される。アノテーションがない場合はバリデーションはスキップされる
- `BodyConvertHandler` は `RoutesMapping`（ルーティングアダプタ）**より後ろ**に配置する必要がある

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2