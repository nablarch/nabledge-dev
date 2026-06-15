**結論**: `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を使ってフォームでJSONを受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**1. フォームの作成**（リクエストボディのJSONをマッピング）

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```
- プロパティは**全てString型**で宣言する。

**2. アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBean Validationを実行（バリデーションエラー時は `ApplicationException` を送出）
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDB登録
- レスポンスはステータスコード `201` (Created) を返す

**3. URLマッピング設定**（コンポーネント設定ファイル）

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
        <!-- Jersey環境の場合 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```
`JerseyJaxRsHandlerListFactory` を設定すると、JSONコンバータ (`Jackson2BodyConverter`) とBean Validationハンドラが自動的に構成される。

**4. ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `PathOptionsProviderRoutesMapping` は `BasicApplicationInitializer` の `initializeList` に追加が必要
- JBoss/WildFlyでは `@Path` アノテーションによるルーティングは使用不可（XMLのルート定義ファイルを使用すること）
- RESTfulウェブサービスでは `@Version` を使った楽観的ロックの際、リクエストボディに直接バージョン番号を含めること（ETag/If-Match は非対応）

参照: restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, libraries-universal-dao.json:s6