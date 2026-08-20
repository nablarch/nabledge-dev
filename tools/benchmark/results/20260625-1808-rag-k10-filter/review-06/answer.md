### Answer

Nablarch の RESTful ウェブサービスでは、**パスパラメータ**と**クエリーパラメータ**の2種類の方法でURLからデータを受け取れます。

---

## パスパラメータ（URLパスの一部を受け取る）

### ルーティング設定

`routes.xml` でパスパラメータに名前を付けます。数値のみ許容する場合は `requirements` で正規表現を指定します。

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

`JaxRsHttpRequest` の引数を受け取り、`getPathParam(String name)` でルーティング設定のパラメータ名を指定して値を取得します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));  // "id" はルーティング設定の名前
    return UniversalDao.findById(User.class, id);
}
```

> **注意:** Jakarta RESTful Web Services の `@PathParam` アノテーションは使用できません。必ず `JaxRsHttpRequest#getPathParam()` を使ってください。

### `@Path` アノテーションによるルーティング（別方式）

`@Path` アノテーションを使う場合は Jakarta RESTful Web Services の記法で記述します。

```java
@GET
@Path("/bar/{id : \\d+}")
@Produces(MediaType.APPLICATION_JSON)
public Person bar(JaxRsHttpRequest request) {
    int id = Integer.parseInt(request.getPathParam("id"));
    // 省略
}
```

---

## クエリーパラメータ（URL末尾の `?key=value` を受け取る）

例: `GET /users/search?name=Duke`

### ルーティング設定

クエリーパラメータ部分は除いたパスでマッピングします。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

### リソースクラスの実装

`JaxRsHttpRequest#getParamMap()` でクエリーパラメータを取得し、`BeanUtil.createAndCopy()` で Form クラスにマッピングします。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    // クエリーパラメータをFormに変換
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

> **注意:** Jakarta RESTful Web Services の `@QueryParam` アノテーションは使用できません。必ず `JaxRsHttpRequest` 経由で取得してください。

---

## まとめ

| 種類 | ルーティング設定 | 取得方法 |
|------|----------------|---------|
| パスパラメータ | `users/:id`（+ `requirements` で正規表現） | `req.getPathParam("id")` |
| クエリーパラメータ | クエリー部分なしのパスでマッピング | `BeanUtil.createAndCopy(Form.class, req.getParamMap())` |