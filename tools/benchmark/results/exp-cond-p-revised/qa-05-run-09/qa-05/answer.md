**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付け、`UniversalDao.insert` でBeanに変換して登録します。

**根拠**:

**1. Formクラスの作成**

クライアントから受信するJSONのフィールドに対応するFormを作成します。プロパティは全て `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でバリデーション(Bean Validation)を実行する
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値としてHTTPステータス `201 Created` を返す

**3. URLマッピングの設定（ルーティングアダプタ）**

`@Path`アノテーションを使用するためには、`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定します。

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
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**4. JSON変換の設定（BodyConvertHandler）**

Jersey用の `JerseyJaxRsHandlerListFactory` を使用すると、JSONコンバータとして `Jackson2BodyConverter` が自動的に設定されます。手動で設定する場合は `BodyConvertHandler` の `bodyConverters` プロパティに `Jackson2BodyConverter` を追加します。

**注意点**:
- Formのプロパティは全て `String` 型で宣言すること（Beanへの変換前に不正な値が入力されても例外を防ぐため）
- `UniversalDao` を使用するには、コンポーネント設定ファイルに `BasicDaoContextFactory` の定義が必要です

参照: restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, libraries-universal-dao.json:s6