**結論**: RESTfulウェブサービスでJSON受信→DB登録を実装するには、Formクラスを作成し、リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付けて `UniversalDao.insert()` でDB登録する。

**根拠**:

① Formクラスの作成（プロパティはすべてString型）

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

② リソースクラスの実装

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラがJSONをFormに変換する
- `@Valid` を付けることでBean Validationによるバリデーションが実行される
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値として `201 Created` を表す `HttpResponse` を返す
- `@Path` + `@POST` アノテーションでURLとHTTPメソッドのマッピングを定義する

③ `@Path` アノテーションによるルーティングを使う場合のディスパッチハンドラ設定

```xml
<component name="packageMapping"
           class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
</component>
```

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの制約）
- `@Path` アノテーションを用いたルーティングは、JBoss/WildFlyでは使用不可。その場合は `routes.xml` を使ったXMLルーティング定義を使うこと
- リクエストボディ変換ハンドラ（`BodyConvertHandler`）はルーティングアダプタより後ろに設定する必要がある

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8