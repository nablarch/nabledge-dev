**結論**: NablarchのRESTful WebサービスでURLパスパラメータは `JaxRsHttpRequest#getPathParam()` で、クエリパラメータは `JaxRsHttpRequest#getParamMap()` で取得する。ルーティング設定はXML方式と `@Path` アノテーション方式の2通りがある。

**根拠**:

### パスパラメータ（例: `GET /users/123`）

**XML方式のルーティング設定（routes.xml）**

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**リソースクラスの実装**

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**`@Path` アノテーション方式**

```java
@Path("/users")
public class UsersAction {

    @GET
    @Path("/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public User find(JaxRsHttpRequest request) {
        Long id = Long.valueOf(request.getPathParam("id"));
        return UniversalDao.findById(User.class, id);
    }
}
```

### クエリパラメータ（例: `GET /users/search?name=Duke`）

ルーティング定義にはクエリパラメータを含めない。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

```java
public HttpResponse search(JaxRsHttpRequest req) {
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
}
```

### `@Path` アノテーション方式のコンポーネント設定

`PathOptionsProviderRoutesMapping` を使う。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
</component>
```

**注意点**:
1. `@PathParam` / `@QueryParam` は使用不可。必ず `JaxRsHttpRequest` 経由で取得する。
2. XML方式とアノテーション方式の併用は非推奨。
3. `@Path` アノテーション方式はJBoss/WildFlyでは使用不可（vfsの制約）。
4. パスパラメータの記法: XML方式は `:id`、`@Path` 方式は `{id}`。

参照: processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s2, #s3, component/adapters/adapters-router-adaptor.json#s4, #s6-s9