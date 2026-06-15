**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションをアクションメソッドに付け、`BodyConvertHandler`（`Jackson2BodyConverter`）でJSONをFormに変換した後、`UniversalDao.insert()` でDB登録する。

**根拠**:

**1. 処理フロー**

```
クライアント
  ↓ POSTリクエスト (application/json)
WebFrontController
  ↓
ハンドラキュー:
  1. グローバルエラーハンドラ
  2. Jakarta RESTful Web Servicesレスポンスハンドラ
  3. データベース接続管理ハンドラ  ← DB接続取得
  4. トランザクション制御ハンドラ  ← トランザクション開始
  5. ルーティングアダプタ          ← URI → アクション特定
  6. リクエストボディ変換ハンドラ  ← JSON → Formクラスに変換
  7. Bean Validationハンドラ      ← バリデーション実行
  ↓
アクションクラス (業務ロジック実行 + UniversalDao.insert)
  ↓
4のハンドラ: トランザクションコミット
```

**2. アクションクラスの実装**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

ポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストのメディアタイプをJSONに指定
- `@Valid` — `JaxRsBeanValidationHandler` によるバリデーションを有効化
- `BeanUtil.createAndCopy()` — FormクラスをEntityクラスに変換
- `UniversalDao.insert()` — EntityをDBに登録

**3. Formクラス**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

**4. JSON → Form変換の仕組み**

`BodyConvertHandler` の `bodyConverters` プロパティに `Jackson2BodyConverter` が設定されており、`Content-Type: application/json` のリクエストボディを自動的にFormクラスへ変換する。Jersey/RESTEasy環境では `JerseyJaxRsHandlerListFactory`（または `ResteasyJaxRsHandlerListFactory`）をファクトリインジェクションすることで自動設定される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jersey環境の場合 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

これにより `Jackson2BodyConverter`（JSON）、`JaxbBodyConverter`（XML）、`FormUrlEncodedConverter` が自動設定される。

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` より後ろに設定すること（アノテーション情報を参照するため）
- サポートしていないメディアタイプのリクエストにはステータスコード `415` が返却される
- `UniversalDao.insert()` は `@Table`、`@Id`、`@Column` などのJakarta PersistenceアノテーションをEntityに付ける必要がある

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2