**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータとクエリパラメータのどちらも `JaxRsHttpRequest` から取得します。ルーティング定義はXML（routes.xml）または `@Path` アノテーションの2方式があります。

**根拠**:

## ルーティング設定（XML方式）

クラスパス直下に `routes.xml` を作成し、ディスパッチハンドラとして `RoutesMapping` を設定します。

```xml
<!-- コンポーネント定義ファイル -->
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>

<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->
      <component-ref name="packageMapping" />
    </list>
  </property>
</component>

<!-- 初期化対象に追加 -->
<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="packageMapping"/>
    </list>
  </property>
</component>
```

## パスパラメータ

`GET /users/123` の `123` をパスパラメータとして受け取る例です。

**routes.xml（ルート定義）**:
```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**リソースクラス（Java）**:
```java
@Produces(MediaType.APPLICATION_JSON)
public User delete(JaxRsHttpRequest req) {
  // JaxRsHttpRequestからパスパラメータの値を取得する
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

## クエリパラメータ

`GET /users/search?name=Duke` のように検索条件をURL末尾で渡す例です。

**routes.xml（クエリパラメータ部分は不要）**:
```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラス（Java）**:
```java
public HttpResponse search(JaxRsHttpRequest req) {

  // リクエストパラメータをBeanに変換
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

  // バリデーションの実行
  ValidatorUtil.validate(form)

  // 業務ロジックを実行する(省略)
}

// クエリーパラメータをマッピングするForm
public UserSearchForm {
  private String name;
  // 省略
}
```

## ルーティング設定（@Path アノテーション方式）

バージョン1.2.0以降では、`@Path` アノテーションによるルーティングも利用できます。この場合、ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更します。

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

アクションクラスへのアノテーション付与例（パスパラメータ含む）:
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

**注意点**:
- Jakarta RESTful Web Services で規定されている `@PathParam` および `@QueryParam` アノテーションはNablarchでは使用できません。必ず `JaxRsHttpRequest#getPathParam` / `getParamMap` で取得してください。
- `@Path` アノテーション方式は、JBossやWildflyなど独自ファイルシステムを使うアプリケーションサーバでは使用できません。その場合はXML方式を使用してください。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9