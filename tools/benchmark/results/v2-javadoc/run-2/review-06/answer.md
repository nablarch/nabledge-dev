セクション内容を取得しました。Step 5: 回答を生成します。

---

**結論**: パスパラメータは `@Path("{id}")` アノテーションでルーティングを定義し `JaxRsHttpRequest#getPathParam()` で取得、クエリーパラメータはルーティングをパスのみで定義し `JaxRsHttpRequest#getParamMap()` + `BeanUtil.createAndCopy()` でFormに変換する。

---

**根拠**:

### ルーティング設定（@Pathアノテーション方式）

`PathOptionsProviderRoutesMapping` をコンポーネント定義に設定することで `@Path` アノテーションによるルーティングが使えるようになる。

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

`PathOptionsProviderRoutesMapping` は初期化リストへの追加も必要。

---

### パスパラメータの実装

`@Path` にて `{パラメータ名}` で定義し、`JaxRsHttpRequest#getPathParam()` で取得する。正規表現制約（`{id : \\d+}`）も指定可能。

```java
@Path("/sample")
public class SampleAction {

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

---

### クエリーパラメータの実装

ルーティングはクエリーパラメータを除いたパスで定義し、メソッド内で `getParamMap()` → `BeanUtil` → `ValidatorUtil` の順で処理する。

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

Formのプロパティは全て `String` 型で宣言する。

---

### （参考）XMLベースのルーティング設定

`routes.xml` で定義する場合はパスパラメータを `:id` 記法で書き、正規表現制約を `<requirements>` で付加する。

```xml
<!-- パスパラメータ -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>

<!-- クエリーパラメータ（パスのみ指定） -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

この場合のパスパラメータ取得も `JaxRsHttpRequest#getPathParam("id")` で同様。

---

**注意点**:
- Jakarta RESTful Web Services 標準の `@PathParam` / `@QueryParam` は**使用不可**。必ず `JaxRsHttpRequest` 経由で取得すること。

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `restful-web-service-getting-started-search.json:s1`, `adapters-router-adaptor.json:s7`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`

---