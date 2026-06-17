**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で取得し、クエリーパラメータは `req.getParamMap()` を `BeanUtil.createAndCopy` でFormに変換して利用する。ルーティングはXMLファイル（`routes.xml`）か `@Path` アノテーションの2方式で設定できる。

---

**根拠**

## パスパラメータ

### ① XMLによるルーティング定義（`routes.xml`）

`routes.xml` にパスパラメータ部を `:パラメータ名` で記述し、`RoutesMapping` をハンドラキューの末尾に設定する。

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

コンポーネント設定（`RoutesMapping` を使う場合）:

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

### ② `@Path` アノテーションによるルーティング定義

`PathOptionsProviderRoutesMapping` + `JaxRsPathOptionsProvider` を設定し、`@Path("{パラメータ名}")` で定義する。正規表現で書式制限も可能。

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

コンポーネント設定（`@Path` を使う場合）:

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

### アクション側でのパスパラメータ取得

いずれの方式でも、アクションメソッドの引数に `JaxRsHttpRequest` を受け取り、`getPathParam` で値を取得する。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

## クエリーパラメータ

ルーティング定義ではクエリーパラメータを含めずパスのみを設定し、アクション側で `req.getParamMap()` を `BeanUtil.createAndCopy` でFormに変換する。

ルーティング（`@Path` 方式）:

```java
@Path("/projects")
public class ProjectAction {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Project> find(JaxRsHttpRequest req) {

        // リクエストパラメータをBeanに変換
        ProjectSearchForm form =
                BeanUtil.createAndCopy(ProjectSearchForm.class, req.getParamMap());

        // BeanValidation実行
        ValidatorUtil.validate(form);

        ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, form);
        return UniversalDao.findAllBySqlFile(Project.class, "FIND_PROJECT", searchCondition);
    }
}
```

XML方式の場合のルーティング定義（クエリーパラメータはパスから除外）:

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

---

**注意点**

- Jakarta RESTful Web Servicesで規定されている `@PathParam` / `@QueryParam` アノテーションは使用できない。`JaxRsHttpRequest` を使って取得すること。
- `@Path` アノテーション方式は、JBoss/WildFly のようにクラスパスをvfsで管理するサーバでは使用できない。その場合はXML方式（`routes.xml` + `RoutesMapping`）を使うこと。
- Formクラスのプロパティは全て `String` 型で宣言すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-getting-started-search.json:s1