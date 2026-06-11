**結論**: JSONを受け取ってDBに登録する場合、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert()` でDBに登録します。

**根拠**:

**1. Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONを受け付ける
- `@Valid` でBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値はステータスコード `201 Created` を示す `HttpResponse` を返す

**3. Jacksonアダプタの設定（JSON変換に必要）**

Jersey環境の場合：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのハンドラキューをファクトリインジェクションするとJSON変換が自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**4. ユニバーサルDAOの設定**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは必ずString型にすること。String以外の型があると、不正な値が送信された場合にバリデーション前にBeanへの変換が失敗し、予期しない例外が発生する
- `BodyConvertHandler` に `Jackson2BodyConverter` が設定されていないと、JSONのリクエストボディが変換できずステータスコード `415` が返される
- Jakarta RESTful Web Servicesで規定されている `@PathParam` / `@QueryParam` はNablarchでは使用できない

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/libraries/libraries-bean-validation.json:s8, component/libraries/libraries-bean-validation.json:s17, component/libraries/libraries-universal-dao.json:s6, component/adapters/adapters-jaxrs-adaptor.json:s2