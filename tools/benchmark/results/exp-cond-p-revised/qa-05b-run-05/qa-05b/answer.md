**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert()` でDB登録します。リクエストボディのJSONは `BodyConvertHandler`（`Jackson2BodyConverter`）が自動的にフォームクラスに変換します。

**根拠**:

**1. リクエストの流れ**

1. `WebFrontController` がリクエストを受信し、ハンドラキューに委譲
2. `BodyConvertHandler` がリクエストボディ（JSON）をフォームクラスに変換
3. `JaxRsBeanValidationHandler` が `@Valid` に基づいてバリデーション実行
4. アクションクラスが業務ロジックを実行してDBに登録

**2. フォームクラスの実装**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

プロパティは全てString型で宣言する。

**3. アクションクラスの実装**

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

- `@Path`・`@POST` でURLとHTTPメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でバリデーション実行
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換
- `UniversalDao.insert()` でDB登録
- ステータスコード `201 Created` を返却

**4. ハンドラキューの最小構成**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | リクエストパスからアクションを決定 |
| 6 | BodyConvertHandler | JSONをフォームクラスへ変換 |
| 7 | JaxRsBeanValidationHandler | `@Valid` によるバリデーション実行 |

**5. JSONサポートの設定（Jersey環境）**

Jersey環境では `JerseyJaxRsHandlerListFactory` を使用することで、JSONコンバータ（`Jackson2BodyConverter`）が自動的に設定される。

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
- `BodyConvertHandler` に設定されたコンバータが対応していないMIMEでリクエストが来た場合、ステータスコード `415`（サポートしていないメディアタイプ）が返される
- ルーティングアダプタより後ろのハンドラ（`BodyConvertHandler` 等）は、ハンドラキューに直接設定せず、ルーティングアダプタに対して設定する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, restful-web-service-resource-signature.json:s1