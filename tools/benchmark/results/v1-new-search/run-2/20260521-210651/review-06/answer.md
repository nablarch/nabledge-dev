必要なセクションを読み込みました。Step 5〜8を実行します。

**Step 4 — read_sections:**
- `restful-web-service-resource-signature.json:s1`
- `restful-web-service-resource-signature.json:s2`
- `restful-web-service-resource-signature.json:s3`
- `adapters-router-adaptor.json:s3`
- `adapters-router-adaptor.json:s4`
- `adapters-router-adaptor.json:s6`
- `adapters-router-adaptor.json:s7`
- `adapters-router-adaptor.json:s8`
- `adapters-router-adaptor.json:s9`
- `restful-web-service-feature-details.json:s5`
- `restful-web-service-feature-details.json:s6`

---

**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリパラメータは `JaxRsHttpRequest#getParamMap()` で取得する。ルーティングは **XMLルート定義ファイル** か **`@Path`アノテーション** の2方式から選択できる。

---

**根拠**:

### ルーティング設定 — 方式1: XMLルート定義ファイル

コンポーネント設定に `RoutesMapping` をディスパッチハンドラとして登録する。

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

クラスパス直下の `routes.xml` にURLとアクションのマッピングを記述する。

---

### ルーティング設定 — 方式2: `@Path`アノテーション（推奨）

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして使用する。

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

アクションクラスでは `@Path`・`@GET` などのアノテーションでマッピングを定義する。

```java
@Path("/sample")
public class SampleAction {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Person> findAll() {
        // 省略
    }

    @POST
    @Produces(MediaType.APPLICATION_JSON)
    public int register(JaxRsHttpRequest request) {
        // 省略
    }
}
```

---

### パスパラメータの取得

**XMLルート定義の場合** — `:paramName` 記法でパラメータを定義し、正規表現で書式を制限できる。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**`@Path`アノテーションの場合** — `{paramName}` または `{paramName : 正規表現}` で定義する。

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

いずれの方式でも **`JaxRsHttpRequest#getPathParam(パラメータ名)`** でパスパラメータの値を取得する。メソッドには仮引数として `JaxRsHttpRequest` を定義する。

---

### クエリパラメータの取得

`GET /users/search?name=Duke` のような場合、ルーティングはクエリパラメータ部分を除いたパスで定義する。

```xml
<!-- XMLルート定義の場合 -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

リソースクラスでは `JaxRsHttpRequest#getParamMap()` でパラメータを取得し、`BeanUtil` でFormクラスにマッピングする。

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
- Jakarta RESTful Web Services仕様の `@PathParam`・`@QueryParam` アノテーションは **使用できない**。パスパラメータ・クエリパラメータはともに `JaxRsHttpRequest` 経由で取得すること。
- `@Path`アノテーション方式はJBoss/WildflyなどVFSを使用するアプリケーションサーバでは使用できない。その場合はXMLルート定義を使用すること。
- `RoutesMapping`（XMLルート定義方式）はコンポーネントの初期化対象リストへの登録が必要。

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s3`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`

---