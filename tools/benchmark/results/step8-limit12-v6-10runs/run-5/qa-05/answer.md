**結論**: `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたPOSTメソッドでJSONをFormとして受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. フォームクラスを作成する**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```
- プロパティは全てString型で宣言する。

**2. リソース（アクション）クラスを実装する**

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

実装のポイント：
- `@Path` + `@POST` でURLとHTTPメソッドをマッピングする。
- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると、リクエストボディ変換ハンドラが `Jackson2BodyConverter` でJSONを `ProjectForm` に変換する。
- `@Valid` を付けることでBean Validationが実行される（`JaxRsBeanValidationHandler` が処理）。
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する。
- 戻り値にステータスコード `201`（CREATED）を表す `HttpResponse` を返す。

**3. JSONコンバータの設定（コンポーネント定義）**

Jersey環境ではルーティングアダプタの設定に `JerseyJaxRsHandlerListFactory` を使うことで、`Jackson2BodyConverter` が自動的に設定される：

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

**4. ユニバーサルDAOの設定（コンポーネント定義）**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `Content-Type: application/json` と異なるMIMEでリクエストされた場合、ステータスコード `415` が返される。
- `@Valid` によるバリデーションエラー時のレスポンスは `JaxRsResponseHandler` の設定に依存する。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s8, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6