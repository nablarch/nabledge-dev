### Answer

RESTfulウェブサービスでパスパラメータとクエリーパラメータを扱う実装方法を説明します。

---

## パスパラメータ（URLパスの一部を受け取る）

### ルーティング設定

`routes.xml` でパスパラメータ部に名前を設定し、`requirements` で書式を制限します。

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

`JaxRsHttpRequest#getPathParam(String)` でパラメータ値を取得します。引数にはルーティング設定で指定したパラメータ名を渡します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

> **注意:** Jakarta RESTful Web Services の `@PathParam` アノテーションは使用できません。

---

## クエリーパラメータ（URL末尾の検索条件を受け取る）

例: `GET /users/search?name=Duke`

### ルーティング設定

クエリーパラメータを除いたパスでマッピングします。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

### リソースクラスの実装

`JaxRsHttpRequest#getParamMap()` でクエリーパラメータを取得し、`BeanUtil` でFormクラスにマッピングします。取り出したパラメータは必要に応じてバリデーションしてください。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する（省略）
}

public class UserSearchForm {
    private String name;
    // 省略
}
```

> **注意:** Jakarta RESTful Web Services の `@QueryParam` アノテーションは使用できません。

---

## `@Path` アノテーションを使ったルーティング定義（別方式）

`@Path` アノテーションでルーティングを定義する場合は、Jakarta RESTful Web Services の仕様に従った記法でパスパラメータを定義します。

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

`{パラメータ名 : 正規表現}` の形式で書式を制限でき、パラメータ値は同様に `JaxRsHttpRequest#getPathParam(String)` で取得します。