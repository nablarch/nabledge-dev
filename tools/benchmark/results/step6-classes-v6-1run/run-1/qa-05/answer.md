**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil.createAndCopy()` でFormをEntityに変換して `UniversalDao.insert()` で登録します。

**根拠**:

**1. Formクラスの作成**

クライアントから送られるJSONを受け取るFormクラスを作成します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言します。

**2. アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストボディをJSON形式で受け付けます。`BodyConvertHandler` がこのアノテーションを見て `Jackson2BodyConverter` でFormに変換します。
- `@Valid` を付けることで `JaxRsBeanValidationHandler` がBean Validationを実行します。バリデーションエラー時は `ApplicationException` が送出されます。
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録します。
- 戻り値にステータスコード `201` (Created) を表す `HttpResponse` を返します。

**3. URLマッピングの設定（Pathアノテーション方式）**

コンポーネント定義に以下を設定します。

```xml
<component name="packageMapping"
    class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

- `JerseyJaxRsHandlerListFactory` により、JSONコンバータ（`Jackson2BodyConverter`）とBean Validationハンドラが自動的に設定されます。

**注意点**:
- `BodyConvertHandler` はルーティングアダプタより後ろ、`JaxRsBeanValidationHandler` はさらにその後ろに設定する必要がありますが、`JerseyJaxRsHandlerListFactory` を使用すると自動で正しい順序で設定されます。
- ユニバーサルDAOを使用するには別途 `BasicDaoContextFactory` のコンポーネント定義が必要です。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8