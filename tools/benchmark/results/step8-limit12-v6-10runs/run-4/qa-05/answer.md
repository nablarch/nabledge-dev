**結論**: REST APIでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormを受け取り、`BeanUtil.createAndCopy` でEntityに変換して `UniversalDao.insert` で登録する。

**根拠**:

**1. Formクラスの作成**

クライアントから受け取る値をマッピングするFormを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションクラスの実装**

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
- `@Valid` を付けることで、JaxRsBeanValidationハンドラがFormに対してBean Validationを実行する
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- 登録成功時はステータスコード `201` (CREATED) を返す
- `@Path` と `@POST` アノテーションでURLとのマッピングを定義する

**3. アダプタの設定**

JSON変換には `Jackson2BodyConverter` が使用される。Jersey環境の場合、コンポーネント設定ファイルに以下を設定する。

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

**4. ユニバーサルDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの仕様要件）
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` よりも後に設定すること（リクエストボディの変換後にバリデーションを実行するため）

参照: restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6