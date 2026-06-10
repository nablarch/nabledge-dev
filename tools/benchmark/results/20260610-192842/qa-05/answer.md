**結論**: RESTful Webサービスでリソースクラスを実装する際は、`@Path`／`@POST`／`@Consumes(APPLICATION_JSON)`／`@Valid` をアクションメソッドに付与し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換後 `UniversalDao.insert()` でDB登録、戻り値は `HttpResponse(201)` を返す。

---

**根拠**

#### 1. フォームクラスの作成

クライアントから受け取るJSONのフィールドに対応したフォームを作成する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. リソース（アクション）クラスの実装

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Path` をクラスに付与して URIとアクションクラスを紐付ける
- `@POST` でHTTPメソッドを指定する
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、BodyConvertHandlerがリクエストボディをフォームクラスへ自動変換する
- `@Valid` を付与することで、JaxRsBeanValidationHandlerがフォームのバリデーションを自動実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 登録成功時は `HttpResponse(201)` を返す

#### 3. メソッドシグネチャの選択肢

| 引数定義 | 説明 |
|---|---|
| 引数無し | パラメータ不要の場合 |
| フォーム(Java Beans) | リクエストボディをフォームに変換して受け取る場合（JSON登録はこれ） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得したい場合 |
| 組み合わせ | 例: `save(ProjectForm form, JaxRsHttpRequest request)` |

戻り値は `void`（204 NoContent）、Java Beans（レスポンスボディに変換）、`HttpResponse`（任意のステータスコード）の3種類から選べる。

#### 4. ルーティング設定（コンポーネント定義）

```xml
<component name="packageMapping"
           class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jerseyの場合: BodyConvertHandler(Jackson2BodyConverter)とBeanValidationHandlerが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

`PathOptionsProviderRoutesMapping` のコンポーネントは初期化対象リストへの追加も必要。

#### 5. UniversalDAO設定

```xml
<!-- コンポーネント名は"daoContextFactory"で固定 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**
- Jerseyアダプタ（`JerseyJaxRsHandlerListFactory`）を使用すると、BodyConvertHandler（Jackson2BodyConverterによるJSON変換）とBeanValidationHandlerが自動設定される。手動でハンドラ構成する場合は7つのハンドラを正しい順序で設定する必要がある。
- フォームのプロパティは全て `String` 型で宣言すること（`int` 等は不可）。
- `UniversalDao.insert()` を使用するには `BasicDaoContextFactory` がコンポーネント定義に存在している必要がある。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, libraries-universal-dao.json:s6