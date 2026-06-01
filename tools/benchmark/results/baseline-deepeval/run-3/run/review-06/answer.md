**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で、クエリパラメータは `req.getParamMap()` を `BeanUtil.createAndCopy()` でFormに変換して取得する。ルーティングはXML (`routes.xml`) か `@Path` アノテーションの2方式で設定できる。

---

**根拠**:

#### パスパラメータ

**ルーティング設定（XML方式）**: クラスパス直下の `routes.xml` にパスパラメータを `:id` の形で定義する。`requirements` で値の書式を正規表現で制約できる。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**ルーティング設定（`@Path` アノテーション方式）**: Jakarta RESTful Web Services仕様に従い `{パラメータ名}` で記述する。`{id : \\d+}` のように正規表現も指定できる。

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

**リソースクラスの実装**: メソッド引数に `JaxRsHttpRequest` を定義し、`getPathParam()` でルーティング定義に指定したパラメータ名を渡して値を取得する。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

#### クエリパラメータ

**ルーティング設定**: クエリパラメータ部（`?name=Duke` の部分）はルーティング定義には含めない。パスのみを記述する。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスの実装**: `JaxRsHttpRequest#getParamMap()` でパラメータMapを取得し、`BeanUtil.createAndCopy()` でFormクラスにマッピングする。

```java
public HttpResponse search(JaxRsHttpRequest req) {

    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する(省略)
}

// クエリーパラメータをマッピングするForm
public class UserSearchForm {
    private String name;
    // 省略
}
```

---

**注意点**:
- Jakarta RESTful Web Services規定の `@PathParam` は**使用できない**。`JaxRsHttpRequest#getPathParam()` を使うこと。
- Jakarta RESTful Web Services規定の `@QueryParam` も**使用できない**。`JaxRsHttpRequest#getParamMap()` + `BeanUtil.createAndCopy()` を使うこと。
- `@Path` アノテーション方式は、クラスパス配下のリソースをvfsなどの独自ファイルシステムで管理するJBoss/Wildflyでは使用できない。そのような場合はXML方式を使うこと。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s9, restful-web-service-resource-signature.json:s1

---