Step 5: 回答を生成します。

---

**結論**: パスパラメータは `routes.xml` に `users/:id` 形式で定義し、`JaxRsHttpRequest#getPathParam()` で取得する。クエリーパラメータはルーティングをパスのみで定義し、`req.getParamMap()` を `BeanUtil` でFormにマッピングして取得する。

---

**根拠**:

### 1. パスパラメータの実装

**ルーティング設定 (`routes.xml`)**

`:id` の部分がパスパラメータ。`requirements` で正規表現による型チェックも設定できる。

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

引数に `JaxRsHttpRequest` を定義し、`getPathParam()` で取得する。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

---

### 2. クエリーパラメータの実装

**ルーティング設定**: クエリーパラメータ部分を除いたパスのみを定義する。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスの実装**

`req.getParamMap()` を `BeanUtil.createAndCopy()` でFormクラスにマッピングする。

```java
public HttpResponse search(JaxRsHttpRequest req) {
  // クエリーパラメータをFormに変換
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
  ValidatorUtil.validate(form);
  // 業務ロジック（省略）
}

public class UserSearchForm {
  private String name;
  // 省略
}
```

URL例: `GET /users/search?name=Duke`

---

### 3. ルーティングアダプタの設定

`RoutesMapping` をハンドラキューの最後に設定し、初期化対象にも追加する。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>

<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- その他のハンドラは省略 -->
      <component-ref name="packageMapping" />
    </list>
  </property>
</component>

<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="packageMapping"/>
    </list>
  </property>
</component>
```

ルート定義はクラスパス直下の `routes.xml` に記述する。

---

### 4. `@Path` アノテーション方式（代替）

バージョン1.2.0以降では、XMLではなく `@Path` アノテーションでもルーティングを定義できる（ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更する必要あり）。

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

**注意点**:
- JAX-RS標準の `@PathParam` は使用できない。パスパラメータは必ず `JaxRsHttpRequest#getPathParam()` で取得すること。
- JAX-RS標準の `@QueryParam` は使用できない。クエリーパラメータは `req.getParamMap()` 経由で取得すること。
- `@Path` アノテーション方式は JBoss/WildFly では使用不可。その場合は `routes.xml` を使用すること。

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s3`, `adapters-router-adaptor.json:s4`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`

---