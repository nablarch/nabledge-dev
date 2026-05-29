Step 5: 回答を生成します。

---

**結論**: パスパラメータは `@Path` アノテーションの `{param}` 記法でルーティング定義し、`JaxRsHttpRequest#getPathParam()` で取得する。クエリパラメータはルーティング設定にパラメータ記述は不要で、`req.getParamMap()` + `BeanUtil` でFormクラスにマッピングする。

**根拠**:

### ルーティング設定（@Path アノテーション方式）

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定する。

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

初期化対象リストへの追加も必要。

---

### パスパラメータ（例: `GET /users/123`）

`@Path` の `{パラメータ名}` 記法で定義し、`getPathParam()` で取得する。正規表現による書式制限も指定可能。

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

    // 数値のみ許容する場合
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

### クエリパラメータ（例: `GET /projects?clientId=1&projectName=foo`）

ルーティング設定ではクエリパラメータ部分は記述せず、パスのみ定義する。アクションでは `getParamMap()` + `BeanUtil` でFormにマッピングする。

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

Formクラスのプロパティはすべて `String` 型で宣言する。

---

**注意点**:
- Jakarta RESTful Web Services の `@PathParam` は使用不可（`JaxRsHttpRequest#getPathParam()` を使う）
- Jakarta RESTful Web Services の `@QueryParam` は使用不可（`req.getParamMap()` + `BeanUtil` を使う）
- `@Path` アノテーション方式は、JBoss/Wildfly など独自ファイルシステム（vfs）を使うアプリケーションサーバでは使用不可。その場合は XML ルーティング方式（`routes.xml` + `RoutesMapping`）を使う

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s7`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`, `restful-web-service-getting-started-search.json:s1`

---