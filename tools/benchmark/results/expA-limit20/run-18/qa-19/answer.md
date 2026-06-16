**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フォームクラスで受け取った値を `BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDB登録する。

**根拠**:

**① フォームクラスの作成**

クライアントから送信されるJSONをマッピングするフォームクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**② アクションクラスの実装**

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
- `@Valid` を付けることで、リクエストボディ変換後に `JaxRsBeanValidationHandler` がBean Validationを自動実行する
- `BeanUtil.createAndCopy` でフォームをエンティティクラスに変換し、`UniversalDao.insert` でDB登録する
- 登録成功時はステータスコード `201` (Created) を返す

**③ ハンドラ構成の仕組み**

リクエストがJSONとして受け取られる仕組みは以下のハンドラが担う（最小ハンドラ構成）:

| # | ハンドラ | 役割 |
|---|---|---|
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | リクエストボディ変換ハンドラ (`BodyConvertHandler`) | JSONリクエストボディをフォームに変換 |
| 7 | Bean Validationハンドラ | フォームのバリデーション実行 |

**④ JSONコンバータの設定**

Jersey環境では `JerseyJaxRsHandlerListFactory` を使用することで、JSONコンバータとして `Jackson2BodyConverter` が自動設定される:

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
- `Content-Type: application/json` がリクエストヘッダに設定されていない場合、ステータスコード `415` (Unsupported Media Type) が返される
- フォームクラスのプロパティは全てString型で宣言すること（Bean Validationの仕様上の制約）
- `@Valid` を省略するとバリデーションが実行されないため、必ず付けること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s5