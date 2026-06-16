**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換後、`UniversalDao.insert()` でDB登録する。JSON→Form変換はフレームワークの `BodyConvertHandler`（内部で `Jackson2BodyConverter` を使用）が自動的に行う。

**根拠**:

**全体的な処理の流れ**

```
リクエスト受信
  → WebFrontController（Servlet Filter）
  → ハンドラキュー処理
      → グローバルエラーハンドラ
      → Jakarta RESTful Web Servicesレスポンスハンドラ（JaxRsResponseHandler）
      → データベース接続管理ハンドラ（DB接続取得/解放）
      → トランザクション制御ハンドラ（コミット/ロールバック）
      → ルーティングアダプタ（URIからアクション特定）
      → リクエストボディ変換ハンドラ（JSON→Formに変換）
      → Bean Validationハンドラ（@Validに基づくバリデーション）
      → アクションクラス（業務ロジック実行）
```

**ハンドラの役割**
- `BodyConvertHandler` がリクエストのContent-Type（`application/json`）を見て、`Jackson2BodyConverter` でJSONをFormオブジェクトに変換する
- `JaxRsBeanValidationHandler` がアクションメソッドの `@Valid` アノテーションを見てBean Validationを実行する（エラー時は `ApplicationException` をスロー）

**実装例（フォームクラス）**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**実装例（アクションクラス）**

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

- `@Consumes(MediaType.APPLICATION_JSON)` で `application/json` を受け付けることを宣言する（これにより `BodyConvertHandler` が適切なコンバータを選択する）
- `@Valid` でリクエストのバリデーションを実行する
- `BeanUtil.createAndCopy()` でフォームのプロパティをエンティティにコピーする
- `UniversalDao.insert()` でエンティティをDBに登録する
- 登録完了時はステータスコード `201` を返す

**アダプタ設定（Jersey環境の例）**

`JaxRsMethodBinderFactory` の `handlerList` に `JerseyJaxRsHandlerListFactory` を設定すると、`Jackson2BodyConverter`（JSON）、`JaxbBodyConverter`（XML）、`FormUrlEncodedConverter`（URLエンコード）が自動的に登録される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**: 
- サポートしていないMIMEのリクエストが来た場合、`BodyConvertHandler` はステータスコード `415`（Unsupported Media Type）を返す
- UniversalDAOを使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要（`name="daoContextFactory"`）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4