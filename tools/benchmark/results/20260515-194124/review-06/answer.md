**結論**: NablarchのRESTful Webサービスでは、パスパラメータとクエリーパラメータはどちらも `JaxRsHttpRequest` から取得します。Jakarta RESTful Web Services標準の `@PathParam` / `@QueryParam` アノテーションは**使用できない**点に注意が必要です。ルーティングには2種類の方法（XMLファイル定義 / `@Path` アノテーション）があります。

**根拠**:

### パスパラメータ（例: `GET /users/123`）

**ルーティング設定（routes.xml）**

クラスパス直下の `routes.xml` に、パスパラメータ部に名前と形式を定義します。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**リソースクラスの実装**

引数に `JaxRsHttpRequest` を受け取り、`getPathParam("id")` で値を取得します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

### `@Path` アノテーションでルーティングする方法（ルーティングアダプタ v1.2.0以降）

XMLの代わりに `@Path` アノテーションを使ってルーティングを定義することもできます。パスパラメータは `{パラメータ名}` 形式、正規表現での制約は `{パラメータ名 : 正規表現}` 形式で記述します。

```java
@Path("/users")
public class UsersResource {

    @GET
    @Path("/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public User find(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        return UniversalDao.findById(User.class, id);
    }
}
```

> **注意**: 一部のサーバ（JBoss/WildFlyなどvfsベースのサーバ）では `@Path` アノテーションが使用できないため、XMLによるルーティング定義を使用すること。

### クエリーパラメータ（例: `GET /users/search?name=Duke`）

**ルーティング設定**

クエリーパラメータはパスに含めず、パスのみでマッピングします。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスの実装**

`JaxRsHttpRequest.getParamMap()` で取得したパラメータを `BeanUtil` を使ってFormクラスにマッピングします。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジックを実行する
}

public class UserSearchForm {
    private String name;
    // ...
}
```

**注意点**:

- Jakarta RESTful Web Services標準の `@PathParam` / `@QueryParam` アノテーションは**使用不可**（Nablarch独自の `JaxRsHttpRequest` を使う）
- `JaxRsHttpRequest` を引数に取ることで、パスパラメータ・クエリーパラメータ・HTTPヘッダの取得が可能
- `@Path` アノテーション方式を使う場合、パスパラメータの記法はJakarta RESTful Web Servicesの仕様に従った形式（`{名前}`）で記述する
- vfsベースのサーバ（JBoss/WildFlyなど）では `@Path` アノテーションが使用できないため、XMLルーティングを使用すること

参照: `restful-web-service-resource-signature.json#s2`, `restful-web-service-resource-signature.json#s3`, `adapters-router-adaptor.json#s9`, `adapters-router-adaptor.json#s6`