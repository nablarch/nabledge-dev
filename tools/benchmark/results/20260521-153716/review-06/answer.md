Step 5・6・7を実行します。

---

**Step 5: 回答生成**

全セクションを確認しました。直接回答を生成します。

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam("名前")` で取得し、クエリーパラメータは `req.getParamMap()` を `BeanUtil` でFormにマッピングして取得します。ルーティングはXMLのルート定義ファイル（`routes.xml`）か `@Path` アノテーションの2方式で設定できます。

**Step 6: Verify**

Nablarch固有のクレームを抽出して確認：
- `JaxRsHttpRequest#getPathParam("id")` → s2に明記 ✅
- `JaxRsHttpRequest` を仮引数として定義 → s1,s2に明記 ✅
- `BeanUtil.createAndCopy` でFormにマッピング → s3に明記 ✅
- `routes.xml` にルート定義 → s4に明記 ✅
- `RoutesMapping` コンポーネント → s3(router)に明記 ✅
- XML記法 `users/:id` → s2に明記 ✅
- `<requirements>` → s2に明記 ✅
- `PathOptionsProviderRoutesMapping` → s7に明記 ✅
- `@Path` アノテーション、`{param}` 記法、`JaxRsPathOptionsProvider` → s8,s9,s7に明記 ✅
- Jakarta RESTful Web Services規定の `@PathParam` / `@QueryParam` は使用不可 → s2,s3に明記 ✅

`verify_result = PASS`

---

## 回答

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam("パラメータ名")` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormクラスにマッピングして取得します。ルーティングはXMLルート定義ファイルと `@Path` アノテーションの2方式があります。

---

**根拠**

### ルーティング方式1: XMLルート定義ファイル

クラスパス直下に `routes.xml` を作成し、URLとアクションクラスをマッピングします。

**コンポーネント設定（ `RoutesMapping` をハンドラキュー末尾に設定）**:

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
```

`RoutesMapping` は初期化対象リストにも追加が必要です。

**routes.xml（パスパラメータ定義）**:

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**routes.xml（クエリーパラメータの場合）**:

クエリーパラメータはルーティング定義に含めず、パスのみでマッピングします。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

---

### ルーティング方式2: `@Path` アノテーション

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定し、アクションクラスに `@Path` アノテーションを付与します。

**コンポーネント設定**:

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**アクションクラス実装例（パスパラメータ）**:

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
    @Path("/bar/{id : \\d+}")  // 正規表現で数値のみ許容
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

---

### パスパラメータの取得（実装）

`JaxRsHttpRequest` を仮引数として定義し、`getPathParam("パラメータ名")` で取得します。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

### クエリーパラメータの取得（実装）

`JaxRsHttpRequest#getParamMap()` で取得したMapを `BeanUtil.createAndCopy` でFormクラスにマッピングします。

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

---

**注意点**

- Jakarta RESTful Web Services標準の `@PathParam` アノテーションは使用できません。パスパラメータの取得には必ず `JaxRsHttpRequest#getPathParam` を使用してください。
- 同様に、`@QueryParam` アノテーションも使用できません。
- `@Path` アノテーション方式は、JBoss/WildFlyのようなvfsファイルシステムを使うアプリケーションサーバでは使用できません。その場合はXMLルート定義ファイルを使用してください。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9

---