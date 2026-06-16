**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、受け取ったFormを `BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録します。

**根拠**:

**1. Formクラスの作成**

JSONのキーにマッピングされるフォームクラスを作成します。プロパティは全てString型で宣言します。

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラ（`BodyConvertHandler`）がJSONボディをFormクラスに変換します。
- `@Valid` アノテーションを付けることで、Bean Validationハンドラ（`JaxRsBeanValidationHandler`）がFormのバリデーションを実行します。バリデーションエラー時は `ApplicationException` がスローされます。
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録します。
- 登録成功時はステータスコード `201` を返します。

**3. JSON変換の仕組み（アダプタ設定）**

JSONの変換には `Jackson2BodyConverter` が使われます。使用するサーバの環境に応じて以下のいずれかをコンポーネント定義に設定します。

Jersey環境:
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

RESTEasy環境では `JerseyJaxRsHandlerListFactory` の代わりに `ResteasyJaxRsHandlerListFactory` を使用します。

**注意点**:
- `@Consumes` に指定したMIMEと異なるContent-Typeがリクエストに設定されていた場合、ステータスコード `415` が返されます。
- `BeanUtil.createAndCopy` でFormからEntityへのコピーを行うため、EntityとFormのプロパティ名を一致させる必要があります。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-jaxrs-adaptor.json:s2