**結論**: RESTfulウェブサービスでURLパスの一部（パスパラメータ）を受け取るには`@Path`アノテーションに`{パラメータ名}`形式で定義し、クエリーパラメータはルーティングから除いたパスで設定する。どちらも`JaxRsHttpRequest`を介して値を取得する。

---

**根拠**:

## ルーティング設定

### 方法1: `@Path`アノテーション（推奨）

`PathOptionsProviderRoutesMapping`をコンポーネント設定ファイルに設定する：

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

### 方法2: `routes.xml`（XMLルーティング）

パスパラメータは `:パラメータ名` 形式、クエリーパラメータはパスから除いて定義する：

```xml
<!-- パスパラメータあり -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>

<!-- クエリーパラメータ（?name=Duke などのURL末尾パラメータ） -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

---

## リソースクラスの実装

### パスパラメータの受け取り（`@Path`アノテーション方式）

```java
@Path("/sample")
public class TestAction {

    // /sample/foo/{任意の文字列}
    @GET
    @Path("/foo/{param}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
        // 省略
    }

    // /sample/bar/{数値のみ}
    @GET
    @Path("/bar/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

### パスパラメータの受け取り（`routes.xml`方式）

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    // JaxRsHttpRequestからパスパラメータの値を取得する
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

### クエリーパラメータの受け取り（`GET /users/search?name=Duke` の例）

```java
public HttpResponse search(JaxRsHttpRequest req) {

    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する（省略）
}

// クエリーパラメータをマッピングするForm
public class UserSearchForm {
    private String name;
    // 省略
}
```

---

**注意点**:
- Jakarta RESTful Web Services標準の`@PathParam`・`@QueryParam`アノテーションは使用できない（`JaxRsHttpRequest`から取得すること）
- `@Path`アノテーション方式はJBoss/Wildflyなどvfsベースのアプリケーションサーバでは使用できない。その場合はXMLルーティング定義を使用すること

参照: adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3