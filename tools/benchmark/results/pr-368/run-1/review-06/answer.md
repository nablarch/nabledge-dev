**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil.createAndCopy()` でFormに変換して取得する。ルーティング定義は `routes.xml`（XMLベース）または `@Path` アノテーション（Javaベース）の2通りで設定できる。

---

**根拠**:

### ① パスパラメータ（例: `GET /users/123`）

**routes.xml によるルーティング定義**（XMLベース）

クラスパス直下に `routes.xml` を作成し、パスパラメータ部に任意の名前を付ける。正規表現で制約も指定できる。

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
  // JaxRsHttpRequestからパスパラメータの値を取得する
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

> `@PathParam` アノテーション（Jakarta RESTful Web Services仕様）は使用できない。`JaxRsHttpRequest#getPathParam` を使うこと。

---

### ② パスパラメータ（`@Path` アノテーションによる方法）

`@Path` アノテーションを使う場合は `{パラメータ名}` または `{パラメータ名 : 正規表現}` の記法でパスを定義する。

```java
@Path("/sample")
public class TestAction {

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

### ③ クエリーパラメータ（例: `GET /users/search?name=Duke`）

**ルーティング定義**（クエリーパラメータはルーティング設定では記述しない）

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスの実装**

```java
public HttpResponse search(JaxRsHttpRequest req) {

  // リクエストパラメータをBeanに変換
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

  // バリデーションの実行
  ValidatorUtil.validate(form);

  // 業務ロジックを実行する(省略)
}

// クエリーパラメータをマッピングするForm
public class UserSearchForm {
  private String name;
  // 省略
}
```

> `@QueryParam` アノテーション（Jakarta RESTful Web Services仕様）は使用できない。

---

### ④ ルーティングのディスパッチハンドラ設定

**XMLベース（routes.xml）の場合**: `RoutesMapping` をコンポーネント名 `packageMapping` で設定する。

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
```

`RoutesMapping` は初期化対象リストへの追加も必要。

**`@Path` アノテーションの場合**: `RoutesMapping` の代わりに `PathOptionsProviderRoutesMapping` を使う。

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

---

**注意点**:
- Jakarta RESTful Web Services標準の `@PathParam` / `@QueryParam` は Nablarch では使用できない。常に `JaxRsHttpRequest` を通じてパラメータを取得すること。
- `@Path` アノテーションによるルーティングは、クラスパス配下を独自ファイルシステム（vfs等）で管理する JBoss/WildFly では使用できない。その場合は routes.xml を使うこと。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9