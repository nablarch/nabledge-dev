**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータはルーティング定義で `:id` 形式（XMLルート定義）または `{id}` 形式（`@Path` アノテーション）で定義し、クエリパラメータはクエリ文字列をそのまま `JaxRsHttpRequest#getParamMap()` で取得します。

**根拠**:

### ルーティング設定（2つの方法）

#### 方法1: XMLルート定義ファイル（`routes.xml`）

まずコンポーネント定義でディスパッチハンドラ `RoutesMapping` を設定します。

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

クラスパス直下の `routes.xml` でURLとアクションをマッピングします。

```xml
<routes>
  <!-- パスパラメータあり: :id でパラメータ定義 -->
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>

  <!-- クエリパラメータあり: クエリ部分はルーティング定義に含めない -->
  <get path="users/search" to="Users#search"/>
</routes>
```

#### 方法2: `@Path` アノテーション（バージョン1.2.0以降）

ディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更します。

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

アクションクラスに `@Path` アノテーションでマッピングを定義します。

```java
@Path("/users")
public class UsersAction {

    // パスパラメータあり: {id} または {id : \d+} で正規表現指定可
    @GET
    @Path("/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public User find(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }

    // クエリパラメータあり: パスにクエリは含めない
    @GET
    @Path("/search")
    public HttpResponse search(JaxRsHttpRequest request) {
        // 省略
    }
}
```

### リソースクラスの実装

**パスパラメータの取得**（`GET /users/123` の `123` を取得する場合）:

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest request) {
    // ルーティング定義のパラメータ名を指定して取得
    Long id = Long.valueOf(request.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**クエリパラメータの取得**（`GET /users/search?name=Duke` の場合）:

```java
public HttpResponse search(JaxRsHttpRequest request) {
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

**注意点**:
- `JaxRsHttpRequest` を使ってパスパラメータ・クエリパラメータの両方を取得します。メソッドの仮引数に `JaxRsHttpRequest` を定義する必要があります。
- Jakarta RESTful Web Servicesで規定されている `@PathParam` や `@QueryParam` アノテーションは**使用できません**。
- JBoss/WildFly環境では `@Path` アノテーションによるルーティングは使用できないため、XMLルート定義を使用してください。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9