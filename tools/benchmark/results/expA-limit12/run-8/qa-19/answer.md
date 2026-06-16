**結論**: NablarchのRESTfulウェブサービスでJSONを受け取りDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付与し、フォームを引数として受け取り、`BeanUtil.createAndCopy()` でエンティティに変換した後 `UniversalDao.insert()` で登録します。

**根拠**:

**1. フォームクラスの作成**

リクエストボディのJSONをマッピングするフォームクラスを作成します。プロパティは全てString型で宣言します。

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

- `@Path` でURLパスを定義し、`@POST` でPOSTリクエストにマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` により、JSONボディがフォームに自動変換される（リクエストボディ変換ハンドラの `Jackson2BodyConverter` が処理する）
- `@Valid` でBeanValidationが実行される
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録する
- 登録完了時はステータスコード `201` を返す

**3. 処理の流れ（最小ハンドラ構成）**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 6 | リクエストボディ変換ハンドラ | JSONボディ → フォームクラスに変換 |
| 7 | Bean Validationハンドラ | フォームのバリデーション実行 |

**4. Jakarta RESTful Web Servicesアダプタの設定**

Jersey環境では `JerseyJaxRsHandlerListFactory` を設定することで、JSONの `Jackson2BodyConverter` が自動的に組み込まれます。

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
- フォームのプロパティは全てString型で宣言すること
- RESTfulウェブサービスでは `@Context` アノテーションを使ったServletリソースのインジェクションやCDIは使用不可
- `application/json` 以外のContent-Typeが送信された場合、ステータスコード `415` が返される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2