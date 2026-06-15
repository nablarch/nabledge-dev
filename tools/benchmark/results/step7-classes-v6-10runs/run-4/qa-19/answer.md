**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert()` でDBに登録する。フレームワーク側では `リクエストボディ変換ハンドラ（BodyConvertHandler）` がJSONをFormクラスに変換し、`Bean Validationハンドラ（JaxRsBeanValidationHandler）` がバリデーションを実行する。

---

**根拠**:

**処理の流れ**

1. `WebFrontController`（jakarta.servlet.Filter）がリクエストを受信
2. ルーティングアダプタ（`RoutesMapping`）が`@Path`/`@POST`アノテーションを元にアクションクラスを特定
3. `BodyConvertHandler` が `Content-Type: application/json` に対応した `Jackson2BodyConverter` でリクエストボディをFormクラスに変換
4. `JaxRsBeanValidationHandler` が `@Valid` 付きメソッドのFormに対してBean Validationを実行
5. アクションメソッドが実行され、`UniversalDao.insert()` でDB登録
6. `JaxRsResponseHandler` がレスポンスをクライアントに返却

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

**実装例（フォームクラス）**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**ハンドラ設定（JSONコンバータの設定）**

Jerseyを使う場合は `JerseyJaxRsHandlerListFactory` を使うと自動的に `Jackson2BodyConverter` が設定される：

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

手動でコンバータを設定する場合：

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSONコンバータ（Jacksonアダプタが必要） -->
      <component class="nablarch.integration.jaxrs.jackson.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

**最小ハンドラ構成**（処理の順序）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー応答 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | RoutesMapping（ルーティングアダプタ） | URIとアクションの紐付け |
| 6 | BodyConvertHandler | JSONボディ→Formへの変換 |
| 7 | JaxRsBeanValidationHandler | Bean Validationの実行 |

**注意点**:
- `@Consumes(MediaType.APPLICATION_JSON)` を設定しないと、`BodyConvertHandler` がどのコンバータを使うか判断できない
- フォームクラスのプロパティは**全てString型**で宣言する（Bean Validationの制約）
- `Content-Type`がサポートされていないMIMEの場合、ステータスコード `415` が返却される
- `BeanUtil.createAndCopy()` でFormクラスをエンティティクラスに変換してから `UniversalDao.insert()` に渡す

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4