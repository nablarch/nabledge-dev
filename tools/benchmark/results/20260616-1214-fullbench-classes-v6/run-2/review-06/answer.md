**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormにマッピングして受け取る。ルーティングはXMLのroutes.xmlか `@Path` アノテーションの2方式で設定できる。

---

**根拠**

#### パスパラメータ (`GET /users/123` の `123` をパスパラメータとする場合)

**方式1: XMLルーティング定義 (routes.xml)**

`:パラメータ名` の記法でパスパラメータを定義する。正規表現による制約も指定可能。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**方式2: `@Path` アノテーション**

`{パラメータ名}` の記法で定義する。`{パラメータ名 : 正規表現}` で書式制約も指定可能。

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

いずれの方式でも、リソースクラスのメソッドには `JaxRsHttpRequest` を引数として定義し、`getPathParam("パラメータ名")` で値を取得する。

---

#### クエリーパラメータ (`GET /users/search?name=Duke` の `name=Duke` を受け取る場合)

ルーティングはクエリーパラメータを除いたパスでマッピングする。

```xml
<!-- XMLルーティング方式 -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

リソースクラスでは `getParamMap()` でパラメータを取得し、`BeanUtil.createAndCopy()` でFormクラスにマッピングする。

```java
public HttpResponse search(JaxRsHttpRequest req) {

  // リクエストパラメータをBeanに変換
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

  // バリデーションの実行
  ValidatorUtil.validate(form);

  // 業務ロジックを実行する(省略)
}

public class UserSearchForm {
  private String name;
  // 省略
}
```

---

#### ルーティング設定

**XML方式 (`RoutesMapping`)**

コンポーネント設定ファイルで `RoutesMapping` をディスパッチハンドラとして設定する。

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

**`@Path` アノテーション方式 (`PathOptionsProviderRoutesMapping`)**

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定し、`JaxRsPathOptionsProvider` でベースパッケージを指定する。

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

**注意点**
- Jakarta RESTful Web Services の `@PathParam` / `@QueryParam` アノテーションは使用できない。必ず `JaxRsHttpRequest` から取得すること。
- `@Path` アノテーション方式はJBoss/WildFlyでは使用不可。それらの場合はXMLルーティング定義を使用すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s9, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s8