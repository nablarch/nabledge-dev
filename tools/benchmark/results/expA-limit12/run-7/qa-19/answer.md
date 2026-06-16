**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドで JSON をフォームクラスとして受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDB登録します。ステータスコード 201 を返す `HttpResponse` を戻り値にします。

**根拠**:

処理の全体的な流れは次の通りです。

1. `BodyConvertHandler`（リクエストボディ変換ハンドラ）が、リクエストヘッダの `Content-Type: application/json` を見て、アクションメソッドの `@Consumes` アノテーションに対応する `Jackson2BodyConverter` を用いてリクエストボディをフォームクラスに変換します。
2. `JaxRsBeanValidationHandler` が `@Valid` アノテーションのあるメソッドに対してBean Validationを実行します。
3. アクションメソッドが実行され、`UniversalDao.insert()` でDBに登録されます。

**フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全て String 型**で宣言すること。

**アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けます。
- `@Valid` でBean Validationを実行します。バリデーションエラー時は後続処理に委譲せず `ApplicationException` を送出します。
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティクラスに変換します。
- 登録成功時のレスポンスはステータスコード `201`（Created）の `HttpResponse` を返します。

**ハンドラの最小構成（BodyConvertHandler での JSON コンバータ設定）**

`Jakarta RESTful Web Services アダプタ`（JerseyまたはRESTEasy用）を使用すると、`BodyConvertHandler` に `Jackson2BodyConverter`（JSONコンバータ）が自動設定されます。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jersey用アダプタを使用する場合 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- `@Consumes` に設定した MIME と異なる `Content-Type` がリクエストヘッダに設定されている場合、ステータスコード `415`（Unsupported Media Type）が返されます。
- RESTful ウェブサービスでは `@Context` アノテーションを使用した Servlet リソースのインジェクションや CDI は使用できません。
- フォームのプロパティは全て String 型で宣言する必要があります（型変換はBeanUtilで行われます）。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2