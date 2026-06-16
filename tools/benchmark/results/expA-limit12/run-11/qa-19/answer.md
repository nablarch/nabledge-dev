Step 5 で回答を生成します。

**結論**: NablarchのRESTfulウェブサービスでJSONを受け取りDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フォームを受け取ったあと `BeanUtil.createAndCopy()` でエンティティに変換し `UniversalDao.insert()` でDBに登録します。

**根拠**:

**1. 処理の流れ**

リクエストを受信したWebフロントコントローラはハンドラキューに処理を委譲し、`BodyConvertHandler` がJSONリクエストボディをフォームクラスに変換、`JaxRsBeanValidationHandler` がバリデーションを実行、その後アクションクラスが実行されます。

**2. アクションクラスの実装例**

フォームクラス（プロパティは全て `String` 型で宣言）:

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

アクションクラス（URLマッピングと登録処理）:

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONを受け付けるメディアタイプを指定
- `@Valid` でBean Validationによるバリデーションを実行
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換
- `UniversalDao.insert()` でDBに登録
- ステータスコード `201`（Created）を返す

**3. ハンドラ構成（最小構成）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み／エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | リクエストボディ変換ハンドラ | JSONボディをフォームクラスに変換 |
| 7 | Bean Validationハンドラ | フォームのバリデーション実行 |

**4. Jersey環境でのJSON対応設定**

JerseyやRESTEasy環境では `JerseyJaxRsHandlerListFactory` を使うと、JSONコンバータ（`Jackson2BodyConverter`）が自動的に設定されます:

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
- フォームクラスのプロパティは全て `String` 型で宣言する（Bean Validationの仕様による）
- `BodyConvertHandler` はルーティングアダプタより後ろに設定すること
- `Content-Type: application/json` が `@Consumes` の設定と一致しない場合はステータスコード `415` が返される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4