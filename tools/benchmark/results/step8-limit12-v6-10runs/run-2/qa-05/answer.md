**結論**: アクションクラスに `@Path`・`@POST`・`@Consumes(APPLICATION_JSON)`・`@Valid` を付けてメソッドを定義し、`BeanUtil.createAndCopy` でFormをEntityに変換後、`UniversalDao.insert()` でDB登録する。レスポンスは `HttpResponse.Status.CREATED`（201）を返却する。

---

**根拠**:

**1. Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` でBean Validationを実行（バリデーションエラー時は自動的に `ApplicationException` を送出）
- `BeanUtil.createAndCopy` でFormをEntityに変換
- `UniversalDao.insert()` でDBへ登録
- 登録成功時はステータスコード `201` を返却

**3. コンポーネント定義（Jerseyの場合）**

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>

  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryにより、JSON用Jackson2BodyConverterとBean Validationハンドラが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

ユニバーサルDAOを使うため、コンポーネント定義に以下も追加する：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- Formのプロパティは**全てString型**で宣言すること（バリデーションルールの設定方法に基づく制約）
- JSONコンバータはJersey環境であれば `JerseyJaxRsHandlerListFactory`、RESTEasy環境であれば `ResteasyJaxRsHandlerListFactory` を使用すること

参照: restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6