**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert` でEntityを登録する。

**根拠**:

**1. フォームの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言する

**2. 業務アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディがFormに変換される
- `@Valid` を付けるとBean Validationが自動実行され、エラー時は `ApplicationException` が送出される
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**3. JSON変換の設定（Jersey環境の場合）**

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

`JerseyJaxRsHandlerListFactory` を設定すると、`Jackson2BodyConverter`（JSON変換用）が自動的に含まれたハンドラ構成が設定される。

**4. ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Consumes` に設定したMIMEと異なるContent-Typeのリクエストが来た場合、ステータスコード `415` が返却される
- RESTfulウェブサービスではETag/If-Matchを使用した楽観的ロックには対応していないため、バージョン番号はリクエストボディに含める

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6