**結論**: RESTfulウェブサービスでパスパラメータ（URLパスの一部）やクエリーパラメータ（URL末尾の `?name=value`）を受け取るには、メソッド引数に `JaxRsHttpRequest` を定義し、それぞれ `getPathParam()` / `getParamMap()` で値を取得する。ルーティング設定はXMLのルート定義ファイル（routes.xml）または `@Path` アノテーションの2方式がある。

---

**根拠**:

## パスパラメータの実装

URLの例: `GET /users/123`（`123` をパスパラメータとして受け取る）

### ルーティング設定（routes.xml）

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

`users/:id` のように `:パラメータ名` の形式でパスの可変部分を定義する。`<requirements>` で値の形式を正規表現で制約できる。

### リソースクラスの実装

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
  // JaxRsHttpRequestからパスパラメータの値を取得する
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

パスパラメータは `JaxRsHttpRequest#getPathParam(パラメータ名)` で取得する。パラメータ名はルーティング定義で設定した名前と一致させる。

---

## クエリーパラメータの実装

URLの例: `GET /users/search?name=Duke`

### ルーティング設定（routes.xml）

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

クエリーパラメータ（`?` 以降）はルーティング設定には含めない。パスのみを定義する。

### リソースクラスの実装

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

クエリーパラメータは `JaxRsHttpRequest#getParamMap()` で取得し、`BeanUtil.createAndCopy()` を使ってFormクラスにマッピングするのが定石。

---

## @Path アノテーションによるルーティング（代替方式）

routes.xml の代わりに `@Path` アノテーションでルーティングを定義することもできる。

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

    @GET
    @Path("/bar/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

`{パラメータ名}` の形式でパスの可変部分を定義し、`{パラメータ名 : 正規表現}` で書式を制約できる。パラメータ値の取得方法は routes.xml 方式と同じく `getPathParam()` を使用する。

この方式を使うには、ディスパッチハンドラを `RoutesMapping` から `PathOptionsProviderRoutesMapping` に変更し、`JaxRsPathOptionsProvider` を設定する必要がある。

---

**注意点**:
- Jakarta RESTful Web Services で規定されている `@PathParam` および `@QueryParam` アノテーションは使用できない。必ず `JaxRsHttpRequest` から値を取得すること。
- `@Path` アノテーション方式は、JBoss/WildFly のようにバーチャルファイルシステムを使うアプリケーションサーバでは使用できない。その場合は routes.xml 方式を使うこと。
- ルーティングの設定では `RoutesMapping`（または `PathOptionsProviderRoutesMapping`）をハンドラキューの最後に設定し、初期化対象のリストにも追加すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, restful-web-service-resource-signature.json:s1, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9

---