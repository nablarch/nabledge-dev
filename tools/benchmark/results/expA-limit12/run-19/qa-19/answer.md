**結論**: NablarchのRESTfulウェブサービスでは、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与するとリクエストボディのJSONが自動的にFormクラスに変換され、`BeanUtil.createAndCopy()`でEntityに変換した後`UniversalDao.insert()`でDBに登録できる。

**根拠**:

**処理の流れ（仕組み）**

```
クライアント
  → WebFrontController
  → ハンドラキュー（トランザクション制御ハンドラ → ルーティングアダプタ → BodyConvertHandler → BeanValidationハンドラ）
  → アクションクラス（業務ロジック実行）
  → JaxRsResponseHandler（レスポンス返却）
```

BodyConvertHandlerが往路でJSONを Formクラスに変換し、アクションの戻り値もBodyConvertHandlerが復路でJSONに変換する。トランザクション制御ハンドラが処理成功時にコミット、例外発生時にロールバックを行う。

**Formクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付けることを指定
- `@Valid`: Bean Validationによるバリデーションを実行（`JaxRsBeanValidationHandler`が処理）
- `BeanUtil.createAndCopy()`: FormをEntityに変換
- `UniversalDao.insert()`: DB登録
- 戻り値としてステータスコード`201`（CREATED）を返却

**BodyConvertHandlerのJSON対応設定**

JerseyまたはRESTEasy環境では、`JerseyJaxRsHandlerListFactory`（または`ResteasyJaxRsHandlerListFactory`）を使用することで、`Jackson2BodyConverter`が自動的に設定され、JSONの変換が行われる。

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

**注意点**:
- FormのプロパティはすべてString型で宣言すること（Bean Validationの要件）
- `@Path`と`@POST`アノテーションでURLとHTTPメソッドのマッピングを定義する
- `@Consumes`のMIMEとリクエストの`Content-Type`が一致しない場合、ステータスコード`415`が返却される
- `BodyConvertHandler`はルーティングアダプタ（`RoutesMapping`）よりも後ろのハンドラキューに設定すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-resource-signature.json:s1, adapters-jaxrs-adaptor.json:s2