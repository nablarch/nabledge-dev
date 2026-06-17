**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータ・クエリーパラメータともに `JaxRsHttpRequest` を使って取得する。ルーティングはXMLの `routes.xml`（`:パラメータ名` 記法）か `@Path` アノテーション（`{パラメータ名}` 記法）の2方式で設定できる。

---

**根拠**

### ルーティング設定：2つの方式

#### 方式A：XMLルート定義ファイル（routes.xml）

`RoutesMapping` をディスパッチハンドラとして設定し、クラスパス直下に `routes.xml` を作成する。

```xml
<!-- コンポーネント定義 -->
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

パスパラメータの場合、`:パラメータ名` で定義し、`requirements` で書式制約を指定できる：

```xml
<!-- routes.xml -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

クエリーパラメータの場合、ルーティングはクエリー部を除いたパスで定義する：

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

#### 方式B：`@Path` アノテーション（Jakarta RESTful Web Services準拠）

`PathOptionsProviderRoutesMapping` + `JaxRsPathOptionsProvider` を使用する：

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

アクションクラスでは `{パラメータ名}` 記法でパスパラメータを定義する：

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
    @Path("/bar/{id : \\d+}")   // 正規表現で書式制約
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

---

### パスパラメータの取得（リソースクラス実装）

`JaxRsHttpRequest` を引数に定義し、`getPathParam("パラメータ名")` で取得する。ルーティング設定で使ったパラメータ名と一致させる：

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

### クエリーパラメータの取得（リソースクラス実装）

`JaxRsHttpRequest` を引数に定義し、`getParamMap()` で取得後、`BeanUtil.createAndCopy` でFormクラスにマッピングする：

```java
public HttpResponse search(JaxRsHttpRequest req) {

    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する（省略）
}

public class UserSearchForm {
    private String name;
    // 省略
}
```

---

**注意点**

- Jakarta RESTful Web Servicesで規定されている `@PathParam` アノテーションは**使用できない**
- 同様に `@QueryParam` アノテーションも**使用できない**
- `@Path` アノテーション方式は、JBoss/WildFlyなどvfsを使用するアプリケーションサーバでは使用不可。その場合はXMLルート定義方式を使うこと

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-resource-signature.json:s1