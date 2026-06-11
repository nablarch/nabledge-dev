**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けたメソッドを実装し、`BeanUtil`でエンティティに変換後、`UniversalDao.insert()`でDBに登録する。

**根拠**:

**1. リソース（アクション）クラスの実装**

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

ポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付ける指定をする
- `@Valid` アノテーションでリクエストのバリデーションを実行する（`JaxRsBeanValidationHandler` が処理する）
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換する
- `UniversalDao.insert()` でDBに登録する
- 登録成功時はステータスコード `201 (CREATED)` を返す

**2. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

ポイント:
- プロパティは全て `String` 型で宣言する
- Bean Validationのアノテーションでバリデーションルールを定義する

**3. JSONコンバータの設定（Jersey使用時）**

Jersey環境では `JerseyJaxRsHandlerListFactory` を使うことで、JSONコンバータ（`Jackson2BodyConverter`）が自動的に設定される。

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
- `@Consumes` に設定されたMIMEと異なるContent-Typeがリクエストに含まれる場合、ステータスコード `415` が返却される
- Jakarta RESTful Web Servicesで規定されている `@PathParam` や `@QueryParam` はNablarchでは使用不可。パスパラメータは `JaxRsHttpRequest.getPathParam()` で取得する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, libraries-bean-validation.json:s17, libraries-universal-dao.json:s6, adapters-jaxrs-adaptor.json:s2