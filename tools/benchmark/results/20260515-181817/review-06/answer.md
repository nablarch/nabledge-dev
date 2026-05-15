**結論**: REST APIでURLパスパラメータ（`/users/123` の `123`）とクエリパラメータ（`?name=Duke`）を受け取るには、`@Path` / `@GET` アノテーションでルーティングを定義し、値の取得には `JaxRsHttpRequest#getPathParam()` または `req.getParamMap()` + `BeanUtil` を使用します。

**根拠**:

### ルーティング設定（2つの方式）

#### 方式1: `@Path` アノテーション（推奨・Jakarta RESTful Web Services準拠）

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定します：

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

#### 方式2: XMLルート定義ファイル（従来方式）

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

### パスパラメータの受け取り（`/users/123` の `123`）

**`@Path` アノテーション方式**:

```java
@Path("/sample")
public class TestAction {

    @GET
    @Path("/foo/{param}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
    }

    @GET
    @Path("/bar/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
    }
}
```

**XMLルート定義方式**:

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

### クエリパラメータの受け取り（`?name=Duke` など）

```java
@Path("/projects")
public class ProjectAction {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Project> find(JaxRsHttpRequest req) {
        ProjectSearchForm form =
            BeanUtil.createAndCopy(ProjectSearchForm.class, req.getParamMap());
        ValidatorUtil.validate(form);
        ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, form);
        return UniversalDao.findAllBySqlFile(Project.class, "FIND_PROJECT", searchCondition);
    }
}
```

**注意点**:
- Jakarta RESTful Web Servicesの `@PathParam` / `@QueryParam` アノテーションは使用できない。必ず `JaxRsHttpRequest#getPathParam()` や `req.getParamMap()` を使うこと
- `@Path` アノテーションによるルーティングは、JBoss/WildflyなどのVFSを使うアプリケーションサーバでは使用不可。その場合はXMLルート定義方式を使う
- パスパラメータに正規表現を指定する場合、`@Path` 方式では `{id : \\d+}` の形式を使う（XML方式とは書き方が異なる）

参照: `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s2`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s3`, `component/adapters/adapters-router-adaptor.json#s8`, `component/adapters/adapters-router-adaptor.json#s9`, `processing-pattern/restful-web-service/restful-web-service-getting-started-search.json#s1`