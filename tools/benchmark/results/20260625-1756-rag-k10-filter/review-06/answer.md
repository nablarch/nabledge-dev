### Answer

NablarchのRESTfulウェブサービスでは、パスパラメータとクエリーパラメータの2通りの方法でURLからパラメータを受け取れます。

---

## パスパラメータ（例：`GET /users/123`）

### ルーティング設定

`routes.xml` でパスパラメータ部に名前と制約を設定します。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

### リソースクラスの実装

`JaxRsHttpRequest#getPathParam(String)` でパラメータを取得します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

> **注意:** Jakarta RESTful Web Servicesの `@PathParam` アノテーションは使用できません。

---

## クエリーパラメータ（例：`GET /users/search?name=Duke`）

### ルーティング設定

クエリーパラメータ部を除いたパスでマッピングします。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

### リソースクラスの実装

`JaxRsHttpRequest#getParamMap()` で取得し、`BeanUtil` でFormクラスにマッピングします。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    // リクエストパラメータをFormに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーション実行
    ValidatorUtil.validate(form);

    // 業務ロジック（省略）
}

public class UserSearchForm {
    private String name;
    // 省略
}
```

> **注意:** Jakarta RESTful Web Servicesの `@QueryParam` アノテーションは使用できません。

---

## `@Path` アノテーションを使う方法（ルーティングアダプタ利用時）

ルーティング設定ファイルではなく `@Path` アノテーションでルーティングを定義する場合は、Jakarta RESTful Web Servicesの記法でパスパラメータを記述できます。

```java
@Path("/sample")
public class TestAction {

    @GET
    @Path("/bar/{id : \\d+}")  // 正規表現で数値のみ許容
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

`{パラメータ名}` でパラメータを定義し、`{パラメータ名 : 正規表現}` で書式を制限できます。値の取得は同様に `getPathParam(String)` を使います。