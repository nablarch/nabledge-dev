## パスパラメータ・クエリーパラメータの実装（RESTfulウェブサービス）

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` + `BeanUtil.createAndCopy()` でFormクラスにマッピングします。ルーティングは `routes.xml` で設定します。

---

**根拠**:

### ルーティング設定（routes.xml）

**パスパラメータの場合** — `:パラメータ名` 形式でパスを定義します。`requirements` で値の制約（正規表現）も設定できます。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**クエリーパラメータの場合** — クエリーパラメータ（`?name=Duke` 等）は **除いた** パスのみを設定します。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

---

### リソースクラスの実装

**パスパラメータの取得**:

```java
@Produces(MediaType.APPLICATION_JSON)
public User delete(JaxRsHttpRequest req) {
    // JaxRsHttpRequestからパスパラメータの値を取得する
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**クエリーパラメータの取得**:

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

- Jakarta RESTful Web Services標準の **`@PathParam`** アノテーションは使用できません。`JaxRsHttpRequest#getPathParam()` を使用してください。
- 同様に **`@QueryParam`** アノテーションも使用できません。`JaxRsHttpRequest#getParamMap()` + `BeanUtil` を使用してください。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3