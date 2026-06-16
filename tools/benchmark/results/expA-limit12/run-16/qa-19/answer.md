**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、引数にフォームクラスを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` で登録します。

**根拠**:

**① フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONがフォームクラスに変換される
- `@Valid` でBean Validationによるバリデーションが実行される
- `BeanUtil.createAndCopy()` でフォームクラスをエンティティクラスに変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse(201)` を返す

**③ 内部処理の流れ**

1. リクエストを受信 → ルーティングアダプタがアクションを特定
2. `BodyConvertHandler`（リクエストボディ変換ハンドラ）がJSONをフォームクラスに変換
3. `JaxRsBeanValidationHandler` がバリデーションを実行
4. アクションメソッドが `UniversalDao.insert()` でDB登録
5. `JaxRsResponseHandler` がレスポンスをクライアントに返却

最小ハンドラ構成（コンポーネント設定）:

```xml
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <component class="nablarch.fw.handler.GlobalErrorHandler"/>
      <component class="nablarch.fw.jaxrs.JaxRsResponseHandler"/>
      <component class="nablarch.common.handler.DbConnectionManagementHandler"/>
      <component class="nablarch.common.handler.TransactionManagementHandler"/>
      <component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
        <property name="methodBinderFactory">
          <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
            <property name="handlerList">
              <!-- Jersey環境ではJerseyJaxRsHandlerListFactoryを使用 -->
              <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
            </property>
          </component>
        </property>
      </component>
    </list>
  </property>
</component>
```

JerseyまたはRESTEasy環境では `JerseyJaxRsHandlerListFactory` / `ResteasyJaxRsHandlerListFactory` を使うと、JSONコンバータ（`Jackson2BodyConverter`）とBeanValidationハンドラが自動的に設定されます。

**注意点**:
- フォームクラスのプロパティは全て `String` 型で宣言する
- `@Consumes` に指定したMIMEタイプと異なるContent-Typeのリクエストが来た場合、ステータスコード `415`（Unsupported Media Type）が返却される
- RESTfulウェブサービスでは `@Context` や Jakarta CDI は使用できない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2