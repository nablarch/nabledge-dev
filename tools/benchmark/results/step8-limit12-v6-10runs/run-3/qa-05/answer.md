**結論**: `@POST` と `@Consumes(MediaType.APPLICATION_JSON)` を組み合わせたアクションメソッドを作成し、`BeanUtil.createAndCopy()` でエンティティに変換後 `UniversalDao.insert()` でDBに登録します。

**根拠**:

**1. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
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

- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付ける
- `@Valid` でBean Validationによるバリデーションを行う
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録
- 登録完了はステータスコード `201` を返す

**3. アダプタ設定（Jersey環境の場合）**

`JerseyJaxRsHandlerListFactory` を使用すると、JSON変換に `Jackson2BodyConverter` が自動設定される。

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
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

RESTEasyを使用する場合は `JerseyJaxRsHandlerListFactory` の代わりに `ResteasyJaxRsHandlerListFactory` を使用する。

**4. ユニバーサルDAOの設定**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティは全て `String` 型で宣言する（Bean Validationのルール）
- Content-Typeが `application/json` でない場合はステータスコード `415` が返される
- `Consumes` に設定したMIMEと異なるContent-Typeのリクエストは受け付けられない

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/adapters/adapters-jaxrs-adaptor.json:s2, component/adapters/adapters-router-adaptor.json:s7, component/adapters/adapters-router-adaptor.json:s8, component/handlers/handlers-body-convert-handler.json:s5, component/libraries/libraries-universal-dao.json:s6