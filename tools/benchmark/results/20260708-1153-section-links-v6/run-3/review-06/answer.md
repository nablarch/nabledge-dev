**結論**: パスパラメータは `routes.xml`（またはXML定義）でパス変数を定義し、リソースクラスのメソッド引数に `JaxRsHttpRequest` を使って `getPathParam("名前")` で取得します。クエリーパラメータは `JaxRsHttpRequest#getParamMap()` で取得し、`BeanUtil.createAndCopy` でFormにマッピングします。

**根拠**:

---

### ルーティングの設定方法

**方法A: XMLによるルート定義ファイル（`routes.xml`）**

`RoutesMapping` をディスパッチハンドラとして設定し、クラスパス直下の `routes.xml` にマッピングを記述します。

```xml
<!-- コンポーネント設定ファイル -->
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

`RoutesMapping` は初期化対象のリストにも追加が必要です。

**方法B: `@Path` アノテーションによるルーティング（バージョン1.2.0以降）**

JBoss/WildFly 以外のアプリケーションサーバで使用できます。`PathOptionsProviderRoutesMapping` を設定します。

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

---

### パスパラメータの実装

**XMLルーティングの場合：**

```xml
<!-- routes.xml -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
  // JaxRsHttpRequestからパスパラメータの値を取得する
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

**`@Path` アノテーションの場合：**

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

---

### クエリーパラメータの実装

ルーティングはクエリーパラメータを除いたパスで定義します。

```xml
<!-- routes.xml -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

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
- Jakarta RESTful Web Services の `@PathParam` / `@QueryParam` アノテーションは使用不可。必ず `JaxRsHttpRequest` を使うこと。
- JBoss/WildFly 環境では `@Path` アノテーションによるルーティングは使用できず、XMLルート定義を使う必要がある。

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
  Jakarta RESTful Web ServicesのPathアノテーションでマッピングする
  ディスパッチハンドラを変更する
  マッピングの実装方法
  パスパラメータの定義