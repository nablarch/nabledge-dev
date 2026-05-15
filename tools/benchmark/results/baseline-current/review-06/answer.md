**結論**: NablarchのREST APIでは、パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` + `BeanUtil` でFormに変換します。ルーティングはXML定義か `@Path` アノテーションの2通りで設定できます。

**根拠**:

### パスパラメータの実装

#### ルーティング設定（XML方式）
`routes.xml` でパスパラメータ部分に名前を定義します。`<requirements>` で値の書式を正規表現で制限できます。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

#### ルーティング設定（@Path アノテーション方式）
`{パラメータ名}` の記法でパスパラメータを定義。`{パラメータ名 : 正規表現}` で書式を制限できます。

```java
@Path("/users")
public class UsersAction {

    @GET
    @Path("/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public User find(JaxRsHttpRequest request) {
        Long id = Long.valueOf(request.getPathParam("id"));
        return UniversalDao.findById(User.class, id);
    }
}
```

#### リソースクラスの実装（共通）
パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で取得します。引数名はルーティング設定で定義した名前と一致させます。

> **重要**: Jakarta RESTful Web Services 標準の `@PathParam` は使用不可です。

### クエリーパラメータの実装

#### ルーティング設定
クエリーパラメータ（`?name=Duke` の部分）はルーティングの定義に含めません。クエリーパラメータを除いたパスのみを定義します。

```xml
<!-- XML方式 -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

#### リソースクラスの実装
`JaxRsHttpRequest#getParamMap()` でパラメータを取得し、`BeanUtil.createAndCopy()` でFormクラスにマッピングします。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジック（省略）
}
```

> **重要**: Jakarta RESTful Web Services 標準の `@QueryParam` は使用不可です。

### @Path アノテーション方式のルーティング設定（コンポーネント定義）

`@Path` アノテーションによるルーティングを有効にするには、ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更します。

```xml
<component name="packageMapping"
    class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  ...
</component>
```

**注意点**:
- `@PathParam` / `@QueryParam`（JAX-RS標準アノテーション）は Nablarch では使用できません。必ず `JaxRsHttpRequest` 経由で取得してください。
- クエリーパラメータのルーティング定義にはクエリー文字列（`?` 以降）を含めないこと。
- `@Path` アノテーション方式では、パスパラメータの記法が XML方式の `:id` ではなく `{id}` になります（Jakarta RESTful Web Services仕様準拠）。
- JBoss/WildFly（vfsを使用するアプリケーションサーバ）では `@Path` アノテーション方式は使用できません。その場合は XML方式を使用してください。

参照: `restful-web-service-resource-signature.json#s2`, `restful-web-service-resource-signature.json#s3`, `adapters-router-adaptor.json#s4`, `adapters-router-adaptor.json#s6`, `adapters-router-adaptor.json#s8`, `adapters-router-adaptor.json#s9`