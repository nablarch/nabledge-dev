**結論**: Nablarch 6のREST APIでパスパラメータ・クエリパラメータを扱うには、`JaxRsHttpRequest` を使って値を取得する。ルーティングは `routes.xml` で定義するか、`@Path` アノテーション（ルーティングアダプタ v1.2.0以降）で定義する2通りの方法がある。

### パスパラメータ（URLパスの一部を受け取る）

**XMLルーティング方式（routes.xml）**

`routes.xml` にパスパラメータ部を `:パラメータ名` で定義する：

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

リソースクラスでは `JaxRsHttpRequest#getPathParam(String)` で取得する：

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**@Path アノテーション方式（ルーティングアダプタ v1.2.0以降）**

`{パラメータ名}` または `{パラメータ名 : 正規表現}` の形式でパスに埋め込む：

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

### クエリパラメータ（URL末尾の `?key=value` を受け取る）

**ルーティング設定**：クエリパラメータは除いたパスでマッピングする：

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスの実装**：`req.getParamMap()` で取得し、`BeanUtil` でFormクラスへマッピングする：

```java
public HttpResponse search(JaxRsHttpRequest req) {
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジックを実行する
}

public class UserSearchForm {
    private String name;
    // ...
}
```

**注意点**:

- Jakarta RESTful Web Servicesの仕様で定義されている `@PathParam` および `@QueryParam` アノテーションは**使用できない**。必ず `JaxRsHttpRequest` 経由で取得すること。
- `@Path` アノテーション方式は、JBoss/WildFlyのようにvfsを使うアプリケーションサーバでは**使用不可**。その場合は `routes.xml` を使う。
- パスパラメータを使うメソッドには必ず仮引数として `JaxRsHttpRequest` を定義すること。

参照: `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s2`, `#s3`, `component/adapters/adapters-router-adaptor.json#s8`, `#s9`, `processing-pattern/restful-web-service/restful-web-service-feature-details.json#s5`, `#s6`