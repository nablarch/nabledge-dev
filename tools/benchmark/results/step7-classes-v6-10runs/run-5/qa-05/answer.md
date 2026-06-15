**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil.createAndCopy` でフォームをエンティティに変換後、`UniversalDao.insert` でDBに登録します。

**根拠**:

**1. フォームクラスの作成**

リクエストのJSONフィールドを受け取るフォームを作成します。プロパティは全てString型で宣言します。

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` アノテーションでフォームに対してBean Validationを実行する（バリデーションエラー時は `ApplicationException` がスローされる）
- `BeanUtil.createAndCopy` でフォームをエンティティに変換する
- `UniversalDao.insert` でDBに登録する
- レスポンスとしてステータスコード `201 Created` を返す

**3. JSONコンバータの設定**

JSON変換は `Jackson2BodyConverter` が担います。Jersey環境では `JerseyJaxRsHandlerListFactory` を設定することで自動的にJSON/XML/form-urlencoded/multipartのコンバータが設定されます。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  <!-- 省略 -->
</component>
```

**注意点**:
- リクエストの `Content-Type` が `application/json` でない場合は、ステータスコード `415`（サポートしていないメディアタイプ）が返される
- 使用するアプリケーションサーバにJacksonがバンドルされていない場合は、Jacksonモジュールをアプリケーションモジュールと一緒にデプロイすること

参照: restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4