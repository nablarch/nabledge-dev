**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドでJSONをFormとして受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDBに登録する。

**根拠**:

**① Formクラスの作成**

クライアントから受け取るJSONのフィールドに対応したFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONをFormクラスに自動変換する（`Jackson2BodyConverter` が使用される）
- `@Valid` を付けることで `JaxRsBeanValidationHandler` がFormのBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でFormからEntityクラスに値をコピーする
- `UniversalDao.insert()` でDBにINSERTする
- `@Path` と `@POST` でURLとHTTPメソッドをマッピングする

**③ リクエストボディ変換ハンドラの設定（Jersey環境の場合）**

`JaxRsMethodBinderFactory` の `handlerList` に `JerseyJaxRsHandlerListFactory` を設定することで、JSONのコンバータ（`Jackson2BodyConverter`）やBean Validationハンドラが自動的に設定される。

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

コンポーネント定義に `BasicDaoContextFactory` を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Content-TypeヘッダとメソッドのConsumes指定が異なる場合、ステータスコード `415` (Unsupported Media Type) が返却される
- `@Valid` が設定されたメソッドでバリデーションエラーが発生した場合、`ApplicationException` がスローされ後続処理は実行されない

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, adapters-router-adaptor.json:s8