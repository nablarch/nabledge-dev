**結論**: NablarchのREST APIでは、パスパラメータは `JaxRsHttpRequest#getPathParam()` で、クエリーパラメータは `getParamMap()` + `BeanUtil` で取得する。ルーティングはXMLまたは `@Path` アノテーションで設定できる。

### パスパラメータ（例：`GET /users/123`）

**ルーティング設定（XMLの場合）**

`routes.xml` でパスパラメータ部分に名前を設定し、必要に応じて正規表現で制約を加える：

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**ルーティング設定（`@Path` アノテーションの場合）**

ルーティングアダプタ v1.2.0 以降は `@Path` アノテーションも使用可能：

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

**リソースクラスでの取得**

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

### クエリーパラメータ（例：`GET /users/search?name=Duke`）

**ルーティング設定**

クエリーパラメータはルーティング設定に含めず、パス部分だけを定義する：

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスでの取得**

```java
public HttpResponse search(JaxRsHttpRequest req) {
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジック...
}
```

**注意点**:
- Jakarta RESTful Web Services 標準の `@PathParam` および `@QueryParam` アノテーションは使用できない。必ず `JaxRsHttpRequest` から取得すること
- `@Path` アノテーションによるルーティングは、JBoss/WildFly など vfs を使うアプリケーションサーバでは動作しない。その場合は XML ルーティング（routes.xml）を使用すること

参照: `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s2`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s3`, `component/adapters/adapters-router-adaptor.json#s6`, `component/adapters/adapters-router-adaptor.json#s9`, `processing-pattern/restful-web-service/restful-web-service-getting-started-search.json#s1`