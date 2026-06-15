**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` をアクションメソッドに付け、引数にFormクラスを受け取り、`BeanUtil.createAndCopy` でEntityに変換して `UniversalDao.insert` でDBに登録する。

**根拠**:

**① フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全て `String` 型**で宣言する（バリデーション前にBeanへの変換が行われるため）。

**② アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける。リクエストボディのFormへの変換はリクエストボディ変換ハンドラが行う（`Jackson2BodyConverter` を使用）。
- `@Valid` アノテーションでバリデーションを有効にする。`JaxRsBeanValidationHandler` がFormのBean Validationを実行する。
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する。
- 戻り値に `HttpResponse(201)` を返すと、ステータスコード `201 Created` がクライアントへ返却される。

**③ コンポーネント設定（JSONアダプタ）**

Jersey環境の場合は `JerseyJaxRsHandlerListFactory` を設定すると、`Jackson2BodyConverter`（JSON変換）と `JaxRsBeanValidationHandler`（バリデーション）が自動的に設定される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**④ ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が異なる場合はHTTP `415` が返却される。
- RESTfulウェブサービスでは `@PathParam`（JAX-RS標準）は使用できない。パスパラメータは `JaxRsHttpRequest#getPathParam` で取得する。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-bean-validation.json:s17, libraries-universal-dao.json:s6