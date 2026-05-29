必要な情報が揃いました。Step 4でセクションを読み込みます。

`read_sections`:
- `restful-web-service-resource-signature.json:s1`
- `restful-web-service-resource-signature.json:s2`
- `restful-web-service-resource-signature.json:s3`
- `adapters-router-adaptor.json:s3`
- `adapters-router-adaptor.json:s4`
- `adapters-router-adaptor.json:s7`
- `adapters-router-adaptor.json:s8`
- `adapters-router-adaptor.json:s9`
- `restful-web-service-feature-details.json:s5`
- `restful-web-service-feature-details.json:s6`

Step 5〜8: 回答を生成します。

---

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得し、クエリパラメータは `JaxRsHttpRequest#getParamMap()` から `BeanUtil` でFormに変換して取得する。ルーティングはXMLベース（routes.xml）と `@Path` アノテーションの2方式から選択できる。

**根拠**:

### パスパラメータの実装

**方式1: XMLベースのルーティング（routes.xml）**

```xml
<!-- routes.xml: パスパラメータ部に名前を設定、正規表現で書式を制約 -->
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
    // ルート定義のパラメータ名を指定して取得
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

**方式2: `@Path` アノテーション**

```java
@Path("/sample")
public class TestAction {

    // {パラメータ名} で定義
    @GET
    @Path("/foo/{param}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
        // 省略
    }

    // {パラメータ名 : 正規表現} で書式制約
    @GET
    @Path("/bar/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

> **注意**: Jakarta RESTful Web Servicesの `@PathParam` は使用不可。必ず `JaxRsHttpRequest#getPathParam()` を使うこと。

---

### クエリパラメータの実装

```xml
<!-- routes.xml: クエリパラメータは除いたパスでマッピング -->
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

```java
public HttpResponse search(JaxRsHttpRequest req) {
    // getParamMap() でクエリパラメータを取得し、BeanUtil でFormへ変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());
    ValidatorUtil.validate(form);
    // 業務ロジックを実行する（省略）
}

public class UserSearchForm {
    private String name;
    // 省略
}
```

> **注意**: Jakarta RESTful Web Servicesの `@QueryParam` は使用不可。必ず `JaxRsHttpRequest#getParamMap()` を使うこと。

---

### ルーティングの設定（ディスパッチハンドラ）

**方式1: XMLベース（RoutesMapping）**

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

クラスパス直下に `routes.xml` を作成してURLとアクションをマッピングする。

**方式2: `@Path` アノテーション（PathOptionsProviderRoutesMapping）**

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

`applicationPath` にAPIのプレフィックス（`ApplicationPath` 相当）、`basePackage` に `@Path` アノテーションを付けたクラスを検索するパッケージを指定する。このコンポーネントは初期化対象リストへの追加も必要。

**注意点**:
- `@Path` アノテーション方式はJBoss/Wildflyのようにvfsでクラスパスを管理するサーバでは使用不可。その場合はXMLベースのルーティングを使うこと。
- XML方式と `@Path` アノテーション方式の併用は推奨されない。

参照: `restful-web-service-resource-signature.json:s2`, `restful-web-service-resource-signature.json:s3`, `adapters-router-adaptor.json:s3`, `adapters-router-adaptor.json:s7`, `adapters-router-adaptor.json:s8`, `adapters-router-adaptor.json:s9`

---