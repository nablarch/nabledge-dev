Step 5〜8: 回答生成、検証、出力を実施します。

**verify**: すべてのNablarch固有の主張（`getPathParam`、`getParamMap`、`BeanUtil.createAndCopy`、XMLルーティング記法、`@Path`アノテーション記法）はセクション内容で直接裏付けられています。`verify_result = PASS`。

---

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil.createAndCopy()` でFormに変換して取得します。ルーティングは XMLベース（`routes.xml`）か `@Path` アノテーションの2通りで定義します。

---

**根拠**

### ルーティング設定 — XMLベース（`routes.xml`）

**パスパラメータの場合**：`:パラメータ名` でURLの該当部分を定義する。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**クエリーパラメータの場合**：クエリー文字列を除いたパスだけを定義する。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

---

### ルーティング設定 — `@Path` アノテーションベース

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして使用している場合は、`@Path` アノテーションでルーティングを定義できる。パスパラメータは `{パラメータ名}` 形式で記述し、正規表現も指定可能。

```java
@Path("/sample")
public class TestAction {

    // パスパラメータ（数値のみ許容）
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

### リソースクラスの実装

**パスパラメータの取得**：`JaxRsHttpRequest#getPathParam()` を使用する。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**クエリーパラメータの取得**：`JaxRsHttpRequest#getParamMap()` でパラメータMapを取得し、`BeanUtil.createAndCopy()` でFormクラスにマッピングする。

```java
public HttpResponse search(JaxRsHttpRequest req) {
    // クエリーパラメータをFormクラスにマッピング
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

---

**注意点**

- Jakarta RESTful Web Services標準の `@PathParam`、`@QueryParam` アノテーションは使用できない。`JaxRsHttpRequest` を経由して取得すること。
- `@Path` アノテーションによるルーティングは、JBoss/WildFlyなど一部のアプリケーションサーバ（vfsファイルシステムを使用するもの）では使用不可。その場合はXMLルーティング（`routes.xml`）を使用すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9

---