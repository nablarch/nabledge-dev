**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスに `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` を呼び出す。

**根拠**:

**1. Formクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ（プロパティは全てString型で宣言する）
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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` でBean Validationが実行される（バリデーションエラー時は `ApplicationException` が送出される）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録
- 登録完了時はステータスコード `201` (CREATED) を返す

**3. Jacksonアダプタの設定（コンポーネント定義）**

Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を使用するとJSONコンバータ（`Jackson2BodyConverter`）が自動設定される：

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

**4. ユニバーサルDAOのコンポーネント設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formクラスのプロパティは**全てString型**で宣言すること（バリデーションルール設定の要件）
- Jacksonがウェブアプリケーションサーバにバンドルされていない場合は、Jacksonモジュールをアプリケーションと一緒にデプロイすること
- Content-TypeがFormに設定されたMIMEと異なる場合、ステータスコード `415` が返却される

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/adapters/adapters-jaxrs-adaptor.json:s2, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/libraries/libraries-universal-dao.json:s6