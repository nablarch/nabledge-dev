**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリーパラメータは `JaxRsHttpRequest#getParamMap()` を `BeanUtil` でFormにマッピングして取得する。ルーティングはXMLベース（`routes.xml`）と `@Path` アノテーション方式の2通りがある。

---

**根拠**:

#### パスパラメータ（例: `GET /users/123`）

**XMLベースのルーティング設定（routes.xml）**:
```xml
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

**リソースクラスの実装**:
```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
  Long id = Long.valueOf(req.getPathParam("id"));
  return UniversalDao.findById(User.class, id);
}
```

`@Path` アノテーション方式でのパスパラメータ定義（Jakarta RESTful Web Services仕様の `{パラメータ名}` 記法を使用）:
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

---

#### クエリーパラメータ（例: `GET /users/search?name=Duke`）

**ルーティング設定**: クエリーパラメータを除いたパスのみマッピングする
```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

**リソースクラスの実装**:
```java
public HttpResponse search(JaxRsHttpRequest req) {
  // リクエストパラメータをBeanに変換
  UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
  // バリデーションの実行
  ValidatorUtil.validate(form);
  // 業務ロジック（省略）
}

public class UserSearchForm {
  private String name;
  // 省略
}
```

---

#### ルーティングアダプタの設定

**XMLベース（`RoutesMapping`）**:
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

**`@Path` アノテーション方式（`PathOptionsProviderRoutesMapping`）**:
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

**注意点**:
- Jakarta RESTful Web Services 標準の `@PathParam` や `@QueryParam` は **使用できない**。必ず `JaxRsHttpRequest` 経由で取得すること。
- JBoss / WildFly を使用する場合は `@Path` アノテーション方式は使用できない（クラスパスが vfs 管理のためアノテーション付きクラスの検索ができない）。この場合は XMLベースの `routes.xml` を使用すること。

---

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