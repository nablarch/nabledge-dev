**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータは`JaxRsHttpRequest#getPathParam(String)`で取得し、クエリパラメータは`JaxRsHttpRequest#getParamMap()`からBeanUtilでFormにマッピングして取得する。ルーティングの定義方法はXML(routes.xml)方式と`@Path`アノテーション方式の2種類がある。

---

**根拠**:

### ルーティングの設定

**方式1: routes.xml（XMLファイル方式）**

クラスパス直下に`routes.xml`を作成し、URLとアクションのマッピングを定義する。

パスパラメータの例（`:id`で定義、正規表現で制約も可）:

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

クエリパラメータの場合、ルーティング定義はクエリ部分を除いたパスのみ記述する:

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**方式2: `@Path`アノテーション方式**

`PathOptionsProviderRoutesMapping`をディスパッチハンドラに設定した上で、アクションクラスに`@Path`アノテーションを付与してルーティングを定義する:

```java
@Path("/sample")
public class SampleAction {

    @GET
    @Path("/foo/{param}")          // パスパラメータは {パラメータ名} で定義
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
        // 省略
    }

    @GET
    @Path("/bar/{id : \\d+}")      // 正規表現で書式を制限することも可能
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

コンポーネント定義での設定例:

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

### リソースクラスでのパラメータ取得

**パスパラメータの取得**（`getPathParam`を使用）:

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    // JaxRsHttpRequestからパスパラメータの値を取得する
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**クエリパラメータの取得**（`getParamMap`→BeanUtilでFormにマッピング）:

```java
public HttpResponse search(JaxRsHttpRequest req) {
    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する（省略）
}

// クエリパラメータをマッピングするForm
public class UserSearchForm {
    private String name;
    // 省略
}
```

---

**注意点**:

- Jakarta RESTful Web Servicesで規定されている`@PathParam`および`@QueryParam`アノテーションは**使用できない**。必ず`JaxRsHttpRequest`経由で取得すること。
- `@Path`アノテーション方式はJBoss/WildFlyなど、クラスパス配下のリソースを独自ファイルシステム(vfs)で管理するアプリケーションサーバでは使用できない。その場合はXMLのroutes.xml方式を使用すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s9, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s3