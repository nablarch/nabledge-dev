**結論**: Nablarch 6 のRESTful Webサービスでは、URLパスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリパラメータは `JaxRsHttpRequest#getParamMap()` + `BeanUtil` で取得します。ルーティングはXML定義（`routes.xml`）または `@Path` アノテーション（ルーティングアダプタ v1.2.0+）で設定します。

**根拠**:

### パスパラメータの実装

**ルーティング設定（`routes.xml`）**

クラスパス直下の `routes.xml` にパスパラメータを含むルートを定義します。

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

パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

### クエリパラメータの実装

クエリパラメータはルーティング設定には含めず、`JaxRsHttpRequest#getParamMap()` で取得して `BeanUtil` でFormクラスにマッピングします。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジックを実行する
}
```

### `@Path` アノテーションによるルーティング（v1.2.0+）

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

**注意点**:

- Jakarta RESTful Web Servicesの `@PathParam`・`@QueryParam` は使用不可。Nablarchでは `JaxRsHttpRequest` 経由で取得します。
- `@Path` アノテーション方式は、JBoss/WildFlyなどvfsを使うアプリケーションサーバでは使用できません。その場合はXML定義（`routes.xml`）を使用してください。
- `routes.xml` の詳細な書式は http-request-router の README（外部サイト）を参照してください。

参照: `restful-web-service-resource-signature.json#s2`, `restful-web-service-resource-signature.json#s3`, `restful-web-service-feature-details.json#s5`, `restful-web-service-feature-details.json#s6`, `adapters-router-adaptor.json#s6`, `adapters-router-adaptor.json#s9`