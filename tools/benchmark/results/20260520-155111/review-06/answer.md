**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリーパラメータは `getParamMap()` + `BeanUtil.createAndCopy()` でFormに変換する。ルーティングはXML定義（routes.xml）または `@Path` アノテーションの2方式がある。

**根拠**:

### ルーティング設定（XML定義方式）

まず `RoutesMapping` をディスパッチハンドラとして設定する：

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

### パスパラメータ（例: `GET /users/123`）

**routes.xml** でパスパラメータ部に名前と制約を設定する：

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**リソースクラス**で `JaxRsHttpRequest#getPathParam()` により取得する：

```java
@Produces(MediaType.APPLICATION_JSON)
public User delete(JaxRsHttpRequest req) {
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

> **注意**: Jakarta RESTful Web Services の `@PathParam` アノテーションは使用できない。

### クエリーパラメータ（例: `GET /users/search?name=Duke`）

**routes.xml** はクエリーパラメータ部を除いたパスのみ設定する：

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラス**で `getParamMap()` → `BeanUtil.createAndCopy()` でFormに変換する：

```java
public HttpResponse search(JaxRsHttpRequest req) {
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
  ValidatorUtil.validate(form);
  // 業務ロジックを実行する（省略）
}

public UserSearchForm {
  private String name;
  // 省略
}
```

> **注意**: Jakarta RESTful Web Services の `@QueryParam` アノテーションは使用できない。

### ルーティング設定（@Pathアノテーション方式）

`@Path` アノテーションを使う場合は、ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更する：

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

アノテーションによるパスパラメータの定義：

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

`{パラメータ名}` でパラメータを定義し、`{パラメータ名 : 正規表現}` で書式制約も指定できる。

**注意点**:
- XML定義方式では `RoutesMapping`、`@Path` アノテーション方式では `PathOptionsProviderRoutesMapping` を使う（混在不可）
- `@Path` アノテーション方式は JBoss/WildFly（vfsファイルシステム）では使用できない
- クエリーパラメータはルーティング設定には含めず、Java側で取得する

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s3`, `adapters-router-adaptor.json:s4`, `adapters-router-adaptor.json:s6`, `adapters-router-adaptor.json:s7`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`