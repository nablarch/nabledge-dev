セクション内容を読み込みました。Step 5〜8を実行します。

---

**結論**: パスパラメータは `routes.xml` で `:id` 記法でマッピングし `JaxRsHttpRequest#getPathParam()` で取得、クエリパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil.createAndCopy()` でFormにマッピングする。ルーティングは `RoutesMapping` をディスパッチハンドラとして設定する。

---

**根拠**:

### 1. ルーティング設定（DispatchHandler）

`RoutesMapping` をハンドラキューの末尾に設定し、初期化リストにも登録する。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>

<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- その他のハンドラは省略 -->
      <component-ref name="packageMapping" />
    </list>
  </property>
</component>

<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="packageMapping"/>
    </list>
  </property>
</component>
```

### 2. ルート定義ファイル（routes.xml）

クラスパス直下に `routes.xml` を作成し、URLとアクションのマッピングを設定する。

### 3. パスパラメータの実装（例：`GET /users/123`）

**routes.xml**:
```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**リソースクラス**:
```java
@Produces(MediaType.APPLICATION_JSON)
public User delete(JaxRsHttpRequest req) {
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

> **注意**: Jakarta RESTful Web Services の `@PathParam` は使用できない。

### 4. クエリパラメータの実装（例：`GET /users/search?name=Duke`）

**routes.xml**（クエリパラメータ部分は除いたパスのみ設定）:
```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラス**:
```java
public HttpResponse search(JaxRsHttpRequest req) {
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
  ValidatorUtil.validate(form);
  // 業務ロジックを実行する(省略)
}

public UserSearchForm {
  private String name;
  // 省略
}
```

> **注意**: Jakarta RESTful Web Services の `@QueryParam` は使用できない。

### 5. @Path アノテーションによる代替ルーティング

`RoutesMapping` のバージョン1.2.0以降では、`@Path` アノテーションでもルーティングを定義できる（一部のアプリケーションサーバは非対応）。

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

`{パラメータ名}` でパスパラメータを定義し、`{パラメータ名 : 正規表現}` で書式制限も指定できる。取得には `JaxRsHttpRequest#getPathParam()` を使用する。

---

**注意点**:
- メソッド引数でパスパラメータやクエリパラメータを扱う場合は `JaxRsHttpRequest` を仮引数に定義する必要がある
- `@PathParam`/`@QueryParam`（Jakarta REST標準）は使用不可
- `@Path` アノテーション方式はJBoss/WildflyのvFSベースのサーバでは使用できないため、XMLルーティングを使う

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s3`, `adapters-router-adaptor.json:s4`, `adapters-router-adaptor.json:s9`

---