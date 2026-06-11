**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BodyConvertHandler` が自動でJSONをFormに変換する仕組みを活用し、`UniversalDao.insert()` でDB登録する。

---

**根拠**（処理の流れ）:

リクエストが届いてからDB登録されるまでの流れは以下のとおり。

```
WebFrontController (Servlet Filter)
  → ハンドラキュー
      → RoutesMapping        ← URLとアクションのマッピング
      → BodyConvertHandler   ← JSONをFormクラスに変換
      → JaxRsBeanValidationHandler ← バリデーション実行
      → アクションクラス     ← DB登録
```

**① Formクラスの作成**（プロパティは全てString型）:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ・セッタは省略
}
```

**② アクションクラスの実装**:

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
- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付ける指定
- `@Valid`: `JaxRsBeanValidationHandler` によりFormのバリデーションを自動実行
- `BeanUtil.createAndCopy(Project.class, project)`: FormからEntityへの変換
- `UniversalDao.insert()`: DB登録
- 戻り値は `HttpResponse(201)` でリソース作成完了を表す

**③ JSONコンバータの設定**（Jersey使用時）:

`JerseyJaxRsHandlerListFactory` を設定することで、`Jackson2BodyConverter`（JSON用）が `BodyConvertHandler` に自動的に組み込まれる。

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

---

**注意点**:
- Formのプロパティは全てString型で宣言すること
- `BodyConvertHandler` はルーティングアダプタ（`RoutesMapping`）より後ろに設定すること（ディスパッチ先を特定してからでないとアノテーション情報を参照できないため）
- RESTfulウェブサービスでは `@Context` アノテーションを使用したServletリソースのインジェクションやCDIは使用不可

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2