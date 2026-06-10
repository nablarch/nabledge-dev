**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormに変換して取得する。ルーティングはXMLベース（`routes.xml`）とJakarta RESTful Web Servicesの `@Path` アノテーションベースの2通りがある。

---

**根拠**:

### ルーティング設定（XMLベース）

クラスパス直下に `routes.xml` を作成する。パスパラメータは `:パラメータ名` の形式で定義する。

```xml
<!-- パスパラメータ（:id）の例 -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>

  <!-- クエリーパラメータはパスに含めない -->
  <get path="users/search" to="Users#search"/>
</routes>
```

ディスパッチハンドラとして `RoutesMapping` をハンドラキューの末尾に設定する：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

---

### ルーティング設定（@Pathアノテーションベース）

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして使うことで、Jakarta RESTful Web Services の `@Path` アノテーションによるルーティングも利用できる。パスパラメータは `{パラメータ名}` または `{パラメータ名 : 正規表現}` の形式で定義する。

```java
@Path("/sample")
public class TestAction {

    @GET
    @Path("/foo/{param}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
        // 省略
    }

    @GET
    @Path("/bar/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

---

### パスパラメータの取得（リソースクラス実装）

メソッド引数に `JaxRsHttpRequest` を宣言し、ルーティング定義で指定したパラメータ名を `getPathParam()` に渡す。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

### クエリーパラメータの取得

ルーティングはクエリーパラメータを除いたパスで定義し、`getParamMap()` を `BeanUtil` でFormに変換する。

```java
// ルーティング: <get path="users/search" to="Users#search"/>
// URL例: GET /users/search?name=Duke

public HttpResponse search(JaxRsHttpRequest req) {
    // クエリーパラメータをFormにマッピング
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジック（省略）
}

public class UserSearchForm {
    private String name;
    // 省略
}
```

---

**注意点**:
- `@PathParam` / `@QueryParam`（Jakarta RESTful Web Services仕様）はNablarchでは使用不可。必ず `JaxRsHttpRequest` を使うこと
- XMLベースのルーティングは `RoutesMapping`、`@Path` アノテーションベースは `PathOptionsProviderRoutesMapping` とディスパッチハンドラが異なる
- `@Path` アノテーションによるルーティングは、JBoss/WildFly（vfsファイルシステム使用環境）では使用不可

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s4, adapters-router-adaptor.json:s6, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9

---