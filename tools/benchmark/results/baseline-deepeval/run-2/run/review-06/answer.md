**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormクラスに変換して取得します。ルーティングはXMLのルート定義ファイル（`routes.xml`）または `@Path` アノテーションで設定します。

**根拠**:

---

### ルーティング設定（方法1: routes.xml）

クラスパス直下に `routes.xml` を作成し、URLとアクションをマッピングします。ディスパッチハンドラとして `RoutesMapping` をハンドラキューの最後に設定します。

```xml
<!-- コンポーネント設定 -->
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

```xml
<!-- routes.xml: パスパラメータあり -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>

  <!-- クエリパラメータはパスから除いて定義 -->
  <get path="users/search" to="Users#search"/>
</routes>
```

---

### ルーティング設定（方法2: @Path アノテーション）

`PathOptionsProviderRoutesMapping` を使うと、アノテーションでルーティングを定義できます。

```java
@Path("/users")
public class UsersAction {

    // パスパラメータあり: /users/{id}
    @GET
    @Path("/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public User find(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }

    // クエリパラメータ: /users/search?name=Duke
    @GET
    @Path("/search")
    public HttpResponse search(JaxRsHttpRequest request) {
        // 省略
    }
}
```

---

### パスパラメータの取得（リソースクラス実装）

`JaxRsHttpRequest#getPathParam()` にルーティング定義で指定した名前を渡して取得します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    // JaxRsHttpRequestからパスパラメータの値を取得する
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

### クエリパラメータの取得（リソースクラス実装）

`JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormクラスに変換します。

```java
public HttpResponse search(JaxRsHttpRequest req) {

    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する（省略）
}

// クエリパラメータをマッピングするForm
public class UserSearchForm {
    private String name;
    // 省略
}
```

**注意点**:
- Jakarta RESTful Web Servicesの `@PathParam` / `@QueryParam` アノテーションは**使用できない**。パス・クエリパラメータの取得は必ず `JaxRsHttpRequest` 経由で行うこと。
- `@Path` アノテーションによるルーティングは、JBoss/WildFlyなど一部のアプリケーションサーバでは使用不可。その場合は `routes.xml` を使用すること。

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s3`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`

---