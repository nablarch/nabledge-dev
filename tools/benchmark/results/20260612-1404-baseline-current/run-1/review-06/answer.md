**結論**: ルーティングはXMLの`routes.xml`または`@Path`アノテーションで定義し、パスパラメータは`JaxRsHttpRequest#getPathParam()`、クエリーパラメータは`JaxRsHttpRequest#getParamMap()`で取得する。Jakarta RESTful Web Servicesの`@PathParam`・`@QueryParam`アノテーションは使用できない点に注意。

---

**根拠**

## ルーティング設定（2つのアプローチ）

### アプローチ1: XMLルート定義ファイル（`routes.xml`）

クラスパス直下に `routes.xml` を作成し、URLとアクションをマッピングする。

**コンポーネント設定（ハンドラキューに追加）:**

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

### アプローチ2: `@Path`アノテーション（ルーティングアダプタ v1.2.0以降）

`PathOptionsProviderRoutesMapping`をディスパッチハンドラとして使用する。

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

アクションクラスには`@Path`と`@GET`等を付与:

```java
@Path("/sample")
public class SampleAction {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Person> findAll() { /* 省略 */ }

    @POST
    @Produces(MediaType.APPLICATION_JSON)
    public int register(JaxRsHttpRequest request) { /* 省略 */ }
}
```

---

## パスパラメータの実装

**XMLルーティング定義（`:パラメータ名`形式）:**

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**`@Path`アノテーション方式（`{パラメータ名}`形式）:**

```java
@GET
@Path("/bar/{id : \\d+}")
@Produces(MediaType.APPLICATION_JSON)
public Person bar(JaxRsHttpRequest request) {
    int id = Integer.parseInt(request.getPathParam("id"));
    // 省略
}
```

**リソースクラスでの取得方法（共通）:**

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    // JaxRsHttpRequestからパスパラメータの値を取得する
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

## クエリーパラメータの実装

**URLの例:** `GET /users/search?name=Duke`

**ルーティング設定（クエリーパラメータを除いたパスのみ）:**

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスでの取得方法:**

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

---

**注意点**:
- Jakarta RESTful Web Servicesの`@PathParam`は**使用できない**。パスパラメータは`JaxRsHttpRequest#getPathParam()`で取得すること。
- Jakarta RESTful Web Servicesの`@QueryParam`も**使用できない**。クエリーパラメータは`JaxRsHttpRequest#getParamMap()`から`BeanUtil`でFormにマッピングすること。
- `@Path`アノテーション方式はJBoss/Wildflyのようなvfsを使うアプリケーションサーバでは使用不可。その場合はXMLルーティング定義を使用すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9