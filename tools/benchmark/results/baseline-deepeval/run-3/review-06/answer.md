Step 4でセクション内容を取得しました。Step 5の回答生成に進みます。

---

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormに変換して取得する。ルーティングの設定は routes.xml（XML定義）または `@Path` アノテーションの2方式が使える。

---

**根拠**:

### ルーティングの設定

**方式1: routes.xml（XMLルート定義）**

`RoutesMapping` をディスパッチハンドラとして設定し、クラスパス直下に `routes.xml` を作成する。

```xml
<!-- コンポーネント定義 -->
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

  <!-- クエリパラメータはパスに含めない -->
  <get path="users/search" to="Users#search"/>
</routes>
```

**方式2: `@Path` アノテーション**

`PathOptionsProviderRoutesMapping` を使い、アクションクラスに `@Path` を付与する。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  <!-- methodBinderFactory は省略 -->
</component>
```

```java
@Path("/sample")
public class SampleAction {

    @GET
    @Path("/foo/{param}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
        // 省略
    }

    // 正規表現で書式制約
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

### パスパラメータの受け取り（routes.xml方式）

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
  // ルート定義で設定したパラメータ名を指定
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

---

### クエリパラメータの受け取り

ルーティングはクエリパラメータを除いたパスで定義し、取得は `getParamMap()` + `BeanUtil` を使う。

```java
public HttpResponse search(JaxRsHttpRequest req) {

  // クエリパラメータをFormにマッピング
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

  // バリデーション
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
- Jakarta RESTful Web Servicesの `@PathParam` / `@QueryParam` アノテーションは使用不可。`JaxRsHttpRequest` のメソッドを使うこと。
- `@Path` アノテーション方式は、JBoss/WildFly（vfsファイルシステム）では使用できない。その場合は routes.xml 方式を使うこと。

参照: `processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s2`, `s3` / `component/adapters/adapters-router-adaptor.json:s3`, `s4`, `s8`, `s9`

---