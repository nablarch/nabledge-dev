**結論**: パスパラメータは `routes.xml` の `:paramName` 記法（またはアノテーション方式の `{paramName}`）でルーティングを定義し、`JaxRsHttpRequest#getPathParam()` で値を取得する。クエリーパラメータはルーティング定義にクエリー部分を含めず、`JaxRsHttpRequest#getParamMap()` から `BeanUtil.createAndCopy()` でFormクラスにマッピングする。なお、Jakarta RESTful Web Services 標準の `@PathParam` / `@QueryParam` は使用できない。

---

**根拠**:

### ルーティング方式の選択

2つのルーティング定義方式がある。

#### 方式1: XML (routes.xml) によるルーティング

ディスパッチハンドラとして `RoutesMapping` をハンドラキューの末尾に設定する。

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

クラスパス直下に `routes.xml` を作成してURLとアクションをマッピングする。

#### 方式2: `@Path` アノテーションによるルーティング

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定する。

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

アクションクラスに `@Path` アノテーションと HTTP メソッドアノテーション（`@GET` など）を付与してマッピングを定義する。

---

### パスパラメータの実装

#### XML方式

`routes.xml` でパスパラメータ部を `:paramName` で定義する（正規表現制約も設定可）。

```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

リソースクラスのメソッドでは `JaxRsHttpRequest#getPathParam()` で値を取得する。

```java
@Produces(MediaType.APPLICATION_JSON)
public User delete(JaxRsHttpRequest req) {
  // JaxRsHttpRequestからパスパラメータの値を取得する
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

#### `@Path` アノテーション方式

パスの一部を `{パラメータ名}` で定義する。`{パラメータ名 : 正規表現}` で書式制約も指定できる。

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
        int id = Integer.parseInt(request.getPathParam("id");
        // 省略
    }
}
```

---

### クエリーパラメータの実装

#### ルーティング設定

クエリーパラメータ部分を除いたパスのみをルーティングに定義する。

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

#### リソースクラスの実装

`JaxRsHttpRequest#getParamMap()` でクエリーパラメータのMapを取得し、`BeanUtil.createAndCopy()` でFormクラスにマッピングする。

```java
public HttpResponse search(JaxRsHttpRequest req) {

  // リクエストパラメータをBeanに変換
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

  // バリデーションの実行
  ValidatorUtil.validate(form)

  // 業務ロジックを実行する(省略)
}

// クエリーパラメータをマッピングするForm
public UserSearchForm {
  private String name;
  // 省略
}
```

---

**注意点**:
- `@PathParam` (Jakarta RESTful Web Services標準) は使用できない。パスパラメータの取得は必ず `JaxRsHttpRequest#getPathParam()` を使用すること。
- `@QueryParam` (Jakarta RESTful Web Services標準) は使用できない。クエリーパラメータの取得は `JaxRsHttpRequest#getParamMap()` を使用すること。
- `@Path` アノテーション方式は、クラスパス配下のリソースをバーチャルファイルシステムで管理するサーバ（JBoss/WildFly等）では使用できないため、その場合は XML 方式を使用すること。

参照:
- リソース(アクション)クラスの実装に関して
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md
  パスパラメータを扱う
  クエリーパラメータを扱う
  リソースクラスのメソッドのシグネチャ
- ルーティングアダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md
  ディスパッチハンドラを設定する
  ルート定義ファイルを作成する
  ディスパッチハンドラを変更する
  マッピングの実装方法
  パスパラメータの定義