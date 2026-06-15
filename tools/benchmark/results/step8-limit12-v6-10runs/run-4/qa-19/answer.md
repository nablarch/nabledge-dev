**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換して `UniversalDao.insert()` でDB登録する。リクエストボディのJSON→Form変換は `BodyConvertHandler`（`Jackson2BodyConverter` を内包）が自動で行う。

---

**根拠**:

**① ハンドラキューの最小構成**

RESTfulウェブサービスには以下のハンドラを設定する（抜粋）:

| No. | ハンドラ | 役割 |
|---|---|---|
| 2 | `JaxRsResponseHandler` | レスポンス書き込み・例外処理 |
| 3 | `DbConnectionManagementHandler` | DB接続管理 |
| 4 | `TransactionManagementHandler` | トランザクション制御 |
| 5 | ルーティングアダプタ | URI→アクションのマッピング |
| 6 | `BodyConvertHandler` | リクエストボディ→Form変換 / レスポンスボディ変換 |
| 7 | `JaxRsBeanValidationHandler` | フォームへのBean Validation実行 |

Jersey環境では `JerseyJaxRsHandlerListFactory` を設定することで `BodyConvertHandler`（`Jackson2BodyConverter` 含む）と `JaxRsBeanValidationHandler` が自動設定される:

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

**② アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると、`BodyConvertHandler` が `application/json` 対応のコンバータ（`Jackson2BodyConverter`）を使ってリクエストボディを `ProjectForm` に変換する
- `@Valid` アノテーションを付与すると、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを実行し、エラー時は `ApplicationException` を送出して後続処理を中断する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換してから `UniversalDao.insert()` でDB登録する
- 戻り値には登録完了を表すステータスコード `201` の `HttpResponse` を返却する

**③ フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ省略
}
```

- プロパティは全て `String` 型で宣言する（Bean Validationの仕様に従う）

**注意点**:
- `BodyConvertHandler` に設定されたコンバータが対応していない `Content-Type` を受け取った場合は、ステータスコード `415`（Unsupported Media Type）が返却される
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろに設定する必要がある（Formへの変換が済んだ後にバリデーションを行うため）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2