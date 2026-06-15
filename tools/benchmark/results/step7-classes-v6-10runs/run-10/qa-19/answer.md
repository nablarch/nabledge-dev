**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたアクションメソッドを定義し、`BodyConvertHandler`（`Jackson2BodyConverter`使用）がJSONをFormオブジェクトに変換、`UniversalDao.insert()`でDB登録します。

**根拠**:

**処理の流れ**（RESTfulウェブサービスの処理フロー）

1. WebフロントコントローラがHTTPリクエストを受信
2. ルーティングアダプタ（`DispatchHandler`）がURIからアクションクラスを特定
3. `BodyConvertHandler`がリクエストボディ（JSON）をFormオブジェクトに変換
4. アクションクラスの業務ロジックが実行され、`UniversalDao`でDB登録
5. `JaxRsResponseHandler`がHTTPレスポンスをクライアントへ返却

**JSONの変換の仕組み**（`BodyConvertHandler` + `Jackson2BodyConverter`）

Jersey環境では `JerseyJaxRsHandlerListFactory` を使うことで、JSONコンバータとして `Jackson2BodyConverter` が自動的に設定されます：

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

**アクションクラスの実装例**

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)`: このメソッドがJSON形式のリクエストを受け付けることを示す。`BodyConvertHandler`がこのアノテーションを見てJSONをFormに変換する
- `@Valid`: `JaxRsBeanValidationHandler`がFormに対してBean Validationを実行する
- `@Path` + `@POST`: URLとメソッドをマッピングする（ルーティングアダプタが使用）
- `BeanUtil.createAndCopy()`: FormクラスをEntityクラスに変換
- `UniversalDao.insert()`: エンティティをDBに登録

**Formクラスの設計**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**注意点**:
- Formクラスのプロパティは全てString型で宣言する必要がある
- `BodyConvertHandler`に設定されたコンバータが対応しないMIMEを使用した場合、ステータスコード`415`が返却される
- アプリケーションサーバにJacksonがバンドルされていない場合は、Jacksonのモジュールをアプリケーションモジュールとセットでデプロイする

参照: processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8