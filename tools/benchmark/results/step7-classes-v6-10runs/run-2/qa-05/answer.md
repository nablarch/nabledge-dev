**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()`でFormをEntityに変換後、`UniversalDao.insert()`でDBに登録します。

**根拠**:

**1. Formクラスの作成**

クライアントから送信されるJSONをマッピングするFormを作成します。プロパティはすべてString型で宣言します。

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する
- `@Valid` でバリデーションを実行する（Jakarta RESTful Web Servcies Bean Validationハンドラが処理）
- `BeanUtil.createAndCopy()` でFormをEntityに変換する
- `UniversalDao.insert()` でDBにINSERTする
- 戻り値として`201 Created`を返す

**3. ルーティング設定（@Pathアノテーション使用の場合）**

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
        <!-- Jersey用アダプタを使用する場合 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

`JerseyJaxRsHandlerListFactory`を使うと、`Jackson2BodyConverter`（JSON変換）と`JaxRsBeanValidationHandler`が自動的に設定されます。

**4. ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Path`アノテーションによるルーティングはJBoss/WildFlyでは使用できません。その場合はXMLベースのルーティング定義（`routes.xml`）を使用してください
- ユニバーサルDAOを使用するには、データベースアクセス（JDBCラッパー）の設定も別途必要です
- Entityには`@Table`、`@Column`、`@Id`などのJakarta Persistenceアノテーションが必要です

参照: restful-web-service-getting-started-create.json:s1, component/adapters/adapters-jaxrs-adaptor.json:s2, component/adapters/adapters-router-adaptor.json:s7, component/adapters/adapters-router-adaptor.json:s8, component/libraries/libraries-universal-dao.json:s6, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4