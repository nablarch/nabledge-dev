全セクション取得完了。回答を生成します。

---

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリパラメータは `JaxRsHttpRequest#getParamMap()` + `BeanUtil.createAndCopy()` で取得する。ルーティングはXML定義と `@Path` アノテーション定義の2方式がある。

**根拠**:

---

### 1. パスパラメータ

**XMLルーティング定義の場合** (`routes.xml` にパラメータ名と形式を設定):

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

```java
@Produces(MediaType.APPLICATION_JSON)
public User delete(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**`@Path` アノテーション定義の場合** (`{パラメータ名}` または `{パラメータ名 : 正規表現}` で記述):

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

### 2. クエリパラメータ

ルーティング定義ではクエリ文字列を除いたパスだけを指定し、パラメータはリソースクラス内で取得する。

```xml
<!-- XMLルーティング定義の場合 -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

```java
public HttpResponse search(JaxRsHttpRequest req) {

    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジック（省略）
}
```

---

### 3. ルーティングのコンポーネント設定

**XMLルーティング方式** (`RoutesMapping` を使用):

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

**`@Path` アノテーション方式** (`PathOptionsProviderRoutesMapping` を使用):

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

どちらの方式も、コンポーネントを `initializer` の `initializeList` に追加して初期化が必要。

**注意点**:
- `@PathParam`（Jakarta RESTful Web Services 標準）は使用不可。必ず `JaxRsHttpRequest#getPathParam()` を使う。
- `@QueryParam`（Jakarta RESTful Web Services 標準）も使用不可。`getParamMap()` + `BeanUtil` を使う。
- `@Path` アノテーション方式は、JBoss/WildFlyのvfsなど独自ファイルシステムを使うアプリケーションサーバでは動作しない場合がある。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-getting-started-search.json:s1